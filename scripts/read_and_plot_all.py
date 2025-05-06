
import pyart
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC", sweep=0):
    print(f"📡 Available fields: {list(radar.fields.keys())}")
    print(f"🌀 Using sweep: {sweep}")

    display = pyart.graph.RadarDisplay(radar)
    data = radar.get_field(sweep, field)

    # Extract sweep-specific mask
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_transition()
    gatefilter.exclude_masked(field)
    gatefilter.exclude_invalid(field)

    start_idx = radar.sweep_start_ray_index[sweep]
    end_idx = radar.sweep_end_ray_index[sweep]
    mask = gatefilter.gate_excluded[start_idx:end_idx + 1]
    filtered_data = np.ma.masked_where(mask, data[start_idx:end_idx + 1])

    # Get lat/lon grid
    lats, lons = radar.get_gate_lat_lon_alt(sweep)[:2]

    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    pm = ax.pcolormesh(lons, lats, filtered_data, cmap="NWSRef", vmin=-32, vmax=64)
    plt.axis("off")
    plt.savefig(f"../static/{site_id}_radar_reflectivity.png", bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()

    bounds = {
        "north": float(np.max(lats)),
        "south": float(np.min(lats)),
        "east": float(np.max(lons)),
        "west": float(np.min(lons))
    }

    with open(f"../static/{site_id}_radar_bounds.json", "w") as f:
        json.dump(bounds, f)

    print(f"✅ Saved image to ../static/{site_id}_radar_reflectivity.png")
    print(f"✅ Saved bounds to ../static/{site_id}_radar_bounds.json")

def main():
    site_id = "KFFC"
    data_dir = Path("../data")
    files = sorted(data_dir.glob(f"{site_id}_*"))

    if not files:
        print("❌ No radar files found.")
        return

    radar_file_path = files[-1]
    print(f"📂 Reading radar file: {radar_file_path}")
    radar = pyart.io.read(str(radar_file_path))
    plot_radar_with_bounds(radar, field="reflectivity", site_id=site_id)

if __name__ == "__main__":
    main()
