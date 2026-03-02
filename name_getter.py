import os
import pyautogui
import time
import shutil
from subscriptable_path import Path
from PIL import ImageGrab
import pytesseract
import json

def bulanci_menu_clicker():
    os.system("gnome-terminal -- wine bulanci_hra/bulanci.exe")
    time.sleep(5.5)
    pyautogui.press("enter") #Click on "Dále"
    pyautogui.moveTo(275, 420)
    pyautogui.click() #Click on Map
    pyautogui.moveTo(20, 20)
    return True

def bulanci_screenshot():
    time.sleep(1)
    img = ImageGrab.grab(bbox=(263, 410, 456, 434), xdisplay= None)
    Name = pytesseract.image_to_string(img, lang = "ces")
    return Name

def chceck_if_named(json_file):
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    if "Name" in data and data["Name"]:
        print("Name exists.")
        return True
    else:
        print("Name is missing. Getting screenshot and extracting name...")
        return False

def main():
    file = str(file_path)
    file = file.replace('_MAPS_/', '')
    json_file = f"./_MAPS_/{file[:-4]}.json"
    print(f"Checking {file}")
    y = chceck_if_named(json_file)
    if y == False:
        shutil.copy(f"./_MAPS_/{file}", "./bulanci_hra/")
        bulanci_menu_clicker()
        Name = bulanci_screenshot().strip()
        print(Name)
        # Load existing file
        with open(json_file, "r", encoding="utf-8") as j_file:
            data = json.load(j_file)
        # Add skill
        data["Name"] = Name
        # Save back
        with open(json_file, "w", encoding="utf-8") as j_file:
            json.dump(data, j_file, indent=4, ensure_ascii=False)
        os.system("wineserver -k")
        os.remove(f"./bulanci_hra/{file}")

if __name__ == "__main__":
    maps = Path("./_MAPS_/")
    for file_path in maps.glob('*.eap'):
        main()