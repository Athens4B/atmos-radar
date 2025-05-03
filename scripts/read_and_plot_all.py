import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC"):
    print(f"🖼️ Plotting {field} for {site_id}...")

    # Output paths
    static_dir = "../static"
    os.makedirs(static_dir, exist_ok=True)
    image_path = os.path.join(static_dir, f"{site_id}_radar.png")
    bounds_path = os.path.join(static_dir, f"{site_id}_radar_bounds.json")

    # Extract radar data
    data = radar.fields[field]["data"]
    lats, lons = pyart.core.antenna_to_latlon(radar)
    
    # Autoscale
    vmin = np.percentile(data.compressed(), 1)
    vmax = np.percentile(data.compressed(), 99)
    print(f"📊 Autoscaling vmin={vmin:.1f}, vmax={vmax:.1f}")

    # Plot
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    mesh = ax.pcolormesh(lons, lats, data, cmap="NWSRef", vmin=vmin, vmax=vmax)
    ax.set_aspect("equal")

    # Clean layout
    ax.axis("off")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"✅ Saved radar image: {image_path}")

    # Save bounds
    bounds = {
        "west": float(lons.min()),
        "east": float(lons.max()),
        "south": float(lats.min()),
        "north": float(lats.max())
    }
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds: {bounds_path}")

def main():
    with open("latest_filename.txt", "r") as f:
        radar_file = f.read().strip()

    print(f"📂 Reading radar file: {radar_file}")
    radar = pyart.io.read(radar_file)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC")

if __name__ == "__main__":
    main()
