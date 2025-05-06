
import pyart
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path
import os

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC"):
    sweep = 0
    print(f"🌀 Using sweep: {sweep}")

    data = radar.fields[field]["data"]
    azimuths = radar.get_azimuth(sweep)
    ranges = radar.range["data"]
    elevation = radar.get_elevation(sweep)[0]

    # Create 2D azimuth and range arrays
    az2d, r2d = np.meshgrid(azimuths, ranges, indexing='ij')
    el2d = np.ones_like(az2d) * elevation

    # Convert to cartesian coordinates
    x, y, z = pyart.core.antenna_to_cartesian(r2d, az2d, el2d)

    # Apply gate filter to remove clutter
    gatefilter = pyart.correct.GateFilter(radar)
    gatefilter.exclude_transition()
    gatefilter.exclude_masked(field)
    gatefilter.exclude_invalid(field)
    gatefilter.exclude_below(field, -32)

    mask = gatefilter.gate_excluded[sweep]
    filtered_data = np.ma.masked_where(mask, data[sweep])

    # Plot
    fig, ax = plt.subplots(figsize=(10, 10))
    pm = ax.pcolormesh(x, y, filtered_data, cmap="NWSRef", vmin=-32, vmax=64)
    ax.set_aspect('equal')
    plt.axis("off")

    # Save overlay image
    output_image = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(output_image, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()

    # Determine geographic bounds (approximate)
    lats, lons = radar.get_gate_lat_lon(sweep)
    min_lat, max_lat = lats.min(), lats.max()
    min_lon, max_lon = lons.min(), lons.max()

    bounds = {
        "north": float(max_lat),
        "south": float(min_lat),
        "east": float(max_lon),
        "west": float(min_lon),
    }

    # Save bounds
    with open(f"../static/{site_id}_radar_bounds.json", "w") as f:
        json.dump(bounds, f)

    print(f"✅ Saved image to {output_image}")
    print(f"✅ Saved bounds to ../static/{site_id}_radar_bounds.json")

def main():
    data_dir = "../data"
    radar_files = sorted(Path(data_dir).glob("KFFC_*"))
    if not radar_files:
        print("❌ No radar files found.")
        return

    latest_file = radar_files[-1]
    print(f"📂 Reading radar file: {latest_file}")
    radar = pyart.io.read(str(latest_file))
    print(f"📡 Available fields: {list(radar.fields.keys())}")

    plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC")

if __name__ == "__main__":
    main()
