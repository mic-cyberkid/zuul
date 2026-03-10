# Phase 2 — Taint Analysis

## Taint Flows from Untrusted Sources to Sinks

### Header Taint Flow (Inbound -> Outbound)
1.  **Source**: `HttpRequestMessage.getHeaders()` (untrusted input from `ClientRequestReceiver`).
2.  **Processing**: Zuul filters (e.g., `Routes.java`, `ZuulResponseFilter.java`) read or modify headers.
3.  **Sink**: `ClientResponseWriter` writes these headers back to the Netty `HttpResponse` sent to the client.
4.  **Risk**: CRLF injection if headers are not sanitized before being added/set.

### Routing Taint Flow
1.  **Source**: `HttpRequestMessage.getPath()`, `getHeaders()`, `getQueryParams()`.
2.  **Processing**: `Routes.java` (sample) or other inbound filters set `context.setRouteVIP()` or `context.setEndpoint()`.
3.  **Sink**: `ProxyEndpoint` uses these values to determine the origin server and construct the outbound request.
4.  **Risk**: SSRF or routing bypass if an attacker can manipulate these values through headers (e.g., `X-Zuul-Target`) or path traversal.

### URI Reconstruction Taint Flow
1.  **Source**: `HttpRequestMessage.getPath()`, `getQueryParams()`.
2.  **Processing**: `ProxyEndpoint.massageRequestURI` can use `context.get("overrideURI")` or `context.get("requestURI")` if set by a filter.
3.  **Sink**: `ProxyEndpoint` calls `request.reconstructURI()` which is used for logging and by some origin implementations.
4.  **Risk**: SSRF if `overrideURI` is derived from untrusted input.

## Filter Chain State Taint

- `SessionContext` acts as a repository for tainted data that persists across the filter chain.
- A vulnerability in an early filter (e.g., setting a sensitive context key based on a header) can be exploited by a later filter that trusts that key.
