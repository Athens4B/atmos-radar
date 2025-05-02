import pyart
import matplotlib.pyplot as plt

# Read the latest radar file
with open("latest_filename.txt", "r") as f:
    filename = f.read().strip()

print(f"Attempting to read: {filename}")
radar = pyart.io.read(filename)
print("Successfully read the radar file.")

# Create plot without axes, labels, or colorbar
display = pyart.graph.RadarMapDisplay(radar)
fig = plt.figure(figsize=(8, 8), dpi=150)
ax = fig.add_subplot(1, 1, 1)

display.plot_ppi_map(
    'reflectivity',
    sweep=0,
    ax=ax,
    vmin=-20,
    vmax=80,
    resolution='i',
    colorbar_flag=False,
    title_flag=False,
    embellish=False
)

# Remove axis and frame
ax.set_axis_off()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Save image with transparent background
plt.savefig("../static/latest_radar_reflectivity.png", transparent=True, bbox_inches='tight', pad_inches=0)
plt.close()
print("Radar image saved without background or extras.")
