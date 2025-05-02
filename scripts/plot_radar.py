import pyart
import matplotlib.pyplot as plt

# Read the radar file saved by fetch script
with open("latest_filename.txt") as f:
    radar_file = f.read().strip()

print(f"Attempting to read: {radar_file}")
radar = pyart.io.read(radar_file)
print("Radar file loaded.")

# Create a display
display = pyart.graph.RadarDisplay(radar)

# Create a plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)

# Plot the reflectivity field (usually 'reflectivity' or 'dBZ')
display.plot('velocity', 0, title=f"Velocity from {radar_file}", ax=ax)
display.set_limits(xlim=(-150, 150), ylim=(-150, 150), ax=ax)
plt.show()
