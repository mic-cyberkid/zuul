# Zuul Security Audit: Local Reproduction Guide

This guide provides instructions on how to set up a local Zuul environment using Docker and execute the identified exploits using Python.

## 1. Environment Setup

We provide a Dockerized setup that includes the Zuul Gateway and a mock backend service.

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ with `requests`

### Step 1: Start the Environment
```bash
# From the repository root
cd zuul-docker
docker-compose up --build
```
This will start:
- **Zuul Gateway:** `http://localhost:7001`
- **Push Messaging:** `http://localhost:7008`
- **Mock Backend:** `http://localhost:8080` (Internal to Docker: `backend:8080`)

### Step 2: Verify Setup
The Gateway is configured to route all traffic to the mock backend.
```bash
curl http://localhost:7001/any-path
# Should return "Backend Response: OK"
```

---

## 2. Python-Based Exploit PoCs

All PoCs are located in the `pocs/zuul/` directory.

### Exploit 1: CRLF Injection / Request Smuggling (ZUUL-01)
**Script:** `pocs/zuul/exploit_crlf_smuggling.py`
Demonstrates injecting a second request via CRLF in headers. Check the `zuul-docker` logs to see multiple requests reaching the backend.

### Exploit 2: Path Normalization ACL Bypass (ZUUL-03)
**Script:** `pocs/zuul/exploit_path_bypass.py`
Demonstrates bypassing filters using double-encoded dots (`%252e%252e`).

### Exploit 3: Push Messaging Auth Bypass (ZUUL-04)
**Script:** `pocs/zuul/exploit_push_auth_bypass.py`
Demonstrates sending push messages without the mandatory secure token.

---

## 3. Running the Exploits

```bash
# Install requirements
pip install requests

# Run CRLF Injection
python pocs/zuul/exploit_crlf_smuggling.py

# Run ACL Bypass
python pocs/zuul/exploit_path_bypass.py

# Run Push Auth Bypass
python pocs/zuul/exploit_push_auth_bypass.py
```
