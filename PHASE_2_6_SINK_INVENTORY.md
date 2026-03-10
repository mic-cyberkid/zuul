# Phase 2.6 — Dangerous Sink Inventory

## Network & Routing Sinks

### `ProxyEndpoint.java`
- `originManager.getOrigin(originName, uri, ctx)`: Determines the origin based on `RouteVIP` and `uri`.
- `origin.connectToOrigin(...)`: Initiates a network connection to the resolved origin.
- `zuulRequest.reconstructURI()`: Reconstructs the URI for logging and potentially other uses.

### `NettyOrigin`
- `connectToOrigin(...)`: The actual Netty-based network client bootstrap.

## Header Manipulation Sinks

### `Headers.add(String name, String value)` / `set(String name, String value)`
- Used in `ClientRequestReceiver` to copy headers from Netty `HttpRequest`.
- Used in `OriginResponseReceiver` to copy headers from origin `HttpResponse`.
- Used in `ClientResponseWriter` to add/set headers on the outbound Netty `HttpResponse`.
- Used in various filters (e.g., `ZuulResponseFilter.java`) to modify headers.

### `HttpHeaderNames` / `HttpHeaderValues`
- Constant names used when setting headers, e.g., `Connection`, `Content-Length`, `Transfer-Encoding`.

## File Operations Sinks

### `BaseSslContextFactory.java`
- `new FileInputStream(serverSslConfig.getCertChainFile())`
- `Files.readAllBytes(serverSslConfig.getClientAuthTrustStoreFile())`
- `new FileInputStream(serverSslConfig.getKeyFile())`

**Note**: These are primarily used during initialization for SSL setup.

## Deserialization & Execution Sinks (None Identified in Main Source Tree)

- No usage of `Runtime.getRuntime().exec()`, `ProcessBuilder`, or `ObjectInputStream.readObject()` found in the core or sample source code.
- No usage of script engines or dynamic filter loading from external sources in the sample.
