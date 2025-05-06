#!/usr/bin/env python3
import os
import sys
import datetime
import requests
import argparse
import time
import json

MESONET_BASE_URL = "https://mesonet-nexrad.agron.iastate.edu/level2/raw"

def fetch_radar_data(site, output_dir, attempts=5, delay=60):
    """Fetch the latest radar data for the given site."""
    now = datetime.datetime.utcnow()
    
    success = False
    filename = None
    
    for attempt in range(attempts):
        # Try current time and go back in time
        for minute_offset in range(0, 20):
            attempt_time = now - datetime.timedelta(minutes=minute_offset)
            timestamp = attempt_time.strftime("%Y%m%d_%H%M")
            filename = f"{site}_{timestamp}"
            url = f"{MESONET_BASE_URL}/{site}/{filename}"
            
            print(f"Attempting to fetch: {url}")
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Create output directory if it doesn't exist
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Save to file
                    save_path = os.path.join(output_dir, filename)
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                    
                    print(f"✅ Successfully downloaded {filename}")
                    
                    # Save metadata 
                    meta_file = os.path.join(output_dir, f"{site}_latest.json")
                    meta_data = {
                        "site": site,
                        "timestamp": timestamp,
                        "file": filename,
                        "downloaded_at": datetime.datetime.utcnow().isoformat()
                    }
                    
                    with open(meta_file, "w") as f:
                        json.dump(meta_data, f, indent=2)
                    
                    success = True
                    break
                else:
                    print(f"❌ Failed to fetch {filename} - HTTP {response.status_code}")
            
            except Exception as e:
                print(f"❌ Error fetching {filename}: {e}")
        
        if success:
            break
        elif attempt < attempts - 1:
            print(f"Retry in {delay} seconds... (Attempt {attempt + 1}/{attempts})")
            time.sleep(delay)
    
    if not success:
        print(f"❌ Failed to fetch radar data for {site} after {attempts} attempts.")
        return None
    
    return filename

def main():
    parser = argparse.ArgumentParser(description="Fetch radar data from NEXRAD")
    parser.add_argument("--site", required=True, help="Radar site ID (e.g. KJKL)")
    parser.add_argument("--output-dir", default="data", help="Output directory for data")
    parser.add_argument("--attempts", type=int, default=3, help="Number of attempts to fetch data")
    
    args = parser.parse_args()
    
    fetch_radar_data(args.site, args.output_dir, args.attempts)

if __name__ == "__main__":
    main()