from pathlib import Path
import pyart
import numpy as np
import matplotlib.pyplot as plt
import json
import os

# Paths
radar_file_path = "/root/atmos-radar/data/KFFC_20250502_0148"  # Full path
output_image_path = "/root/atmos-radar/static/KFFC_radar_reflectivity.png"
output_bounds_path = "/root/atmos-radar/static/KFFC_radar_bounds.json"

def main():
    print(f"📂 Reading radar file: {radar_file_path}")
    radar = pyart.io.read(radar_file_path)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    # Use the lowest sweep
    sweep = 0
    field = "reflectivity"

    # Get data and mask clutter
    data = radar.fields[field]["data"]
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_above(field, 100)
    gatefilter.exclude_below(field, -32)
    data_masked = np.ma.masked_where(gatefilter.gate_excluded, data)

    # Get gate latitude and longitude
    lats, lons = radar.get_gate_lat_lon_alt(sweep)[:2]

    # Plot
    print(f"🖼️ Plotting reflectivity for {radar.metadata['instrument_name']}...")
    fig, ax = plt.subplots(figsize=(10, 8))
    mesh = ax.pcolormesh(lons, lats, data_masked[sweep], cmap="NWSRef", vmin=-32, vmax=64)
    ax.set_xlim(np.min(lons), np.max(lons))
    ax.set_ylim(np.min(lats), np.max(lats))
    ax.axis("off")
    plt.savefig(output_image_path, dpi=150, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved image to {output_image_path}")

    # Save bounding box as JSON
    bounds = {
        "west": float(np.min(lons)),
        "east": float(np.max(lons)),
        "south": float(np.min(lats)),
        "north": float(np.max(lats)),
    }
    with open(output_bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {output_bounds_path}")

main()
