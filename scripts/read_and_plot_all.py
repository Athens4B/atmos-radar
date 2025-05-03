import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt

def plot_radar_with_bounds(radar, field, site_id):
    from mpl_toolkits.basemap import Basemap

    print(f"🖼️ Plotting {field} for {site_id}...")

    # Get radar location
    radar_lat = radar.latitude['data'][0]
    radar_lon = radar.longitude['data'][0]

    # Get gate lat/lon
    lats, lons = radar.get_gate_lat_lon(0)  # Sweep 0 only

    # Get field data
    data = radar.fields[field]['data']
    data = np.ma.masked_where(np.isnan(data), data)

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)

    # Plot using actual lat/lon bins
    mesh = ax.pcolormesh(lons, lats, data, cmap="pyart_NWSRef", vmin=-32, vmax=64)

    # Clean up layout
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    ax.set_aspect('equal')  # Preserve aspect ratio
    plt.axis('off')

    # Save transparent PNG
    image_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"✅ Saved {image_path}")

    # Calculate bounds
    bounds = {
        "west": np.min(lons),
        "east": np.max(lons),
        "south": np.min(lats),
        "north": np.max(lats)
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
