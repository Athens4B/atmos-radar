import os
import pyart
import matplotlib.pyplot as plt

def plot_radar():
    try:
        with open("/root/atmos-radar/scripts/latest_filename.txt", "r") as f:
            radar_file = f.read().strip()
    except FileNotFoundError:
        print("❌ latest_filename.txt not found.")
        return

    print(f"Reading radar file: {radar_file}")
    radar = pyart.io.read(os.path.join("/root/atmos-radar/scripts", radar_file))
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    os.makedirs("/root/atmos-radar/static", exist_ok=True)

    # Fields to try
    fields = {
        "reflectivity": "latest_radar_reflectivity.png",
        "velocity": "latest_radar_velocity.png",
        "differential_reflectivity": "latest_radar_differential_reflectivity.png",
    }

    for field, output_name in fields.items():
        if field not in radar.fields:
            print(f"⚠️  Skipping {field} — field not found.")
            continue

        print(f"🖼️  Plotting {field} image with transparent background...")

        display = pyart.graph.RadarDisplay(radar)
        fig = plt.figure(figsize=(6, 6), dpi=150)
        ax = fig.add_subplot(111)

        display.plot_ppi(
            field=field,
            ax=ax,
            cmap="NWSRef" if field == "reflectivity" else "NWSVel",
            colorbar_flag=False,
            axislabels_flag=False,
            title_flag=False,
        )

        ax.set_axis_off()
        output_path = os.path.join("/root/atmos-radar/static", output_name)
        plt.savefig(output_path, bbox_inches="tight", pad_inches=0, transparent=True)
        plt.close()
        print(f"✅ Saved {output_path}")

if __name__ == "__main__":
    plot_radar()
