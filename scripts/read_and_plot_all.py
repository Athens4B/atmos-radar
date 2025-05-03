# read_and_plot_all.py
import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def plot_radar_with_bounds(radar, site_id, field, image_filename, bounds_filename, cmap="NWSRef", vmin=None, vmax=None):
    display = pyart.graph.RadarMapDisplay(radar)

    image_path = os.path.join("../static", image_filename)
    bounds_path = os.path.join("../static", bounds_filename)

    print(f"🖼️ Plotting {field} image with transparent background...")
    fig = plt.figure(figsize=(6, 6), dpi=150)
    proj = ccrs.PlateCarree()
    ax = fig.add_subplot(111, projection=proj)

    display.plot_ppi(
        field=field,
        ax=ax,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        colorbar_flag=False,
    )

    # Hide axes and grid
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    ax.set_frame_on(False)

    # Save image
    plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Estimate map bounds
    lat = radar.latitude["data"][0]
    lon = radar.longitude["data"][0]
    max_range_km = radar.range["data"][-1] / 1000.0
    deg_offset = max_range_km / 111.0

    bounds = {
        "west": lon - deg_offset,
        "east": lon + deg_offset,
        "south": lat - deg_offset,
        "north": lat + deg_offset,
    }

    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")

def main():
    with open("latest_filename.txt", "r") as f:
        radar_file = f.read().strip()

    site_id = radar_file.split("_")[0]  # e.g., 'KFFC'
    print(f"📥 Reading radar file: {radar_file}")

    radar = pyart.io.read(radar_file)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    os.makedirs("../static", exist_ok=True)

    plot_radar_with_bounds(
        radar,
        site_id,
        field="reflectivity",
        image_filename=f"{site_id}_radar_reflectivity.png",
        bounds_filename=f"{site_id}_radar_bounds.json",
        cmap="NWSRef",
        vmin=-32,
        vmax=64,
    )

if __name__ == "__main__":
    main()
