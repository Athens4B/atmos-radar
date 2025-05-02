# read_and_plot_all.py

import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def plot_radar_with_bounds(radar, field, image_filename, bounds_filename, cmap="NWSRef", vmin=None, vmax=None):
    display = pyart.graph.RadarMapDisplay(radar)

    # Output paths
    image_path = os.path.join("../static", image_filename)
    bounds_path = os.path.join("../static", bounds_filename)

    print(f"🖼️ Plotting {field} image with transparent background...")

    fig = plt.figure(figsize=(8, 8), dpi=120)
    proj = ccrs.PlateCarree()
    ax = fig.add_subplot(111, projection=proj)

    display.plot_ppi(
        field=field,
        sweep=0,
        ax=ax,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        colorbar_flag=False
    )

    # Remove extra metadata and formatting
    ax.set_title("")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    # Save image with transparency, no tight crop
    plt.savefig(image_path, transparent=True, pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Estimate bounds
    lat = radar.latitude['data'][0]
    lon = radar.longitude['data'][0]
    max_range_km = radar.range['data'][-1] / 1000.0
    delta_deg = max_range_km / 111.0

    bounds = {
        "west": lon - delta_deg,
        "east": lon + delta_deg,
        "south": lat - delta_deg,
        "north": lat + delta_deg,
    }

    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")


def main():
    # Load latest filename
    with open("latest_filename.txt", "r") as f:
        radar_file = f.read().strip()

    print(f"Reading radar file: {radar_file}")
    radar = pyart.io.read(radar_file)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    os.makedirs("../static", exist_ok=True)

    # Plot reflectivity and save bounds
    plot_radar_with_bounds(
        radar,
        field="reflectivity",
        image_filename="latest_radar_reflectivity.png",
        bounds_filename="latest_radar_bounds.json",
        cmap="NWSRef",
        vmin=-32,
        vmax=64,
    )


if __name__ == "__main__":
    main()
