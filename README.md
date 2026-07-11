# honeypot-trap (decoyops)

A honeypot that plants fake credential files (`.env`, `~/.aws/credentials`) at paths
attackers commonly scan for. Each file embeds a real AWS canary token minted from a
[canarytokens](https://github.com/thinkst/canarytokens) server — a decoy credential
that's silently monitored, so using it anywhere triggers an alert. decoyops logs who
*scraped* the bait and correlates it with who later *used* the leaked key, turning a
single "someone scanned me" alert into scanner IP → credential → user IP attribution.

> Built as a learning project for defensive security / detection engineering. Only
> deploy this against infrastructure you own or are authorized to monitor.

## How it works

```
 attacker/scanner                 decoyops                     canarytokens server
────────────────────         ───────────────────           ────────────────────────
 GET /.env            ──────▶  bait_server.py
                                  │
                                  ├─ mint_aws_key() ────────▶  POST /generate
                                  │                       ◀── {token, keys, auth_token}
                                  ├─ store harvest_event
                                  │  (visitor, token_id)
                                  ◀── fake .env with the
                                      real decoy AWS key

 (same or different actor tries the leaked key against real AWS, days/weeks later)

                                                               CloudTrail sees the
                                                               decoy key used
                                                                     │
                              webhook_receiver.py  ◀────────────────┘
                                  │                    POST /webhook {token, src_ip, time}
                                  └─ store usage_event

 correlate.py  ──  joins harvest_events + usage_events on token_id  ──▶  incident report
```

1. **`bait_server.py`** serves fake credential files on scan-bait paths (`/.env`,
   `/.aws/credentials`). On each hit it mints a fresh canary token via
   `canary_client.py`, templates it into the fake file, and logs the visitor.
2. **`canary_client.py`** wraps a canarytokens server's `POST /generate` — the same
   unauthenticated endpoint the public canarytokens.org web form uses. It returns a
   real (but decoy) AWS access key/secret plus the token's id and management auth token.
3. **`store.py`** is the SQLite event log: `visitors`, `tokens`, `harvest_events`
   (bait served), `usage_events` (key used).
4. **`webhook_receiver.py`** is the endpoint the canarytokens server calls when a
   minted key gets used anywhere. Because canarytokens test-pings this URL and
   requires a 2xx response before it will even mint a token, it must be deployed and
   publicly reachable *before* `bait_server.py` can hand out tokens.
5. **`correlate.py`** joins `harvest_events` and `usage_events` on `token_id` to answer:
   who scraped a bait file, and did they (or anyone) ever try to use what they found?

## Project layout

```
decoyops/
├── canary_client.py         # mint_aws_key() — talks to a canarytokens server
├── store.py                 # SQLite: visitors, tokens, harvest_events, usage_events
├── bait_server.py           # FastAPI app serving fake credential files on scan-bait paths
├── webhook_receiver.py      # FastAPI route the canarytokens server POSTs to when a key fires
├── correlate.py             # joins harvest_events + usage_events into incidents
├── templates/
│   ├── env.fake              # fake .env template
│   └── aws_credentials.fake  # fake ~/.aws/credentials template
├── config.py                 # canarytokens server URL, webhook URL, bait paths, ports
└── requirements.txt
```

## Setup

### 1. A canarytokens server

You need something running `POST /generate`. Either:

- **Self-host** (recommended): run [thinkst/canarytokens](https://github.com/thinkst/canarytokens)
  via their Docker setup, or
- Point `CANARYTOKENS_API_BASE` at `https://canarytokens.org` and use the public instance.

### 2. Install dependencies

```bash
pip install -r decoyops/requirements.txt
```

### 3. Configure

Set environment variables (see `config.py` for the full list and defaults):

| Variable | Purpose |
|---|---|
| `CANARYTOKENS_API_BASE` | Base URL of your canarytokens server |
| `DECOYOPS_WEBHOOK_URL` | Public URL of `webhook_receiver.py` — must be reachable from the internet, not `localhost` |
| `DECOYOPS_DB_PATH` | Path to the SQLite file (default: `decoyops/decoyops.sqlite3`) |
| `BAIT_SERVER_PORT` / `WEBHOOK_PORT` | Ports for the two FastAPI apps |

For local development, expose `webhook_receiver.py` with a tunnel (e.g. `ngrok http 8081`)
and set `DECOYOPS_WEBHOOK_URL` to the tunnel's HTTPS URL — canarytokens refuses
private/internal addresses and validates the URL responds before minting a token.

### 4. Run

```bash
python decoyops/webhook_receiver.py   # start this first
python decoyops/bait_server.py
```

### 5. Read results

```bash
python decoyops/correlate.py
```

## Status

Work in progress — built as a learning project.
