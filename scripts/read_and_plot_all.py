import os
import pyart
import matplotlib.pyplot as plt
from matplotlib import rcParams
from datetime import datetime

rcParams["figure.facecolor"] = "none"

def read_latest_radar_file():
    try:
        with open("latest_filename.txt", "r") as f:
            radar_file = f.read().strip()
            print(f"Reading radar file: {radar_file}")
            radar = pyart.io.read(radar_file)
            print("✅ Successfully read radar file.")
            print("📡 Available fields:", list(radar.fields.keys()))
            return radar
    except FileNotFoundError:
        print("❌ latest_filename.txt not found.")
        return None

def plot_field(radar, field_name, output_name):
    if field_name not in radar.fields:
        print(f"⚠️  Skipping {field_name} — field not found in file.")
        return

    display = pyart.graph.RadarDisplay(radar)
    fig = plt.figure(figsize=(6, 6), dpi=150)
    ax = fig.add_subplot(111)

    print(f"🖼️ Plotting {field_name} image with transparent background...")

    # Choose valid colormaps since pyart_* are not always available
    cmap = "turbo" if field_name == "reflectivity" else "seismic"

    display.plot_ppi(
        field=field_name,
        ax=ax,
        cmap=cmap,
        vmin=-32 if field_name == "reflectivity" else -60,
        vmax=64 if field_name == "reflectivity" else 60,
        colorbar_label=field_name.replace("_", " ").title(),
    )
    display.set_limits(ylim=[-150, 150], xlim=[-150, 150])
    plt.axis("off")

    output_path = os.path.join("../static", output_name)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved {output_path}")

def main():
    radar = read_latest_radar_file()
    if radar is None:
        return

    plot_field(radar, "reflectivity", "latest_radar_reflectivity.png")
    plot_field(radar, "velocity", "latest_radar_velocity.png")
    plot_field(radar, "differential_reflectivity", "latest_radar_differential_reflectivity.png")
    plot_field(radar, "cross_correlation_ratio", "latest_radar_correlation_ratio.png")

if __name__ == "__main__":
    main()
