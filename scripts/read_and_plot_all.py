# read_and_plot_all.py

import pyart
import matplotlib.pyplot as plt
import numpy as np
import os
import json

def plot_fixed_extent_radar(radar_file, output_image, output_bounds):
    print(f"📂 Reading radar file: {radar_file}")
    radar = pyart.io.read(radar_file)
    print("✅ Successfully read radar file.")
    print("📡 Available fields:", list(radar.fields.keys()))

    display = pyart.graph.RadarMapDisplay(radar)
    field = 'reflectivity'

    fig = plt.figure(figsize=(6, 6), dpi=150)
    ax = fig.add_subplot(111)

    display.plot_ppi(field=field, ax=ax, cmap="NWSRef", vmin=-32, vmax=64)
    ax.set_axis_off()

    image_path = os.path.join("../static", output_image)
    bounds_path = os.path.join("../static", output_bounds)

    # Save PNG
    plt.savefig(image_path, bbox_inches="tight", transparent=True, pad_inches=0)
    plt.close()
    print(f"✅ Saved image to {image_path}")

    # Use a known bounding box for the site (approximate values for KFFC)
    bounds = {
        "west": -85.5,
        "east": -83.3,
        "south": 32.6,
        "north": 34.8
    }
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")

# === MAIN ===
if __name__ == "__main__":
    with open("latest_filename.txt", "r") as f:
        radar_file = f.read().strip()
    plot_fixed_extent_radar(radar_file, "radar_overlay.png", "radar_bounds.json")
