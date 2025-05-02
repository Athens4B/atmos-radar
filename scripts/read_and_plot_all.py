import os
import pyart
import matplotlib.pyplot as plt

def plot_radar(station_id):
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

    # Plot reflectivity
    if "reflectivity" in radar.fields:
        print("🖼️ Plotting reflectivity image with transparent background...")
        fig = plt.figure(figsize=(6, 6), dpi=150)
        ax = fig.add_subplot(111)
        display.plot_ppi(
            field="reflectivity",
            ax=ax,
            cmap="NWSRef",  # safe fallback
            vmin=-32,
            vmax=64,
            colorbar_label="Reflectivity (dBZ)",
        )
        plt.axis("off")
        plt.savefig("../static/latest_radar_reflectivity.png", bbox_inches="tight", pad_inches=0, transparent=True)
        plt.close()
        print("✅ Saved ../static/latest_radar_reflectivity.png")
    else:
        print("⚠️  'reflectivity' field not found.")

# Run the function
plot_radar("KFFC")
