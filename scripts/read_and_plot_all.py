# read_and_plot_all.py
import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def save_world_file(output_image, bounds):
    # Write PGW (PNG World File) for georeferencing in Mapbox
    pgw_path = output_image.replace(".png", ".pgw")
    west, east = bounds["west"], bounds["east"]
    south, north = bounds["south"], bounds["north"]

    # Calculate pixel size
    img_width = 800  # Based on figsize=(8, 8) and dpi=100
    img_height = 800
    pixel_x = (east - west) / img_width
    pixel_y = (south - north) / img_height  # Note: negative for north-up

    with open(pgw_path, "w") as f:
        f.write(f"{pixel_x:.10f}\n")  # x pixel size
        f.write("0.0\n")              # rotation (0)
        f.write("0.0\n")              # rotation (0)
        f.write(f"{pixel_y:.10f}\n")  # y pixel size (negative)
        f.write(f"{west + pixel_x / 2:.10f}\n")  # x of center of upper-left pixel
        f.write(f"{north + pixel_y / 2:.10f}\n")  # y of center of upper-left pixel


def plot_radar_with_bounds(radar, field, image_filename, bounds_filename, cmap="NWSRef", vmin=None, vmax=None):
    display = pyart.graph.RadarMapDisplay(radar)

    image_path = os.path.join("../static", image_filename)
    bounds_path = os.path.join("../static", bounds_filename)

    print(f"🖼️ Plotting {field} image with transparent background...")

    fig = plt.figure(figsize=(8, 8), dpi=100)
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

    # Remove metadata, ticks, and frame
    ax.set_title("")
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Bounding box calculation
    lat = radar.latitude["data"][0]
    lon = radar.longitude["data"][0]
    max_range_km = radar.range["data"][-1] / 1000.0
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

    save_world_file(image_path, bounds)
    print(f"🌍 World file saved alongside image.")


def main():
    try:
        with open("latest_filename.txt", "r") as f:
            radar_file = f.read().strip()
    except FileNotFoundError:
        print("❌ latest_filename.txt not found.")
        return

    print(f"Reading radar file: {radar_file}")
    radar = pyart.io.read(radar_file)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    os.makedirs("../static", exist_ok=True)

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
