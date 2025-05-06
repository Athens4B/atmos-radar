import os
import pyart
import numpy as np
import matplotlib.pyplot as plt
import json

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC"):
    sweep = 0
    print(f"🌀 Using sweep: {sweep}")

    # Create a gatefilter to remove clutter
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_transition()
    gatefilter.exclude_masked(field)
    gatefilter.exclude_below(field, -32)

    # Get sweep start and end ray indices
    start_idx = radar.sweep_start_ray_index['data'][sweep]
    end_idx = radar.sweep_end_ray_index['data'][sweep]

    # Get the reflectivity data and apply the gate filter
    data = radar.fields[field]['data']
    reflectivity = data[start_idx:end_idx]
    filtered_data = np.ma.masked_where(gatefilter.gate_excluded[start_idx:end_idx], reflectivity)

    # Get lat/lon values
    lats, lons, _ = radar.get_gate_lat_lon_alt(sweep)
    lats = lats[start_idx:end_idx]
    lons = lons[start_idx:end_idx]

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    pm = ax.pcolormesh(lons, lats, filtered_data, cmap="pyart_NWSRef", vmin=-32, vmax=64, shading="auto")
    ax.set_aspect('equal')
    ax.set_xlim(np.min(lons), np.max(lons))
    ax.set_ylim(np.min(lats), np.max(lats))
    ax.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Save PNG with transparent background
    output_image_path = f"../static/{site_id}_radar_reflectivity.png"
    fig.patch.set_alpha(0.0)
    plt.savefig(output_image_path, dpi=100, transparent=True)
    plt.close(fig)
    print(f"✅ Saved image to {output_image_path}")

    # Save bounds as JSON
    bounds = {
        "north": float(np.max(lats)),
        "south": float(np.min(lats)),
        "east": float(np.max(lons)),
        "west": float(np.min(lons)),
    }
    output_bounds_path = f"../static/{site_id}_radar_bounds.json"
    with open(output_bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {output_bounds_path}")

def main():
    data_dir = "/root/atmos-radar/data"
    files = sorted([f for f in os.listdir(data_dir) if f.startswith("KFFC") and f.endswith(".gz")])
    if not files:
        print("❌ No radar files found.")
        return

    latest_file = files[-1]
    radar_file_path = os.path.join(data_dir, latest_file)
    print(f"📂 Reading radar file: {radar_file_path}")
    radar = pyart.io.read(radar_file_path)
    print(f"📡 Available fields: {list(radar.fields.keys())}")

    plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC")

if __name__ == "__main__":
    main()
