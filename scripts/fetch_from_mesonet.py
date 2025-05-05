import os
import datetime
import requests

station = "KFFC"

def fetch_latest_file(station):
    now = datetime.datetime.utcnow()
    for minute_offset in range(0, 10):
        attempt_time = now - datetime.timedelta(minutes=minute_offset)
        timestamp = attempt_time.strftime("%Y%m%d_%H%M")
        filename = f"{station}_{timestamp}"
        url = f"https://mesonet-nexrad.agron.iastate.edu/level2/raw/{station}/{filename}"
        print(f"Trying: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                os.makedirs("/root/atmos-radar/data", exist_ok=True)
                save_path = os.path.join("/root/atmos-radar/data", filename)
                with open(save_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Downloaded: {filename}")
                with open("/root/atmos-radar/data/latest_filename.txt", "w") as f:
                    f.write(filename)
                return filename
        except Exception as e:
            print(f"❌ Failed to fetch {filename}: {e}")
    print("❌ No recent file found.")
    return None

if __name__ == "__main__":
    fetch_latest_file(station)
