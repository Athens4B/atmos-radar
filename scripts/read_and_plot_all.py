import os
import glob
import numpy as np
import pyart
import matplotlib.pyplot as plt
import json

def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC", sweep=0):
    print(f"📡 Available fields: {list(radar.fields.keys())}")
    print(f"🌀 Using sweep: {sweep}")

    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_transition()
    gatefilter.exclude_masked(field)
    gatefilter.exclude_invalid(field)

    start_idx = radar.sweep_start_ray_index['data'][sweep]
    end_idx = radar.sweep_end_ray_index['data'][sweep]

    azimuths = radar.azimuth['data'][start_idx:end_idx + 1]
    ranges = radar.range['data']
    elevations = radar.fixed_angle['data'][sweep]

    data = radar.fields[field]['data'][start_idx:end_idx + 1]
    mask = gatefilter.gate_excluded[start_idx:end_idx + 1]

    # Mask out clutter and invalid data
    filtered_data = np.ma.masked_where(mask, data)

    x, y, z = pyart.core.antenna_to_cartesian(ranges, azimuths, elevations)

    # Convert to latitude/longitude grid
    radar_lon = radar.longitude['data'][0]
    radar_lat = radar.latitude['data'][0]

    lons, lats = pyart.core.cartesian_to_geographic(x, y, radar_lon, radar_lat)

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_facecolor("none")
    ax.axis("off")

    pm = ax.pcolormesh(
        lons,
        lats,
        filtered_data,
        cmap="NWSRef",
        vmin=-32,
        vmax=64,
        shading="auto"
    )

    ax.set_xlim(np.min(lons), np.max(lons))
    ax.set_ylim(np.min(lats), np.max(lats))

    output_image_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(output_image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()

    print(f"✅ Saved image to {output_image_path}")

    bounds = {
        "west": float(np.min(lons)),
        "east": float(np.max(lons)),
        "south": float(np.min(lats)),
        "north": float(np.max(lats))
    }

    bounds_path = f"../static/{site_id}_radar_bounds.json"
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)

    print(f"✅ Saved bounds to {bounds_path}")


def main():
    site_id = "KFFC"
    radar_files = sorted(
        glob.glob(f"../data/{site_id}_*"),
        key=os.path.getmtime,
        reverse=True
    )

    if not radar_files:
        print("❌ No radar files found.")
        return

    radar_file_path = radar_files[0]
    print(f"📂 Reading radar file: {radar_file_path}")

    radar = pyart.io.read(radar_file_path)
    plot_radar_with_bounds(radar, field="reflectivity", site_id=site_id)


if __name__ == "__main__":
    main()
