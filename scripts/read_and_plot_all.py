# read_and_plot_all.py
import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from pathlib import Path

def plot_radar_with_grid(radar_file, field, image_filename, bounds_filename):
    radar = pyart.io.read(radar_file)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    grid = pyart.map.grid_from_radars(
        radar,
        grid_shape=(1, 300, 300),
        grid_limits=((1000, 1000), (-150000.0, 150000.0), (-150000.0, 150000.0)),
        fields=[field],
        weighting_function='Barnes',
        gridding_algo='map_gates_to_grid'
    )

    field_data = grid.fields[field]["data"][0]

    radar_lat = radar.latitude["data"][0]
    radar_lon = radar.longitude["data"][0]

    extent_km = 150.0
    delta_deg = extent_km / 111.0
    bounds = {
        "west": radar_lon - delta_deg,
        "east": radar_lon + delta_deg,
        "south": radar_lat - delta_deg,
        "north": radar_lat + delta_deg,
    }

    output_dir = Path("../static")
    output_dir.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(8, 8), dpi=150)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.imshow(
        np.ma.masked_invalid(field_data[::-1]),
        extent=[bounds["west"], bounds["east"], bounds["south"], bounds["north"]],
        origin="lower",
        cmap="NWSRef",
        vmin=-32,
        vmax=64,
        alpha=1.0,
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    plt.savefig(output_dir / image_filename, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved image to {output_dir / image_filename}")

    with open(output_dir / bounds_filename, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {output_dir / bounds_filename}")

def main():
    try:
        with open("latest_filename.txt", "r") as f:
            radar_filename = f.read().strip()
    except FileNotFoundError:
        raise RuntimeError("❌ 'latest_filename.txt' not found. Cannot proceed.")

    plot_radar_with_grid(radar_filename, "reflectivity", "latest_radar_reflectivity.png", "latest_radar_bounds.json")

if __name__ == "__main__":
    main()
