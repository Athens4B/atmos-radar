import os
import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import json
from pyart.map.grid_mapper import grid_from_radars


def plot_composite_radar_with_bounds(radar, field, image_filename, bounds_filename, cmap="NWSRef", vmin=None, vmax=None):
    # Interpolate radar data to a Cartesian grid
    print("🧮 Gridding radar volume for full sweep composite...")
    grid = grid_from_radars(
        radar,
        grid_shape=(1, 500, 500),
        grid_limits=((1000, 10000), (-150000, 150000), (-150000, 150000)),
        fields=[field]
    )

    # Extract the 2D grid slice
    grid_field = grid.fields[field]["data"][0]
    lons, lats = grid.point_longitude["data"][0], grid.point_latitude["data"][0]

    # Output paths
    image_path = os.path.join("../static", image_filename)
    bounds_path = os.path.join("../static", bounds_filename)

    # Plotting
    print(f"🖼️ Plotting {field} composite image with transparent background...")
    fig = plt.figure(figsize=(8, 8), dpi=150)
    proj = ccrs.PlateCarree()
    ax = fig.add_subplot(111, projection=proj)

    mesh = ax.pcolormesh(lons, lats, grid_field, cmap=cmap, vmin=vmin, vmax=vmax, transform=proj)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    # Save the image
    plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Calculate bounds for Mapbox overlay
    bounds = {
        "west": np.min(lons),
        "east": np.max(lons),
        "south": np.min(lats),
        "north": np.max(lats),
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

    # Generate composite image from all sweeps
    plot_composite_radar_with_bounds(
        radar,
        field="reflectivity",
        image_filename="latest_radar_reflectivity.png",
        bounds_filename="latest_radar_bounds.json",
        cmap="NWSRef",
        vmin=-32,
        vmax=64,
    )


main()
