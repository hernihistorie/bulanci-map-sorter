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
## Metadata structure
There is 13 metadata attributes describing the maps. Some of them are generated from the source files, some are attributed with external tool or manually.

### Automatically generated metadata
Some metadata are obtained from the orginall `.eap` file. Namelly:
- **guid**: Originall ID given to the map by the editor.
- **name**: Name visible in the menu of the game.
- **author_eap**: Author stored in a `.eap` file.
- **music**: Name of the sound file stored in `.eap` file.

### Description metadata
Metadata describing the contents of the map and context in which was map made, and which has assigned source from which this information was acquired.
- **year**: Year in which was map first distributed.
- **description**: Description given by the creator of the map. The description allways comes from the website or other place that is directly connected to the maker of the map.
- **description_source**: URL, PoO ID or other source from which the **year** and **description** attributes were taken. 
- **description_note**: Note giving additional context which is not apparent from the source alone. If the same note relates to more than one map, it is written just in one main `.json` file and in all other `.json` files is the **description_note** filled with the whole name of the main `.json` file.

### Visibility
- **privacy**: Some maps can be hidden because author asked for that. Maps are either *public* or *hidden*.
- **nsfw**: Some maps contains not safe for work content. Attribute is set as *false* if it is **safe for work**, and as *true* if it is **not safe for work**.

### Other metadata
- **author**: Author name assigned by the curator. This metadata may differ from the **author_eap** entry and represents the canonical form of the author's name. 
- **places_of_occurences**: A set of all the virtual places where the map was distributed. If the map was distributed on the website, it is a string of a shortened URL is used (`bulanci.cz` for instance), if the map was distributed on a cloud storage like UložTo or Webshare, it is a string made of the name of the cloud combined with URL slug (for example `UlozTo_sqdUsfss`).
- **duplicate_of**: Some maps have different guid and hash, but looks completely the same. The map, which is declared an original has this attribute missing, the one, which is declared as a copy has a string in form of the name of the original `.eap` file stripped of the file extension. 

### What is used where?
Some of the metadata is visible on the website, some of them are used for filtering the maps and some are here just for the curator.
#### Visible on the website
- **name**
- **year**
- **description**
- **author**
- **music**
- **places_of_occurrences**
#### Used for filtering what is present on website
- **duplicate_of**: If it is filled, the file itself is not present on the website and metadata are merged with the "original".
- **privacy**: If the map is *hidden* than the both metadata and `.eap` file is not shown on the website.
- **nsfw**: *I dunno, hidden screenshots IG????*
#### Only for curators
- **guid**
- **description_source**
- **description_note**
- **author_eap**

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
