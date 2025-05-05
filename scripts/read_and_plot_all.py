from pathlib import Path
import pyart
import numpy as np
import matplotlib.pyplot as plt
import json

# Set paths
DATA_DIR = Path("/root/atmos-radar/data")
STATIC_DIR = Path("/root/atmos-radar/static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC", sweep=0):
    # Get sweep indices
    start_idx = radar.sweep_start_ray_index[sweep]
    end_idx = radar.sweep_end_ray_index[sweep]
    
    # Get radar data
    data = radar.fields[field]["data"][start_idx:end_idx + 1]
    gatefilter = pyart.correct.GateFilter(radar)
    gatefilter.exclude_transition()
    gatefilter.exclude_masked(field)
    gatefilter.exclude_below(field, -32)

    # Apply filter to data
    filtered_data = np.ma.masked_where(gatefilter.gate_excluded[start_idx:end_idx + 1], data)

    # Get lat/lon coordinates
    lats, lons = radar.get_gate_lat_lon(sweep)

    # Define bounds
    bounds = {
        "north": float(lats.max()), "south": float(lats.min()),
        "east": float(lons.max()), "west": float(lons.min())
    }

    # Plot radar data
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.pcolormesh(lons, lats, filtered_data, cmap="NWSRef", vmin=-32, vmax=64)
    ax.set_xlim(bounds["west"], bounds["east"])
    ax.set_ylim(bounds["south"], bounds["north"])
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    # Save image and bounds
    image_path = STATIC_DIR / f"{site_id}_radar_reflectivity.png"
    bounds_path = STATIC_DIR / f"{site_id}_radar_bounds.json"
    plt.savefig(image_path, dpi=150, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)

    print(f"✅ Saved image to {image_path}")
    print(f"✅ Saved bounds to {bounds_path}")

def main():
    site_id = "KFFC"
    radar_files = sorted(DATA_DIR.glob(f"{site_id}_*"))
    if not radar_files:
        print("❌ No radar files found.")
        return

    latest_file = radar_files[-1]
    print(f"📂 Reading radar file: {latest_file}")
    radar = pyart.io.read(str(latest_file))
    print(f"📡 Available fields: {list(radar.fields.keys())}")
    
    plot_radar_with_bounds(radar, field="reflectivity", site_id=site_id)

if __name__ == "__main__":
    main()
