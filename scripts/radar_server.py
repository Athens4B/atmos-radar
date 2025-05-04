from flask import Flask, send_from_directory, jsonify
import os

app = Flask(__name__, static_folder="static")

# Serve the homepage
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# Serve the radar image
@app.route("/static/<path:filename>")
def static_files(filename):
    filepath = os.path.join(app.static_folder, filename)
    if os.path.exists(filepath):
        return send_from_directory(app.static_folder, filename)
    return jsonify({"error": f"File '{filename}' not found"}), 404

# Optional: ping endpoint for testing
@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
