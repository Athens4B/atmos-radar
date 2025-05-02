import os
import pyart
import matplotlib.pyplot as plt
from datetime import datetime

def plot_field(radar, field, filename):
    print(f"🖼️ Plotting {field} image with transparent background...")

    display = pyart.graph.RadarDisplay(radar)

    fig = plt.figure(figsize=(6, 6), dpi=150)
    ax = fig.add_subplot(111)

    # Shift image to bottom left by changing xlim and ylim
    display.plot_ppi(
        field=field,
        ax=ax,
        cmap="NWSRef" if field == "reflectivity" else "viridis",
        colorbar_flag=False,
        title_flag=False,
        axislabels_flag=False,
    )

    # Clean transparent background
    ax.set_axis_off()
    fig.patch.set_alpha(0.0)
    ax.set_facecolor((0, 0, 0, 0))

    output_path = f"../static/latest_radar_{field}.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved {output_path}")

def main():
    try:
        with open("latest_filename.txt", "r") as f:
            radar_file = f.read().strip()
    except FileNotFoundError:
        print("❌ latest_filename.txt not found.")
        return

    print(f"Reading radar file: {radar_file}")
    try:
        radar = pyart.io.read(radar_file)
        print("✅ Successfully read radar file.")
    except Exception as e:
        print(f"❌ Failed to read radar file: {e}")
        return

    print("📡 Available fields:", list(radar.fields.keys()))

    for field in [
        "reflectivity",
        "velocity",
        "differential_reflectivity",
        "cross_correlation_ratio",
    ]:
        if field in radar.fields:
            plot_field(radar, field, f"latest_radar_{field}.png")
        else:
            print(f"⚠️  Skipping {field} — field not found in file.")

if __name__ == "__main__":
    main()
