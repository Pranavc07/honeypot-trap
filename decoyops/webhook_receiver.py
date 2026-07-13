"""FastAPI route that canarytokens.org POSTs to when a minted key fires.

Must always return 2xx: canarytokens test-pings this URL with a synthetic
payload before it'll issue a token, and disables the webhook after repeated
non-2xx responses. Neither a malformed body nor an unrecognized token_id
should ever surface as a failure here.
"""
import logging

from fastapi import FastAPI, Request

import config
import store

log = logging.getLogger("decoyops.webhook_receiver")

app = FastAPI(title="decoyops webhook receiver")


@app.on_event("startup")
def startup():
    store.init_db()


@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()

    # canarytokens' "generic" webhook format (channel_output_webhook.py /
    # webhook_formatting.py TokenAlertDetailGeneric): {token, src_ip, time, ...}
    token_id = payload.get("token")
    source_ip = payload.get("src_ip", "")

    if token_id and store.token_exists(token_id):
        store.record_usage_event(
            token_id=token_id,
            source_ip=source_ip,
            raw_payload=str(payload),
        )
    else:
        log.info("Ignoring webhook payload with unrecognized token: %s", payload)

    return {"status": "recorded"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.WEBHOOK_RECEIVER_HOST, port=config.WEBHOOK_RECEIVER_PORT)
