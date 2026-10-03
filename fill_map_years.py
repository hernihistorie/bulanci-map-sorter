import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

MAPS_DIR = "_MAPS_"
META_DIR = "maps_metadata"
DATES_DIR = "unsorted_maps"
MAP_EXT = ".eap"


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_date(path: Path) -> datetime:
    """Lowest of the available creation / modification timestamps.

    Note: on Windows st_ctime is the creation time. On macOS st_birthtime is.
    On Linux there is no reliable creation time, so only mtime is effectively used.
    """
    st = path.stat()
    stamps = [st.st_mtime]
    birth = getattr(st, "st_birthtime", None)
    if birth:
        stamps.append(birth)
    if os.name == "nt":
        stamps.append(st.st_ctime)
    return datetime.fromtimestamp(min(stamps))


def read_json(path: Path):
    for enc in ("utf-8-sig", "utf-8", "cp1250"):
        try:
            with open(path, "r", encoding=enc) as f:
                return json.load(f), enc
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return None, None


def write_json(path: Path, data, indent):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
        f.write("\n")


def source_folder_name(eap_path: Path, dates_root: Path) -> str:
    """Name of the first-level folder under map_dates that contains the file."""
    rel = eap_path.relative_to(dates_root)
    return rel.parts[0] if len(rel.parts) > 1 else dates_root.name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=".", help="folder containing _MAPS_, maps_metadata, map_dates")
    ap.add_argument("--dry-run", action="store_true", help="do not modify any JSON file")
    ap.add_argument("--indent", type=int, default=2, help="JSON indent when writing (default 2)")
    ap.add_argument("--cutoff", default="2023-11-27",
                    help="maps whose lowest date is on/after this date (YYYY-MM-DD) are NOT updated "
                         "(default 2023-11-27)")
    args = ap.parse_args()

    try:
        cutoff = datetime.strptime(args.cutoff, "%Y-%m-%d")
    except ValueError:
        sys.exit("--cutoff must be in YYYY-MM-DD format")

    base = Path(args.base)
    maps_root = base / MAPS_DIR
    meta_root = base / META_DIR
    dates_root = base / DATES_DIR
    for p in (maps_root, meta_root, dates_root):
        if not p.is_dir():
            sys.exit(f"Folder not found: {p}")

    # ---- Step 1: JSONs with empty year -> hashes of same-named maps ----------
    maps_by_stem = {}
    for p in maps_root.rglob("*"):
        if p.is_file() and p.suffix.lower() == MAP_EXT:
            maps_by_stem.setdefault(p.stem.lower(), []).append(p)

    todo = {}          # json path -> (data, set of hashes)
    no_map = []
    for jp in sorted(meta_root.rglob("*.json")):
        data, _ = read_json(jp)
        if not isinstance(data, dict):
            print(f"[skip] cannot read JSON object: {jp}")
            continue
        year = data.get("year")
        if not (isinstance(year, str) and year.strip() == ""):
            continue
        maps = maps_by_stem.get(jp.stem.lower(), [])
        if not maps:
            no_map.append(jp)
            continue
        todo[jp] = (data, {file_hash(m) for m in maps})

    print(f"JSONs with empty year: {len(todo) + len(no_map)} "
          f"({len(no_map)} without a matching map in {MAPS_DIR})")

    wanted = {}        # hash -> list of json paths
    for jp, (_, hashes) in todo.items():
        for h in hashes:
            wanted.setdefault(h, []).append(jp)

    # ---- Step 2: scan map_dates, keep the lowest date per json ---------------
    best = {}          # json path -> (datetime, folder name, eap path)
    scanned = 0
    for p in dates_root.rglob("*"):
        if not (p.is_file() and p.suffix.lower() == MAP_EXT):
            continue
        scanned += 1
        h = file_hash(p)
        if h not in wanted:
            continue
        d = file_date(p)
        folder = source_folder_name(p, dates_root)
        for jp in wanted[h]:
            if jp not in best or d < best[jp][0]:
                best[jp] = (d, folder, p)
    print(f"Scanned {scanned} .eap files in {DATES_DIR}")

    # ---- Step 3: write results ------------------------------------------------
    updated = 0
    too_new = []
    for jp, (data, _) in todo.items():
        if jp not in best:
            continue
        d, folder, src = best[jp]
        # best[jp] is already the LOWEST date over all copies; if even that is
        # on/after the cutoff, the date is not trustworthy -> skip this map.
        if d >= cutoff:
            too_new.append((jp, d, folder))
            continue
        print(f"{jp.name}: year={d.year}  source={folder}  ({src})")
        if not args.dry_run:
            data["year"] = d.year
            data["description_source"] = folder
            write_json(jp, data, args.indent)
        updated += 1

    not_found = [jp for jp in todo if jp not in best]
    skipped = {jp for jp, _, _ in too_new}
    print()
    print(f"{'Would update' if args.dry_run else 'Updated'}: {updated}")
    print(f"Skipped, lowest date on/after {cutoff.date()}: {len(too_new)}")
    print(f"No identical copy found in {DATES_DIR}: {len(not_found)}")
    print(f"No map with the same name in {MAPS_DIR}: {len(no_map)}")
    if too_new:
        print(f"\nMaps skipped (lowest date >= {cutoff.date()}):")
        for jp, d, folder in too_new:
            print(f"   {jp.name}: {d:%Y-%m-%d} ({folder})")
    if not_found:
        print("\nMaps without date match:")
        for jp in not_found:
            print("  ", jp.name)


if __name__ == "__main__":
    main()
