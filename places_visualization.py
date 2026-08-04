import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from collections import defaultdict

# ── 1. Načtení dat ────────────────────────────────────────────────────────────

MAPS_DIR = "_MAPS_"

poo_to_maps = defaultdict(set)

for filename in os.listdir(MAPS_DIR):
    if not filename.endswith(".json"):
        continue
    filepath = os.path.join(MAPS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Chyba při čtení: {filename}")
            continue

    map_id = filename
    poo_list = data.get("Places of Occurrences", [])
    for poo in poo_list:
        poo_to_maps[poo].add(map_id)

# ── 2. Příprava skupin ────────────────────────────────────────────────────────

def poo_category(name: str) -> int:
    if "UlozTo"   in name: return 0
    if "Webshare" in name: return 1
    return 2

def is_storage(name: str) -> bool:
    return "UlozTo" in name or "Webshare" in name

def is_ulozto(name: str) -> bool:
    return "UlozTo" in name

def is_webshare(name: str) -> bool:
    return "Webshare" in name

# Skupiny
ulozto_poo   = sorted((p for p in poo_to_maps if is_ulozto(p)),   key=lambda p: len(poo_to_maps[p]))
webshare_poo = sorted((p for p in poo_to_maps if is_webshare(p)),  key=lambda p: len(poo_to_maps[p]))
web_poo      = sorted((p for p in poo_to_maps if not is_storage(p)), key=lambda p: len(poo_to_maps[p]))
storage_poo  = ulozto_poo + webshare_poo   # UlozTo pak Webshare

all_x_poo = sorted(                         # X pro obrázek 1
    poo_to_maps.keys(),
    key=lambda p: (poo_category(p), len(poo_to_maps[p]))
)

# ── 3. Pomocné funkce ─────────────────────────────────────────────────────────

def build_matrix(y_poos, x_poos):
    mat = np.zeros((len(y_poos), len(x_poos)), dtype=float)
    for ri, yp in enumerate(y_poos):
        maps_y = poo_to_maps[yp]
        sy = len(maps_y)
        if sy == 0:
            continue
        for ci, xp in enumerate(x_poos):
            shared = len(maps_y & poo_to_maps[xp])
            mat[ri, ci] = shared / sy
    return mat

def x_label(poo):
    return f"{poo}  ({len(poo_to_maps[poo])})"

def y_label(poo, row):
    return f"{poo}  ({len(poo_to_maps[poo])})  Σ={row.sum():.2f}"

def make_cmap():
    base_colors = plt.get_cmap("coolwarm")(np.linspace(0, 1, 256))
    new_colors  = np.vstack([np.array([[0, 0, 0, 1]]), base_colors])
    cmap        = mcolors.ListedColormap(new_colors)
    bounds      = np.concatenate([[0], np.linspace(1e-9, 1.0, 256)])
    norm        = mcolors.BoundaryNorm(bounds, ncolors=cmap.N)
    return cmap, norm

def render(y_poos, x_poos, title, xlabel, filename,
           cell_size=0.5, font_size=15):
    mat = build_matrix(y_poos, x_poos)

    xl = [x_label(p) for p in x_poos]
    yl = [y_label(y_poos[i], mat[i]) for i in range(len(y_poos))]

    df = pd.DataFrame(mat, index=yl, columns=xl)
    cmap, norm = make_cmap()

    fig_w = max(12, len(x_poos) * cell_size + 8)
    fig_h = max( 8, len(y_poos) * cell_size + 4)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    sns.heatmap(
        df, ax=ax,
        cmap=cmap, norm=norm,
        linewidths=0.5, linecolor="white",
        xticklabels=True, yticklabels=True,
        cbar_kws={"label": "| mapy(X) ∩ mapy(Y) | / | mapy(Y) |"},
    )

    ax.set_title(title, fontsize=14, pad=14)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel("PoO bez úložišť (osa Y)", fontsize=11)
    ax.tick_params(axis="x", labelsize=font_size, rotation=90)
    ax.tick_params(axis="y", labelsize=font_size, rotation=0)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    print(f"Uloženo: {filename}")
    plt.close(fig)

# ── 4. Generování tří obrázků ─────────────────────────────────────────────────

# Obrázek 1 – vše (Y: weby, X: UlozTo | Webshare | weby)
render(
    y_poos   = web_poo,
    x_poos   = all_x_poo,
    title    = "Heatmap – Vše",
    xlabel   = "Všechny místa výskytu",
    filename = "heatmap_1_vse.png",
)

# Obrázek 2 – Y: vše, X: pouze UlozTo + Webshare
render(
    y_poos   = web_poo,
    x_poos   = storage_poo,
    title    = "Heatmap – Úložiště",
    xlabel   = "Úložiště  [UlozTo | Webshare]",
    filename = "heatmap_2_uloziste.png",
)

# Obrázek 3 – Y: vše, X: pouze weby
render(
    y_poos   = web_poo,
    x_poos   = web_poo,
    title    = "Heatmapa – X: pouze weby",
    xlabel   = "Weby – seřazeno podle počtu map",
    filename = "heatmap_3_weby.png",
)