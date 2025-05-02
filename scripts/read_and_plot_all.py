import os
import pyart
import matplotlib.pyplot as plt
from pyart.graph import RadarDisplay
from datetime import datetime


def create_world_file(display, output_image_path, img_width=900, img_height=900):
    """
    Creates a .pgw world file to georeference a radar PNG image.
    """
    xlim = display._get_x_limits()
    ylim = display._get_y_limits()

    # These are in meters
    x0, x1 = xlim
    y0, y1 = ylim

    # Compute pixel size in projected coordinates
    px_size_x = (x1 - x0) / img_width
    px_size_y = (y0 - y1) / img_height  # Y-axis flip

    # Top-left pixel center
    top_left_x = x0 + px_size_x / 2
    top_left_y = y0 - px_size_y / 2

    # Output .pgw file path
    world_file_path = output_image_path.replace(".png", ".pgw")

    with open(world_file_path, "w") as f:
        f.write(f"{px_size_x:.10f}\n")   # A: pixel size X
        f.write("0.0000000000\n")        # D: rotation
        f.write("0.0000000000\n")        # B: rotation
        f.write(f"-{abs(px_size_y):.10f}\n")  # E: pixel size Y (negative)
        f.write(f"{top_left_x:.10f}\n")  # C: X of top-left center
        f.write(f"{top_left_y:.10f}\n")  # F: Y of top-left center

    print(f"🗺️ World file saved: {world_file_path}")


def plot_field(radar, field_name, output_filename):
    """
    Plot radar field and generate a world file.
    """
    if field_name not in radar.fields:
        print(f"⚠️ Skipping {field_name} — field not found in file.")
        return

    print(f"🖼️ Plotting {field_name} image with transparent background...")
    display = RadarDisplay(radar)

    os.makedirs("../static", exist_ok=True)
    output_path = f"../static/{output_filename}"

    fig = plt.figure(figsize=(6, 6), dpi=150)
    ax = fig.add_subplot(111)

    display.plot_ppi(
        field=field_name,
        ax=ax,
        cmap="pyart_NWSRef" if field_name == "reflectivity" else "pyart_NWSVel",
        vmin=-32 if field_name == "reflectivity" else -60,
        vmax=64 if field_name == "reflectivity" else 60,
        colorbar_label=field_name.replace("_", " ").title(),
    )

    plt.axis("off")
    plt.savefig(output_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved {output_path}")

    create_world_file(display, output_path)


def main():
    try:
        with open("latest_filename.txt", "r") as f:
            radar_file = f.read().strip()
    except FileNotFoundError:
        print("❌ latest_filename.txt not found.")
        return

    print(f"Reading radar file: {radar_file}")
    radar = pyart.io.read(radar_file)
    print("✅ Successfully read radar file.")
    print(f"📡 Available fields: {list(radar.fields.keys())}")

    plot_field(radar, "reflectivity", "latest_radar_reflectivity.png")
    plot_field(radar, "velocity", "latest_radar_velocity.png")


if __name__ == "__main__":
    main()
