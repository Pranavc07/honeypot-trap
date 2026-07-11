"""Joins harvest_events and usage_events into incidents.

An incident is: a token was harvested by some visitor (harvest_event),
and later that same token fired (usage_event) — meaning whoever scraped
the bait file actually tried to use the leaked credential.
"""
import store


def find_incidents():
    """Return a list of incidents: harvest + subsequent usage of the same token."""
    with store.get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                h.token_id,
                h.bait_path,
                h.served_at,
                v.ip_address AS harvester_ip,
                v.user_agent AS harvester_user_agent,
                u.source_ip AS user_ip,
                u.fired_at,
                u.raw_payload
            FROM harvest_events h
            JOIN visitors v ON v.id = h.visitor_id
            JOIN usage_events u ON u.token_id = h.token_id
            WHERE u.fired_at >= h.served_at
            ORDER BY h.served_at ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def print_incidents():
    incidents = find_incidents()
    if not incidents:
        print("No incidents found.")
        return

    for incident in incidents:
        print(
            f"[{incident['fired_at']}] token {incident['token_id']} "
            f"harvested from {incident['harvester_ip']} via {incident['bait_path']} "
            f"at {incident['served_at']}, used from {incident['user_ip']}"
        )


if __name__ == "__main__":
    print_incidents()
