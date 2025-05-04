import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt

def plot_and_export(site_id, radar_file, field="reflectivity"):
    print(f"📂 Processing {site_id} → {radar_file}")
    radar = pyart.io.read(radar_file)
    print(f"📡 Available fields: {list(radar.fields.keys())}")

    sweep = 0
    ranges = radar.range['data']
    azimuths = radar.azimuth['data']
    elevations = radar.elevation['data']

    # Transform polar coordinates to Cartesian (centered on radar)
    x, y, _ = pyart.core.antenna_to_cartesian(ranges, azimuths, elevations)

    # Pull reflectivity or other selected field
    data_raw = radar.get_field(sweep, field)
    # Filter low values (clutter/noise)
    data = np.ma.masked_where(data_raw < -10, data_raw)

    # Plot settings
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    mesh = ax.pcolormesh(x, y, data, cmap="NWSRef", vmin=-32, vmax=64)
    ax.set_aspect('equal')
    ax.axis("off")

    # Save image to static folder
    image_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()

    # Save bounding box for Mapbox overlay
    lat, lon = radar.latitude['data'][0], radar.longitude['data'][0]
    max_range_km = radar.range['data'][-1] / 1000.0
    delta_deg = max_range_km / 111.0  # ~111 km per degree

    bounds = {
        "west": lon - delta_deg,
        "east": lon + delta_deg,
        "south": lat - delta_deg,
        "north": lat + delta_deg,
    }

    bounds_path = f"../static/{site_id}_radar_bounds.json"
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)

    print(f"✅ Saved image to {image_path}")
    print(f"✅ Saved bounds to {bounds_path}")


def main():
    # Add radar sites and filenames here
    radar_sites = {
        "KFFC": "KFFC_20250502_0148",
        # Add more sites like:
        # "KJKL": "KJKL_20250502_0150",
        # "KJGX": "KJGX_20250502_0152"
    }

    for site_id, radar_file in radar_sites.items():
        plot_and_export(site_id, radar_file, field="reflectivity")


if __name__ == "__main__":
    main()
