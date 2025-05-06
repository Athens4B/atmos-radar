from datetime import datetime
import os
import pyart
import matplotlib.pyplot as plt
import numpy as np
import json

# Config
RADAR_DIR = "/root/atmos-radar/data"
STATIC_DIR = "/root/atmos-radar/static"
SITE_ID = "KFFC"
FIELD = "reflectivity"
CMAP = "NWSRef"
VMIN = -32
VMAX = 64

def find_latest_radar_file():
    files = sorted(
        [f for f in os.listdir(RADAR_DIR) if f.startswith(SITE_ID)],
        reverse=True
    )
    return os.path.join(RADAR_DIR, files[0]) if files else None

def plot_radar_with_bounds(radar, field, site_id):
    sweep = 0
    print(f"🌀 Using sweep: {sweep}")

    azimuths = radar.get_azimuth(sweep)
    ranges = radar.range["data"]
    data = radar.fields[field]["data"][radar.sweep_start_ray_index["data"][sweep]:
                                        radar.sweep_end_ray_index["data"][sweep]+1, :]
    
    # Gate filter
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_invalid(field)
    gatefilter.exclude_below(field, -20)
    mask = gatefilter.gate_excluded[radar.sweep_start_ray_index["data"][sweep]:
                                     radar.sweep_end_ray_index["data"][sweep]+1, :]
    masked_data = np.ma.masked_where(mask, data)

    # Coordinates
    r, az = np.meshgrid(ranges, azimuths)
    elev = radar.fixed_angle["data"][sweep]
    elevs = np.full_like(r, elev)
    from pyart.core.transforms import antenna_to_cartesian
    x, y, _ = antenna_to_cartesian(r, az, elevs)
    x_km = x / 1000.0
    y_km = y / 1000.0

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    pm = ax.pcolormesh(x_km, y_km, masked_data, cmap=CMAP, vmin=VMIN, vmax=VMAX)
    plt.colorbar(pm, ax=ax, label="Reflectivity (dBZ)")
    ax.set_title(f"{site_id} {field.title()} Sweep {sweep}")
    ax.set_xlabel("East-West distance (km)")
    ax.set_ylabel("North-South distance (km)")

    # Save image
    image_path = os.path.join(STATIC_DIR, f"{site_id}_radar_reflectivity.png")
    plt.savefig(image_path, bbox_inches="tight")
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Save bounds
    lat, lon = radar.latitude["data"][0], radar.longitude["data"][0]
    bounds = {
        "north": lat + 1,
        "south": lat - 1,
        "east": lon + 1,
        "west": lon - 1
    }
    json_path = os.path.join(STATIC_DIR, f"{site_id}_radar_bounds.json")
    with open(json_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {json_path}")

def main():
    radar_file_path = find_latest_radar_file()
    if not radar_file_path:
        print("❌ No radar files found.")
        return
    print(f"📂 Reading radar file: {radar_file_path}")
    radar = pyart.io.read(radar_file_path)
    print(f"📡 Available fields: {list(radar.fields.keys())}")
    plot_radar_with_bounds(radar, FIELD, SITE_ID)

if __name__ == "__main__":
    main()
