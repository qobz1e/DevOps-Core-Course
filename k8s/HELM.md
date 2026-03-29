
# Lab 10 — Helm Package Manager

![difficulty](https://img.shields.io/badge/difficulty-intermediate-yellow)
![topic](https://img.shields.io/badge/topic-Helm-blue)
![points](https://img.shields.io/badge/points-12%2B2.5-orange)
![tech](https://img.shields.io/badge/tech-Helm-informational)

> Package your Kubernetes applications with Helm for reusable, configurable deployments across environments.

---

## Chart Overview

This Helm chart (`myapp`) converts Kubernetes manifests from Lab 9 into a reusable, configurable deployment system.

### Structure

```

myapp/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
└── templates/
├── deployment.yaml
├── service.yaml
└── hooks/
├── pre-install-job.yaml
└── post-install-job.yaml

````

### Key Components

- **Deployment template** — runs the Python application with configurable replicas, image, and resources
- **Service template** — exposes the application inside cluster (NodePort / ClusterIP)
- **Values files** — environment-based configuration (dev/prod)
- **Hooks** — lifecycle jobs executed before and after deployment

---

## Configuration Guide

### Main values (`values.yaml`)

- `replicaCount` — number of pods
- `image.repository` — Docker image name
- `image.tag` — image version
- `service.port` — exposed port
- `service.targetPort` — container port (5000)
- `resources` — CPU/memory limits
- `livenessProbe` — health check configuration
- `readinessProbe` — readiness check configuration

### Dev environment (`values-dev.yaml`)

- 1 replica
- lightweight CPU/memory limits
- NodePort service
- relaxed probes

### Prod environment (`values-prod.yaml`)

- 3–5 replicas
- higher resource limits
- LoadBalancer-ready configuration
- stricter probes

### Example usage

```bash
helm install myapp-dev ./myapp -f values-dev.yaml
helm install myapp-prod ./myapp -f values-prod.yaml
````

---

## Hook Implementation

### Pre-install hook

Executes before deployment starts.

* Used for initialization / validation
* Runs a Kubernetes Job

### Post-install hook

Executes after deployment completes.

* Used for smoke tests or verification
* Confirms application readiness

### Hook execution order

```
Pre-install → Deploy resources → Post-install
```

### Hook weights

* `-5` → pre-install (runs first)
* `5` → post-install (runs last)

### Deletion policy

Hooks are configured with:

```
hook-delete-policy: hook-succeeded
```

This ensures:

* cleanup after successful execution
* no leftover Jobs in cluster

---

## Installation Evidence

### Helm release list

```bash
helm list
```

📸 Screenshot: `lab10-set.png`

---

### Kubernetes resources

```bash
kubectl get all
```

📸 Screenshot: `lab10-set.png`

---

### Application running

```bash
kubectl get pods
kubectl get svc
```

📸 Screenshot: `lab10-app.png`

---

### Hooks execution

```bash
kubectl get jobs
kubectl logs job/<pre-install-job>
kubectl logs job/<post-install-job>
```

📸 Screenshot: `lab10-hooks.png`

---

## Operations

### Install

```bash
helm install myapp-release ./myapp
```

### Upgrade

```bash
helm upgrade myapp-release ./myapp
```

### Rollback

```bash
helm rollback myapp-release 1
```

### Uninstall

```bash
helm uninstall myapp-release
```

---

## Testing & Validation

### Chart validation

```bash
helm lint ./myapp
```

### Template rendering

```bash
helm template myapp ./myapp
```

### Dry-run install

```bash
helm install test ./myapp --dry-run --debug
```

### Result

* Deployment successfully created
* Service exposed via NodePort
* Application accessible in browser via `http://localhost:8080`

---

## Summary

This Helm chart demonstrates:

* templating Kubernetes manifests
* environment-based configuration
* lifecycle hooks (pre/post install)
* production-ready structure
* reusable deployment patterns

Helm significantly improves maintainability, scalability, and repeatability of Kubernetes deployments.

---

## Screenshots

### Cluster setup & Helm state

![lab10-set](lab10-set.png)

### Application running

![lab10-app](lab10-app.png)

### Hooks execution

![lab10-hooks](lab10-hooks.png)
