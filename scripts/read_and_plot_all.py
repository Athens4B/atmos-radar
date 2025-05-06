from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pyart
import json

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC"):
    sweep = 0
    print(f"🌀 Using sweep: {sweep}")

    # Get data from the sweep
    data = radar.fields[field]["data"]
    data_sweep = data[radar.get_slice(sweep)]

    # Use x and y from sweep-aligned cartesian gates
    x, y, _ = radar.get_gate_x_y_z(sweep)

    # Prepare the plot
    fig, ax = plt.subplots(figsize=(10, 10))
    mesh = ax.pcolormesh(x, y, data_sweep, cmap="NWSRef", vmin=-32, vmax=64)
    ax.axis("off")
    ax.set_aspect("equal")

    output_image = f"../static/{site_id}_radar_reflectivity.png"
    fig.savefig(output_image, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    # Get bounding box for mapping
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
