# LAB07 — Observability & Logging with Loki Stack

## 1. Architecture

**Components:**

- **Loki 3.0** — log storage (TSDB backend)  
- **Promtail 3.0** — log collector, scrapes Docker container logs  
- **Grafana 12.3** — visualization and dashboards  
- **app-python** — Flask application with JSON logging  

**Diagram:**

```

app-python ── stdout/logs ──► Promtail ──► Loki ──► Grafana

```

**Network:** all services share `logging` network.

---

## 2. Setup Guide

### Prerequisites

- Docker Desktop (WSL2 backend on Windows 11)  
- Python 3.11+  
- VS Code  

### Steps

1. Project structure:

```

labs/
├── app_python/      # Flask app + Dockerfile
└── monitoring/      # docker-compose.yml + Loki/Promtail configs

````

2. Build and start stack:

```bash
cd labs/monitoring
docker compose up -d --build
````

3. Verify services:

```bash
docker compose ps
```

4. Access Grafana:

```
http://localhost:3000
```

Admin credentials: `admin` / `admin123`

---

## 3. Configuration

### docker-compose.yml

* **Volumes:**

  * `loki-data` — persistent Loki storage
  * `grafana-data` — Grafana dashboards and configs
* **Ports:**

  * Loki: 3100
  * Promtail: 9080
  * Grafana: 3000
  * app-python: 5000
* **Resource limits** configured under `deploy.resources`
* **Healthchecks** configured for all services

### Loki config (`loki/config.yml`)

* TSDB storage with filesystem
* Schema v13
* Retention period: 7 days (`168h`)
* Compactor enabled

### Promtail config (`promtail/config.yml`)

* Docker service discovery enabled via `/var/run/docker.sock`
* Relabeling: container name → `container`, label `app` → `app`
* Clients: `http://loki:3100/loki/api/v1/push`

---

## 4. Application Logging

### app-python

* Flask application with JSON logging using `python-json-logger`
* Logs every request and response in JSON:

```json
{
  "asctime": "2026-03-23T07:00:00",
  "levelname": "INFO",
  "message": "request_completed",
  "method": "GET",
  "path": "/",
  "status": 200,
  "client_ip": "172.17.0.1",
  "duration": 0.002
}
```

* Error handling logs 404 and other errors
* Logging middleware uses `before_request` and `after_request`

---

## 5. Dashboard

**Dashboard:** `DevOps Logs Dashboard`
**Panels:**

1. **All Logs** — Logs, `{app=~"devops-.*"}`
2. **Requests per second** — Time series, `sum by (app) (rate({app=~"devops-.*"}[1m]))`
3. **Error Logs** — Logs, `{app=~"devops-.*"} | json | status=404`
4. **Log Levels** — Pie / Stat, `sum by (levelname) (count_over_time({app="devops-python"} | json | __error__="" [5m]))`

---

## 6. Production Config

* Grafana security: anonymous access disabled, admin password set
* Resource limits: CPUs and memory configured in `docker-compose.yml`
* Healthchecks: defined for Loki, Promtail, Grafana, and app-python
* Volumes: persistent Loki and Grafana data

---

## 7. Testing

### Verify logs:

```bash
curl http://localhost:5000/
curl http://localhost:5000/health
curl http://localhost:5000/invalid  # to generate 404
```

### Grafana queries:

```logql
{app="devops-python"}
{app="devops-python"} | json
{app="devops-python"} | json | method="GET"
{app="devops-python"} | json | status=404
```

### Verify health:

```bash
docker compose ps
```

All services should show `healthy`.

---

## 8. Challenges

* Promtail initially did not parse `app` label — fixed by `__meta_docker_container_label_app` relabel
* JSONParserErr in Log Levels panel — fixed with `| __error__=""` filter
* Grafana anonymous access needed to be disabled for production compliance

---

## 9. Evidence

### 9.1 Logs from all containers

* Grafana Explore query: `{job="docker"}`
  ![All Docker logs](screenshots/all_logs.png)

### 9.2 JSON logs from app-python

* Grafana Explore query: `{app="devops-python"}`
  ![App Python JSON logs](screenshots/app_logs.png)

### 9.3 Dashboard

* DevOps Logs Dashboard with 4 panels:

  1. All Logs
  2. Requests per second
  3. Error Logs
  4. Log Levels
     ![DevOps Logs Dashboard](screenshots/dashboard.png)

### 9.4 Docker Compose status / Healthchecks

* PowerShell command: `docker compose ps`
  ![Docker Compose ps](screenshots/healthchecks.png)
