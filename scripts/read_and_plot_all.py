import os
import pyart
import numpy as np
import matplotlib.pyplot as plt
import json

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC"):
    print(f"📡 Available fields: {list(radar.fields.keys())}")
    
    # Select sweep
    sweep = 0
    print(f"🌀 Using sweep: {sweep}")

    # Gate filter
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_transition()
    gatefilter.exclude_masked(field)
    gatefilter.exclude_invalid(field)

    # Extract reflectivity field and apply mask
    data = radar.get_field(sweep, field)
    mask = gatefilter.gate_excluded  # <-- FIXED LINE
    filtered_data = np.ma.masked_where(mask, data)

    # Get lat/lon coordinates
    lats, lons = radar.get_gate_lat_lon_alt(sweep)[:2]

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 8))
    pm = ax.pcolormesh(
        lons, lats, filtered_data,
        cmap="NWSRef", vmin=-32, vmax=64,
        shading="auto"
    )
    ax.set_title(f"{site_id} - {field.capitalize()}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.colorbar(pm, ax=ax, label="dBZ")
    ax.set_aspect("equal")

    # Save radar image
    out_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight", transparent=True)
    print(f"✅ Saved image to {out_path}")

    # Compute and save bounds
    bounds = {
        "north": float(np.nanmax(lats)),
        "south": float(np.nanmin(lats)),
        "east": float(np.nanmax(lons)),
        "west": float(np.nanmin(lons)),
    }
    with open(f"../static/{site_id}_radar_bounds.json", "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to ../static/{site_id}_radar_bounds.json")

    plt.close()

def main():
    data_dir = "../data"
    radar_files = sorted(
        f for f in os.listdir(data_dir)
        if f.startswith("KFFC") and not f.endswith(".json")
    )
    if not radar_files:
        print("❌ No radar files found.")
        return

    latest_file = radar_files[-1]
    radar_file_path = os.path.join(data_dir, latest_file)
    print(f"📂 Reading radar file: {radar_file_path}")
    radar = pyart.io.read(radar_file_path)

    plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC")

if __name__ == "__main__":
    main()
