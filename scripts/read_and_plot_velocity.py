import pyart
import matplotlib.pyplot as plt

with open("latest_filename.txt", "r") as f:
    filename = f.read().strip()

radar = pyart.io.read(filename)
display = pyart.graph.RadarMapDisplay(radar)

fig = plt.figure(figsize=(8, 8), dpi=150)
ax = fig.add_subplot(1, 1, 1)

display.plot_ppi_map(
    'velocity',
    sweep=0,
    ax=ax,
    vmin=-60,
    vmax=60,
    resolution='i',
    colorbar_flag=False,
    title_flag=False,
    embellish=False
)

ax.set_axis_off()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig("../static/latest_radar_velocity.png", transparent=True, bbox_inches='tight', pad_inches=0)
plt.close()
