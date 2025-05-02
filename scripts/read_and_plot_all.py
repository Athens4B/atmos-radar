# read_and_plot_all.py
import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def save_world_file(image_path, bounds, width, height):
    pgw_path = image_path.replace(".png", ".pgw")
    west, east, south, north = bounds
    pixel_x = (east - west) / width
    pixel_y = (south - north) / height  # Negative for north-up

    with open(pgw_path, "w") as f:
        f.write(f"{pixel_x:.10f}\n")
        f.write("0.0\n")
        f.write("0.0\n")
        f.write(f"{pixel_y:.10f}\n")
        f.write(f"{west + pixel_x / 2:.10f}\n")
        f.write(f"{north + pixel_y / 2:.10f}\n")


def plot_radar_with_geo(radar, field, image_filename, bounds_filename, cmap="NWSRef", vmin=None, vmax=None):
    display = pyart.graph.RadarMapDisplay(radar)

    image_path = os.path.join("../static", image_filename)
    bounds_path = os.path.join("../static", bounds_filename)

    fig = plt.figure(figsize=(8, 8), dpi=100)
    ax = fig.add_subplot(111, projection=ccrs.PlateCarree())

    # Plot radar data (assumes sweep 0 is full azimuth)
    display.plot_ppi_map(
        field=field,
        sweep=0,
        ax=ax,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        colorbar_flag=False,
        embellish=False,
        lat_lines=[],
        lon_lines=[]
    )

    # Strip extra metadata
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_axis_off()
    fig.patch.set_alpha(0.0)

    # Match bounds to image
    extent = ax.get_extent()  # (west, east, south, north)
    width, height = fig.get_size_inches() * fig.dpi

    # Save image exactly as rendered
    plt.savefig(image_path, transparent=True, bbox_inches=None, pad_inches=0)
    plt.close()

    print(f"✅ Saved image to {image_path}")
    print(f"🗺️  Bounds: {extent}")

    with open(bounds_path, "w") as f:
        json.dump({
            "west": extent[0],
            "east": extent[1],
            "south": extent[2],
            "north": extent[3]
        }, f)
    print(f"✅ Saved bounds to {bounds_path}")

    save_world_file(image_path, extent, width, height)
    print(f"✅ Saved PGW to match image.")


def main():
    with open("latest_filename.txt", "r") as f:
        radar_file = f.read().strip()

    print(f"📂 Reading radar file: {radar_file}")
    radar = pyart.io.read(radar_file)

    print("✅ Radar loaded.")
    print("📡 Fields:", list(radar.fields.keys()))

    os.makedirs("../static", exist_ok=True)

    plot_radar_with_geo(
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
