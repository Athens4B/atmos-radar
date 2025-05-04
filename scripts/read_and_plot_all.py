import os
import json
import numpy as np
import matplotlib.pyplot as plt
import pyart

def plot_radar_with_bounds(radar, field, site_id):
    print(f"🖼️ Plotting {field} for {site_id}...")

    sweep = 0  # Lowest elevation scan (usually 0.5°)
    data = radar.fields[field]["data"]
    data = np.ma.masked_where(data < 5, data)  # Filter out clutter/noise (<5 dBZ)

    # Get lat/lon for sweep
    lats, lons = radar.get_gate_lat_lon_alt(sweep)[0:2]
    reflectivity = data[sweep]

    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    mesh = ax.pcolormesh(lons, lats, reflectivity, cmap="NWSRef", vmin=-32, vmax=64)

    ax.set_xlim(np.min(lons), np.max(lons))
    ax.set_ylim(np.min(lats), np.max(lats))
    ax.axis("off")

    # Save image
    output_image = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(output_image, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {output_image}")

    # Save bounds as JSON
    bounds = {
        "west": float(np.min(lons)),
        "east": float(np.max(lons)),
        "south": float(np.min(lats)),
        "north": float(np.max(lats)),
    }
    with open(f"../static/{site_id}_radar_bounds.json", "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to ../static/{site_id}_radar_bounds.json")

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
