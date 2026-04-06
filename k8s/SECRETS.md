# Kubernetes Secrets & HashiCorp Vault — Lab 11

## 1. Kubernetes Secrets

### Secret creation

Secret `app-credentials` was created using kubectl:

```bash
kubectl create secret generic app-credentials \
  --from-literal=username=admin \
  --from-literal=password=secret123
```

### Viewing the secret

```bash
kubectl get secret app-credentials -o yaml
```

Example output:

```yaml
data:
  username: YWRtaW4=
  password: c2VjcmV0MTIz
```

### Decoding values

```bash
echo "YWRtaW4=" | base64 -d   # admin
echo "c2VjcmV0MTIz" | base64 -d  # secret123
```

### Security understanding

* Kubernetes Secrets are **only base64 encoded**, not encrypted.
* Anyone with API access can decode them easily.
* etcd encryption must be enabled separately for real security.
* Recommended production practices:

  * Enable etcd encryption at rest
  * Use RBAC to restrict access
  * Prefer external secret managers (Vault, AWS Secrets Manager)

---

## 2. Helm-Managed Secrets

### Secret template (templates/secrets.yaml)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "myapp.fullname" . }}-secret
  labels:
    app: {{ include "myapp.name" . }}
type: Opaque
data:
  username: {{ .Values.secret.username | b64enc }}
  password: {{ .Values.secret.password | b64enc }}
```

### values.yaml

```yaml
secret:
  username: admin
  password: secret123
```

### Secret usage in Deployment

```yaml
envFrom:
  - secretRef:
      name: myapp-release-secret
```

### Verification inside pod

```bash
kubectl exec -it <pod> -c app -- printenv | grep USERNAME
kubectl exec -it <pod> -c app -- printenv | grep PASSWORD
```

Secrets are NOT visible via `kubectl describe pod`.

---

## 3. Resource Management

### Container resources

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "200m"
    memory: "256Mi"
```

### Explanation

* **requests**: guaranteed minimum resources
* **limits**: maximum allowed resources

This ensures:

* stable scheduling in cluster
* protection from resource exhaustion

---

## 4. HashiCorp Vault Integration

### Vault installation

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update
helm install vault hashicorp/vault \
  --set server.dev.enabled=true \
  --set injector.enabled=true
```

### Vault status

```bash
kubectl get pods
```

```
vault-0 Running
vault-agent-injector Running
```

### KV secrets engine

```bash
vault secrets enable -path=secret kv-v2
vault kv put secret/myapp username="admin" password="secret123"
```

### Kubernetes auth

Vault is configured with Kubernetes authentication and role:

* Role: `myapp-role`
* Policy: allows read access to `secret/data/myapp`

### Vault injection annotations

```yaml
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/role: "myapp-role"
  vault.hashicorp.com/agent-inject-secret-config: "secret/data/myapp"
  vault.hashicorp.com/agent-inject-token: "true"
```

### Proof of injection

Inside pod:

```bash
kubectl exec -it <pod> -c app -- ls /vault/secrets
```

Output:

```
config
token
```

Secret content:

```bash
kubectl exec -it <pod> -c app -- cat /vault/secrets/config
```

Example output:

```
data: map[password:secret123 username:admin]
```

### Sidecar pattern explanation

Vault Agent Injector automatically:

* injects init container
* starts sidecar vault-agent
* renders secrets into shared volume
* keeps secrets updated dynamically

---

## 5. Security Comparison

| Feature              | Kubernetes Secrets | Vault                   |
| -------------------- | ------------------ | ----------------------- |
| Encryption           | base64 only        | encrypted storage       |
| Access control       | RBAC               | policies + auth methods |
| Rotation             | manual             | automatic               |
| Audit                | limited            | full audit logs         |
| Production readiness | medium             | high                    |

### Recommendation

* Use Kubernetes Secrets for simple internal configs
* Use Vault for production-grade secret management
* Prefer Vault for dynamic and rotating secrets

---

## Conclusion

Vault integration is fully working:

* Kubernetes Secrets created and used
* Helm-managed secrets implemented
* Vault Agent Injector configured
* Secrets successfully injected into pod
