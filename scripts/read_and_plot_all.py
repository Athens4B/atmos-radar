import pyart
import os
import glob

def find_latest_radar_file(directory, site_prefix="KFFC"):
    files = sorted(
        glob.glob(f"{directory}/{site_prefix}_*.gz"),
        key=os.path.getmtime,
        reverse=True
    )
    return files[0] if files else None

def main():
    data_dir = "/root/atmos-radar/data"
    radar_file_path = find_latest_radar_file(data_dir)
    
    if not radar_file_path:
        print("❌ No radar file found.")
        return

    print(f"📂 Reading radar file: {radar_file_path}")
    radar = pyart.io.read(radar_file_path)

    # Continue with the rest of your plotting...

if __name__ == "__main__":
    main()
