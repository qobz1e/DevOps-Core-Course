# Lab 12 — ConfigMaps & Persistent Volumes

## Application Changes

The application was extended with a visit counter that:

- Increments on each request to `/`
- Stores counter value in `/data/visits`
- Reads counter on startup (defaults to 0 if file does not exist)
- Provides `/visits` endpoint returning current count

### Example result:
```json
{"visits": 407}
````

The counter persists across pod restarts using a PersistentVolumeClaim.

---

## ConfigMap Implementation

### ConfigMap from file

A ConfigMap is created from `config.json` using Helm `.Files.Get`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  config.json: |-
    {
      "appName": "devops-info-service",
      "environment": "dev",
      "featureFlags": {
        "enableVisits": true
      }
    }
```

### Mounted as file

ConfigMap is mounted into the container at:

```
/config/config.json
```

### Verification

```bash
kubectl exec <pod> -- cat /config/config.json
```

Output:

```json
{
  "appName": "devops-info-service",
  "environment": "dev",
  "featureFlags": {
    "enableVisits": true
  }
}
```

---

## Environment Variables (ConfigMap)

ConfigMap is also used for environment variables via `envFrom`:

```yaml
envFrom:
  - configMapRef:
      name: myapp-env
```

### Verification

```bash
kubectl exec <pod> -- printenv | findstr APP
```

Output:

```
APP_ENV=dev
```

---

## Persistent Volume (PVC)

### PVC configuration

* Size: 100Mi
* Access mode: ReadWriteOnce
* Mounted to: `/data`

### Purpose

Stores visit counter file `/data/visits`.

---

## Persistence Test

### Before pod deletion

```json
visits: 348
```

### Pod deletion

```bash
kubectl delete pod myapp-845844856d-w4tgd
```

### After pod restart

```json
visits: 407
```

### Conclusion

Counter persists across pod restarts successfully.

---

## ConfigMap vs Secret

### ConfigMap

Used for non-sensitive configuration:

* application settings
* environment flags
* feature toggles

### Secret

Used for sensitive data:

* passwords
* tokens
* API keys

---

## Conclusion

This lab demonstrates:

* Externalized configuration using ConfigMaps
* File-based configuration mounting
* Environment variable injection
* Persistent storage using PVC
* Data persistence across pod restarts