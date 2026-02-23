# Chainlink Security Audit: Local Reproduction Guide

This guide provides instructions on how to set up a local Chainlink environment and execute the identified exploits using Python.

## 1. Environment Setup

The most reliable way to run a "real" Chainlink node for testing is via Docker.

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ with `requests`, `eth-account`, and `PyJWT`

### Step 1: Create a `docker-compose.yaml`
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: chainlink
    ports:
      - "5432:5432"

  node:
    image: smartcontract/chainlink:latest
    environment:
      - ROOT=/chainlink
      - LOG_LEVEL=debug
      - ETH_URL=ws://host.docker.internal:8545 # Use a local simulator like Anvil if needed
      - ETH_CHAIN_ID=1337
      - DATABASE_URL=postgresql://postgres:password@db:5432/chainlink?sslmode=disable
      - PASSWORD_ASSETS_DIR=/chainlink
    ports:
      - "6688:6688"
    depends_on:
      - db
```

### Step 2: Configure and Start
1. Create `api` and `password` files for the node's initial credentials.
2. Run `docker-compose up -d`.
3. Log into the UI at `http://localhost:6688` to verify the node is running.

---

## 2. Python-Based Exploit PoCs

All PoCs are located in the `pocs/chainlink/` directory.

### Exploit 1: JWT Replay Race (CL-01)
**Script:** `pocs/chainlink/exploit_jwt_race.py`
This script uses concurrent threads to send the same valid JWT trigger request to the Gateway.

### Exploit 2: CORS Wildcard Bypass (CL-02)
**Script:** `pocs/chainlink/exploit_cors_bypass.py`
This script demonstrates how an unauthorized origin (e.g., `attackerethereum.org`) can bypass a wildcard policy (`*.ethereum.org`).

### Exploit 3: Unauthenticated Task Resumption (CL-03)
**Script:** `pocs/chainlink/exploit_unauth_resume.py`
This script demonstrates that any task ID can be resumed without authentication.

---

## 3. Running the Exploits

First, install dependencies:
```bash
pip install requests eth-account PyJWT
```

Then, run any of the scripts:
```bash
python pocs/chainlink/exploit_cors_bypass.py
```
