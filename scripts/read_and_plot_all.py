import os
import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import json

def plot_radar_with_bounds(radar_file, output_image_path, bounds_json_path):
    radar = pyart.io.read(radar_file)
    display = pyart.graph.RadarMapDisplay(radar)

    # Output directory
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)

    # Use PlateCarree projection (common for web mapping)
    proj = ccrs.PlateCarree()

    # Create figure and axis
    fig = plt.figure(figsize=(8, 8), dpi=150)
    ax = fig.add_subplot(1, 1, 1, projection=proj)

    # Plot radar PPI
    display.plot_ppi_map(
        field="reflectivity",
        ax=ax,
        colorbar_flag=False,
        title_flag=False,
        embellish=False,
        projection=proj
    )

    # Get extent and apply to axis
    ax.set_extent(display._get_map_extent(), crs=proj)
    extent = ax.get_extent(crs=proj)

    # Save PNG with transparent background
    fig.savefig(output_image_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close(fig)
    print(f"✅ Saved: {output_image_path}")

    # Save bounds JSON for Mapbox image overlay
    west, east, south, north = extent[0], extent[1], extent[2], extent[3]
    bounds = [
        [west, north],
        [east, north],
        [east, south],
        [west, south]
    ]
    with open(bounds_json_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds: {bounds_json_path}")

def main():
    try:
        with open("latest_filename.txt", "r") as f:
            radar_file = f.read().strip()
    except FileNotFoundError:
        print("❌ latest_filename.txt not found.")
        return

    plot_radar_with_bounds(
        radar_file=radar_file,
        output_image_path="../static/latest_radar_reflectivity.png",
        bounds_json_path="../static/latest_radar_bounds.json"
    )

if __name__ == "__main__":
    main()
