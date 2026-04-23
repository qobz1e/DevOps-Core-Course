# ArgoCD GitOps Deployment

## Overview

This document describes the GitOps deployment setup for Lab 13 using ArgoCD. The application is deployed using a Helm chart with separate configurations for `dev` and `prod` environments.

---

## 1. ArgoCD Setup

### Installation
ArgoCD was installed using Helm in a dedicated namespace:

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

kubectl create namespace argocd
helm install argocd argo/argo-cd -n argocd
````

All ArgoCD components are running in the `argocd` namespace:

```bash
kubectl get pods -n argocd
```

---

### UI Access

Port-forward was used to access the UI:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

ArgoCD UI is available at:

```
https://localhost:8080
```

Login:

* Username: `admin`
* Password: retrieved from `argocd-initial-admin-secret`

---

### CLI Access

ArgoCD CLI was installed and configured:

```bash
argocd login localhost:8080 --insecure
```

Connection verified:

```bash
argocd app list
```

---

## 2. Application Deployment

### Application Manifest

The main application is defined in:

```
k8s/argocd/application.yaml
```

Example structure:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/qobz1e/DevOps-Core-Course.git
    targetRevision: lab13
    path: k8s/myapp
    helm:
      valueFiles:
        - values.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
```

---

### Deployment

Applied via:

```bash
kubectl apply -f k8s/argocd/application.yaml
```

Initial sync performed:

```bash
argocd app sync myapp
```

Application status:

```bash
argocd app get myapp
```

---

### GitOps Verification

Changes in Git (e.g. replica count in values.yaml) are automatically detected and synchronized by ArgoCD.

---

## 3. Multi-Environment Deployment

### Namespaces

Created namespaces:

```bash
kubectl create namespace dev
kubectl create namespace prod
```

---

### Dev Application (Auto Sync)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-dev
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/qobz1e/DevOps-Core-Course.git
    targetRevision: lab13
    path: k8s/myapp
    helm:
      valueFiles:
        - values-dev.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: dev
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

---

### Prod Application (Manual Sync)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-prod
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/qobz1e/DevOps-Core-Course.git
    targetRevision: lab13
    path: k8s/myapp
    helm:
      valueFiles:
        - values-prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: prod
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
```

---

### Environment Differences

| Environment | Sync Mode | Replicas | Purpose     |
| ----------- | --------- | -------- | ----------- |
| dev         | Auto      | 1–5      | Development |
| prod        | Manual    | 2+       | Production  |

---

## 4. Self-Healing & Drift Detection

### Manual Scaling Test

Dev deployment was manually scaled:

```bash
kubectl scale deployment myapp-dev -n dev --replicas=5
```

ArgoCD detected drift and reverted to Git state due to `selfHeal: true`.

---

### Pod Deletion Test

A pod was deleted manually:

```bash
kubectl delete pod -n dev -l app=myapp
```

Kubernetes recreated the pod automatically via ReplicaSet controller.

---

### Configuration Drift Test

Manual edits in Kubernetes were reverted automatically by ArgoCD during sync reconciliation.

---

## 5. Observations

### Kubernetes vs ArgoCD Healing

* Kubernetes ensures pod availability (ReplicaSet level)
* ArgoCD ensures configuration matches Git (GitOps level)

---

### Sync Behavior

* ArgoCD polls Git repository periodically (~3 minutes)
* Sync can be triggered manually via CLI or UI
* Automated sync applies changes immediately when detected

---

## 6. Final Status

### Dev Environment

* Synced: Yes
* Auto-sync: Enabled
* Self-healing: Enabled
* Pods running: Yes

### Prod Environment

* Synced: Yes
* Auto-sync: Disabled
* Manual control: Enabled
* Pods running: Yes

---

## 7. Conclusion

This setup demonstrates full GitOps workflow:

* Git is the single source of truth
* ArgoCD automatically reconciles cluster state
* Separate environments for dev and prod
* Controlled production deployment with manual approval
* Self-healing ensures consistency in dev environment

---