import os
import json
import numpy as np
import pyart
import matplotlib.pyplot as plt
from pyart.core.transforms import antenna_to_cartesian

def plot_radar_with_bounds(radar, field, site_id):
    print(f"🖼️ Plotting {field} for {site_id}...")

    # Get the lowest sweep
    sweep = 0
    start = radar.sweep_start_ray_index['data'][sweep]
    end = radar.sweep_end_ray_index['data'][sweep]

    # Extract data
    azimuths = radar.azimuth['data'][start:end+1]
    ranges = radar.range['data']
    elevations = np.full_like(azimuths, radar.fixed_angle['data'][sweep])

    # Create 2D grids
    az2d, r2d = np.meshgrid(azimuths, ranges, indexing='ij')
    el2d = np.full_like(az2d, radar.fixed_angle['data'][sweep])

    # Convert to cartesian coordinates (in meters)
    x, y, z = antenna_to_cartesian(r2d, az2d, el2d)

    # Get reflectivity data and mask clutter
    data = radar.fields[field]['data'][start:end+1]
    data = np.ma.masked_where(data.filled(0) < 5, data)  # Mask reflectivity < 5 dBZ

    # Convert to km for plotting
    x_km, y_km = x / 1000.0, y / 1000.0

    # Setup plot
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    mesh = ax.pcolormesh(x_km, y_km, data, cmap="NWSRef", vmin=-32, vmax=64)
    ax.set_axis_off()
    ax.set_aspect("equal")

    output_path = "../static/radar_overlay.png"
    plt.savefig(output_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {output_path}")

    # Estimate bounds in degrees
    lat0 = radar.latitude['data'][0]
    lon0 = radar.longitude['data'][0]
    max_range_km = ranges[-1] / 1000.0
    deg_delta = max_range_km / 111.0  # Rough conversion

    bounds = {
        "north": lat0 + deg_delta,
        "south": lat0 - deg_delta,
        "east": lon0 + deg_delta,
        "west": lon0 - deg_delta
    }

    with open("../static/radar_bounds.json", "w") as f:
        json.dump(bounds, f)
    print("✅ Saved bounds to ../static/radar_bounds.json")

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
