import pyart
import matplotlib.pyplot as plt

# Load saved filename
with open("latest_filename.txt") as f:
    radar_file = f.read().strip()

print(f"Reading radar file: {radar_file}")

try:
    radar = pyart.io.read_nexrad_archive(radar_file)
    display = pyart.graph.RadarDisplay(radar)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    display.plot('reflectivity', 0, vmin=-20, vmax=75, ax=ax, title="Reflectivity")
    plt.show()
except Exception as e:
    print(f"Error reading radar file: {e}")
