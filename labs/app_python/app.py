"""
DevOps Info Service with JSON Logging
"""

import os
import socket
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from pythonjsonlogger import jsonlogger

# Flask app
app = Flask(__name__)

# ENV config
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

START_TIME = datetime.now(timezone.utc)

# Docker info
IS_DOCKER = os.path.exists('/.dockerenv')
CONTAINER_ID = socket.gethostname() if IS_DOCKER else None

# ----------------------------
# JSON LOGGING CONFIG
# ----------------------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(message)s %(method)s %(path)s %(status)s %(client_ip)s %(duration)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# ----------------------------
# HELPERS
# ----------------------------
def get_uptime():
    delta = datetime.now(timezone.utc) - START_TIME
    seconds = int(delta.total_seconds())
    return {'seconds': seconds, 'human': f"{seconds} seconds"}

# ----------------------------
# LOGGING MIDDLEWARE
# ----------------------------
@app.before_request
def log_request():
    request.start_time = datetime.now(timezone.utc)
    logging.info(
        "request_received",
        extra={
            "method": request.method,
            "path": request.path,
            "client_ip": request.remote_addr
        }
    )

@app.after_request
def log_response(response):
    duration = (datetime.now(timezone.utc) - request.start_time).total_seconds()
    logging.info(
        "request_completed",
        extra={
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "client_ip": request.remote_addr,
            "duration": duration
        }
    )
    return response

# ----------------------------
# ROUTES
# ----------------------------
@app.route('/')
def main_endpoint():
    return jsonify({
        'service': 'devops-info-service',
        'status': 'running',
        'time': datetime.now(timezone.utc).isoformat()
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'uptime': get_uptime()['seconds']
    })

@app.route('/docker')
def docker_info():
    return jsonify({
        'is_docker': IS_DOCKER,
        'container_id': CONTAINER_ID
    })

# ----------------------------
# ERRORS
# ----------------------------
@app.errorhandler(404)
def not_found(error):
    logging.error(
        "not_found",
        extra={
            "method": request.method,
            "path": request.path,
            "status": 404,
            "client_ip": request.remote_addr
        }
    )
    return jsonify({'error': 'Not Found'}), 404

# ----------------------------
# START
# ----------------------------
if __name__ == '__main__':
    logging.info(
        "service_started",
        extra={
            "host": HOST,
            "port": PORT,
            "debug": DEBUG,
            "docker": IS_DOCKER,
            "container_id": CONTAINER_ID
        }
    )
    app.run(host=HOST, port=PORT, debug=DEBUG)