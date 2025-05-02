import os
import pyart
import matplotlib.pyplot as plt

def plot_radar(site_id):
    # Load radar file path
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

    display = pyart.graph.RadarDisplay(radar)
    os.makedirs("../static", exist_ok=True)

    field_configs = {
        "reflectivity": {
            "filename": "../static/latest_radar_reflectivity.png",
            "cmap": "NWSRef",
            "vmin": -32,
            "vmax": 64,
            "label": "Reflectivity (dBZ)"
        },
        "velocity": {
            "filename": "../static/latest_radar_velocity.png",
            "cmap": "NWSVel",
            "vmin": -50,
            "vmax": 50,
            "label": "Velocity (m/s)"
        },
        "differential_reflectivity": {
            "filename": "../static/latest_radar_differential_reflectivity.png",
            "cmap": "Spectral",
            "vmin": -1,
            "vmax": 8,
            "label": "ZDR (dB)"
        },
        "cross_correlation_ratio": {
            "filename": "../static/latest_radar_correlation_ratio.png",
            "cmap": "plasma",
            "vmin": 0.5,
            "vmax": 1.05,
            "label": "Correlation Coefficient"
        },
    }

    for field, cfg in field_configs.items():
        if field not in radar.fields:
            print(f"⚠️  Skipping {field} — field not found in file.")
            continue

        print(f"🖼️  Plotting {field} image with transparent background...")
        fig = plt.figure(figsize=(6, 6), dpi=150)
        ax = fig.add_subplot(111)
        display.plot_ppi(
            field=field,
            ax=ax,
            cmap=cfg["cmap"],
            vmin=cfg["vmin"],
            vmax=cfg["vmax"],
            colorbar_label=cfg["label"],
        )
        plt.axis("off")
        plt.savefig(cfg["filename"], bbox_inches="tight", pad_inches=0, transparent=True)
        plt.close()
        print(f"✅ Saved {cfg['filename']}")

# Run if called directly
if __name__ == "__main__":
    plot_radar("KFFC")  # Change if necessary
