import os
import pyart
import matplotlib.pyplot as plt

# Read the latest radar filename
try:
    with open("latest_filename.txt", "r") as f:
        radar_file = f.read().strip()
except FileNotFoundError:
    print("❌ latest_filename.txt not found.")
    exit(1)

print(f"Reading radar file: {radar_file}")
radar = pyart.io.read(radar_file)
print("✅ Successfully read radar file.")
print("📡 Available fields:", list(radar.fields.keys()))

# Create output folder if needed
static_dir = os.path.abspath("../static")
os.makedirs(static_dir, exist_ok=True)

# Plot reflectivity and save as transparent PNG
output_path = os.path.join(static_dir, "latest_radar_reflectivity.png")
print("🖼️ Plotting reflectivity image with transparent background...")

display = pyart.graph.RadarMapDisplay(radar)
fig = plt.figure(figsize=(6, 6), dpi=150)
ax = fig.add_subplot(111)

display.plot_ppi(
    field="reflectivity",
    ax=ax,
    cmap="NWSRef",  # Use valid Matplotlib colormap
    vmin=-32,
    vmax=64,
    colorbar_label="Reflectivity (dBZ)"
)

plt.axis("off")
plt.savefig(output_path, bbox_inches="tight", pad_inches=0, transparent=True)
plt.close()

print(f"✅ Saved {output_path}")
