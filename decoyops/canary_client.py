"""Client wrapper around canarytokens.org for minting canary tokens.

Status: in progress.
"""
import requests

import config

CREATE_TOKEN_ENDPOINT = f"{config.CANARYTOKENS_API_BASE}/generate"


def mint_aws_key(memo: str) -> dict:
    """Mint a fake AWS key canary token via canarytokens.org.

    TODO: confirm the exact request payload canarytokens.org expects for
    the aws-keys token type (their API isn't fully documented; may need
    to reverse-engineer from the web form submission).
    TODO: handle rate limiting / retries.
    TODO: validate response schema before returning.
    """
    payload = {
        "type": "aws_keys",
        "memo": memo,
        "webhook_url": config.WEBHOOK_PUBLIC_URL,
    }
    response = requests.post(CREATE_TOKEN_ENDPOINT, data=payload, timeout=10)
    response.raise_for_status()
    data = response.json()

    # TODO: canarytokens.org's response shape needs verifying against a
    # real account/token before this mapping can be trusted.
    return {
        "token_id": data.get("token"),
        "aws_access_key_id": data.get("aws_access_key_id"),
        "aws_secret_access_key": data.get("aws_secret_access_key"),
    }


def mint_token(token_type: str, memo: str) -> dict:
    """Generic entrypoint for other token types (not yet implemented).

    TODO: support additional token types (DNS, web bug, doc, etc.)
    """
    raise NotImplementedError(f"token type not yet supported: {token_type}")
