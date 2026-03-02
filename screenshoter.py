import os
import pyautogui
import time
import shutil
import getpixelcolor
from subscriptable_path import Path
from PIL import ImageGrab

def bulanci_menu_clicker():
    os.system("gnome-terminal -- wine bulanci_hra/bulanci.exe")
    time.sleep(5.5)
    pyautogui.click(x=285, y=213) #Click on "2 hráči"
    pyautogui.press("enter") #Click on "Dále"
    pyautogui.moveTo(275, 420)
    pyautogui.click() #Click on Map
    time.sleep(0.5)
    pyautogui.press("enter") #Click on "Začít hru"
    return True

def bulanci_screenshot(file_name):
    time.sleep(1)
    green = (135, 210, 33, 255)
    counter = 0
    while True:
        time.sleep(0.5)
        counter = counter + 1
        color = getpixelcolor.pixel(550, 574)
        print(color)
        if counter == 5:
            pyautogui.press("enter")
        if color == green:
            screenshot = ImageGrab.grab(bbox=(0, 0, 800, 600), xdisplay= None)
            screenshot.save(f"./_MAPS_/{file_name}_load.png")
            time.sleep(3)
            screenshot = ImageGrab.grab(bbox=(0, 0, 800, 600), xdisplay= None)
            screenshot.save(f"./_MAPS_/{file_name}.png")
            break
    print(f"Screenshot of {file_name}.eap taken.")
    return True

def screenshot_exist_check(file_name):
    screenshot_file = f"./_MAPS_/{file_name}.png"
    return os.path.isfile(screenshot_file)

def main():
    file = str(file_path)
    file = file.replace('_MAPS_/', '')
    file_name = file[:-4]
    screenshot_check = screenshot_exist_check(file_name)
    if screenshot_check == True:
        print("Screenshot already exist.")
    elif screenshot_check == False:
        shutil.copy(f"./_MAPS_/{file}", "./bulanci_hra/")
        y = bulanci_menu_clicker()
        if y == True:
            x = bulanci_screenshot(file_name)
        if x == True:
            os.system("wineserver -k")
            os.remove(f"./bulanci_hra/{file}")


if __name__ == "__main__":
    maps = Path("./_MAPS_/")
    for file_path in maps.glob('*.eap'):
        main()