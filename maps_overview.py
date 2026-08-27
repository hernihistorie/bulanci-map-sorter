import os
import json

MAPS_DIR = "./maps_metadata"  # Directory containing the JSON files
IMG_DIR = "./maps"  # Directory containing the images
OUTPUT_FILE = "maps_overview.html"

rows_html = ""

for filename in os.listdir(MAPS_DIR):
    if filename.endswith(".json"):
        filepath = os.path.join(MAPS_DIR, filename)

        base_name = filename[:-5]  # remove .json
        print(f"Processing {filename}...")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

            name = data.get("Name", "")
            year = data.get("Year", "")
            author = data.get("Author", "")
            places_list = data.get("Places of Occurrences", [])
            places = ", ".join(places_list)
            places_count = len(places_list)

            image_main = f"{base_name}.png"
            image_load = f"{base_name}_load.png"

            rows_html += f"""
            <tr>
                <td>{base_name}</td>
                <td>{name}</td>
                <td>{year}</td>
                <td>{author}</td>
                <td>{places}</td>
                <td>{places_count}</td>
                <td><a href="{IMG_DIR}/{image_main}" target="_blank"><img src="{IMG_DIR}/{image_main}" class="thumb"></a></td>
                <td><a href="{IMG_DIR}/{image_load}" target="_blank"><img src="{IMG_DIR}/{image_load}" class="thumb"></a></td>
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

.filters {{
    margin: 15px 0;
}}

input {{
    padding: 6px;
    margin-right: 10px;
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
    width: 110px;
    border-radius: 6px;
    transition: transform 0.2s;
}}

.thumb:hover {{
    transform: scale(1.6);
    z-index: 1000;
}}
</style>
</head>

<body>

<h2>Maps Overview</h2>

<div class="filters">
    <input type="text" id="nameFilter" onkeyup="filterTable()" placeholder="Filter by Name">
    <input type="text" id="authorFilter" onkeyup="filterTable()" placeholder="Filter by Author">
    <input type="text" id="placeFilter" onkeyup="filterTable()" placeholder="Filter by Place">
</div>

<table id="mapsTable">
    <thead>
        <tr>
            <th onclick="sortTable(0)">JSON File</th>
            <th onclick="sortTable(1)">Name</th>
            <th onclick="sortTable(2)">Year</th>
            <th onclick="sortTable(3)">Author</th>
            <th onclick="sortTable(4)">Places</th>
            <th onclick="sortTable(5)">Places Count</th>
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
    let authorInput = document.getElementById("authorFilter").value.toLowerCase();
    let placeInput = document.getElementById("placeFilter").value.toLowerCase();

    let table = document.getElementById("mapsTable");
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {{
        let nameCell = rows[i].cells[1];
        let authorCell = rows[i].cells[3];
        let placeCell = rows[i].cells[4];

        if (nameCell && authorCell && placeCell) {{
            let nameText = nameCell.textContent.toLowerCase();
            let authorText = authorCell.textContent.toLowerCase();
            let placeText = placeCell.textContent.toLowerCase();

            if (
                nameText.includes(nameInput) &&
                authorText.includes(authorInput) &&
                placeText.includes(placeInput)
            ) {{
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
        let A = a.cells[columnIndex].textContent;
        let B = b.cells[columnIndex].textContent;

        if (columnIndex === 5) {{
            A = parseInt(A);
            B = parseInt(B);
            return ascending ? A - B : B - A;
        }}

        if (columnIndex === 2) {{
            A = parseInt(A) || 0;
            B = parseInt(B) || 0;
            return ascending ? A - B : B - A;
        }}

        return ascending 
            ? A.toLowerCase().localeCompare(B.toLowerCase())
            : B.toLowerCase().localeCompare(A.toLowerCase());
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

print("Full dashboard created successfully.")