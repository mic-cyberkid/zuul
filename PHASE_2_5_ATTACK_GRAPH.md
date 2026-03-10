# Phase 2.5 — Attack Graph Construction

## Request Lifecycle & Attack Graph

### 1. Inbound Stage (Entry Points)
- **Netty `HttpServerCodec`**: First stage of decoding the raw HTTP stream. Vulnerable to Smuggling (Phase 3).
- **`ClientRequestReceiver`**: Entry point for Zuul. Transforms Netty `HttpRequest` to `HttpRequestMessage`. Vulnerable to Path Normalization Bypass (Phase 1).
- **Inbound Filter Chain**:
    - `InboundPassportStampingFilter`: Identity/Passport initialization.
    - `Routes.java` (sample): **Privilege Node**. Sets `RouteVIP` and `Endpoint`. Vulnerable to Routing Abuse/SSRF (Phase 5).
    - `SurgicalDebugFilter`: **Privilege Node**. Can override routing based on debug headers/properties.

### 2. Endpoint Stage (Processing & Logic)
- **`ZuulEndPointRunner`**: Dispatches the request to the selected endpoint.
- **`Healthcheck`** (sample): Local endpoint. No outbound network activity.
- **`ProxyEndpoint`**: **Sink Node**. Construction of outbound request.
    - `massageRequestURI()`: **Taint Sink**. Processes path and query overrides.
    - `getOrigin()`: **Taint Sink**. Resolves the origin server using the `OriginManager` and the assigned `RouteVIP`.
    - `connectToOrigin()`: **Taint Sink**. Initiates the connection to the origin server.

### 3. Outbound Stage (Egress)
- **`OriginResponseReceiver`**: Receives response from the origin.
- **Outbound Filter Chain**:
    - `ZuulResponseFilter.java`: **Taint Sink**. Modifies headers based on `SessionContext`. Vulnerable to CRLF Injection (Phase 4).
    - `GZipResponseFilter`: Compression logic.
- **`ClientResponseWriter`**: **Sink Node**. Final conversion back to Netty `HttpResponse` and writing to the client channel.

### 4. Attack Impact Nodes
- **Origin SSRF**: Achieved by manipulating routing logic (Phase 5) to point the `ProxyEndpoint` to an arbitrary internal/external host.
- **Request Smuggling**: Achieved by desynchronizing the Netty `HttpServerCodec` and the origin's HTTP parser (Phase 3).
- **Response Splitting**: Achieved by injecting CRLF sequences into response headers (Phase 4).
- **Auth/ACL Bypass**: Achieved by bypassing security filters (Phase 6) or exploiting state poisoning in `SessionContext`.
