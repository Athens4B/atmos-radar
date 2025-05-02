import os
import re
import gzip
import shutil
import requests
import pyart
import matplotlib.pyplot as plt

# === CONFIG ===
station = "KJKL"
api_key = "be324b8febc3304211303c4d97106a37"
base_url = f"https://level2.allisonhouse.com/level2/{api_key}/data/nexrad/{station}"
data_dir = f"./data/{station}"
os.makedirs(data_dir, exist_ok=True)

# === STEP 1: Read dir.list and get latest 3 files ===
with open("dir.list", "r") as f:
    contents = f.read()

matches = re.findall(rf"({station}_\d{{8}}_\d{{4}})\.gz", contents)
if not matches:
    print("No valid radar files found in directory listing.")
    exit(1)

latest_files = sorted(matches)[-3:]
print("Latest files:", latest_files)

# === STEP 2: Download and decompress each file ===
for fname in latest_files:
    url = f"{base_url}/{fname}.gz"
    gz_path = os.path.join(data_dir, f"{fname}.gz")
    raw_path = os.path.join(data_dir, fname)

    # Download
    print(f"Downloading: {url}")
    r = requests.get(url)
    if r.status_code == 200:
        with open(gz_path, "wb") as f:
            f.write(r.content)
        print(f"Downloaded: {gz_path}")
    else:
        print(f"Failed to download {fname}.gz ({r.status_code})")
        continue

    # Decompress
    with gzip.open(gz_path, "rb") as f_in, open(raw_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    print(f"Decompressed: {raw_path}")

# === STEP 3: Plot reflectivity using Py-ART ===
for fname in latest_files:
    raw_path = os.path.join(data_dir, fname)
    image_path = os.path.join(data_dir, f"{fname}_reflectivity.png")

    try:
        radar = pyart.io.read(raw_path)
        display = pyart.graph.RadarDisplay(radar)

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)
        display.plot("reflectivity", 0, ax=ax, title=fname, colorbar_label="dBZ")
        plt.savefig(image_path)
        plt.close(fig)

        print(f"Saved image: {image_path}")
    except Exception as e:
        print(f"Error processing {fname}: {e}")
