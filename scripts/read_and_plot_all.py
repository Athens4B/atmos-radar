import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from pyart.map import grid_from_radars

def plot_radar_composite(radar, site_id="KFFC"):
    print(f"🖼️ Plotting reflectivity for {site_id}...")

    # Grid radar data to fill in full sweep
    grid = grid_from_radars(
        radar,
        grid_shape=(1, 500, 500),
        grid_limits=((1000, 10000), (-150000, 150000), (-150000, 150000)),
        fields=['reflectivity'],
        weighting_function='Nearest',
        gridding_algo='map_gates_to_grid',
    )

    reflectivity = grid.fields['reflectivity']['data'][0]

    # Calculate plot bounds in degrees
    lat = radar.latitude['data'][0]
    lon = radar.longitude['data'][0]
    extent_deg = 150 / 111.0
    bounds = {
        "west": lon - extent_deg,
        "east": lon + extent_deg,
        "south": lat - extent_deg,
        "north": lat + extent_deg
    }

    os.makedirs("../static", exist_ok=True)
    image_path = f"../static/{site_id}_radar_composite.png"
    bounds_path = f"../static/{site_id}_radar_bounds.json"

    # Plot image
    fig = plt.figure(figsize=(8, 8), dpi=150)
    ax = plt.axes(projection=ccrs.PlateCarree())

    x = grid.x['data'] / 1000.0
    y = grid.y['data'] / 1000.0
    x2d, y2d = np.meshgrid(x, y)

    ax.pcolormesh(x2d, y2d, reflectivity, cmap="NWSRef", vmin=-32, vmax=64)
    ax.set_extent([bounds["west"], bounds["east"], bounds["south"], bounds["north"]])
    ax.axis("off")

    plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()

    # Save bounds
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)

    print(f"✅ Saved image to {image_path}")
    print(f"✅ Saved bounds to {bounds_path}")

def main():
    with open("latest_filename.txt", "r") as f:
        filename = f.read().strip()
    print(f"📂 Reading radar file: {filename}")
    radar = pyart.io.read(filename)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    plot_radar_composite(radar, site_id="KFFC")

if __name__ == "__main__":
    main()
