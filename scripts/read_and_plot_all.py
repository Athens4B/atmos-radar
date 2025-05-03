import os
import json
import numpy as np
import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def plot_radar_with_bounds(radar, field, site_id):
    display = pyart.graph.RadarMapDisplay(radar)

    # Output filenames
    image_filename = f"{site_id}_radar.png"
    bounds_filename = f"{site_id}_radar_bounds.json"
    image_path = os.path.join("../static", image_filename)
    bounds_path = os.path.join("../static", bounds_filename)

    print(f"🖼️ Plotting {field} for {site_id}...")

    # Get data range for autoscaling
    data = radar.fields[field]["data"].filled(np.nan)
    vmin = np.nanpercentile(data, 5)
    vmax = np.nanpercentile(data, 95)
    print(f"📊 Autoscaling vmin={vmin:.1f}, vmax={vmax:.1f}")

    # Set up map
    fig = plt.figure(figsize=(6, 6), dpi=150)
    proj = ccrs.PlateCarree()
    ax = fig.add_subplot(111, projection=proj)

    display.plot_ppi(
        field=field,
        ax=ax,
        cmap="NWSRef",
        vmin=vmin,
        vmax=vmax,
        colorbar_flag=False,
    )

    # Hide all axis ticks, gridlines, and frame
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    ax.grid(False)

    # Save transparent image
    plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Calculate approximate geographic bounds
    radar_lat = radar.latitude["data"][0]
    radar_lon = radar.longitude["data"][0]
    max_range_km = radar.range["data"][-1] / 1000.0
    deg_offset = max_range_km / 111.0

    bounds = {
        "west": radar_lon - deg_offset,
        "east": radar_lon + deg_offset,
        "south": radar_lat - deg_offset,
        "north": radar_lat + deg_offset,
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
