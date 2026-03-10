# Phase 17 — Final Audit Reports

---

## [Sentinel-01] Cross-Origin WebSocket Hijacking (COSH) in PushAuthHandler

### Title
Cross-Origin WebSocket Hijacking (COSH) via flawed Origin validation in PushAuthHandler

### Severity (CVSS Score)
High (7.5) - CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N

### Exploitability Score (0-10)
8.0

### Bug Bounty Likelihood
High

### Affected Code
- File: `zuul-core/src/main/java/com/netflix/zuul/netty/server/push/PushAuthHandler.java`
- Function: `isInvalidOrigin(FullHttpRequest req)`

### Root Cause
The `isInvalidOrigin` method uses `endsWith(originDomain)` to validate the `Origin` header. This check is insufficient because it doesn't ensure that the origin is a subdomain of `originDomain`. An attacker can use a domain like `attacker.sample.netflix.com` to pass a check for `.sample.netflix.com`.

### Taint Flow
1.  **Source**: `Origin` header from `FullHttpRequest`.
2.  **Processing**: `PushAuthHandler.isInvalidOrigin()` performs a flawed suffix check.
3.  **Sink**: `channelRead0()` proceeds with the WebSocket handshake if the origin is accepted.

### Impact
An attacker can establish a WebSocket connection to the Push messaging service on behalf of a victim user. This allows the attacker to intercept sensitive push notifications intended for the victim.

### Proof of Concept
See `pocs/zuul/push_csrf_poc.py` and `PHASE_15_POCS.md`.

### Patch Recommendation
Use a more robust domain validation logic that checks for exact match or a leading dot:
```java
protected boolean isInvalidOrigin(FullHttpRequest req) {
    String origin = req.headers().get(HttpHeaderNames.ORIGIN);
    if (origin == null) return true;
    String originLower = origin.toLowerCase(Locale.ROOT);
    return !(originLower.equals(originDomain) || originLower.endsWith("." + originDomain));
}
```

---

## [Sentinel-02] CRLF Injection / Response Splitting Risk in Outbound Headers

### Title
Inbound Response Splitting via unsanitized header manipulation

### Severity (CVSS Score)
Medium (6.1) - CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N

### Exploitability Score (0-10)
6.0

### Bug Bounty Likelihood
Medium

### Affected Code
- File: `zuul-core/src/main/java/com/netflix/zuul/message/Headers.java`
- Component: Core and sample outbound filters (e.g., `ZuulResponseFilter.java`).

### Root Cause
While Zuul provides `setAndValidate()` in `Headers.java`, most filters use the standard `set()` method which does not perform CRLF validation. This allows potentially tainted data to be injected into outbound response headers.

### Taint Flow
1.  **Source**: Tainted data in request path or query params.
2.  **Processing**: `HttpRequestMessageImpl.reconstructURI()` includes the tainted path.
3.  **Sink**: `ZuulResponseFilter` calls `headers.set(X_ORIGINATING_URL, reconstructURI())` without validation.

### Impact
Response splitting can be used to perform cross-site scripting (XSS), session hijacking (via `Set-Cookie` injection), or cache poisoning.

### Proof of Concept
See `PHASE_15_POCS.md` (PoC 2).

### Patch Recommendation
Ensure all filters use `setAndValidate()` or `addAndValidate()` when setting headers based on untrusted input. Alternatively, update the standard `set()` and `add()` methods to perform validation by default.

---

## [Sentinel-03] Path Normalization Discrepancy (ACL Bypass)

### Title
ACL/Routing Bypass via path normalization discrepancy

### Severity (CVSS Score)
Medium (5.3) - CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N

### Exploitability Score (0-10)
5.0

### Bug Bounty Likelihood
Medium

### Affected Code
- File: `zuul-core/src/main/java/com/netflix/zuul/netty/server/ClientRequestReceiver.java`
- Function: `parsePath(String uri)`

### Root Cause
The `parsePath` method has limited manual normalization logic. Discrepancies between Zuul's normalization and the backend origin's normalization could lead to security filters being bypassed.

### Taint Flow
1.  **Source**: Malformed URI path (e.g., encoded dots, traversal sequences).
2.  **Processing**: `ClientRequestReceiver.parsePath()` performs incomplete normalization.
3.  **Sink**: Inbound filters perform routing/ACL checks on the resulting path.

### Impact
Attackers might bypass path-based security rules in Zuul and reach restricted endpoints on the origin server.

### Proof of Concept
See `PHASE_14_EXPLOIT_CHAINS.md` (Chain 3).

### Patch Recommendation
Adopt a more rigorous and standardized path normalization library or approach that aligns with common backend servers (like Tomcat or Netty origins). Ensure all security-sensitive path matching is performed on fully normalized and decoded paths.
