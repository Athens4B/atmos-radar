import pyart
import os
import numpy as np
import matplotlib.pyplot as plt
import json
from glob import glob

def get_latest_radar_file(data_dir, station_id):
    files = sorted(
        [f for f in os.listdir(data_dir) if f.startswith(station_id)],
        reverse=True
    )
    if not files:
        return None
    return os.path.join(data_dir, files[0])

def plot_radar_with_bounds(radar, field, site_id):
    sweep = 0
    print(f"🌀 Using sweep: {sweep}")
    
    display = pyart.graph.RadarMapDisplay(radar)
    lats, lons = radar.get_gate_lat_lon_alt(sweep)[0:2]
    
    data = radar.fields[field]["data"]
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_masked(field)
    data_filtered = np.ma.masked_where(gatefilter.gate_excluded, data) 

    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes()

    pm = ax.pcolormesh(
        lons, lats, data_filtered,
        cmap="pyart_NWSRef",
        vmin=-32, vmax=64,
        shading="auto"
    )
    ax.set_aspect('equal')
    plt.axis("off")

    output_image = f"../static/{site_id}_radar_reflectivity.png"
    output_json = f"../static/{site_id}_radar_bounds.json"
    plt.savefig(output_image, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()

    bounds = {
        "north": float(lats.max()),
        "south": float(lats.min()),
        "east": float(lons.max()),
        "west": float(lons.min())
    }

    with open(output_json, "w") as f:
        json.dump(bounds, f)

    print(f"✅ Saved image to {output_image}")
    print(f"✅ Saved bounds to {output_json}")

def main():
    data_dir = "/root/atmos-radar/data"
    site_id = "KFFC"

    radar_file_path = get_latest_radar_file(data_dir, site_id)
    if not radar_file_path:
        print("❌ No radar files found.")
        return

    print(f"📂 Reading radar file: {radar_file_path}")
    radar = pyart.io.read(radar_file_path)
    print(f"📡 Available fields: {list(radar.fields.keys())}")

    plot_radar_with_bounds(radar, field="reflectivity", site_id=site_id)

if __name__ == "__main__":
    main()
