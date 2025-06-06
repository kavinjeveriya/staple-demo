from flask import Flask, jsonify
import logging
import os
from datetime import datetime
from prometheus_flask_exporter import PrometheusMetrics

# Create logs directory if not exists
log_dir = "/var/staple-demo/logs"
os.makedirs(log_dir, exist_ok=True)

# Configure logging
log_file = os.path.join(log_dir, "api.logs")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.route("/health", methods=["GET"])
def health():
    logging.info("Health check called")
    return jsonify({"status": "OK"}), 200

@app.route("/time", methods=["GET"])
def get_time():
    now = datetime.now().isoformat()
    logging.info(f"Time endpoint called. Returning time: {now}")
    return jsonify({"time": now}), 200

@app.errorhandler(Exception)
def handle_error(e):
    logging.error(f"Unhandled error: {str(e)}")
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    logging.info("Starting Flask app on port 5000")
    app.run(host="0.0.0.0", port=5000)
