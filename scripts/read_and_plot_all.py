import pyart
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

def plot_radar_with_bounds(radar, field, site_id):
    sweep = 0
    print(f"📡 Available fields: {list(radar.fields.keys())}")
    print(f"🌀 Using sweep: {sweep}")

    # Get the radar data
    data = radar.get_field(sweep, field)
    azimuths = radar.get_azimuth(sweep)
    ranges = radar.range['data']
    elevation = radar.fixed_angle['data'][sweep]
    elevations = np.full_like(azimuths, elevation)

    # Convert to Cartesian coordinates
    x, y, z = pyart.core.antenna_to_cartesian(ranges, azimuths, elevations)
    x_grid, y_grid = np.meshgrid(x, y)

    # Clutter filter
    gatefilter = pyart.correct.GateFilter(radar)
    gatefilter.exclude_transition()
    mask = gatefilter.gate_excluded[sweep]
    data_filtered = np.ma.masked_where(mask, data)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    pm = ax.pcolormesh(x_grid, y_grid, data_filtered, cmap="NWSRef", vmin=-32, vmax=64)
    ax.axis("off")
    plt.savefig(f"../static/{site_id}_radar_reflectivity.png", bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()

    # Compute approximate bounds for overlay (1° ≈ 111km)
    lat = radar.latitude["data"][0]
    lon = radar.longitude["data"][0]
    max_range_km = ranges.max() / 1000.0
    deg_buffer = max_range_km / 111.0
    bounds = {
        "north": lat + deg_buffer,
        "south": lat - deg_buffer,
        "east": lon + deg_buffer,
        "west": lon - deg_buffer,
    }

    with open(f"../static/{site_id}_radar_bounds.json", "w") as f:
        json.dump(bounds, f)

def main():
    import os
    radar_dir = "../data"
    radar_files = sorted(Path(radar_dir).glob("KFFC*"))
    if not radar_files:
        print("❌ No radar files found.")
        return

    radar_file = radar_files[-1]
    print(f"📂 Reading radar file: {radar_file}")
    radar = pyart.io.read(str(radar_file))
    plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC")

if __name__ == "__main__":
    main()
