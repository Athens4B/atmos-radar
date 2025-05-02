import time
import subprocess

UPDATE_INTERVAL = 120  # seconds (every 2 minutes)

while True:
    print("Fetching latest radar file...")
    subprocess.call(["python", "fetch_from_mesonet.py"])
    
    print("Generating radar images...")
    subprocess.call(["python", "read_and_plot_all.py"])

    print(f"Sleeping for {UPDATE_INTERVAL} seconds...\n")
    time.sleep(UPDATE_INTERVAL)
