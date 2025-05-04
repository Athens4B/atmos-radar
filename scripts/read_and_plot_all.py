import os
import json
import numpy as np
import pyart
import matplotlib.pyplot as plt

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC"):
    print(f"🖼️ Plotting {field} for {site_id}...")

    sweep = 0
    data = radar.fields[field]['data'][radar.get_slice(sweep)]
    gate_lat, gate_lon, _ = radar.get_gate_lat_lon_alt(sweep)

    lat_min, lat_max = gate_lat.min(), gate_lat.max()
    lon_min, lon_max = gate_lon.min(), gate_lon.max()

    # Plot
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    mesh = ax.pcolormesh(gate_lon, gate_lat, data, cmap="NWSRef", vmin=-32, vmax=64)
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    ax.axis("off")

    # Save image
    image_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(image_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()

    print(f"✅ Saved image to {image_path}")

    # Save bounds
    bounds = {
        "north": float(lat_max),
        "south": float(lat_min),
        "east": float(lon_max),
        "west": float(lon_min),
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
