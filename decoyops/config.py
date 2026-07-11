"""Central configuration for decoyops."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# --- Database ---
DB_PATH = os.environ.get("DECOYOPS_DB_PATH", str(BASE_DIR / "decoyops.sqlite3"))

# --- canarytokens instance ---
# Base URL of a self-hosted canarytokens server (or https://canarytokens.org
# if you'd rather use the public instance). /generate is unauthenticated on
# both, so no API key is needed here.
CANARYTOKENS_API_BASE = os.environ.get("CANARYTOKENS_API_BASE", "http://localhost:8083")

# Public URL webhook_receiver.py is reachable at. canarytokens pings this
# URL and requires a 2xx response *before* it will mint a token, and it
# refuses private/internal addresses -- this must be a real public URL
# (e.g. an ngrok tunnel during local dev) before canary_client.py will work.
WEBHOOK_PUBLIC_URL = os.environ.get("DECOYOPS_WEBHOOK_URL", "https://example.com/webhook")

# --- Bait server ---
BAIT_SERVER_HOST = os.environ.get("BAIT_SERVER_HOST", "0.0.0.0")
BAIT_SERVER_PORT = int(os.environ.get("BAIT_SERVER_PORT", "8080"))

# Paths that serve fake credential files, e.g. scanners/crawlers poking
# around for exposed secrets will find these first.
BAIT_PATHS = {
    "/.env": "env.fake",
    "/.aws/credentials": "aws_credentials.fake",
}

TEMPLATES_DIR = BASE_DIR / "templates"

# --- Webhook receiver ---
WEBHOOK_RECEIVER_HOST = os.environ.get("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_RECEIVER_PORT = int(os.environ.get("WEBHOOK_PORT", "8081"))
