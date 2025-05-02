import os
import requests
import subprocess
from datetime import datetime, timedelta

def fetch_latest_file(station_id):
    base_url = "https://mesonet-nexrad.agron.iastate.edu/level2/raw"
    now = datetime.utcnow()

    for minutes_ago in range(0, 30):
        dt = now - timedelta(minutes=minutes_ago)
        timestamp = dt.strftime("%Y%m%d_%H%M")
        filename = f"{station_id}_{timestamp}"
        url = f"{base_url}/{station_id}/{filename}"
        save_path = os.path.join("scripts", filename)

        print(f"Trying: {url}")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            with open("latest_filename.txt", "w") as out:
                out.write(save_path)

            print(f"✅ Downloaded and saved: {save_path}")
            return save_path

    print("❌ No recent file available.")
    return None

# Run fetch and plot
if __name__ == "__main__":
    station = "KFFC"  # 🔁 Change this to any other site ID as needed
    downloaded_file = fetch_latest_file(station)

    if downloaded_file:
        print("📡 Calling read_and_plot_all.py...")
        subprocess.run(["python", "read_and_plot_all.py"])

# To run directly
if __name__ == "__main__":
    fetch_latest_file("KFFC")
