import os
import time

# Folder where radar PNGs are stored
STATIC_DIR = "/root/atmos-radar/static"
MAX_AGE_HOURS = 6

def cleanup_old_images():
    now = time.time()
    cutoff = now - (MAX_AGE_HOURS * 3600)

    for filename in os.listdir(STATIC_DIR):
        if filename.endswith(".png"):
            filepath = os.path.join(STATIC_DIR, filename)
            try:
                if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    print(f"🗑️ Deleted: {filename}")
            except Exception as e:
                print(f"⚠️ Error deleting {filename}: {e}")

if __name__ == "__main__":
    cleanup_old_images()
