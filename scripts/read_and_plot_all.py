import os
import pyart
import numpy as np
import json
import matplotlib.pyplot as plt

def plot_radar_with_bounds(radar, field, site_id):
    print(f"🖼️ Plotting {field} for {site_id}...")

    sweep = 0
    data = radar.fields[field]["data"]
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_masked(field)
    filtered_data = np.ma.masked_where(gatefilter.gate_excluded, data[sweep])

    lats, lons, _ = radar.get_gate_lat_lon_alt(sweep)

    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    mesh = ax.pcolormesh(lons, lats, filtered_data, cmap="NWSRef", vmin=-32, vmax=64)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_axis_off()
    image_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(image_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    lat, lon = radar.latitude['data'][0], radar.longitude['data'][0]
    max_range_km = radar.range['data'][-1] / 1000.0
    delta_deg = max_range_km / 111.0
    bounds = {
        "west": lon - delta_deg,
        "east": lon + delta_deg,
        "south": lat - delta_deg,
        "north": lat + delta_deg
    }

    bounds_path = f"../static/{site_id}_radar_bounds.json"
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")

def main():
    with open("/root/atmos-radar/data/latest_filename.txt", "r") as f:
        filename = f.read().strip()
    radar_file_path = os.path.join("/root/atmos-radar/data", filename)
    print(f"📂 Reading radar file: {radar_file_path}")
    radar = pyart.io.read(radar_file_path)
    print("📡 Available fields:", list(radar.fields.keys()))

    plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC")

if __name__ == "__main__":
    main()
