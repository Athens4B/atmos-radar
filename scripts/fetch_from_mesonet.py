import os
import requests
from datetime import datetime, timedelta, timezone

def fetch_latest_file(station_id):
    base_url = "https://mesonet-nexrad.agron.iastate.edu/level2/raw"
    now = datetime.now(timezone.utc)

    for minutes_ago in range(0, 30):
        dt = now - timedelta(minutes=minutes_ago)
        timestamp = dt.strftime("%Y%m%d_%H%M")
        filename = f"{station_id}_{timestamp}"
        url = f"{base_url}/{station_id}/{filename}"

        print(f"Trying: {url}")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Save directly in scripts/ without double path
            save_path = filename
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            with open("latest_filename.txt", "w") as out:
                out.write(save_path)
            print(f"✅ Downloaded and saved: {save_path}")
            return save_path
    print("❌ No recent file available.")
    return None

# To run directly
if __name__ == "__main__":
    fetch_latest_file("KFFC")
