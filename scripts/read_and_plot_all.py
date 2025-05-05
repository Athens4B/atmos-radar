import pyart
import numpy as np
import matplotlib.pyplot as plt
import json
import os

def plot_radar_with_bounds(radar, field, site_id):
    if radar.nsweeps < 1:
        print(f"❌ No sweeps found in radar file for {site_id}.")
        return

    # Safely assign the lowest sweep
    sweep = 0 if 0 in radar.sweep_start_ray_index else radar.get_start_end(0)[0]

    print(f"🌀 Using sweep: {sweep}")

    # Extract data for this sweep
    data = radar.fields[field]["data"]
    ranges = radar.range['data']
    azimuths = radar.get_azimuth(sweep)
    elevations = radar.get_elevation(sweep)

    # Gate filtering to reduce clutter
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_below(field, 0)
    filtered_data = np.ma.masked_where(gatefilter.gate_excluded, data)

    # Get lat/lon coordinates for sweep
    lats, lons = radar.get_gate_lat_lon_alt(sweep)[:2]

    # Plot
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    pm = ax.pcolormesh(lons, lats, filtered_data, cmap="pyart_NWSRef", vmin=-32, vmax=64)
    ax.set_title(f"{site_id} Reflectivity", fontsize=14)
    ax.set_xlim(np.min(lons), np.max(lons))
    ax.set_ylim(np.min(lats), np.max(lats))
    ax.set_aspect('equal')
    ax.axis("off")

    # Save image
    image_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(image_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Save bounds for Mapbox overlay
    bounds = {
        "north": float(np.max(lats)),
        "south": float(np.min(lats)),
        "east": float(np.max(lons)),
        "west": float(np.min(lons))
    }

    bounds_path = f"../static/{site_id}_radar_bounds.json"
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")

def main():
    site_id = "KFFC"
    data_dir = "/root/atmos-radar/data"
    radar_files = sorted([
        f for f in os.listdir(data_dir)
        if f.startswith(site_id) and not f.endswith(".gz")
    ], reverse=True)

    if not radar_files:
        print("❌ No radar files found.")
        return

    radar_file_path = os.path.join(data_dir, radar_files[0])
    print(f"📂 Reading radar file: {radar_file_path}")

    radar = pyart.io.read(radar_file_path)
    print(f"📡 Available fields: {list(radar.fields.keys())}")
    plot_radar_with_bounds(radar, field="reflectivity", site_id=site_id)

if __name__ == "__main__":
    main()
