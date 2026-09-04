import os
import json

MAPS_DIR = "./maps_metadata"  # Directory containing the JSON files

def remove_place_from_all():
    place_to_remove = input("Enter place to remove: ").strip()

    if not place_to_remove:
        print("No place entered. Exiting.")
        return

    modified_files = 0

    for filename in os.listdir(MAPS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(MAPS_DIR, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            places = data.get("places_of_occurrences", [])

            if place_to_remove in places:
                places.remove(place_to_remove)
                data["places_of_occurrences"] = places

                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)

                modified_files += 1
                print(f"Updated: {filename}")

    print(f"\nDone. Modified {modified_files} file(s).")

if __name__ == "__main__":
    remove_place_from_all()