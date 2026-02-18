# Lab 4 — Infrastructure as Code (Terraform & Pulumi)

## Task 1 — Terraform VM Creation

### 1.1 Terraform Implementation

**Version:** Terraform v1.10.5

**Project Structure:**
```
terraform/
├── main.tf
├── outputs.tf
└── .terraform/
```

**Key Decisions:**
- Used Docker provider instead of cloud provider due to network access issues
- Created container as VM equivalent with Ubuntu 22.04
- Exposed ports 22, 80, 5000 for future labs
- Added SSH server for remote access

### 1.2 Commands Executed

```bash
terraform init
terraform plan
terraform apply -auto-approve
terraform output
```

### 1.3 Created Resources

| Resource Type | Name | Purpose |
|--------------|------|---------|
| docker_network | lab_network | Isolated network |
| docker_container | lab_vm | Ubuntu container with SSH |
| docker_volume | lab_data | Persistent storage |

### 1.4 Output Results

```
container_id = "bf152e897867..."
container_name = "devops-lab-container"
ssh_command = "ssh -p 2222 root@localhost"
web_url = "http://localhost:8080"
app_url = "http://localhost:5000"
```

### 1.5 Verification

```bash
$ docker ps
CONTAINER ID   IMAGE          COMMAND                  PORTS                                                                                             NAMES
bf152e897867   ubuntu:22.04   "/bin/bash -c 'apt-g…"   0.0.0.0:2222->22/tcp, 0.0.0.0:8080->80/tcp, 0.0.0.0:5000->5000/tcp   devops-lab-container

$ ssh -p 2222 root@localhost
root@bf152e897867:~# netstat -tulpn
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      3942/sshd
tcp6       0      0 :::22                   :::*                    LISTEN      3942/sshd
```

### 1.6 Observations
- Container created and accessible via SSH
- Port 22 open and listening
- Ports 80 and 5000 exposed on host (services will be added in Lab 5)

---

## Task 2 — Pulumi VM Creation

### 2.1 Pulumi Implementation

**Version:** Pulumi v3.142.0
**Language:** Python 3.12

**Project Structure:**
```
pulumi/
├── __main__.py
├── requirements.txt
├── Pulumi.yaml
└── venv/
```

### 2.2 Commands Executed

```bash
pulumi login --local
pulumi stack init dev
pulumi up
pulumi stack output
```

### 2.3 Created Resources

| Resource Type | Name | Purpose |
|--------------|------|---------|
| docker.Network | lab-network | Isolated network |
| docker.Container | lab-container | Ubuntu container with SSH |
| docker.Volume | lab-data | Persistent storage |

### 2.4 Output Results

```
app_url         http://localhost:5001
container_id    e71a3478d66ea2d00593e0a29ca429e16a909b17aed0bd38c43b16b24b1ea8cf
container_name  devops-lab-container-pulumi
ssh_command     ssh -p 2223 root@localhost
web_url         http://localhost:8081
```

### 2.5 Verification

```bash
$ docker ps
CONTAINER ID   IMAGE                           COMMAND                  PORTS                                                                NAMES
e71a3478d66e   ubuntu:22.04                    "sh -c 'apt-get upda…"   0.0.0.0:2223->22/tcp, 0.0.0.0:8081->80/tcp, 0.0.0.0:5001->5000/tcp   devops-lab-container-pulumi
bf152e897867   ubuntu:22.04                    "/bin/bash -c 'apt-g…"   0.0.0.0:5000->5000/tcp, 0.0.0.0:2222->22/tcp, 0.0.0.0:8080->80/tcp   devops-lab-container

$ ssh -p 2223 root@localhost
root@e71a3478d66e:~#
```

### 2.6 Observations
- Pulumi container created successfully
- Different ports used to avoid conflicts with Terraform container
- Same functionality achieved with Python code

---

## Task 3 — Terraform vs Pulumi Comparison

| Aspect | Terraform | Pulumi |
|--------|-----------|--------|
| **Language** | HCL (declarative) | Python (imperative) |
| **Container Name** | devops-lab-container | devops-lab-container-pulumi |
| **SSH Port** | 2222 | 2223 |
| **Web Port** | 8080 | 8081 |
| **App Port** | 5000 | 5001 |
| **Creation Time** | ~2 minutes | ~2 minutes |
| **Syntax** | Specific to Terraform | Familiar Python |
| **Flexibility** | Limited (count, for_each) | Full (loops, conditions) |
| **State Management** | Local .tfstate file | Local (file://) |
| **Error Messages** | Can be cryptic | Python tracebacks |

### 3.1 Ease of Learning
[Your answer]

### 3.2 Code Readability
[Your answer]

### 3.3 Debugging Experience
[Your answer]

### 3.4 When to Use Terraform
- Simple infrastructure deployments
- Teams with operations background
- When you need maximum community support

### 3.5 When to Use Pulumi
- Complex infrastructure with business logic
- Teams with Python/JS development background
- When you need testing and reusability

### 3.6 My Preference
[Your choice and why]

---

## Challenges & Solutions

### Challenge 1: Network access to Terraform registry
**Solution:** Manually downloaded and installed provider plugins locally

### Challenge 2: Provider version mismatches
**Solution:** Used working versions (3.0.2 for kreuzwerker/docker)

### Challenge 3: Pulumi Python environment
**Solution:** Used `py` command instead of `python` and manually created venv

---

## Lab 5 Preparation

**VM Status:** Keeping Terraform container for Lab 5
- Container: `devops-lab-container`
- SSH: `ssh -p 2222 root@localhost`
- Password: `password`

**Alternative:** Container can be recreated using Terraform code if destroyed

---

## Cleanup

```bash
# Destroy Terraform resources
cd terraform
terraform destroy -auto-approve

# Destroy Pulumi resources
cd ../pulumi
pulumi destroy
```

---

## Conclusion

This lab demonstrated Infrastructure as Code using both Terraform and Pulumi. Despite initial challenges with provider access, both tools successfully created equivalent infrastructure. Terraform's declarative HCL is simpler for straightforward infrastructure, while Pulumi's Python approach offers more flexibility for complex scenarios. Both tools are valuable in a DevOps toolkit.