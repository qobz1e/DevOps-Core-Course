"""
DevOps Info Service
Веб-сервис для предоставления информации о системе и состоянии сервиса
"""

import os
import socket
import platform
from datetime import datetime, timezone
from flask import Flask, jsonify, request

# Prometheus
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Создаем приложение Flask
app = Flask(__name__)

# Настройки из переменных окружения
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Время запуска сервиса
START_TIME = datetime.now(timezone.utc)

# Docker информация
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
    system_info = {
        'hostname': socket.gethostname(),
        'platform': platform.system(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'cpu_count': os.cpu_count(),
        'python_version': platform.python_version(),
        'is_docker_container': IS_DOCKER,
        'container_id': CONTAINER_ID
    }

    runtime_info = {
        'uptime_seconds': get_uptime()['seconds'],
        'uptime_human': get_uptime()['human'],
        'current_time': datetime.now(timezone.utc).isoformat(),
        'timezone': 'UTC',
        'start_time': START_TIME.isoformat()
    }

    request_info = {
        'client_ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'method': request.method,
        'path': request.path
    }

    return jsonify({
        'service': {
            'name': 'devops-info-service',
            'version': '2.0.0',
            'description': 'DevOps course info service (Dockerized)',
            'framework': 'Flask',
            'environment': 'docker' if IS_DOCKER else 'local'
        },
        'system': system_info,
        'runtime': runtime_info,
        'request': request_info
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'uptime_seconds': get_uptime()['seconds'],
        'environment': 'docker' if IS_DOCKER else 'local',
        'container_id': CONTAINER_ID
    })

@app.route('/docker')
def docker_info():
    return jsonify({
        'is_docker': IS_DOCKER,
        'container_id': CONTAINER_ID,
        'docker_env': dict(os.environ) if IS_DOCKER else None,
        'message': 'Running in Docker container' if IS_DOCKER else 'Running locally'
    })

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# ----------------------------
# ERRORS
# ----------------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'Endpoint does not exist'
    }), 404

# ----------------------------
# START
# ----------------------------

if __name__ == '__main__':
    print(f"Starting DevOps Info Service on {HOST}:{PORT}")
    print(f"Debug mode: {DEBUG}")
    print(f"Docker environment: {IS_DOCKER}")
    print(f"Container ID: {CONTAINER_ID}")

    app.run(host=HOST, port=PORT, debug=DEBUG)