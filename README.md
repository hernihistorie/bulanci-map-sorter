# Bulánci map-sorter

This app is designed for sorting, creating screenshots, and adding metadata to fan-made maps for the game **Bulánci**.

The application is started by:

```bash
python main.py
```

The processing pipeline consists of the following steps:
* Hasher
* Name getter
* Screenshoter
* Creating HTML overview

---

## Hasher

This part sorts `.eap` files from the `unsorted_maps` folder by creating hashes of the files and checking whether a file has already been processed.

* If the file has already been sorted, the script increases the occurrence counter for the existing map.
* If the file is new, it is moved to the `_MAPS_` folder and a `.json` file with metadata for this map is created.

---

## Name getter

This script semi-automatically retrieves the name of the map.

Due to the compression of `.eap` files, it is too difficult to extract the map name directly from the binary data. Instead, the name is obtained from a screenshot of the game menu using OCR.

For this script to work correctly, you must grant permission to access the mouse and display. The easiest way to do this is:

```bash
xhost +
```

The extracted name is then added to the corresponding `.json` metadata file.

---

## Screenshoter

This script creates a screenshot of the map and its loading screen.

Like the Name getter, this script requires permission to access the display and mouse. The easiest way to allow this is:

```bash
xhost +
```

The resulting images are saved as `.png` files in the `_MAPS_` folder.

---

## Create HTML maps overview

This script generates an HTML table from all `.json` metadata files. The table contains selected metadata and preview images of the maps.

The generated HTML file must be opened in a web browser for browsing.
