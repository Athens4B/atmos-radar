import os
import pyart
import matplotlib.pyplot as plt

def create_world_file(radar, image_path, image_width=900, image_height=900, extent_km=460):
    radar_lon = radar.longitude['data'][0]
    radar_lat = radar.latitude['data'][0]

    degrees_per_km = 1 / 111.0  # Approximate at mid-latitudes
    half_deg = (extent_km / 2) * degrees_per_km

    min_lon = radar_lon - half_deg
    max_lon = radar_lon + half_deg
    max_lat = radar_lat + half_deg
    min_lat = radar_lat - half_deg

    pixel_size_x = (max_lon - min_lon) / image_width
    pixel_size_y = (min_lat - max_lat) / image_height  # negative because Y goes down

    upper_left_x = min_lon
    upper_left_y = max_lat

    world_file_path = os.path.splitext(image_path)[0] + ".pgw"
    with open(world_file_path, "w") as f:
        f.write(f"{pixel_size_x}\n0.0\n0.0\n{pixel_size_y}\n{upper_left_x}\n{upper_left_y}\n")

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
        colorbar_label="Reflectivity (dBZ)"
    )
    plt.axis("off")
    plt.savefig(output_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved {output_path}")

    create_world_file(radar, output_path)

if __name__ == "__main__":
    plot_radar()
