import os
import json
import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def plot_radar_with_bounds(radar_file, output_image_path, bounds_json_path):
    radar = pyart.io.read(radar_file)
    display = pyart.graph.RadarMapDisplay(radar)

    # Radar site location
    radar_lat = radar.latitude['data'][0]
    radar_lon = radar.longitude['data'][0]

    # Approximate coverage range in degrees
    max_range_km = radar.range['data'][-1] / 1000.0
    degree_padding = max_range_km / 111.0  # 1 degree ≈ 111 km

    west = radar_lon - degree_padding
    east = radar_lon + degree_padding
    south = radar_lat - degree_padding
    north = radar_lat + degree_padding

    fig = plt.figure(figsize=(8, 8), dpi=150)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    display.plot_ppi_map(
        field="reflectivity",
        ax=ax,
        cmap="turbo",  # use any valid colormap
        colorbar_flag=False,
        title_flag=False
    )

    ax.set_extent([west, east, south, north], crs=ccrs.PlateCarree())
    plt.axis("off")
    plt.savefig(output_image_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved image to {output_image_path}")

    # Save bounding box as JSON
    bounds = [
        [west, north],  # top-left
        [east, north],  # top-right
        [east, south],  # bottom-right
        [west, south]   # bottom-left
    ]
    with open(bounds_json_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_json_path}")

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
