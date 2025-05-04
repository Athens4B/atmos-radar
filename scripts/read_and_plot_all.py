import os
import pyart
import numpy as np
import json
import matplotlib.pyplot as plt
from pyart.core.transforms import antenna_to_cartesian


def plot_and_export(site_id, radar_file):
    radar = pyart.io.read(radar_file)
    print(f"📂 Processing {site_id} → {radar_file}")
    print("📡 Available fields:", list(radar.fields.keys()))

    sweep = 0
    azimuths = radar.azimuth['data']
    ranges = radar.range['data']
    elevations = radar.fixed_angle['data'][sweep] * np.ones_like(azimuths)

    x, y, _ = antenna_to_cartesian(ranges, azimuths, elevations)
    x = x / 1000.0 + radar.longitude['data'][0]
    y = y / 1000.0 + radar.latitude['data'][0]

    reflectivity = radar.fields["reflectivity"]["data"]
    data = reflectivity[sweep]
    data = np.ma.masked_where(data < -10, data)

    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    mesh = ax.pcolormesh(x, y, data, cmap="NWSRef", vmin=-32, vmax=64)
    ax.axis("off")
    plt.axis("equal")

    overlay_path = f"../static/{site_id}_radar_reflectivity.png"
    bounds_path = f"../static/{site_id}_radar_bounds.json"
    plt.savefig(overlay_path, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved image to {overlay_path}")

    bounds = {
        "west": float(x.min()),
        "east": float(x.max()),
        "south": float(y.min()),
        "north": float(y.max())
    }
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")


# Run for multiple sites
site_files = {
    "KFFC": "KFFC_20250502_0148",
    "KJGX": "KJGX_20250502_0148",
    "KJKL": "KJKL_20250502_0148"
}

os.makedirs("../static", exist_ok=True)
for site_id, radar_file in site_files.items():
    plot_and_export(site_id, radar_file)
