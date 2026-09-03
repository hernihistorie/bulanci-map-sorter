from pathlib import Path
import json
from eap_parser import eap

# List of maps that could not be processed
skipped_maps = []

def chceck_if_named(json_file):
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    if "Name" in data and data["Name"]:
        print("Name exists.")
        return True
    else:
        print("Name is missing. Extracting name...")
        return False

def main():
    file = str(file_path)
    file = file.replace('_MAPS_/', '')
    json_file = f"./maps_metadata/{file[:-4]}.json"
    print(f"Checking {file}")
    y = chceck_if_named(json_file)
    if y == False:
        try:
            Name = eap.MapData.from_file(file_path).info.name
            print(Name)
        except Exception as e:
            print(f"ERROR READING {file} SKIPPING!!!")
            # Add the map to the skipped list
            skipped_maps.append(file)
            return            
        # Load existing file
        with open(json_file, "r", encoding="utf-8") as j_file:
            data = json.load(j_file)
        # Add skill
        data["Name"] = Name
        # Save back
        with open(json_file, "w", encoding="utf-8") as j_file:
            json.dump(data, j_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    maps = Path("./_MAPS_/")
    for file_path in maps.glob('*.eap'):
        main()
    if skipped_maps:
        print(f"\nSKIPPED MAPS")
        for map_name in skipped_maps:
            print(f"{map_name}")
    else:
        print("\nNo maps were skipped.")