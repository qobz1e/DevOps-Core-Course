import os
import socket
import platform
import json
from datetime import datetime, timezone
from flask import Flask, jsonify, request

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

START_TIME = datetime.now(timezone.utc)

DATA_DIR = os.getenv("DATA_DIR", "/data")
VISITS_FILE = os.path.join(DATA_DIR, "visits.json")

CONFIG_PATH = "/config/config.json"

os.makedirs(DATA_DIR, exist_ok=True)

IS_DOCKER = os.path.exists('/.dockerenv')
CONTAINER_ID = socket.gethostname() if IS_DOCKER else None

# ----------------------------
# PROMETHEUS METRICS
# ----------------------------

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress'
)

# ----------------------------
# DATA FUNCTIONS
# ----------------------------

def load_visits():
    try:
        with open(VISITS_FILE, "r") as f:
            return json.load(f).get("visits", 0)
    except:
        return 0


def save_visits(count):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(VISITS_FILE, "w") as f:
        json.dump({"visits": count}, f)


def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except:
        return {}

# ----------------------------
# HELPERS
# ----------------------------

def get_uptime():
    delta = datetime.now(timezone.utc) - START_TIME
    seconds = int(delta.total_seconds())

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if secs > 0 or not parts:
        parts.append(f"{secs} second{'s' if secs != 1 else ''}")

    return {
        'seconds': seconds,
        'human': ', '.join(parts)
    }

# ----------------------------
# METRICS MIDDLEWARE
# ----------------------------

@app.before_request
def before_request():
    request.start_time = datetime.now(timezone.utc)
    http_requests_in_progress.inc()

@app.after_request
def after_request(response):
    duration = (datetime.now(timezone.utc) - request.start_time).total_seconds()

    http_requests_total.labels(
        method=request.method,
        endpoint=request.path,
        status=str(response.status_code)
    ).inc()

    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.path
    ).observe(duration)

    http_requests_in_progress.dec()

    return response

# ----------------------------
# ROUTES
# ----------------------------

@app.route('/')
def main_endpoint():
    visits = load_visits()
    visits += 1
    save_visits(visits)

    config = load_config()

    return jsonify({
        'service': {
            'name': 'devops-info-service',
            'version': '2.0.0',
            'environment': config.get("environment", "unknown")
        },
        'visits': visits,
        'config': config
    })

@app.route('/visits')
def visits():
    return jsonify({
        "visits": load_visits()
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# ----------------------------

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)