"""FastAPI route that canarytokens.org POSTs to when a minted key fires."""
from fastapi import FastAPI, Request

import config
import store

app = FastAPI(title="decoyops webhook receiver")


@app.on_event("startup")
def startup():
    store.init_db()


@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()

    token_id = payload.get("canarytoken") or payload.get("token")
    source_ip = payload.get("src_ip") or request.headers.get("x-forwarded-for", "")

    store.record_usage_event(
        token_id=token_id,
        source_ip=source_ip,
        raw_payload=str(payload),
    )

    return {"status": "recorded"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.WEBHOOK_RECEIVER_HOST, port=config.WEBHOOK_RECEIVER_PORT)
