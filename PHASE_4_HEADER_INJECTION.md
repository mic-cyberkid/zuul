# Phase 4 — Response Splitting & Header Injection

## Analysis of Outbound Header Manipulation

### `Headers.java` Validation
- `Headers.java` provides `setAndValidate` and `addAndValidate` methods which use `validateField` to check for invalid characters (ASCII < 31 or 127).
- `validateField` effectively blocks CRLF (`\r\n` or `0x0D0A`) as they are ASCII control characters.

**Risk**: Most filters and core components use the standard `set()` and `add()` methods, which **do not** perform this validation.

### `ZuulResponseFilter.java` (Sample)
- Uses `headers.set(X_ORIGINATING_URL, response.getInboundRequest().reconstructURI())`.
- `reconstructURI()` includes the `getPathAndQuery()`.
- If a client sends a request with CRLF in the query string, and the origin doesn't strip it, it could reach this sink.
- `HttpRequestMessageImpl.generatePathAndQuery` uses `queryParams.toEncodedString()`, which should URL-encode CRLF. However, if the `path` itself contains CRLF (and isn't properly normalized or rejected by Netty), it could be injected.

### `OriginResponseReceiver`
- Copies all headers from the origin response to the Zuul response using `nettyReq.headers().add(h.getKey(), h.getValue())`.
- This is a common pattern that trusts the origin. If an origin is compromised or susceptible to header injection, Zuul will propagate it.

### `ClientResponseWriter`
- Final stage of writing headers to the client. Uses `nativeHeaders.add(entry.getKey(), entry.getValue())`.
- No additional validation is performed at this stage in Zuul.

## CRLF Injection / Response Splitting Risk

The primary risk is when untrusted data from the request (headers, path, query) or the origin response is used to set headers on the final response sent to the client.

- **Direct Injection**: If a filter takes a header from the request and sets it on the response without sanitization.
- **`X-Originating-URL`**: As noted above, this header is a prime candidate if the path reconstruction logic doesn't properly sanitize the input.

## Mitigation in Zuul

Zuul has the tools (`setAndValidate`) to prevent this, but they are not used consistently in the sample or core filters.
