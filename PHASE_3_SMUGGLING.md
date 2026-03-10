# Phase 3 — Request Smuggling & H2C Analysis

## Netty `HttpServerCodec` Analysis

The `BaseZuulChannelInitializer` configures the `HttpServerCodec` (and `HttpClientCodec` for origins) with the following properties:
- `maxInitialLineLength`: 16384 (Default)
- `maxHeaderSize`: 32768 (Default)
- `maxChunkSize`: 32768 (Default)
- `validateHeaders`: `false` (in `createHttpServerCodec`)

**Risk**: Setting `validateHeaders` to `false` in `HttpServerCodec` can make Netty more lenient during parsing, potentially allowing malformed headers that could be interpreted differently by a more strict backend origin.

## Manual Header Parsing & Validation

### `ClientRequestReceiver`
- **Multiple Host Headers**: Explicitly checks for multiple `Host` headers and rejects with 400 if found. This is a good security measure.
- **Expect: 100-continue**: Handles this header by sending a 100 Continue response and then *removing* the header before proxying.

### `HttpRequestMessageImpl.parseHostHeader`
- Uses `java.net.URI` for host header parsing.
- If `STRICT_HOST_HEADER_VALIDATION` is false (default is true), it falls back to a simple colon split, which might be less secure.

## Request Smuggling Potential (TE.CL, CL.TE)

Zuul's `ProxyEndpoint` streams the request body to the origin. If there's a discrepancy in how Zuul and the origin handle `Transfer-Encoding` vs. `Content-Length`, smuggling could occur.

- **`ZuulMessageImpl.setContentLength`**: When a filter modifies the body as text/bytes, it explicitly removes `Transfer-Encoding` and sets `Content-Length`. This is a safe pattern.
- **`ProxyEndpoint.writeClientRequestToOrigin`**: Directly writes the `HttpRequestMessage` (which contains the original headers unless modified) to the origin channel.

## H2C Analysis

Zuul supports HTTP/2 via `Http2SslChannelInitializer` and `Http2OrHttpHandler`.

**Risk**: If H2C (HTTP/2 Cleartext) upgrade is supported without proper validation, it could lead to smuggling. However, the sample primarily shows SSL-terminated HTTP/2. I need to check if there's any cleartext H2C upgrade handler.

Checking for `HttpServerUpgradeHandler`:
- `grep -r HttpServerUpgradeHandler .`
