"""FastAPI app that serves fake credential files on scan-bait paths.

Each request for a bait path mints/reuses a canary token, templates it
into the fake file, and logs the visitor + harvest event so it can later
be correlated with a usage_event if the leaked credential is ever used.
"""
from fastapi import FastAPI, Request, Response

import config
import store
from canary_client import mint_aws_key

app = FastAPI(title="decoyops bait server")


@app.on_event("startup")
def startup():
    store.init_db()


def render_bait_file(template_name: str, token: dict) -> str:
    template_path = config.TEMPLATES_DIR / template_name
    content = template_path.read_text(encoding="utf-8")
    content = content.replace("{{TOKEN_ID}}", token["token_id"])
    content = content.replace("{{AWS_ACCESS_KEY_ID}}", token["aws_access_key_id"])
    content = content.replace("{{AWS_SECRET_ACCESS_KEY}}", token["aws_secret_access_key"])
    content = content.replace("{{DB_PASSWORD}}", "changeme")
    content = content.replace("{{SECRET_KEY}}", token["token_id"])
    return content


def register_bait_route(path: str, template_name: str):
    @app.get(path, name=f"bait_{template_name}")
    async def serve_bait(request: Request):
        token = mint_aws_key(memo=f"decoyops:{path}")
        store.record_token(token["token_id"], token["auth_token"], "aws_keys", path)

        visitor_id = store.upsert_visitor(
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", ""),
        )
        store.record_harvest_event(visitor_id, token["token_id"], path)

        body = render_bait_file(template_name, token)
        return Response(content=body, media_type="text/plain")


for bait_path, template in config.BAIT_PATHS.items():
    register_bait_route(bait_path, template)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.BAIT_SERVER_HOST, port=config.BAIT_SERVER_PORT)
