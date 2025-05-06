import os
import pyart
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC"):
    sweep = 0
    print(f"🌀 Using sweep: {sweep}")

    # Extract data
    data = radar.fields[field]['data']
    ranges = radar.range['data']
    azimuths = radar.get_azimuth(sweep)
    elevations = radar.get_elevation(sweep)

    # Coordinates (lat/lon)
    lats, lons, _ = radar.get_gate_lat_lon_alt(sweep)

    # Gate filter to remove clutter
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_transition()
    gatefilter.exclude_masked(field)
    gatefilter.exclude_invalid(field)

    reflectivity = data[sweep]
    filtered_data = np.ma.masked_where(gatefilter.gate_excluded[sweep], reflectivity)

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
    ax.set_facecolor("none")  # Transparent background

    pm = ax.pcolormesh(
        lons, lats, filtered_data,
        cmap="NWSRef", vmin=-32, vmax=64,
        shading='auto'
    )
    plt.axis('off')

    # Save image
    image_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(image_path, bbox_inches='tight', pad_inches=0, transparent=True)
    print(f"✅ Saved image to {image_path}")

    # Save bounds
    bounds = {
        "north": float(np.nanmax(lats)),
        "south": float(np.nanmin(lats)),
        "east": float(np.nanmax(lons)),
        "west": float(np.nanmin(lons)),
    }

    bounds_path = f"../static/{site_id}_radar_bounds.json"
    with open(bounds_path, "w") as f:
        import json
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")

    plt.close(fig)

def main():
    site_id = "KFFC"
    data_dir = "../data"

    # Find latest radar file for the site
    files = sorted([
        f for f in os.listdir(data_dir)
        if f.startswith(site_id) and os.path.isfile(os.path.join(data_dir, f))
    ], reverse=True)

    if not files:
        print("❌ No radar files found.")
        return

    radar_file = files[0]
    radar_file_path = os.path.join(data_dir, radar_file)
    print(f"📂 Reading radar file: {radar_file_path}")

    # Read and plot
    radar = pyart.io.read(radar_file_path)
    print(f"📡 Available fields: {list(radar.fields.keys())}")
    plot_radar_with_bounds(radar, field="reflectivity", site_id=site_id)

if __name__ == "__main__":
    main()
