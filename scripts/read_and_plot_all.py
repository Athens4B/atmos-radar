import os
import json
import numpy as np
import pyart
import matplotlib.pyplot as plt

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC"):
    print(f"🖼️ Plotting {field} for {site_id}...")

    sweep = 0  # First sweep (0.5° angle)

    # Get reflectivity data as 2D array
    reflectivity = radar.fields[field]["data"]
    sweep_start = radar.sweep_start_ray_index['data'][sweep]
    sweep_end = radar.sweep_end_ray_index['data'][sweep]

    # Extract sweep data
    reflectivity = reflectivity[sweep_start:sweep_end+1]

    # Convert to masked array and handle shape
    reflectivity = np.ma.masked_invalid(reflectivity)

    # Get lat/lon positions for sweep
    lats, lons = radar.get_gate_lat_lon(sweep)

    # Set file paths
    image_path = f"../static/{site_id}_radar_reflectivity.png"
    bounds_path = f"../static/{site_id}_radar_bounds.json"

    # Plot
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    mesh = ax.pcolormesh(lons, lats, reflectivity, cmap="NWSRef", vmin=-32, vmax=64)
    ax.set_aspect('equal')
    ax.axis("off")
    plt.savefig(image_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Compute bounds
    min_lat, max_lat = lats.min(), lats.max()
    min_lon, max_lon = lons.min(), lons.max()
    bounds = {
        "west": float(min_lon),
        "east": float(max_lon),
        "south": float(min_lat),
        "north": float(max_lat)
    }
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")

def main():
    with open("latest_filename.txt", "r") as f:
        filename = f.read().strip()

    print(f"📂 Reading radar file: {filename}")
    radar = pyart.io.read(filename)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    os.makedirs("../static", exist_ok=True)
    plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC")

if __name__ == "__main__":
    main()
