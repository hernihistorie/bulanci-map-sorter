from pathlib import Path
import json

folder = Path("./maps_metadata")

total_maps = 0
no_year = 0
no_description = 0
no_author = 0

for json_file in folder.glob("*.json"):
    #print (f"Processing {json_file.name}...")
    total_maps += 1

    with json_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not data.get("year"):
        no_year += 1

    if not data.get("description"):
        no_description += 1

    author = data.get("author", [])
    if not author or author == [""]:
        no_author += 1

print(f"Total maps: {total_maps}")
print(f"Maps with no author: {no_author} ({100 - (no_author / total_maps) * 100:.2f}% done)")
print(f"Maps with no year: {no_year} ({100 - (no_year / total_maps) * 100:.2f}% done)")
print(f"Maps with no description: {no_description} ({100 - (no_description / total_maps) * 100:.2f}% done)")