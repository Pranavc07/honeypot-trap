"""Client for a canarytokens server's /generate endpoint.

/generate is unauthenticated on both the public canarytokens.org instance
and a self-hosted one -- the only prerequisite is that WEBHOOK_PUBLIC_URL
already resolves and returns 2xx, since the server test-pings it before
issuing a token.
"""
import requests

import config

GENERATE_ENDPOINT = f"{config.CANARYTOKENS_API_BASE}/generate"


def mint_aws_key(memo: str) -> dict:
    """Mint an AWS-keys canary token and return its identifiers + credentials."""
    payload = {
        "token_type": "aws_keys",
        "memo": memo,
        "webhook_url": config.WEBHOOK_PUBLIC_URL,
    }
    response = requests.post(GENERATE_ENDPOINT, json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()

    return {
        "token_id": data["token"],
        "auth_token": data["auth_token"],
        "aws_access_key_id": data["aws_access_key_id"],
        "aws_secret_access_key": data["aws_secret_access_key"],
        "region": data["region"],
    }
