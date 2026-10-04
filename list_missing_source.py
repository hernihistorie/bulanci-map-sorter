import argparse
import json
import sys
from pathlib import Path

META_DIR = "maps_metadata"


def read_json(path: Path):
    for enc in ("utf-8-sig", "utf-8", "cp1250"):
        try:
            with open(path, "r", encoding=enc) as f:
                return json.load(f)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return None


def is_empty(value) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=".", help="folder containing maps_metadata")
    args = ap.parse_args()

    meta_root = Path(args.base) / META_DIR
    if not meta_root.is_dir():
        sys.exit(f"Folder not found: {meta_root}")

    total = 0
    matched = 0
    unreadable = 0

    for jp in sorted(meta_root.rglob("*.json")):
        total += 1
        data = read_json(jp)
        if not isinstance(data, dict):
            unreadable += 1
            print(f"[unreadable] {jp}")
            continue

        if not is_empty(data.get("year")) and is_empty(data.get("description_source")):
            matched += 1
            print(f"{jp.name}  (year: {data['year']})")

    print()
    print(f"Checked: {total} | year filled, no description_source: {matched} | unreadable: {unreadable}")


if __name__ == "__main__":
    main()
