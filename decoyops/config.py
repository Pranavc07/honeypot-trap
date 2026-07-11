"""Central configuration for decoyops."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# --- Database ---
DB_PATH = os.environ.get("DECOYOPS_DB_PATH", str(BASE_DIR / "decoyops.sqlite3"))

# --- canarytokens.org ---
CANARYTOKENS_API_BASE = os.environ.get("CANARYTOKENS_API_BASE", "https://canarytokens.org")
CANARYTOKENS_AUTH_TOKEN = os.environ.get("CANARYTOKENS_AUTH_TOKEN", "")

# Public URL this app is reachable at, used when registering the webhook
# with canarytokens.org so it knows where to POST alerts.
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
