import os
import json
import numpy as np
import pyart
import matplotlib.pyplot as plt
from pyart.core.transforms import antenna_to_cartesian, cartesian_to_geographic

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC"):
    print(f"🖼️ Plotting {field} for {site_id}...")

    sweep = 0  # 0.5 degree
    start = radar.sweep_start_ray_index['data'][sweep]
    end = radar.sweep_end_ray_index['data'][sweep]

    # Extract 2D reflectivity data
    refl = radar.fields[field]['data'][start:end+1]
    refl = np.ma.masked_invalid(refl)

    # Get gate coordinates
    rng = radar.range['data']  # 1D
    az = radar.azimuth['data'][start:end+1]  # 1D

    # Convert to 2D Cartesian coordinates
    x, y, z = antenna_to_cartesian(rng, az)
    x2d, y2d = np.meshgrid(x / 1000.0, y / 1000.0)  # km

    # Convert to lat/lon
    radar_lat = radar.latitude['data'][0]
    radar_lon = radar.longitude['data'][0]
    lons, lats = cartesian_to_geographic(x2d * 1000, y2d * 1000, radar_lon, radar_lat)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    mesh = ax.pcolormesh(lons, lats, refl, cmap="NWSRef", vmin=-32, vmax=64)
    ax.set_aspect('equal')
    ax.axis("off")

    image_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(image_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Get bounds
    bounds = {
        "west": float(np.min(lons)),
        "east": float(np.max(lons)),
        "south": float(np.min(lats)),
        "north": float(np.max(lats))
    }
    bounds_path = f"../static/{site_id}_radar_bounds.json"
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
