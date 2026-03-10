# Phase 7 — Deserialization Audit

## Java Deserialization (`ObjectInputStream`)

A thorough search of the codebase was conducted for the use of `ObjectInputStream.readObject()`.

**Findings**: No instances of native Java deserialization were found in the `zuul-core` or `zuul-sample` modules.

## Jackson JSON Deserialization

The project uses Jackson for JSON processing.

### Polymorphic Type Handling
A search for `@JsonTypeInfo` and `ObjectMapper.enableDefaultTyping()` was performed.

**Findings**:
- No usage of `@JsonTypeInfo` was found.
- `ObjectMapper.enableDefaultTyping()` is not used.

### `ObjectMapper` Usage
`ObjectMapper` is used in:
- `com.netflix.zuul.niws.RequestAttempt`
- `com.netflix.zuul.niws.RequestAttempts`

In both cases, it is primarily used for **serialization** to JSON (via `toJSON()` methods). There is no evidence of deserializing untrusted JSON into complex object graphs with attacker-controlled types.

## Conclusion

The risk of insecure deserialization in the current version of Zuul (based on the analyzed source code) is **Low**. The project avoids native Java deserialization and does not appear to use dangerous Jackson configurations.
