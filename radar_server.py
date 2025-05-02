from flask import Flask, send_from_directory, jsonify, request
import os

app = Flask(__name__, static_folder="static")

# Home route serves the map HTML
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# Serve the radar site list GeoJSON
@app.route("/radar_sites.geojson")
def radar_sites():
    return send_from_directory(app.static_folder, "radar_sites.geojson")

# Serve the requested radar image for any site+field
@app.route("/radar/<site>")
def get_radar_image(site):
    field = request.args.get("field", "reflectivity")

    # Construct expected filename based on convention
    field_map = {
        "reflectivity": "latest_radar_reflectivity.png",
        "velocity": "latest_radar_velocity.png",
        "differential_reflectivity": "latest_radar_differential_reflectivity.png",
        "cross_correlation_ratio": "latest_radar_correlation_ratio.png"
    }

    filename = field_map.get(field)
    if not filename:
        return jsonify({"error": f"Unsupported field '{field}'"}), 400

    filepath = os.path.join(app.static_folder, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": f"Radar image for field '{field}' not found."}), 404

    return send_from_directory(app.static_folder, filename)

# Serve any static asset directly (e.g., JavaScript or CSS)
@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
