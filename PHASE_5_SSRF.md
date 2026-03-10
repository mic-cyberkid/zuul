# Phase 5 — SSRF & Routing Abuse

## Routing Mechanism in Zuul

Routing in Zuul is primarily controlled by the `SessionContext` keys:
- `routeVIP`: The Eureka VIP address used to find the origin server(s).
- `routeHost`: A direct URL to the origin server (bypassing Discovery).
- `overrideURI`: An optional URI to override the inbound path and query string.
- `requestURI`: Another optional key for the URI.

## SSRF Analysis

### `ProxyEndpoint.getOrigin()`
1.  Retrieves `routeVIP` from `SessionContext`.
2.  Optionally calls `injectCustomOriginName(request)` for an override.
3.  Calls `getOrCreateOrigin(originManager, originName, request.reconstructURI(), context)`.
4.  `originManager` resolves the VIP to a list of servers.

**Risk**: If an inbound filter sets `routeVIP` or `routeHost` based on untrusted input (e.g., a header like `X-Zuul-Target`), it could lead to SSRF. In the sample `Routes.java`, the VIP is hardcoded to `api`, which is safe.

### `ProxyEndpoint.massageRequestURI()`
- If `context.get("requestURI")` or `context.get("overrideURI")` is set, it overrides the `request` path and query parameters.
- These overrides are then used by `request.reconstructURI()`.

**Risk**: If a filter sets `overrideURI` to an absolute URL based on user input, and the downstream origin uses the reconstructed URI for sensitive operations, it could be exploited.

## Potential for Routing Abuse

- **`SurgicalDebugFilter`**: This filter can route requests to a debug VIP or host specified by `zuul.debug.vip` or `zuul.debug.host`. While these are static properties, if they were to be influenced by request state, it would be a high-risk area.
- **Path Traversal -> Routing Bypass**: If an attacker can bypass path normalization in `ClientRequestReceiver` (Phase 1) and reach a routing filter that matches on path, they might trigger unintended routing rules.

## Internal Metadata Manipulation

Filters often use `SessionContext` to store internal state. If an attacker can "poison" this state (e.g., by sending a header that is blindly copied to the context), they might influence routing decisions in later filters.
