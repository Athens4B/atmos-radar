from nexradaws import NexradAwsRadarFile

filename = "KJKL_20250430_2129"

try:
    with open(filename, "rb") as f:
        radar = NexradAwsRadarFile(f)
        print(f"Radar site ID: {radar.site_id}")
        print(f"Scan time: {radar.scan_time}")
        print(f"Number of messages: {len(radar.messages)}")
        print(f"Message types: {set(m['type'] for m in radar.messages)}")
except Exception as e:
    print(f"Failed to parse file: {e}")
