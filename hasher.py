import hashlib
import os
from pathlib import Path
import shutil
import json

def compute_file_hash(file_path):
    algorithm="md5"
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def write_hash(file_hash, file_name):
    file_str = file_name.replace('unsorted_maps/', '')
    f = open(hash_ls, "a")
    f.write(f"|+| {file_str} = {file_hash}\n")
    f.close()

def find_map_name(start_str, end_str):
    with open(hash_ls) as f:
        text = f.read()
        parts = text.split(start_str)
        for part in parts[1:]:
            remaining_text_parts = part.split(end_str, 1)
            if len(remaining_text_parts) == 2:
                substring = remaining_text_parts[0]
        print(f"Original file: {substring}")
        return substring

def add_occurence(substring):
    json_file = f"./_MAPS_/{substring[:-4]}.json"
    print(json_file)
    # Load existing file
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    # Add place
    if place not in data["Places of Occurrences"]:
        data["Places of Occurrences"].append(place)
    # Save back
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def check_hash(file_hash, place): 
    with open(hash_ls) as f:
        if file_hash in f.read():
            start_str = "|+| "
            end_str = f" = {file_hash}"
            substring = find_map_name(start_str, end_str)
            add_occurence(substring)
            print("Removing file from unsorted maps...")
            return True
        else:
            file_str = str(file)
            file_str = file_str.replace('unsorted_maps/', '')
            base_name = (file_str)[:-4]
            json_file = f"./_MAPS_/{base_name}.json"
            counter = 1
            while os.path.exists(json_file):
                json_file = f"./_MAPS_/{base_name}_{counter}.json"
                counter += 1
            data = {
                "Name": "",
                "Year": "",
                "Author": "",
                "Places of Occurrences": []
            }
            if place not in data["Places of Occurrences"]:
                data["Places of Occurrences"].append(place)
            with open(json_file, "w", encoding="utf-8") as j_file:
                json.dump(data, j_file, indent=4, ensure_ascii=False)
            print(f'File with hash "{file_hash}" not found. Moving to _MAPS_...')
            return False

def move_with_rename(src_path, dest_dir):
    filename = os.path.basename(src_path)
    name, ext = os.path.splitext(filename)
    dest_path = os.path.join(dest_dir, filename)
    counter = 1
    while os.path.exists(dest_path):
        print(f"{dest_path} ALREADY EXISTS!!!!!")
        new_filename = f"{name}_{counter}{ext}"
        dest_path = os.path.join(dest_dir, new_filename)
        counter += 1
        filename = new_filename
    shutil.move(src_path, dest_path)
    return filename

def main():
    try:
        file_hash = compute_file_hash(file)
        print(f"{file} = {file_hash}")
        y = check_hash(file_hash, place)
        if y == True:
            os.remove(file)
        if y == False:
            new_filename = move_with_rename(file, sorted_maps_dir)
            write_hash(file_hash, new_filename)
    except FileNotFoundError:
        print("File not found!")

if __name__ == "__main__":
    maps_for_sort_dir = Path("./unsorted_maps")
    sorted_maps_dir = Path("./_MAPS_/")
    hash_ls = "hashes.txt"

    # Check if unsorted_maps contains subfolders
    subfolders = [f for f in maps_for_sort_dir.iterdir() if f.is_dir()]

    if subfolders:
        print("Folder mode detected (using subfolder names as place IDs).")

        for folder in subfolders:
            place = folder.name
            print(f"\nProcessing folder: {place}")

            for file in folder.glob("*.eap"):
                try:
                    file_hash = compute_file_hash(file)
                    print(f"{file} = {file_hash}")

                    y = check_hash(file_hash, place)

                    if y:
                        os.remove(file)
                    else:
                        new_filename = move_with_rename(file, sorted_maps_dir)
                        write_hash(file_hash, new_filename)

                except FileNotFoundError:
                    print("File not found!")

    else:
        # Fallback to old manual mode
        print("Single folder mode detected.")
        place = input("Enter place ID: ")

        for file in maps_for_sort_dir.glob("*.eap"):
            try:
                file_hash = compute_file_hash(file)
                print(f"{file} = {file_hash}")

                y = check_hash(file_hash, place)

                if y:
                    os.remove(file)
                else:
                    new_filename = move_with_rename(file, sorted_maps_dir)
                    write_hash(file_hash, new_filename)

            except FileNotFoundError:
                print("File not found!")