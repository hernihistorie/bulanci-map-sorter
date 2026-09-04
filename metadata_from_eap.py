from pathlib import Path
import json
from eap_parser import eap

# List of maps that could not be processed
skipped_maps = []

def main():
    file = str(file_path)
    file = file.replace('_MAPS_/', '')
    json_file = f"./maps_metadata/{file[:-4]}.json"
    with open(json_file, "r", encoding="utf-8") as j_file:
            data = json.load(j_file)
    print(f"\nChecking {file}")
    try: #Try to read GUID and write it to the JSON file
        guid = eap.MapData.from_file(file_path).guid
        data["guid"] = guid
        print(guid)
    except Exception as e:
        print(f"ERROR READING GUID OF {file} SKIPPING!!!")
    try: #Try to read Name and write it to the JSON file
        Name = eap.MapData.from_file(file_path).info.name
        data["name"] = Name
        print(Name)
    except Exception as e:
        print(f"ERROR READING NAME OF {file} SKIPPING!!!")
    try: #Try to read Author and write it to the JSON file
        Author_eap = eap.MapData.from_file(file_path).info.author
        data["author_eap"] = Author_eap
        print(Author_eap)
    except Exception as e:
        print(f"ERROR READING AUTHOR OF {file} SKIPPING!!!")
    try: #Try to read Music Title and Author and write it to the JSON file
        Music_Title = eap.MapData.from_file(file_path).music.tags.title
        Music_Author = eap.MapData.from_file(file_path).music.tags.artist
        Music = Music_Title + " (" + Music_Author +")"
        data["music"] = Music
        print(Music)
    except Exception as e:
        print(f"ERROR READING MUSIC INFO OF {file} SKIPPING!!!")
    # Save back
    with open(json_file, "w", encoding="utf-8") as j_file:
        json.dump(data, j_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    maps = Path("./_MAPS_/")
    for file_path in maps.glob('*.eap'):
        main()