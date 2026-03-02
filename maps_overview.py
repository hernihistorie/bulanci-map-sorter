import os
import json

MAPS_DIR = "./_MAPS_"
OUTPUT_FILE = "maps_overview.html"

rows_html = ""

for filename in os.listdir(MAPS_DIR):
    if filename.endswith(".json"):
        filepath = os.path.join(MAPS_DIR, filename)

        base_name = filename[:-5]  # remove .json

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

            name = data.get("Name", "")
            places_list = data.get("Places of Occurrences", [])
            places = ", ".join(places_list)

            image_main = f"{MAPS_DIR}/{base_name}.png"
            image_load = f"{MAPS_DIR}/{base_name}_load.png"

            rows_html += f"""
            <tr>
                <td>{base_name}</td>
                <td>{name}</td>
                <td>{places}</td>
                <td>
                    <a href="{image_main}" target="_blank">
                        <img src="{image_main}" class="thumb">
                    </a>
                </td>
                <td>
                    <a href="{image_load}" target="_blank">
                        <img src="{image_load}" class="thumb">
                    </a>
                </td>
            </tr>
            """

html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Maps Overview</title>

<style>
body {{
    font-family: Arial;
    background-color: #f4f6f8;
}}

h2 {{
    text-align: center;
}}

input {{
    margin: 5px 10px 15px 0;
    padding: 6px;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    background: white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}}

th, td {{
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}}

th {{
    background-color: #2c3e50;
    color: white;
    cursor: pointer;
}}

tr:hover {{
    background-color: #f1f1f1;
}}

.thumb {{
    width: 120px;
    border-radius: 6px;
    transition: transform 0.2s;
}}

.thumb:hover {{
    transform: scale(1.5);
    z-index: 1000;
}}
</style>
</head>

<body>

<h2>Maps Overview</h2>

<label>Filter by Name:</label>
<input type="text" id="nameFilter" onkeyup="filterTable()" placeholder="Search name...">

<label>Filter by Place:</label>
<input type="text" id="placeFilter" onkeyup="filterTable()" placeholder="Search place...">

<table id="mapsTable">
    <thead>
        <tr>
            <th onclick="sortTable(0)">File name</th>
            <th onclick="sortTable(1)">Map name</th>
            <th onclick="sortTable(2)">Places</th>
            <th>Preview</th>
            <th>Loading</th>
        </tr>
    </thead>
    <tbody>
        {rows_html}
    </tbody>
</table>

<script>
function filterTable() {{
    let nameInput = document.getElementById("nameFilter").value.toLowerCase();
    let placeInput = document.getElementById("placeFilter").value.toLowerCase();
    let table = document.getElementById("mapsTable");
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {{
        let nameCell = rows[i].getElementsByTagName("td")[1];
        let placeCell = rows[i].getElementsByTagName("td")[2];

        if (nameCell && placeCell) {{
            let nameText = nameCell.textContent.toLowerCase();
            let placeText = placeCell.textContent.toLowerCase();

            if (nameText.includes(nameInput) && placeText.includes(placeInput)) {{
                rows[i].style.display = "";
            }} else {{
                rows[i].style.display = "none";
            }}
        }}
    }}
}}

function sortTable(columnIndex) {{
    let table = document.getElementById("mapsTable");
    let rows = Array.from(table.rows).slice(1);
    let ascending = table.getAttribute("data-sort") !== "asc";

    rows.sort((a, b) => {{
        let A = a.cells[columnIndex].textContent.toLowerCase();
        let B = b.cells[columnIndex].textContent.toLowerCase();
        return ascending ? A.localeCompare(B) : B.localeCompare(A);
    }});

    table.setAttribute("data-sort", ascending ? "asc" : "desc");

    rows.forEach(row => table.tBodies[0].appendChild(row));
}}
</script>

</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Gallery overview created successfully.")