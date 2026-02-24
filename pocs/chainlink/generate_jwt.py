import jwt
import time
import uuid
import sys
from eth_account import Account
from eth_account.messages import encode_defunct

def generate_chainlink_jwt(private_key_hex, request_digest):
    account = Account.from_key(private_key_hex)

    # Payload matching Chainlink's expectations
    payload = {
        "digest": request_digest,
        "jti": str(uuid.uuid4()),
        "iss": account.address,
        "iat": int(time.time()),
        "exp": int(time.time()) + 300
    }

    # Chainlink uses a custom 'ETH' algorithm which is essentially an Ethereum signature
    # However, for simplicity in PoC, if the Gateway is configured to use standard JWT libs
    # it might use ES256K.
    # NOTE: The real Chainlink code uses utils.VerifyRequestJWT which recovers the address from the signature.

    # Header: {"alg": "ETH", "typ": "JWT"}
    # The 'ETH' algorithm is not standard in PyJWT, so we manually sign the data.

    import json
    import base64

    header = {"alg": "ETH", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')

    signing_input = f"{header_b64}.{payload_b64}"

    # Sign with Ethereum
    message = encode_defunct(text=signing_input)
    signed_message = account.sign_message(message)
    signature_b64 = base64.urlsafe_b64encode(signed_message.signature).decode().rstrip('=')

    token = f"{signing_input}.{signature_b64}"
    return token

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_jwt.py <private_key_hex> <request_digest_hex>")
        sys.exit(1)

    print(generate_chainlink_jwt(sys.argv[1], sys.argv[2]))
