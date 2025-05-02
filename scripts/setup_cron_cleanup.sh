#!/bin/bash

# Paths (update if different)
PYTHON_PATH="/root/miniconda3/envs/radar_env/bin/python"
SCRIPT_PATH="/root/atmos-radar/scripts/cleanup_old_images.py"
LOG_FILE="/root/atmos-radar/scripts/cleanup.log"

# 1. Make cleanup script executable
echo "Making sure the script is executable..."
chmod +x "$SCRIPT_PATH"

# 2. Add cron job
echo "Installing cron job..."
(crontab -l 2>/dev/null; echo "0 * * * * $PYTHON_PATH $SCRIPT_PATH >> $LOG_FILE 2>&1") | crontab -

# 3. Confirm
echo "✅ Cron job set to run hourly."
crontab -l
