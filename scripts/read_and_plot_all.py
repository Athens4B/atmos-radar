import os
import pyart
import matplotlib.pyplot as plt
import numpy as np

def create_world_file(radar, image_path, image_width=900, image_height=900):
    radar_lon = radar.longitude['data'][0]
    radar_lat = radar.latitude['data'][0]

    max_range_km = radar.range['data'][-1] / 1000.0
    degrees_per_km = 1 / 111.0  # Approximate conversion

    half_deg = max_range_km * degrees_per_km

    min_lon = radar_lon - half_deg
    max_lon = radar_lon + half_deg
    max_lat = radar_lat + half_deg
    min_lat = radar_lat - half_deg

    pixel_size_x = (max_lon - min_lon) / image_width
    pixel_size_y = (min_lat - max_lat) / image_height  # Y axis is inverted

    upper_left_x = min_lon
    upper_left_y = max_lat

    world_file_path = os.path.splitext(image_path)[0] + ".pgw"
    with open(world_file_path, "w") as f:
        f.write(f"{pixel_size_x:.10f}\n0.0\n0.0\n{pixel_size_y:.10f}\n{upper_left_x:.10f}\n{upper_left_y:.10f}\n")

    print(f"🌍 Created world file: {world_file_path}")

def plot_radar():
    try:
        with open("latest_filename.txt", "r") as f:
            radar_file = f.read().strip()
    except FileNotFoundError:
        print("❌ latest_filename.txt not found.")
        return

    print(f"Reading radar file: {radar_file}")
    radar = pyart.io.read(radar_file)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))
    display = pyart.graph.RadarMapDisplay(radar)

    os.makedirs("../static", exist_ok=True)

    output_path = "../static/latest_radar_reflectivity.png"
    print("🖼️ Plotting reflectivity image with transparent background...")
    fig = plt.figure(figsize=(6, 6), dpi=150)
    ax = fig.add_subplot(111)

    display.plot_ppi(
        field="reflectivity",
        ax=ax,
        cmap="NWSRef",
        vmin=-32,
        vmax=64,
        title_flag=False,
        axislabels_flag=False,
        colorbar_flag=False
    )

    plt.axis("off")
    plt.savefig(output_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved {output_path}")

    create_world_file(radar, output_path)

if __name__ == "__main__":
    plot_radar()
