from pathlib import Path
import json
import yaml

json_folder = Path("./maps_metadata")
yaml_file = Path("./authors_metadata.yaml")

# Load YAML authors
with yaml_file.open("r", encoding="utf-8") as file:
    authors_metadata = yaml.safe_load(file)

# Collect authors from JSON files
json_authors = set()
json_count = 0

for json_file in json_folder.rglob("*.json"):
    json_count += 1

    with json_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    authors = data.get("author", [])

    if isinstance(authors, str):
        authors = [authors]

    for author in authors:
        if author:
            json_authors.add(author)

# Compare authors
missing_authors = [
    author for author in authors_metadata
    if author not in json_authors
]

# Report
print(f"JSON files processed: {json_count}")
print(f"Authors in YAML: {len(authors_metadata)}")
print(f"Authors found in JSONs: {len(json_authors)}")
print(f"Authors not used in any JSON: {len(missing_authors)}")

for author in missing_authors:
    print(f"- {author}")