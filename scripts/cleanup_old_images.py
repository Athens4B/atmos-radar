# cleanup_old_images.py

import os
import time

STATIC_DIR = os.path.join(os.path.dirname(__file__), '../static')
AGE_THRESHOLD_HOURS = 3

# Ensure static directory exists
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
    print(f"Created directory: {STATIC_DIR}")

# Delete files older than threshold
now = time.time()
for filename in os.listdir(STATIC_DIR):
    filepath = os.path.join(STATIC_DIR, filename)
    if os.path.isfile(filepath):
        file_age_hours = (now - os.path.getmtime(filepath)) / 3600
        if file_age_hours > AGE_THRESHOLD_HOURS:
            os.remove(filepath)
            print(f"Deleted old file: {filename}")
