import os
import json
import pyart
import matplotlib.pyplot as plt

def plot_radar_with_bounds(radar, field, image_filename, bounds_filename, cmap="NWSRef", vmin=None, vmax=None):
    # Paths
    image_path = os.path.join("../static", image_filename)
    bounds_path = os.path.join("../static", bounds_filename)

    print(f"🖼️ Plotting {field} image with transparent background...")

    # Set up figure and axis
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    display = pyart.graph.RadarDisplay(radar)

    # Plot without embellish (removed due to error)
    display.plot_ppi(
        field=field,
        sweep=0,
        ax=ax,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        colorbar_flag=False
    )

    # Strip all frame elements
    ax.set_title("")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_axis_off()

    # Save image
    plt.savefig(image_path, transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Compute bounds for overlay
    lat = radar.latitude['data'][0]
    lon = radar.longitude['data'][0]
    max_range_km = radar.range['data'][-1] / 1000.0
    delta_deg = max_range_km / 111.0

    bounds = {
        "west": lon - delta_deg,
        "east": lon + delta_deg,
        "south": lat - delta_deg,
        "north": lat + delta_deg
    }

    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")


def main():
    with open("latest_filename.txt", "r") as f:
        radar_file = f.read().strip()

    print(f"Reading radar file: {radar_file}")
    radar = pyart.io.read(radar_file)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    os.makedirs("../static", exist_ok=True)

    plot_radar_with_bounds(
        radar,
        field="reflectivity",
        image_filename="latest_radar_reflectivity.png",
        bounds_filename="latest_radar_bounds.json",
        cmap="NWSRef",
        vmin=-32,
        vmax=64
    )


if __name__ == "__main__":
    main()
