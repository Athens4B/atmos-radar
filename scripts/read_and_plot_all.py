import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def plot_radar_with_bounds(radar, field, image_filename, bounds_filename, cmap="NWSRef", vmin=None, vmax=None):
    from pyart.graph import RadarMapDisplay

    display = RadarMapDisplay(radar)

    # Output paths
    image_path = os.path.join("../static", image_filename)
    bounds_path = os.path.join("../static", bounds_filename)

    print(f"🖼️ Plotting {field} image with transparent background...")
    fig = plt.figure(figsize=(6, 6), dpi=150)
    proj = ccrs.PlateCarree()
    ax = fig.add_subplot(1, 1, 1, projection=proj)

    display.plot_ppi(
        field=field,
        ax=ax,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        colorbar_flag=False,
        title_flag=False,
        axislabels_flag=False
    )

    # Clean up plot
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    ax.set_frame_on(False)

    plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Save bounding box
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
    with open("latest_filename.txt", "r") as f:
        radar_file = f.read().strip()

    print(f"Reading radar file: {radar_file}")
    radar = pyart.io.read(radar_file)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    os.makedirs("../static", exist_ok=True)

    plot_radar_with_bounds(
        radar,
        field="reflectivity",
        image_filename="KFFC_radar.png",
        bounds_filename="KFFC_radar_bounds.json",
        cmap="NWSRef",
        vmin=-32,
        vmax=64
    )

if __name__ == "__main__":
    main()
