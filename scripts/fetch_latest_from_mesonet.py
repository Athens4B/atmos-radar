import os
import requests
from datetime import datetime, timedelta

def fetch_latest_radar(site_code: str, max_attempts: int = 12):
    now = datetime.utcnow().replace(second=0, microsecond=0)
    time_pointer = now - timedelta(minutes=now.minute % 5)  # Round down to nearest 5-min

    base_url = "https://mesonet-nexrad.agron.iastate.edu/level2/raw"

    for attempt in range(max_attempts):
        timestamp = time_pointer.strftime("%Y%m%d_%H%M")
        filename = f"{site_code}_{timestamp}"
        url = f"{base_url}/{site_code}/{filename}"

        print(f"Trying: {url}")
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Downloaded: {filename}")
            with open("latest_filename.txt", "w") as txt:
                txt.write(filename)
            return filename

        # Step back 5 minutes
        time_pointer -= timedelta(minutes=5)

    print("❌ No recent file available to download.")
    return None

# Example use (replace with dynamically passed site code from UI)
if __name__ == "__main__":
    site = input("Enter radar site code (e.g. KJKL): ").strip().upper()
    fetch_latest_radar(site)
