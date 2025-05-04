import os
import json
import numpy as np
import pyart
import matplotlib.pyplot as plt

from pyart.core.transforms import antenna_to_cartesian

def plot_and_export(site_id, radar_file, field="reflectivity"):
    print(f"📂 Processing {site_id} → {radar_file}")
    radar = pyart.io.read(radar_file)
    print("📡 Available fields:", list(radar.fields.keys()))

    # Extract sweep 0
    sweep = 0
    ranges = radar.range['data']
    azimuths = radar.get_azimuth(sweep)
    elevation = radar.fixed_angle['data'][sweep]

    # Grid coordinates
    r_mesh, az_mesh = np.meshgrid(ranges, azimuths)
    elev_array = np.full_like(r_mesh, np.deg2rad(elevation))

    x, y, z = antenna_to_cartesian(r_mesh, az_mesh, elev_array)

    # Get reflectivity data
    data = radar.get_field(sweep, field)

    # Clean up NaNs and clutter
    data = np.ma.masked_invalid(data)
    data = np.ma.masked_where(data < 0, data)  # remove ground clutter

    # Plot
    print(f"🖼️ Plotting {field} for {site_id}...")
    fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
    mesh = ax.pcolormesh(x / 1000, y / 1000, data, cmap="NWSRef", vmin=-32, vmax=64)
    ax.axis("off")
    ax.set_aspect("equal")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # File paths
    image_path = f"../static/radar_overlay.png"
    bounds_path = f"../static/radar_bounds.json"

    plt.savefig(image_path, transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Calculate lat/lon bounds for image overlay
    radar_lat = radar.latitude['data'][0]
    radar_lon = radar.longitude['data'][0]

    max_km = np.max(ranges) / 1000
    delta_deg = max_km / 111.0  # approx 1 deg = 111 km

    bounds = {
        "west": radar_lon - delta_deg,
        "east": radar_lon + delta_deg,
        "south": radar_lat - delta_deg,
        "north": radar_lat + delta_deg,
    }

    with open(bounds_path, "w") as f:
        json.dump(bounds, f)

    print(f"✅ Saved bounds to {bounds_path}")

def main():
    site_id = "KFFC"
    with open("latest_filename.txt") as f:
        radar_file = f.read().strip()
    plot_and_export(site_id, radar_file, field="reflectivity")

if __name__ == "__main__":
    main()
