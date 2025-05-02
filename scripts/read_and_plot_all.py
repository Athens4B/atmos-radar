import os
import json
import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def plot_radar_with_bounds(radar_file, output_image_path, bounds_json_path):
    radar = pyart.io.read(radar_file)
    display = pyart.graph.RadarMapDisplay(radar)

    # Radar site lat/lon
    radar_lat = radar.latitude['data'][0]
    radar_lon = radar.longitude['data'][0]

    # Get max range in degrees (approx 1° ≈ 111 km)
    max_range_km = radar.range['data'][-1] / 1000.0
    deg_padding = max_range_km / 111.0

    west = radar_lon - deg_padding
    east = radar_lon + deg_padding
    south = radar_lat - deg_padding
    north = radar_lat + deg_padding

    # Plot image
    fig = plt.figure(figsize=(8, 8), dpi=150)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    display.plot_ppi(
        field="reflectivity",
        ax=ax,
        colorbar_flag=False,
        title_flag=False,
        embellish=False,
    )

    ax.set_extent([west, east, south, north], crs=ccrs.PlateCarree())
    plt.axis("off")
    plt.savefig(output_image_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved: {output_image_path}")

    # Save geographic bounds
    bounds = [
        [west, north],  # Top-left
        [east, north],  # Top-right
        [east, south],  # Bottom-right
        [west, south]   # Bottom-left
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
