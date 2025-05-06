from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pyart
import json

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC"):
    sweep = 0
    print(f"🌀 Using sweep: {sweep}")

    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_transition()
    gatefilter.exclude_masked(field)
    gatefilter.exclude_below(field, -999)

    data = radar.fields[field]["data"]
    filtered_data = data[sweep]  # no gatefilter masking to avoid shape issues

    x, y = radar.get_gate_x_y(sweep)

    fig, ax = plt.subplots(figsize=(10, 10))
    pm = ax.pcolormesh(x, y, filtered_data, cmap="NWSRef", vmin=-32, vmax=64)
    ax.axis("off")
    ax.set_aspect("equal")

    output_image = f"../static/{site_id}_radar_reflectivity.png"
    fig.savefig(output_image, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    lons, lats = radar.get_gate_longitude_latitude(sweep)
    bounds = {
        "west": float(np.nanmin(lons)),
        "east": float(np.nanmax(lons)),
        "south": float(np.nanmin(lats)),
        "north": float(np.nanmax(lats))
    }

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
