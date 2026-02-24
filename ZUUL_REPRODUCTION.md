# Zuul Security Audit: Local Reproduction Guide

This guide provides instructions on how to set up a local Zuul environment and execute the identified exploits.

---

## 1. Environment Setup (Standard / Manual)

If you are not using Docker, follow these steps to set up the test environment.

### Prerequisites
- Java 21 (JDK)
- Python 3.9+ with `requests` library

### Step 1: Configure Zuul for Static Routing
To test without a full Eureka/Discovery infrastructure, configure Zuul to route to a local mock backend.
Edit `zuul-sample/src/main/resources/application-test.properties`:

```properties
# Enable static server list for the 'api' VIP
api.ribbon.listOfServers=localhost:8080
api.ribbon.NIWSServerListClassName=com.netflix.loadbalancer.ConfigurationBasedServerList
api.ribbon.eureka.enabled=false

# Push messaging config
zuul.push.http.port=7008
```

### Step 2: Start a Mock Backend
Run a simple Python-based mock backend that logs incoming requests:
```python
# Save as mock_backend.py
from http.server import HTTPServer, BaseHTTPRequestHandler
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"Received Request: {self.path}")
        print(f"Headers: {self.headers}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Mock Backend Response: OK")
HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
```
Run it: `python mock_backend.py`

### Step 3: Build and Start Zuul
```bash
./gradlew :zuul-sample:run
```
Zuul should now be listening on `http://localhost:7001`.

---

## 2. Running the Exploits

All PoC scripts are located in the `pocs/zuul/` directory.

### Exploit 1: CRLF Injection / Request Smuggling (ZUUL-01)
**Script:** `python pocs/zuul/exploit_crlf_smuggling.py`
*   **What it does:** Sends a request with injected CRLFs in headers to smuggle a second request.
*   **Success Criteria:** Check your `mock_backend.py` logs. You should see TWO requests received: the original `/api/v1/resource` and the smuggled `/admin/internal-only`.

### Exploit 2: Path Normalization ACL Bypass (ZUUL-03)
**Script:** `python pocs/zuul/exploit_path_bypass.py`
*   **What it does:** Uses double-encoded dots to bypass path-based filters.
*   **Success Criteria:** If Zuul has an inbound filter blocking `/admin`, this script will show that the request reached the backend regardless.

### Exploit 3: Push Messaging Auth Bypass (ZUUL-04)
**Script:** `python pocs/zuul/exploit_push_auth_bypass.py`
*   **What it does:** Sends a push message without the required secure token.
*   **Success Criteria:** The script will report `200 OK` and "Authentication Bypass Successful".

---

## 3. Common Issues & Troubleshooting

- **ClassCastException:** If you see a `ClassCastException` related to `DiscoveryEnabledServer`, ensure you have applied the patch to `DiscoveryResult.java`.
- **Port Conflicts:** Ensure ports 7001, 7008, and 8080 are free before starting.
- **LoadBalancer Misconfiguration:** If Zuul returns a 502, check its logs for "current list of Servers". It should only contain `localhost:8080`. If it contains other ports (like 80 or 7001), it might be picking the wrong one. Add `api.ribbon.eureka.enabled=false` to your properties.
