# read_and_plot_all.py
import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def plot_radar_with_bounds(radar, field, image_filename, bounds_filename, cmap="NWSRef", vmin=None, vmax=None):
    display = pyart.graph.RadarMapDisplay(radar)

    # Get radar center and range
    lat, lon = radar.latitude['data'][0], radar.longitude['data'][0]
    max_range_km = radar.range['data'][-1] / 1000.0
    delta_deg = max_range_km / 111.0  # ~111 km per degree

    bounds = {
        "west": lon - delta_deg,
        "east": lon + delta_deg,
        "south": lat - delta_deg,
        "north": lat + delta_deg,
    }

    aspect_ratio = (bounds["north"] - bounds["south"]) / (bounds["east"] - bounds["west"])
    fig_width = 8
    fig_height = fig_width * aspect_ratio

    fig = plt.figure(figsize=(fig_width, fig_height), dpi=150)
    proj = ccrs.PlateCarree()
    ax = fig.add_subplot(111, projection=proj)

    display.plot_ppi(
        field=field,
        sweep=0,
        ax=ax,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        colorbar_flag=False,
        embellish=False
    )

    # Force bounds to remove default auto-zooming
    ax.set_extent([
        bounds["west"],
        bounds["east"],
        bounds["south"],
        bounds["north"]
    ], crs=proj)

    # Turn off any axes decorations
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("off")
    ax.spines['geo'].set_visible(False)

    os.makedirs("../static", exist_ok=True)

    image_path = os.path.join("../static", image_filename)
    bounds_path = os.path.join("../static", bounds_filename)

    plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()

    print(f"✅ Saved image to {image_path}")
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

    plot_radar_with_bounds(
        radar,
        field="reflectivity",
        image_filename="latest_radar_reflectivity.png",
        bounds_filename="latest_radar_bounds.json",
        cmap="NWSRef",
        vmin=-32,
        vmax=64
    )


if __name__ == "__main__":
    main()
