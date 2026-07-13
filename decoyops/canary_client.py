"""Client for canarytokens.org's /generate endpoint.

AWS-keys tokens are minted through Thinkst's proprietary AWS backend
(AWSID_URL/AWSID_AUTH in their frontend settings), which isn't available on
self-hosted instances -- so this targets the public canarytokens.org
instance specifically. /generate is unauthenticated; the only prerequisite
is that WEBHOOK_PUBLIC_URL already resolves and returns 2xx, since the
server test-pings it before issuing a token.
"""
import requests

import config

GENERATE_ENDPOINT = f"{config.CANARYTOKENS_API_BASE}{config.CANARYTOKENS_API_PREFIX}/generate"


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
