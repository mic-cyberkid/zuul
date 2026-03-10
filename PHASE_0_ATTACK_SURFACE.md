# Phase 0 — Attack Surface Mapping

## Registered Filters

### Inbound Filters
- `com.netflix.zuul.filters.common.SurgicalDebugFilter`: High-risk if it allows arbitrary debug routing.
- `com.netflix.zuul.filters.passport.InboundPassportStampingFilter`: Passport/Identity handling.
- `com.netflix.zuul.sample.filters.inbound.Routes`: Primary routing logic in the sample.
- `com.netflix.zuul.sample.filters.inbound.DebugRequest`: Logs request details.
- `com.netflix.zuul.sample.filters.inbound.SampleServiceFilter`: Demonstrates service integration.
- `com.netflix.zuul.sample.filters.Debug`: Generic debug filter.

### Endpoint Filters
- `com.netflix.zuul.filters.endpoint.ProxyEndpoint`: Core proxying logic to origins.
- `com.netflix.zuul.filters.endpoint.MissingEndpointHandlingFilter`: 404 handler.
- `com.netflix.zuul.sample.filters.endpoint.Healthcheck`: Local healthcheck endpoint.

### Outbound Filters
- `com.netflix.zuul.filters.common.GZipResponseFilter`: Response compression.
- `com.netflix.zuul.filters.passport.OutboundPassportStampingFilter`: Passport/Identity handling.
- `com.netflix.zuul.sample.filters.outbound.ZuulResponseFilter`: Sample response modification.

## Routing Rules

### Static & Dynamic Routing
- `zuul-sample/src/main/java/com/netflix/zuul/sample/filters/inbound/Routes.java`:
    - Path `/healthcheck` (case-insensitive) -> `com.netflix.zuul.sample.filters.endpoint.Healthcheck`.
    - All other paths -> `com.netflix.zuul.filters.endpoint.ProxyEndpoint` with `context.setRouteVIP("api")`.

## Netty Pipeline Configuration

The pipeline is initialized in `BaseZuulChannelInitializer` and `ZuulServerChannelInitializer`:

1.  **Timeouts**: `IdleStateHandler`, `CloseOnIdleStateHandler`.
2.  **Passport**: `ServerStateHandler.InboundHandler`, `ServerStateHandler.OutboundHandler`.
3.  **TCP/Metrics**: `SourceAddressChannelHandler`, `ElbProxyProtocolChannelHandler` (optional), `MaxInboundConnectionsHandler`.
4.  **HTTP/1.1 Codec**: `HttpServerCodec`.
5.  **Connection Management**: `Http1ConnectionCloseHandler`, `Http1ConnectionExpiryHandler`.
6.  **HTTP Related**: `HttpHeadersTimeoutHandler.InboundHandler`, `PassportStateHttpServerHandler`, `HttpRequestReadTimeoutHandler`, `HttpServerLifecycleChannelHandler`, `HttpBodySizeRecordingChannelHandler`, `HttpMetricsChannelHandler`.
7.  **Access Logs**: `AccessLogChannelHandler`.
8.  **Security**: `StripUntrustedProxyHeadersHandler`, `RateLimitingChannelHandler` (if provided).
9.  **Zuul Core**:
    - `ClientRequestReceiver`: Converts Netty `HttpRequest` to Zuul `HttpRequestMessage`.
    - `ZuulFilterChainHandler`: Executes the filter chain.
    - `ClientResponseWriter`: Converts Zuul `HttpResponseMessage` to Netty `HttpResponse`.

## Archaius Configurations

Found in `zuul-sample/src/main/resources/application.properties`:
- `zuul.filters.packages`: Defines which packages are scanned for filters.
- `eureka.name=zuul`, `eureka.port=7001`.
- `api.ribbon.NIWSServerListClassName`: Configures the server list for the `api` VIP.
- `server.http.decoder.maxInitialLineLength`: 16384.
- `server.http.decoder.maxHeaderSize`: 32768.
- `server.http.decoder.maxChunkSize`: 32768.
