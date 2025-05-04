import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC"):
    print(f"🖼️ Plotting {field} for {site_id}...")

    # Get radar gate lats/lons and data
    sweep = 0
    lats, lons = radar.get_gate_lat_lon(sweep)
    data = radar.fields[field]['data']

    # Mask invalid values
    data = np.ma.masked_where(data <= -9999, data)

    # Create figure with transparent background
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150, subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent([
        radar.longitude['data'][0] - 1.2,
        radar.longitude['data'][0] + 1.2,
        radar.latitude['data'][0] - 1.2,
        radar.latitude['data'][0] + 1.2,
    ], crs=ccrs.PlateCarree())

    # Plot radar sweep with no labels or colorbar
    mesh = ax.pcolormesh(
        lons,
        lats,
        data,
        cmap="NWSRef",
        vmin=-32,
        vmax=64,
        shading='auto',
        transform=ccrs.PlateCarree(),
    )

    # Clean look
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['geo'].set_visible(False)

    # Save image and bounds
    image_path = f"../static/radar_overlay.png"
    bounds_path = f"../static/radar_bounds.json"
    plt.savefig(image_path, transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()

    print(f"✅ Saved image to {image_path}")

    bounds = {
        "west": ax.get_xlim()[0],
        "east": ax.get_xlim()[1],
        "south": ax.get_ylim()[0],
        "north": ax.get_ylim()[1],
    }
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")


def main():
    with open("latest_filename.txt", "r") as f:
        radar_file = f.read().strip()

    print(f"📂 Reading radar file: {radar_file}")
    radar = pyart.io.read(radar_file)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    os.makedirs("../static", exist_ok=True)
    plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC")


if __name__ == "__main__":
    main()
