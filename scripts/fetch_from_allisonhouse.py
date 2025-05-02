# fetch_from_allisonhouse.py
import os
import requests
import shutil
import subprocess

# Configuration
radar_site = "KJKL"
allisonhouse_key = "be324b8febc3304211303c4d97106a37"
radar_base_url = f"https://level2.allisonhouse.com/level2/{allisonhouse_key}/data/nexrad/{radar_site}/"
dirlist_url = radar_base_url + "dir.list"

print(f"Fetching directory: {dirlist_url}")
response = requests.get(dirlist_url)
if response.status_code != 200:
    print("Failed to fetch dir.list")
    exit()

# Parse dir.list and find most recent file
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

# Use `file` command to inspect downloaded file
print(f"Checking file format of: {latest_file}")
try:
    file_output = subprocess.check_output(["file", latest_file]).decode().strip()
    print(f"File info: {file_output}")
except Exception as e:
    print(f"Failed to determine file type: {e}")

# Save filename for next script
with open("latest_filename.txt", "w") as f:
    f.write(latest_file)
print("Filename saved for plotting.")
