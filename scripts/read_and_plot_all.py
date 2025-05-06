import os
import glob
import numpy as np
import pyart
import matplotlib.pyplot as plt
import json

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC", sweep=0):
    print(f"📡 Available fields: {list(radar.fields.keys())}")
    print(f"🌀 Using sweep: {sweep}")

    # Generate gatefilter to reduce clutter
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_transition()
    gatefilter.exclude_masked(field)
    gatefilter.exclude_invalid(field)
    gatefilter.exclude_below(field, -10)

    # Get sweep slice
    start = radar.sweep_start_ray_index['data'][sweep]
    end = radar.sweep_end_ray_index['data'][sweep]
    data = radar.fields[field]['data'][start:end]
    data_filtered = np.ma.masked_where(gatefilter.gate_excluded[start:end], data)

    # Get lat/lon for the sweep
    lats, lons = radar.get_gate_lat_lon(sweep)

    # Plot setup
    fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
    ax.axis("off")

    # Plot reflectivity
    pm = ax.pcolormesh(
        lons, lats, data_filtered,
        cmap="NWSRef", vmin=-32, vmax=64,
        shading='auto'
    )

    # Save transparent image without axes
    out_img = f"../static/{site_id}_radar_reflectivity.png"
    fig.savefig(out_img, dpi=150, bbox_inches='tight', pad_inches=0, transparent=True)
    print(f"✅ Saved image to {out_img}")
    plt.close(fig)

    # Save bounds for mapping overlay
    bounds = {
        "west": np.min(lons),
        "east": np.max(lons),
        "south": np.min(lats),
        "north": np.max(lats)
    }
    out_bounds = f"../static/{site_id}_radar_bounds.json"
    with open(out_bounds, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {out_bounds}")

def main():
    site_id = "KFFC"
    data_dir = "/root/atmos-radar/data"
    radar_files = sorted(
        glob.glob(os.path.join(data_dir, f"{site_id}_*")),
        key=os.path.getmtime,
        reverse=True
    )

    if not radar_files:
        print("❌ No radar files found.")
        return

    radar_file = radar_files[0]
    print(f"📂 Reading radar file: {radar_file}")
    radar = pyart.io.read(radar_file)

    plot_radar_with_bounds(radar, field="reflectivity", site_id=site_id)

if __name__ == "__main__":
    main()
