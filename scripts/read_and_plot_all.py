import os
import glob
import pyart
import numpy as np
import matplotlib.pyplot as plt
from pyart.filters import GateFilter
from pyart.core.transforms import antenna_to_lat_lon
import json

def plot_radar_with_bounds(radar, field="reflectivity", site_id="RADAR"):
    sweep = 0
    print(f"🌀 Using sweep: {sweep}")

    # Get gate lat/lon
    lats, lons = antenna_to_lat_lon(radar, sweep)

    # Get radar data
    data = radar.fields[field]['data']
    data = data[sweep] if data.ndim == 3 else data

    # Apply gate filter to remove clutter
    gatefilter = GateFilter(radar)
    gatefilter.exclude_transition()
    gatefilter.exclude_masked(field)
    gatefilter.exclude_invalid(field)
    filtered_data = np.ma.masked_where(gatefilter.gate_excluded, data)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
    pm = ax.pcolormesh(lons, lats, filtered_data, cmap="NWSRef", vmin=-32, vmax=64)
    ax.axis("off")
    ax.set_aspect('equal', adjustable='box')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Save image
    out_img_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(out_img_path, bbox_inches="tight", pad_inches=0, transparent=True)
    print(f"✅ Saved image to {out_img_path}")

    # Save bounds for overlay
    bounds = {
        "west": float(np.min(lons)),
        "east": float(np.max(lons)),
        "south": float(np.min(lats)),
        "north": float(np.max(lats)),
    }

    out_bounds_path = f"../static/{site_id}_radar_bounds.json"
    with open(out_bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {out_bounds_path}")

    plt.close()

def find_latest_radar_file(station_id):
    search_path = f"../data/{station_id}_*"
    files = sorted(glob.glob(search_path))
    return files[-1] if files else None

def main():
    site_id = "KFFC"
    radar_file_path = find_latest_radar_file(site_id)

    if radar_file_path is None:
        print("❌ No radar files found.")
        return

    print(f"📂 Reading radar file: {radar_file_path}")
    radar = pyart.io.read(radar_file_path)
    print(f"📡 Available fields: {list(radar.fields.keys())}")

    plot_radar_with_bounds(radar, field="reflectivity", site_id=site_id)

if __name__ == "__main__":
    main()
