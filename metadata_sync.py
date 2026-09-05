import json
from pathlib import Path
import yaml
import subprocess
import sys

def write_authors_to_yaml(maps_metadata, authors_metadata):
    # Load existing YAML
    if authors_metadata.exists():
        with authors_metadata.open("r", encoding="utf-8") as f:
            authors_data = yaml.safe_load(f) or {}
    else:
        authors_data = {}
    # Process JSON files
    for json_file in maps_metadata.glob("*.json"):
        try:
            with json_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            authors = data.get("author", [])
            # Handle both a list and a single string
            if isinstance(authors, str):
                authors = [authors]
            for author in authors:
                if not isinstance(author, str):
                    continue
                author = author.strip()
                if not author:
                    continue
                # Add only authors that aren't already in the YAML
                if author not in authors_data:
                    authors_data[author] = None
                    print(f"Adding author: {author}")
        except Exception as e:
            print(f"ERROR processing {json_file.name}: {e}")

    # Sort authors alphabetically while preserving their metadata
    authors_data = dict(
        sorted(authors_data.items(), key=lambda item: item[0].casefold())
    )
    # Write updated YAML
    with authors_metadata.open("w", encoding="utf-8") as f:
        yaml.safe_dump(authors_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"\nDone. Total authors: {len(authors_data)}")


def compare_authors(file_path, authors_data):
    file = str(file_path)
    file = file.replace('_MAPS_/', '')
    with open(file_path, "r", encoding="utf-8") as j_file:
        data = json.load(j_file)
    Author_eap = data["author_eap"]
    Author_list = data["author"]
    Author = ", ".join(Author_list)
    if Author_eap == "" and Author == "":
        None
    elif Author == "" and Author_eap != "":
        print(f"\n{file_path}")
        print(f"Author is empty, Author_eap is {Author_eap}")
    elif Author_eap != Author:
        aliases = authors_data.get(Author, [])
        alias_match = False
        if aliases:
            for alias in aliases:
                if isinstance(alias, dict) and alias.get("alias") == Author_eap:
                    alias_match = True
                    break
        if not alias_match:
            print(f"\n{file_path}")
            print(f"{Author_eap} != {Author}")
    elif Author_eap == Author:
        None


if __name__ == "__main__":
    map_metadata = Path("./maps_metadata/")
    authors_metadata = Path("authors_metadata.yaml")
    print(f"WRITING NEW AUTHORS TO {authors_metadata}")
    write_authors_to_yaml(map_metadata, authors_metadata)
    print("-"*50)

    print(f"\nCREATING NEW MAPS OVERVIEW")
    subprocess.run([sys.executable, "maps_overview.py"])
    print("-"*50)

    print(f"\nPRINTING AUTHORS DIFFERENCES")
    with open(authors_metadata, "r", encoding="utf-8") as y_file:
        authors_data = yaml.safe_load(y_file) or {}
    for file_path in map_metadata.glob("*.json"):
        compare_authors(file_path, authors_data)