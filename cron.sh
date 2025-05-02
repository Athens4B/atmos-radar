#!/bin/bash

# Activate Conda environment
source /root/miniconda3/etc/profile.d/conda.sh
conda activate radar_env

# Move to scripts directory
cd /root/atmos-radar/scripts

# Fetch latest radar file
python fetch_from_mesonet.py

# Plot radar image to static folder
python read_and_plot_all.py
