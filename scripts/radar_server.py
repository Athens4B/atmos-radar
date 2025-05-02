from flask import Flask, send_from_directory, jsonify, request
import os

# Ensure we're using an absolute path for the static folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, "../static")

app = Flask(__name__, static_folder=STATIC_FOLDER)

# Serve homepage (index.html)
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# Serve radar site GeoJSON
@app.route("/radar_sites.geojson")
def radar_sites():
    return send_from_directory(app.static_folder, "radar_sites.geojson")

# Route to serve radar images
@app.route("/radar/<site>")
def get_radar_image(site):
    field = request.args.get("field", "reflectivity")

    filename_map = {
        "reflectivity": "latest_radar_reflectivity.png",
        "velocity": "latest_radar_velocity.png",
        "differential_reflectivity": "latest_radar_differential_reflectivity.png",
        "cross_correlation_ratio": "latest_radar_correlation_ratio.png",
    }

    filename = filename_map.get(field)
    if not filename:
        return jsonify({"error": f"Unsupported field: {field}"}), 400

    filepath = os.path.join(app.static_folder, filename)
    print(f"🔍 Checking file path: {filepath}")  # Debug print

    if not os.path.exists(filepath):
        return jsonify({"error": f"Radar image for '{field}' not found."}), 404

    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    print(f"🚀 Starting Flask server using static folder: {STATIC_FOLDER}")
    app.run(host="0.0.0.0", port=5000)
