# For every slide in FOLDER_IDS (and all their subfolders):
 
#   1. Rename these layers (exact old name -> new name) here are some examples:
#         non_globally_sclerotic_glomeruli       -> Glom unit non-GSG
#         globally_sclerotic_glomeruli           -> GSG

 
#   2. Access control, so logged-in NON-ADMIN users see only those Y layers:
#         - the Y layers: everyone who can open the slide (the slide folder's
#           users and groups) gets READ access. Nobody's existing access is reduced.
#         - every other layer: all non-admin users and all groups are removed,
#           and public is turned off. Site admins still see everything.
 
#   3. PROTECTED_NAMES are NEVER renamed, and are made visible like the Y layers (PROTECTED_VISIBLE = True).
#      So non-admins see X layers in total; everything else is hidden.
 
# Nothing is ever deleted. Shapes are never changed.
 
# Safety:
#   - DRY_RUN = True (default) prints the full plan and writes plan.csv. No changes.
#   - A live run asks you to type YES, backs up every name and access list it
#     changes into runs/<time>/, and logs every change to changes.csv.
#   - Re-running is safe: it only changes what is still not right.
#   - Layer names that LOOK like one of the rename but are spelled differently
#     (e.g."GLOBALLY_sclerotic_glomeruli") are left completely
#     untouched and listed in the report for you to decide.
#   - Undo a live run: set RESTORE_RUN = "runs/<time>" and run again.
 
# How to run:
#   1. Fill in API_KEY and the 6 FOLDER_IDS.
#   2. Run with DRY_RUN = True. Read the report and plan.csv.
#   3. Set DRY_RUN = False, run, type YES.
#   4. Set DRY_RUN = True and run once more: it should report 0 changes left.
#   5. Log in as a normal (non-admin) user and open a few slides to confirm.

import os
import csv
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from collections import Counter, defaultdict
from girder_client import GirderClient

API_URL = "https://athena.rc.ufl.edu/api/v1/"
API_KEY = os.environ.get("ATHENA-API-KEY")

FOLDER_IDS = [
    # "FOLDER-ID-1",
    # "FOLDER-ID-2",
    # "FOLDER-ID-3",
    # "FOLDER-ID-4",
    # "FOLDER-ID-5",
    # "FOLDER-ID-6",
]
RECURSIVE = True

RENAME_MAP = {
    "non_globally_sclerotic_glomeruli": "Glom unit non-GSG",
    "globally_sclerotic_glomeruli": "GSG",
    "tubules": "Tubules",
    "arteries/arterioles": "Muscular vessels",
    "peritubular_capillaries": "PTC",
    "non_globally_sclerotic_glomeruli_tuft": "Glom tuft non-GSG",
}
 
# the only layers non-admin users should see
VISIBLE_NAMES = set(RENAME_MAP.values())
 
# never renamed or edited (matched ignoring capitals and spaces at the ends) add more annotations if needed for protecting
PROTECTED_NAMES = {"IFS", "cortical heatmap", "medullary heatmap", "muscular_vessels"}
# True  = visible to non-admins, so they see 9 layers: the 6 renamed + these 3
# False = hidden from non-admins (they would see only the 6)
PROTECTED_VISIBLE = True

#  if a slide has 2+ copies of one of the 6 layers after renaming:
#   "hide"   = keep the copy with the most shapes visible, hide the others (nothing deleted)
#   "report" = leave all copies as they are, just list them
DUPLICATE_MODE = "hide"
 
DRY_RUN = True

# how many slides to work on at the same time. 8 is a safe speed-up for a shared server; don't go above ~16 so the server isn't overloaded for other users.
WORKERS = 16
# False = don't print a line per change (thousands of lines slow a notebook down a lot).
# Everything is still in plan.csv / changes.csv and the final report.
VERBOSE = False
# to try it on a few slides first, set e.g. 20. None = all slides.
MAX_SLIDES = None

# undo: set to a live run's folder, e.g. "runs/20261104_140000", then run
RESTORE_RUN = ""
 
READ, WRITE, ADMIN = 0, 1, 2

NEAR_MISS = {k.lower() for k in RENAME_MAP} | {v.lower() for v in VISIBLE_NAMES}
PROTECTED_LOWER = {p.strip().lower() for p in PROTECTED_NAMES}
 
run_dir = os.path.join("runs", datetime.now().strftime("%Y%m%d_%H%M%S") + ("_dryrun" if DRY_RUN else ""))
log_rows = []
report = defaultdict(list)      # section -> lines
stats = Counter()
_folder_cache = {}
_admin_cache = {}
_lock = threading.Lock()
_tls = threading.local()
_token = None
 
 
def client():
    """One GirderClient per worker thread, all using your login."""
    if not _token:
        raise RuntimeError("Worker has no login token. Log in (gc.authenticate) before main(gc).")
    if not hasattr(_tls, "gc"):
        c = GirderClient(apiUrl=API_URL)
        c.setToken(_token)
        _tls.gc = c
    return _tls.gc
 
 
def bump(key, n=1):
    with _lock:
        stats[key] += n
 
 
def add_report(section, line):
    with _lock:
        report[section].append(line)
 
 
def say(msg):
    if VERBOSE:
        print(msg)
 
 
def walk_items(gc, folder_id, path):
    for item in gc.listItem(folder_id):
        yield path, item
    if RECURSIVE:
        for sub in gc.listFolder(folder_id, parentFolderType="folder"):
            yield from walk_items(gc, sub["_id"], f"{path}/{sub['name']}")
 
 
def folder_access(gc, folder_id):
    """(access dict, public bool) of the folder a slide lives in, cached."""
    if folder_id not in _folder_cache:
        acc = gc.get(f"folder/{folder_id}/access")
        pub = bool(gc.getFolder(folder_id).get("public"))
        _folder_cache[folder_id] = (acc, pub)
    return _folder_cache[folder_id]
 
 
def is_site_admin(gc, user_id):
    if user_id not in _admin_cache:
        try:
            _admin_cache[user_id] = bool(gc.get(f"user/{user_id}").get("admin"))
        except Exception:
            _admin_cache[user_id] = False
    return _admin_cache[user_id]
 
 
def entry(e, level=None):
    return {"id": e["id"], "level": e["level"] if level is None else level,
            "flags": e.get("flags", [])}
 
 
def access_key(acc, public):
    """Comparable form of an access list, to skip PUTs that change nothing."""
    return (frozenset((u["id"], u["level"]) for u in acc.get("users", [])),
            frozenset((g["id"], g["level"]) for g in acc.get("groups", [])),
            bool(public))
 
 
def visible_access(current, cur_public, f_acc, f_public):
    """Current access + READ for everyone who can open the slide. Never reduces."""
    users = {u["id"]: entry(u) for u in current.get("users", [])}
    for u in f_acc.get("users", []):
        users.setdefault(u["id"], entry(u, READ))
    groups = {g["id"]: entry(g) for g in current.get("groups", [])}
    for g in f_acc.get("groups", []):
        groups.setdefault(g["id"], entry(g, READ))
    return {"users": list(users.values()), "groups": list(groups.values())}, (cur_public or f_public)
 
 
def hidden_access(gc, current, me):
    """Only site admins (and you, so you can still fix it) stay. No groups, not public."""
    users = [entry(u) for u in current.get("users", [])
             if u["id"] == me["_id"] or is_site_admin(gc, u["id"])]
    if not any(u["id"] == me["_id"] for u in users):
        users.append({"id": me["_id"], "level": ADMIN, "flags": []})
    return {"users": users, "groups": []}, False
 
 
def save_backup(kind, ann_id, data):
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, f"{kind}_{ann_id}.json"), "w") as f:
        json.dump(data, f)
 
 
def log(slide_path, item, ann_id, old, new, category, action):
    with _lock:
        log_rows.append({"slide": slide_path, "item_id": item["_id"], "annotation_id": ann_id,
                     "old_name": old, "final_name": new, "category": category,
                     "action": action})
 
 
def classify(name):
    """-> (final_name, category). category: visible | protected | other | near_miss"""
    if name in RENAME_MAP:
        return RENAME_MAP[name], "visible"
    if name in VISIBLE_NAMES:
        return name, "visible"
    if name.lower() in PROTECTED_LOWER:
        return name, "protected"
    if name.lower() in NEAR_MISS:
        return name, "near_miss"
    return name, "other"
 
 
def element_count(gc, ann_id):
    full = gc.get(f"annotation/{ann_id}")
    return len(full["annotation"].get("elements", [])), full.get("updated", "")
 
 
def process_slide(gc, me, slide_path, item):
    bump("slides")
    anns = gc.get("annotation", parameters={"itemId": item["_id"], "limit": 0})
    layers = []
    for ann in anns:
        raw = ann["annotation"].get("name", "")
        old = raw.strip()
        final, cat = classify(old)
        layers.append({"ann": ann, "raw": raw, "old": old, "final": final, "cat": cat})
        bump(f"names:{final if cat != 'other' else old}")
 
    # ---- duplicates among the 6 visible layers (judged by the name AFTER renaming)
    by_name = defaultdict(list)
    for L in layers:
        if L["cat"] == "visible":
            by_name[L["final"]].append(L)
    for name, copies in by_name.items():
        if len(copies) < 2:
            continue
        sized = []
        for L in copies:
            n, upd = element_count(gc, L["ann"]["_id"])
            sized.append((n, upd, L))
        sized.sort(key=lambda s: (s[0], s[1]), reverse=True)
        keep = sized[0]
        for n, upd, L in sized[1:]:
            line = (f"{slide_path}: {len(copies)} copies of '{name}'. kept {keep[2]['ann']['_id']} "
                    f"({keep[0]} shapes); {L['ann']['_id']} ({n} shapes, updated {upd})")
            if DUPLICATE_MODE == "hide":
                L["cat"] = "duplicate"
                add_report("Duplicates hidden", line)
            else:
                add_report("Duplicates (left as is)", line)
    for name in VISIBLE_NAMES:
        if name not in by_name:
            add_report("Slides missing one of the 6 layers", f"{slide_path}: no '{name}'")
 
    # ---- apply
    for L in layers:
        ann, ann_id, old, final, cat = L["ann"], L["ann"]["_id"], L["old"], L["final"], L["cat"]
        try:
            if cat == "near_miss":
                add_report("Look-alike names NOT touched (fix by hand or add to RENAME_MAP)", 
                    f"{slide_path}: '{old}' ({ann_id})")
                log(slide_path, item, ann_id, old, old, cat, "untouched")
                continue
 
            # rename: only the 6 layers (incl. cleaning stray spaces, e.g. "Tubules ").
            # protected and other layers are never renamed.
            if cat in ("visible", "duplicate") and L["raw"] != final:
                bump("renames")
                if DRY_RUN:
                    say(f"[dry run] {slide_path}: rename {L['raw']!r} -> {final!r}")
                else:
                    full = gc.get(f"annotation/{ann_id}")
                    save_backup("name", ann_id, {"old_name": full["annotation"].get("name"),
                                                 "item_id": item["_id"]})
                    full["annotation"]["name"] = final
                    gc.put(f"annotation/{ann_id}", json=full["annotation"])
                    say(f"{slide_path}: renamed {L['raw']!r} -> {final!r}")
                log(slide_path, item, ann_id, old, final, cat, "rename")
 
            # access
            current = gc.get(f"annotation/{ann_id}/access")
            cur_public = bool(ann.get("public"))
            make_visible = cat == "visible" or (cat == "protected" and PROTECTED_VISIBLE)
            if make_visible:
                f_acc, f_pub = folder_access(gc, item["folderId"])
                new_acc, new_pub = visible_access(current, cur_public, f_acc, f_pub)
                what = "make visible to slide users (read)"
            else:
                new_acc, new_pub = hidden_access(gc, current, me)
                what = "hide from non-admins"
 
            if access_key(current, cur_public) == access_key(new_acc, new_pub):
                continue
            bump("access_changes")
            if DRY_RUN:
                say(f"[dry run] {slide_path}: '{final}' [{cat}] -> {what}")
            else:
                save_backup("access", ann_id, {"access": current, "public": cur_public})
                gc.put(f"annotation/{ann_id}/access",
                       parameters={"access": json.dumps(new_acc),
                                   "public": "true" if new_pub else "false"})
                say(f"{slide_path}: '{final}' [{cat}] -> {what}")
            log(slide_path, item, ann_id, old, final, cat, what)
 
        except Exception as e:
            bump("errors")
            add_report("ERRORS (these layers were not finished, re-run to retry)", 
                f"{slide_path}: '{old}' ({ann_id}): {e}")
 
 
def restore(gc):
    files = sorted(f for f in os.listdir(RESTORE_RUN)
                   if f.endswith(".json") and f.startswith(("name_", "access_")))
    print(f"Restoring {len(files)} backups from {RESTORE_RUN}  DRY_RUN={DRY_RUN}")
    for fname in files:
        kind, ann_id = fname[:-5].split("_", 1)
        with open(os.path.join(RESTORE_RUN, fname)) as f:
            data = json.load(f)
        if DRY_RUN:
            print(f"[dry run] would restore {kind} on {ann_id}")
            continue
        if kind == "name":
            full = gc.get(f"annotation/{ann_id}")          # current shapes are kept
            full["annotation"]["name"] = data["old_name"]
            gc.put(f"annotation/{ann_id}", json=full["annotation"])
            print(f"name of {ann_id} back to '{data['old_name']}'")
        elif kind == "access":
            gc.put(f"annotation/{ann_id}/access",
                   parameters={"access": json.dumps({"users": data["access"].get("users", []),
                                                     "groups": data["access"].get("groups", [])}),
                               "public": "true" if data["public"] else "false"})
            print(f"access of {ann_id} restored")
 
 
def main(gc):
    global _token
    _token = gc.token                  # hand your login to the worker threads
    me = gc.get("user/me")
    if not me or not _token:
        raise SystemExit("Not logged in. Run gc.authenticate(...) first.")
    print(f"Logged in as {me['login']}  (site admin: {me.get('admin')})")
    if not me.get("admin"):
        print("WARNING: you are not a site admin. You will stay on every hidden layer's access "
              "list so you can fix things, which means YOU will still see them.")
 
    if RESTORE_RUN:
        restore(gc)
        return
 
    print("\nFolders to process:")
    for fid in FOLDER_IDS:
        f = gc.getFolder(fid)              # stops here if an ID is wrong
        print(f"   {f['name']}  ({fid})")
    print(f"\nDRY_RUN = {DRY_RUN}   DUPLICATE_MODE = {DUPLICATE_MODE}   "
          f"PROTECTED_VISIBLE = {PROTECTED_VISIBLE}")
 
    if not DRY_RUN:
        if input("\nThis changes the OFFICIAL server. Type YES to continue: ").strip() != "YES":
            print("Stopped. Nothing changed.")
            return
 
    print("\nListing slides...")
    slides = []
    for fid in FOLDER_IDS:
        top = gc.getFolder(fid)["name"]
        found = [(f"{path}/{item['name']}", item) for path, item in walk_items(gc, fid, top)]
        print(f"   {top}: {len(found)} slides")
        slides.extend(found)
    if MAX_SLIDES:
        slides = slides[:MAX_SLIDES]
        print(f"   MAX_SLIDES = {MAX_SLIDES}: only the first {len(slides)} slides this run")
    print(f"Processing {len(slides)} slides with {WORKERS} workers...")
 
    def work(args):
        process_slide(client(), me, *args)
 
    start = time.time()
    pool = ThreadPoolExecutor(max_workers=WORKERS)
    futures = [pool.submit(work, sl) for sl in slides]
    try:
        for n, fut in enumerate(as_completed(futures), 1):
            fut.result()
            if n % 25 == 0 or n == len(slides):
                el = time.time() - start
                left = el / n * (len(slides) - n)
                print(f"   {n}/{len(slides)} slides done, {el/60:.1f} min so far, ~{left/60:.1f} min left")
    except BaseException:
        # stop everything that hasn't started yet, then show the error
        pool.shutdown(wait=True, cancel_futures=True)
        print("\nSTOPPED because of the error below. Slides already finished are in the backups; "
              "fix the problem and run again (finished slides are skipped).")
        raise
    pool.shutdown(wait=True)
    log_rows.sort(key=lambda r: (r["slide"], r["old_name"]))
 
    # ---- outputs
    os.makedirs(run_dir, exist_ok=True)
    csv_name = "plan.csv" if DRY_RUN else "changes.csv"
    with open(os.path.join(run_dir, csv_name), "w", newline="") as f:
        fields = ["slide", "item_id", "annotation_id", "old_name", "final_name", "category", "action"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(log_rows)
 
    print("\n================ REPORT ================")
    print(f"slides: {stats['slides']}   renames: {stats['renames']}   "
          f"access changes: {stats['access_changes']}   errors: {stats['errors']}"
          + ("   (DRY RUN, nothing changed)" if DRY_RUN else ""))
    print("\nLayer names found (after renaming):")
    for key, n in sorted(((k[6:], v) for k, v in stats.items() if k.startswith("names:")),
                         key=lambda kv: -kv[1]):
        _, cat = classify(key)
        label = "VISIBLE" if cat == "visible" else ("protected" if cat == "protected"
                 else ("LOOK-ALIKE" if cat == "near_miss" else "hidden"))
        print(f"   {n:5d}  {key!r:45} {label}")
    for section, lines in report.items():
        print(f"\n{section}: {len(lines)}")
        for line in lines:
            print("   " + line)
    print(f"\n{csv_name} and backups: {run_dir}")
    if not DRY_RUN:
        print(f"To undo this run: RESTORE_RUN = '{run_dir}'")
        
if __name__ == "__main__":
    gc = GirderClient(apiUrl=API_URL)
    if API_KEY and API_KEY != "ATHENA-API-KEY":
        gc.authenticate(apiKey=API_KEY)
    else:
        # no API key: asks for your athena username and password (password is hidden)
        gc.authenticate(interactive=True)
    _token = gc.token
    main(gc)