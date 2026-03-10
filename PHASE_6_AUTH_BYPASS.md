# Phase 6 — Authentication & ACL Bypass

## Push Messaging Authentication Bypass (CSRF)

### Affected Component
`com.netflix.zuul.netty.server.push.PushAuthHandler`

### Root Cause
The method `isInvalidOrigin(FullHttpRequest req)` performs a flawed validation of the `Origin` header:

```java
protected boolean isInvalidOrigin(FullHttpRequest req) {
    String origin = req.headers().get(HttpHeaderNames.ORIGIN);
    if (origin == null || !origin.toLowerCase(Locale.ROOT).endsWith(originDomain)) {
        logger.error("Invalid Origin header {} in WebSocket upgrade request", origin);
        return true;
    }
    return false;
}
```

The use of `endsWith(originDomain)` without a leading dot or additional checks allows an attacker to bypass this check by using a domain they control that ends with the `originDomain`.

### Exploit Scenario
- **Target Domain**: `.sample.netflix.com` (configured in `SamplePushAuthHandler`)
- **Attacker Domain**: `attacker-sample.netflix.com`
- **Impact**: An attacker can host a malicious page on `attacker-sample.netflix.com` that performs a Cross-Origin WebSocket hijacking attack against Zuul's Push messaging endpoint. Since authentication is often cookie-based (as seen in `SamplePushAuthHandler`), the attacker's request will include the user's cookies, allowing the attacker to establish a push connection on behalf of the user.

## Routing-Based ACL Bypass Potential

### Path Normalization Issues
As documented in Phase 1, `ClientRequestReceiver.parsePath` has limited normalization logic.
- It handles `/..` at the start of the path but relies on `java.net.URI.normalize()` for mid-path traversal.
- If a security filter uses the `path` from `HttpRequestMessage` (which might be the raw path or partially normalized) to make access control decisions, an attacker might bypass it using:
    - Encoded dots/slashes (if Netty's decoder is lenient).
    - Traversal sequences that `java.net.URI` doesn't normalize but the backend origin does.

### State Poisoning in `SessionContext`
- Zuul's security model heavily relies on filters setting state in `SessionContext`.
- If an early, untrusted filter (e.g., one that handles a specific header) can be tricked into setting a "privileged" context key, later security filters might be bypassed.
- No specific instance of this was found in the sample, but it is an inherent risk in the Zuul architecture.
