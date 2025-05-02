import os
import pyart
import matplotlib.pyplot as plt

# Load latest radar file
try:
    with open("latest_filename.txt", "r") as f:
        radar_file = f.read().strip()
except FileNotFoundError:
    print("❌ latest_filename.txt not found.")
    exit()

# Read radar data
print(f"Reading radar file: {radar_file}")
radar = pyart.io.read(radar_file)
print("✅ Successfully read radar file.")

site_id = radar.metadata.get("instrument_name", "RADAR").upper()
available_fields = radar.fields.keys()
print(f"📡 Available fields: {list(available_fields)}")

# Set up output folder
output_folder = "../static"
os.makedirs(output_folder, exist_ok=True)

# Define fields to plot
fields_to_plot = {
    "reflectivity": {
        "vmin": -32,
        "vmax": 64,
        "cmap": "NWSRef",
        "label": "Reflectivity (dBZ)"
    },
    "velocity": {
        "vmin": -32,
        "vmax": 32,
        "cmap": "NWSVel",
        "label": "Velocity (m/s)"
    },
    "differential_reflectivity": {
        "vmin": -1,
        "vmax": 8,
        "cmap": "Spectral",
        "label": "ZDR (dB)"
    },
    "cross_correlation_ratio": {
        "vmin": 0.7,
        "vmax": 1.05,
        "cmap": "viridis",
        "label": "ρhv"
    }
}

# Plot each field
for field_name, settings in fields_to_plot.items():
    if field_name not in radar.fields:
        print(f"⚠️  Skipping {field_name} — not in radar file.")
        continue

    print(f"🖼️  Plotting {field_name} image with transparent background...")
    display = pyart.graph.RadarDisplay(radar)
    fig = plt.figure(figsize=(6, 6), dpi=150)
    ax = fig.add_subplot(111)

    display.plot_ppi(
        field=field_name,
        ax=ax,
        cmap=settings["cmap"],
        vmin=settings["vmin"],
        vmax=settings["vmax"],
        colorbar_label=settings["label"]
    )

    plt.axis("off")

    output_file = os.path.join(output_folder, f"{site_id}_{field_name}.png")
    plt.savefig(output_file, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved {output_file}")

# Run the function
plot_radar("KFFC")
