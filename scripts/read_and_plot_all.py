import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt

def plot_radar_with_bounds(radar, field, site_id):
    print(f"🖼️ Plotting {field} for {site_id}...")

    # Apply clutter filtering
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_below(field, 5)  # Remove values below 5 dBZ (likely clutter)
    gatefilter.exclude_invalid(field)

    # Extract filtered reflectivity data
    sweep = 0
    data = radar.fields[field]['data']
    reflectivity = np.ma.masked_where(gatefilter.gate_excluded, data[sweep])

    # Get coordinates
    lats, lons = radar.get_gate_lat_lon_alt(sweep)[:2]

    # Determine plot bounds
    lat0, lon0 = radar.latitude['data'][0], radar.longitude['data'][0]
    max_range_km = radar.range['data'][-1] / 1000.0
    delta = max_range_km / 111.0  # Rough degrees

    bounds = {
        "west": lon0 - delta,
        "east": lon0 + delta,
        "south": lat0 - delta,
        "north": lat0 + delta
    }

    # Save bounds
    bounds_path = f"../static/{site_id}_radar_bounds.json"
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")

    # Plot
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    mesh = ax.pcolormesh(lons, lats, reflectivity, cmap="NWSRef", vmin=-32, vmax=64)
    ax.axis('off')
    ax.set_aspect('equal', 'box')

    # Save image
    image_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(image_path, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved image to {image_path}")

def main():
    site_id = "KFFC"
    with open("latest_filename.txt") as f:
        radar_file = f.read().strip()

    print(f"📂 Processing {site_id} → {radar_file}")
    radar = pyart.io.read(radar_file)
    print("📡 Available fields:", list(radar.fields.keys()))

    os.makedirs("../static", exist_ok=True)
    plot_radar_with_bounds(radar, field="reflectivity", site_id=site_id)

if __name__ == "__main__":
    main()
