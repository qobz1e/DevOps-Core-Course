# DevOps Info Service

## Overview
DevOps Info Service is a web application that provides detailed information about the service itself and its runtime environment. This service will be developed throughout the DevOps course into a comprehensive monitoring tool.

## Prerequisites
- Python 3.11 or higher
- pip package manager

## Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

## Running the Application
```bash
# Basic startup
python app.py

# With custom configuration
PORT=8080 python app.py

# With all environment variables
HOST=127.0.0.1 PORT=3000 DEBUG=True python app.py
```

## API Endpoints

### GET `/`
Returns comprehensive information about the service, system, and current request.

**Example response:**
```json
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "Flask"
  },
  "system": {
    "hostname": "my-pc",
    "platform": "Linux",
    "cpu_count": 8,
    "python_version": "3.11.5"
  },
  "runtime": {
    "uptime_seconds": 120,
    "uptime_human": "2 minutes",
    "current_time": "2024-01-27T10:30:00.000Z"
  }
}
```

### GET `/health`
Returns the health status of the service. Used for monitoring and Kubernetes probes.

**Example response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-27T10:30:00.000Z",
  "uptime_seconds": 120
}
```

## Configuration

The application can be configured using environment variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `HOST` | Host to bind the server to | `0.0.0.0` |
| `PORT` | Port to run the server on | `5000` |
| `DEBUG` | Enable Flask debug mode | `False` |


## 🐳 Docker

### Building the Image
To build the Docker image locally, navigate to the application directory and use:
```bash
docker build -t qobz1e/devops-info-service:lab2 .
```

The Dockerfile follows security best practices including non-root user execution and optimized layer caching.

### Running the Container
Run the container with port mapping to access the service:
```bash
docker run -d -p 5000:5000 --name devops-app qobz1e/devops-info-service:lab2
```

### Pulling from Docker Hub
Pull the pre-built image from Docker Hub:
```bash
docker pull qobz1e/devops-info-service:lab2
```

### Quick Commands
```bash
# Build
docker build -t qobz1e/devops-info-service:lab2 .

# Run
docker run -d -p 5000:5000 --name devops-app qobz1e/devops-info-service:lab2

# Test
curl http://localhost:5000/
curl http://localhost:5000/health
```

### Configuration
Set environment variables when running:
- `HOST`: Binding address (default: 0.0.0.0)
- `PORT`: Application port (default: 5000)
- `DEBUG`: Debug mode (default: False)

Example:
```bash
docker run -d -p 8080:5000 -e PORT=5000 -e DEBUG=True qobz1e/devops-info-service:lab2
```

### Health Check
The container includes a health endpoint at `/health` for monitoring and orchestration systems.
