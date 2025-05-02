# scripts/fetch_and_process.py

import os
import datetime
import requests
import pyart
import matplotlib.pyplot as plt

RADAR_SITE = "KOUN"  # change to your preferred site
DATA_DIR = "../data"
OUTPUT_DIR = "../latest"
ALLISONHOUSE_URL = f"https://example.com/path/to/{RADAR_SITE}_latest.gz"  # replace this

def fetch_radar_file():
    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    site_dir = os.path.join(DATA_DIR, today, RADAR_SITE)
    os.makedirs(site_dir, exist_ok=True)

    local_path = os.path.join(site_dir, f"{RADAR_SITE}_{today}.gz")

    print(f"Fetching: {ALLISONHOUSE_URL}")
    response = requests.get(ALLISONHOUSE_URL)
    if response.status_code == 200:
        with open(local_path, "wb") as f:
            f.write(response.content)
        print(f"Saved to: {local_path}")
        return local_path
    else:
        print(f"Failed to download file: {response.status_code}")
        return None

def process_radar_file(file_path):
    radar = pyart.io.read_nexrad_archive(file_path)
    display = pyart.graph.RadarMapDisplay(radar)

    plt.figure(figsize=(8, 8))
    display.plot_ppi_map(0, resolution='i', projection='merc', vmin=-32, vmax=64)
    output_file = os.path.join(OUTPUT_DIR, f"{RADAR_SITE}.png")
    plt.savefig(output_file)
    plt.close()
    print(f"Radar image saved to {output_file}")

if __name__ == "__main__":
    radar_file = fetch_radar_file()
    if radar_file:
        process_radar_file(radar_file)
