from flask import Flask, request, jsonify, send_from_directory
import os
import datetime
import json
import pyart
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import cartopy.crs as ccrs
from io import BytesIO
import base64

app = Flask(__name__, static_folder="static")

# Define valid radar products and their configuration
RADAR_PRODUCTS = {
    "reflectivity": {
        "field": "reflectivity",
        "cmap": "pyart_NWSRef",
        "vmin": -20,
        "vmax": 75,
        "title": "Reflectivity (dBZ)"
    },
    "velocity": {
        "field": "velocity",
        "cmap": "pyart_NWSVel",
        "vmin": -30,
        "vmax": 30,
        "title": "Radial Velocity (m/s)"
    },
    "differential_reflectivity": {
        "field": "differential_reflectivity",
        "cmap": "pyart_RefDiff",
        "vmin": -4,
        "vmax": 8,
        "title": "Differential Reflectivity (dB)"
    },
    "cross_correlation_ratio": {
        "field": "cross_correlation_ratio",
        "cmap": "pyart_RefDiff",
        "vmin": 0.5,
        "vmax": 1.05,
        "title": "Correlation Coefficient"
    },
    "storm_relative_velocity": {
        "field": "velocity",  # We'll apply storm motion correction in processing
        "cmap": "pyart_NWSVel",
        "vmin": -30,
        "vmax": 30,
        "title": "Storm Relative Velocity (m/s)"
    }
}

# Serve index.html as homepage
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# Serve static files
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

# Get radar site locations
@app.route("/static/radar_sites.geojson")
def radar_sites():
    return send_from_directory("static", "radar_sites.geojson")

# Endpoint for fetching radar data
@app.route("/radar/<site>")
def get_radar_data(site):
    product = request.args.get("field", "reflectivity")
    
    # Validate product
    if product not in RADAR_PRODUCTS:
        return jsonify({
            "error": f"Invalid radar product: {product}",
            "valid_products": list(RADAR_PRODUCTS.keys())
        }), 400
    
    # Get the most recent file for this radar site
    data_dir = os.path.join(app.root_path, "data")
    
    # Find latest file for the given site
    matching_files = []
    try:
        for filename in os.listdir(data_dir):
            if filename.startswith(site):
                matching_files.append(filename)
    except FileNotFoundError:
        return jsonify({"error": f"No data directory found"}), 500
    
    if not matching_files:
        return jsonify({"error": f"No data files found for site: {site}"}), 404
    
    # Sort by timestamp (assuming format SITE_YYYYMMDD_HHMM)
    latest_file = sorted(matching_files)[-1]
    file_path = os.path.join(data_dir, latest_file)
    
    # Process the radar data and create image
    try:
        # Create product specific image
        img_data, bounds = create_radar_image(file_path, product)
        
        # Store image in static folder with unique name
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        img_filename = f"{site}_{product}_{timestamp}.png"
        img_path = os.path.join(app.static_folder, img_filename)
        
        with open(img_path, "wb") as f:
            f.write(img_data)
        
        # Clean up old image files (keep only the most recent 5 per site/product)
        cleanup_old_images(site, product)
        
        # Return metadata including image URL and bounds
        image_url = f"/static/{img_filename}"
        return jsonify({
            "site": site,
            "product": product,
            "timestamp": timestamp,
            "image_url": image_url,
            "bounds": bounds
        })
        
    except Exception as e:
        return jsonify({"error": f"Error processing radar data: {str(e)}"}), 500

def create_radar_image(file_path, product_name):
    """Create a radar image for the specified product."""
    product_config = RADAR_PRODUCTS[product_name]
    
    # Load radar data using PyART
    radar = pyart.io.read(file_path)
    
    # Get the specified field
    field = product_config["field"]
    
    # Apply storm motion correction if needed
    if product_name == "storm_relative_velocity":
        # Default storm motion (you can enhance this with real-time data)
        u_motion = -10  # m/s
        v_motion = -5   # m/s
        
        # Get azimuth and range
        azimuths = radar.azimuth['data']
        ranges = radar.range['data']
        
        # Get velocity data
        velocity = radar.fields['velocity']['data'].copy()
        
        # Apply correction (simplified approach)
        for i, azimuth in enumerate(azimuths):
            az_rad = np.deg2rad(azimuth)
            storm_component = u_motion * np.sin(az_rad) + v_motion * np.cos(az_rad)
            velocity[i, :] = velocity[i, :] - storm_component
            
        # Create temporary field for storm-relative velocity
        radar.add_field_like('velocity', 'storm_relative_velocity', velocity)
        field = 'storm_relative_velocity'
    
    # Create display and plot
    display = pyart.graph.RadarMapDisplay(radar)
    
    # Create figure
    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # Plot the radar field
    display.plot_ppi_map(
        field,
        0,  # sweep/elevation
        vmin=product_config["vmin"],
        vmax=product_config["vmax"],
        cmap=product_config["cmap"],
        colorbar_label=product_config["title"],
        ax=ax,
        projection=ccrs.PlateCarree()
    )
    
    # Get the latitude/longitude bounds
    lon_min, lon_max = ax.get_xlim()
    lat_min, lat_max = ax.get_ylim()
    
    bounds = {
        "north": lat_max,
        "south": lat_min,
        "east": lon_max,
        "west": lon_min
    }
    
    # Save figure to bytes
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer.getvalue(), bounds

def cleanup_old_images(site, product, max_to_keep=5):
    """Delete old image files, keeping only the most recent ones."""
    static_dir = app.static_folder
    pattern = f"{site}_{product}"
    
    matching_files = []
    for filename in os.listdir(static_dir):
        if filename.startswith(pattern) and filename.endswith(".png"):
            matching_files.append(filename)
    
    # Sort by timestamp (part of filename)
    matching_files.sort()
    
    # Delete old files
    for old_file in matching_files[:-max_to_keep]:
        try:
            os.remove(os.path.join(static_dir, old_file))
        except:
            pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)