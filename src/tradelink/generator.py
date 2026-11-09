"""Deterministic *synthetic* marketplace telemetry; no real accounts or attacks."""
from datetime import datetime, timedelta, timezone
import json
import random
from pathlib import Path

BASE = datetime(2026, 10, 19, 9, 0, tzinfo=timezone.utc)


def generate(seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    events = []
    seq = 0

    def add(minutes: int, action: str, user: str, ip: str, outcome: str = "success", **kw):
        nonlocal seq
        seq += 1
        event = {
            "@timestamp": (BASE + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z"),
            "event": {"id": f"evt-{seq:04d}", "action": action, "outcome": outcome,
                      "category": "authentication" if action.startswith("login") else "web"},
            "user": {"name": user}, "source": {"ip": ip},
            "service": {"name": "tradelink-marketplace"},
        }
        event.update(kw)
        events.append(event)

    customers = ["supplier_alpha", "supplier_beta", "buyer_us", "analyst_demo"]
    for i in range(75):
        user = rng.choice(customers)
        ip = "198.51.100." + str(15 + customers.index(user))
        action = rng.choice(["login_success", "order_view", "order_view", "product_search"])
        add(i * 3, action, user, ip, order={"owner": user, "id": f"ORD-{1000+i}"})

    # Credential stuffing against a supplier account (lab-only documentation IP).
    for i in range(9):
        add(240 + i, "login_failure", "supplier_alpha", "203.0.113.77", outcome="failure")
    add(250, "login_success", "supplier_alpha", "203.0.113.77")
    # Unauthorized object access (application returns 403; prevented, not exfiltrated).
    for i in range(3):
        add(253 + i, "order_view", "supplier_alpha", "203.0.113.77", outcome="failure",
            http={"response": {"status_code": 403}}, order={"owner": "supplier_beta", "id": f"ORD-B{i}"})
    # Successful high-volume export (the anomalous event; simulated synthetic records).
    add(258, "data_export", "supplier_alpha", "203.0.113.77",
        export={"record_count": 1500, "dataset": "buyer_contacts_synthetic"})
    # Privilege change without an approved ticket; lab detection checks event context.
    add(260, "role_change", "supplier_alpha", "203.0.113.77",
        iam={"old_role": "supplier", "new_role": "admin", "approved": False})
    return sorted(events, key=lambda e: (e["@timestamp"], e["event"]["id"]))


def write_jsonl(path: str | Path, events: list[dict]):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, sort_keys=True) + "\n")


def read_jsonl(path: str | Path) -> list[dict]:
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
