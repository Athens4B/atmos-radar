import os
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC"):
    print(f"🖼️ Plotting {field} for {site_id}...")

    # Use fallback for older Py-ART
    sweep = 0
    lats, lons = radar.get_gate_lat_lon_alt(sweep)[:2]
    data = radar.fields[field]['data'][radar.sweep_start_ray_index['data'][sweep] :
                                        radar.sweep_end_ray_index['data'][sweep] + 1]

    # Mask invalid values
    data = np.ma.masked_where(data <= -9999, data)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150, subplot_kw={'projection': ccrs.PlateCarree()})

    # Plot radar data
    mesh = ax.pcolormesh(
        lons,
        lats,
        data,
        cmap="NWSRef",
        vmin=-32,
        vmax=64,
        shading='auto',
        transform=ccrs.PlateCarree()
    )

    # Set tight radar extents
    lat_c = radar.latitude['data'][0]
    lon_c = radar.longitude['data'][0]
    delta = 1.2
    ax.set_extent([lon_c - delta, lon_c + delta, lat_c - delta, lat_c + delta])

    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['geo'].set_visible(False)

    # Save transparent PNG and bounding box
    os.makedirs("../static", exist_ok=True)
    image_path = "../static/radar_overlay.png"
    bounds_path = "../static/radar_bounds.json"
    plt.savefig(image_path, transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    bounds = {
        "west": lon_c - delta,
        "east": lon_c + delta,
        "south": lat_c - delta,
        "north": lat_c + delta
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
    plot_radar_with_bounds(radar, field="reflectivity", site_id="KFFC")


if __name__ == "__main__":
    main()
