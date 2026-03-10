# Phase 1 — Input Source Mapping

## Attacker-Controlled Inputs in `HttpRequestMessage`

- **Headers**: All incoming HTTP headers are accessible via `getHeaders()`.
- **Query Parameters**: Accessible via `getQueryParams()`.
- **Path**: The request URI path is accessible via `getPath()`.
- **Decoded Path**: `HttpRequestMessageImpl` provides a `decodedPath` which is the URL-decoded version of the path.
- **Body**: The request body is accessible as text or bytes.
- **Cookies**: Parsed from the `Cookie` header.
- **Method**: The HTTP method (GET, POST, etc.).
- **Protocol**: The HTTP protocol version (HTTP/1.1, HTTP/2).

## Population from Netty `HttpRequest`

The `ClientRequestReceiver.buildZuulHttpRequest` method populates the `HttpRequestMessage` as follows:

- **Headers**: Copied from Netty `HttpRequest.headers()` using `copyHeaders`.
- **Query Parameters**: Extracted from Netty `HttpRequest.uri()` using `copyQueryParams` (delegates to `HttpQueryParams.parse`).
- **Path**: Extracted from Netty `HttpRequest.uri()` and normalized using `parsePath`.
- **Client IP**: Obtained from the Netty `Channel`.
- **Scheme**: Determined based on whether SSL is used.
- **Port/Server Name**: Obtained from the Netty `Channel`.
- **Body**: If it's a `FullHttpRequest`, the content is buffered into the `HttpRequestMessage`. Otherwise, subsequent `HttpContent` chunks are buffered as they arrive.

## Path Normalization Logic (`ClientRequestReceiver.parsePath`)

The logic for path normalization is:
1.  Try to parse and normalize using `java.net.URI`.
2.  If `URI.getRawPath()` is null, return the original URI.
3.  Manually remove leading `/..` sequences.
4.  If `java.net.URI` fails, manual path parsing is used (handling absolute and relative URIs).
5.  Remove query string if still present.
6.  Again, manually remove leading `/..` sequences.

**Potential Vulnerability**: The manual removal of `/..` only handles the *beginning* of the path. Mid-path traversal (e.g., `/foo/../bar`) is handled by `java.net.URI.normalize()`, but if that fails or is bypassed (e.g., via encoding), the manual logic might be insufficient.

## `SessionContext` State

`SessionContext` is a `HashMap` that stores request-specific state. It can be influenced by:
- **`SessionContextDecorator`**: Allows custom logic to populate the context.
- **Filters**: Any filter can read/write to the context, potentially based on untrusted input.
- **Common Context Keys**: Like `REWRITE_URI`, `ZUUL_USE_DECODED_URI`, etc.
