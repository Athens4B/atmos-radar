import os
import pyart
import numpy as np
import matplotlib.pyplot as plt
import json
from pyart.core.transforms import antenna_to_cartesian
from pyart.io import read

site_id = "KFFC"
radar_file = "KFFC_20250502_0148"
output_dir = "../static"
os.makedirs(output_dir, exist_ok=True)

radar = read(radar_file)
print("📡 Available fields:", list(radar.fields.keys()))

sweep = 0
azimuths = radar.get_azimuth(sweep)
ranges = radar.range['data']
elevations = radar.get_elevation(sweep)
reflectivity = radar.get_field(sweep, "reflectivity")

ranges_2d, azimuths_2d = np.meshgrid(ranges, azimuths)
x, y, _ = antenna_to_cartesian(ranges_2d, azimuths_2d, elevations[:, np.newaxis])

radar_lat = radar.latitude['data'][0]
radar_lon = radar.longitude['data'][0]
deg_per_km = 1.0 / 111.0
x_deg = x / 1000.0 * deg_per_km
y_deg = y / 1000.0 * deg_per_km
lons = radar_lon + x_deg
lats = radar_lat + y_deg

fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
mesh = ax.pcolormesh(lons, lats, reflectivity, cmap="NWSRef", vmin=-32, vmax=64)
ax.set_axis_off()
plt.axis("equal")

image_path = os.path.join(output_dir, f"{site_id}_radar_reflectivity.png")
plt.savefig(image_path, transparent=True, bbox_inches="tight", pad_inches=0)
plt.close()
print(f"✅ Saved image to {image_path}")

bounds = {
    "west": float(np.min(lons)),
    "east": float(np.max(lons)),
    "south": float(np.min(lats)),
    "north": float(np.max(lats)),
}
bounds_path = os.path.join(output_dir, f"{site_id}_radar_bounds.json")
with open(bounds_path, "w") as f:
    json.dump(bounds, f)
print(f"✅ Saved bounds to {bounds_path}")
