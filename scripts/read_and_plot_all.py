import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt

def plot_radar_with_bounds(radar, field, site_id):
    print(f"🖼️ Plotting {field} for {site_id}...")

    # Get radar origin
    radar_lat = radar.latitude['data'][0]
    radar_lon = radar.longitude['data'][0]

    # Get gate lat/lon for first sweep
    lats, lons = radar.get_gate_lat_lon(0)

    # Get field data
    data = radar.fields[field]['data']
    data = np.ma.masked_invalid(data)

    # Prepare figure
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    mesh = ax.pcolormesh(lons, lats, data, cmap="pyart_NWSRef", vmin=-32, vmax=64)

    # Hide axes and frame
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    ax.set_aspect('equal')
    plt.axis('off')

    # Save image
    image_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"✅ Saved {image_path}")

    # Save bounds
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
        radar_file = f.read().strip()

    print(f"📂 Reading radar file: {radar_file}")
    radar = pyart.io.read(radar_file)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    os.makedirs("../static", exist_ok=True)
    plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC")

if __name__ == "__main__":
    main()
