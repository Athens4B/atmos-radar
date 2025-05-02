from flask import Flask, send_from_directory, jsonify, request
import os

app = Flask(__name__, static_folder="static")

# Serve index.html (homepage)
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# Serve radar sites GeoJSON
@app.route("/radar_sites.geojson")
def radar_sites():
    return send_from_directory(app.static_folder, "radar_sites.geojson")

# Serve radar images per site and field
@app.route("/radar/<site>")
def get_radar_image(site):
    field = request.args.get("field", "reflectivity")

    valid_fields = {
        "reflectivity",
        "velocity",
        "differential_reflectivity",
        "cross_correlation_ratio"
    }

    if field not in valid_fields:
        return jsonify({"error": f"Invalid radar field: {field}"}), 400

    filename = f"{site}_{field}.png"
    filepath = os.path.join(app.static_folder, filename)

    if not os.path.exists(filepath):
        return jsonify({"error": f"Radar image for {site} and field '{field}' not found"}), 404

    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
