# honeypot-trap (decoyops)

A small honeypot that plants fake credential files (`.env`, `~/.aws/credentials`) at
paths attackers commonly scan for, embeds a real [canarytokens.org](https://canarytokens.org)
AWS key in each one, and correlates who *scraped* the bait with who later *used* the
leaked credential.

## How it works

1. `bait_server.py` serves fake credential files on scan-bait paths and mints a canary
   token per visitor via `canary_client.py`.
2. Each visit is logged in SQLite (`store.py`) as a `harvest_event`.
3. If the leaked key is ever used anywhere, canarytokens.org POSTs to
   `webhook_receiver.py`, logged as a `usage_event`.
4. `correlate.py` joins the two into incidents: scanner IP → token → user IP.

## Project layout

```
decoyops/
├── canary_client.py         # mint_aws_key() — wraps canarytokens.org
├── store.py                 # SQLite: visitors, tokens, harvest_events, usage_events
├── bait_server.py           # FastAPI app serving fake credential files on scan-bait paths
├── webhook_receiver.py      # FastAPI route that canarytokens.org POSTs to when a key fires
├── correlate.py             # joins harvest_events + usage_events into incidents
├── templates/
│   ├── env.fake              # fake .env template
│   └── aws_credentials.fake  # fake ~/.aws/credentials template
├── config.py
└── requirements.txt
```

## Status

Work in progress — built as a learning project.
