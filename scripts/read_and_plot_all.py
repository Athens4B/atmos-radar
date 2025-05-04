import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
from pyart.core.transforms import antenna_to_lat_lon
import cartopy.crs as ccrs

def plot_radar_with_bounds(radar, field, site_id):
    sweep = 0  # lowest elevation angle
    data = radar.fields[field]["data"][radar.get_slice(sweep)]
    azimuths = radar.azimuth["data"][radar.get_slice(sweep)]
    ranges = radar.range["data"]

    # Get lat/lon coordinates of radar gates
    lats, lons = antenna_to_lat_lon(radar, sweep)

    # Filter bounds using valid data
    valid_lats = lats[np.isfinite(data)]
    valid_lons = lons[np.isfinite(data)]

    bounds = {
        "west": float(np.min(valid_lons)),
        "east": float(np.max(valid_lons)),
        "south": float(np.min(valid_lats)),
        "north": float(np.max(valid_lats)),
    }

    print(f"🖼️ Plotting reflectivity for {site_id}...")

    fig = plt.figure(figsize=(8, 8), dpi=150)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.pcolormesh(lons, lats, data, cmap="NWSRef", vmin=-32, vmax=64, transform=ccrs.PlateCarree())
    ax.set_extent([bounds["west"], bounds["east"], bounds["south"], bounds["north"]])
    ax.axis("off")

    image_path = f"../static/{site_id}_radar_reflectivity.png"
    bounds_path = f"../static/{site_id}_radar_bounds.json"

    plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")


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
