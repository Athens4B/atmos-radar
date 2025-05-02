import os
import requests
import shutil
import pyart
import matplotlib.pyplot as plt
import subprocess

# Radar site and AllisonHouse configuration
radar_site = "KJKL"
allisonhouse_key = "be324b8febc3304211303c4d97106a37"
radar_base_url = f"https://level2.allisonhouse.com/level2/{allisonhouse_key}/data/nexrad/{radar_site}/"
dirlist_url = radar_base_url + "dir.list"

print(f"Fetching directory: {dirlist_url}")
response = requests.get(dirlist_url)
if response.status_code != 200:
    print("Failed to fetch dir.list")
    exit()

# Find the latest radar file in the list
lines = response.text.strip().splitlines()
print("Searching for the latest available radar file...")
latest_file = None

for line in reversed(lines):
    parts = line.split()
    if len(parts) == 2:
        base_filename = parts[1]
        tried_files = [base_filename + ".gz", base_filename]
        for filename in tried_files:
            file_url = radar_base_url + filename
            print(f"Trying: {file_url}")
            try:
                r = requests.get(file_url, stream=True)
                if r.status_code == 200:
                    with open(filename, "wb") as f:
                        shutil.copyfileobj(r.raw, f)
                    print(f"Downloaded {filename}")
                    latest_file = filename
                    break
            except Exception as e:
                print(f"Download failed: {e}")
        if latest_file:
            break

if not latest_file:
    print("No downloadable radar file found in dir.list.")
    exit()

# Identify file type before reading
print(f"Checking file format of: {latest_file}")
try:
    file_output = subprocess.check_output(["file", latest_file]).decode().strip()
    print(f"File info: {file_output}")
except Exception as e:
    print(f"Failed to determine file type: {e}")

# Read and plot radar file
print(f"Reading radar file: {latest_file}")
try:
    radar = pyart.io.read(latest_file, file_format="NEXRAD_ARCHIVE")
except Exception as e:
    print(f"Error reading radar file: {e}")
    exit()

# Plot radar reflectivity
print("Plotting reflectivity...")
display = pyart.graph.RadarDisplay(radar)
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)
display.plot("reflectivity", 0, ax=ax, title=f"{radar_site} Reflectivity")
plt.show()

# Clean up older files, keeping only the latest
def cleanup_old_files(keep_file):
    for f in os.listdir("."):
        if f.startswith(radar_site) and f != keep_file:
            try:
                os.remove(f)
                print(f"Deleted old file: {f}")
            except Exception as e:
                print(f"Failed to delete {f}: {e}")

cleanup_old_files(latest_file)
