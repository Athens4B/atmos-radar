import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
from pyart.core.transforms import antenna_to_cartesian
import cartopy.crs as ccrs

def plot_radar_with_bounds(radar, field, site_id):
    sweep = 0  # lowest tilt
    data = radar.fields[field]["data"][radar.get_slice(sweep)]
    azimuths = radar.azimuth["data"][radar.get_slice(sweep)]
    ranges = radar.range["data"]

    # Convert polar to lat/lon
    lats, lons = radar.get_gate_lat_lon(sweep)

    # Calculate image bounds
    valid_lats = lats[np.isfinite(data)]
    valid_lons = lons[np.isfinite(data)]

    bounds = {
        "west": float(np.min(valid_lons)),
        "east": float(np.max(valid_lons)),
        "south": float(np.min(valid_lats)),
        "north": float(np.max(valid_lats)),
    }

    # Plotting
    print(f"🖼️ Plotting reflectivity for {site_id}...")
    fig = plt.figure(figsize=(8, 8), dpi=150)
    ax = plt.axes(projection=ccrs.PlateCarree())
    mesh = ax.pcolormesh(lons, lats, data, cmap="NWSRef", vmin=-32, vmax=64, transform=ccrs.PlateCarree())
    ax.set_extent([bounds["west"], bounds["east"], bounds["south"], bounds["north"]])
    ax.axis("off")

    out_img = f"../static/{site_id}_radar_reflectivity.png"
    out_bounds = f"../static/{site_id}_radar_bounds.json"

    plt.savefig(out_img, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {out_img}")

    with open(out_bounds, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {out_bounds}")


def main():
    with open("latest_filename.txt") as f:
        radar_file = f.read().strip()
    site_id = "KFFC"
    print(f"📂 Processing {site_id} → {radar_file}")

    radar = pyart.io.read(radar_file)
    print("📡 Available fields:", list(radar.fields.keys()))
    os.makedirs("../static", exist_ok=True)
    plot_radar_with_bounds(radar, field="reflectivity", site_id=site_id)


if __name__ == "__main__":
    main()
