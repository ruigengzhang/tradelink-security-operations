"""Transparent rule-based detection engine over synthetic ECS-like events."""
from collections import defaultdict
from datetime import datetime, timedelta


def timestamp(e):
    return datetime.fromisoformat(e["@timestamp"].replace("Z", "+00:00"))


def alert(rule_id, severity, description, evidence, subject):
    return {"rule_id": rule_id, "severity": severity, "description": description,
            "user": subject, "event_ids": sorted(set(evidence)), "evidence_count": len(set(evidence))}


def detect(events: list[dict]) -> list[dict]:
    """Five types: brute force, unfamiliar successful login, IDOR, mass export, privilege escalation."""
    ordered = sorted(events, key=timestamp)
    result = []
    by_user_ip = defaultdict(list)
    for e in ordered:
        if e["event"]["action"] == "login_failure":
            by_user_ip[(e["user"]["name"], e["source"]["ip"])].append(e)
    for (user, ip), failures in by_user_ip.items():
        # Sliding 10-min window; emit at most one alert per principal / IP pair.
        for i, start in enumerate(failures):
            hit = [x for x in failures[i:] if timestamp(x)-timestamp(start) <= timedelta(minutes=10)]
            if len(hit) >= 5:
                result.append(alert("TL-001", "high", f"5+ login failures/10m from {ip}",
                                    [x["event"]["id"] for x in hit], user))
                break

    # Novelty baseline from prior successful logins for a principal, not just a hardcoded IP.
    seen_success_ip = defaultdict(set)
    for e in ordered:
        user, ip, action = e["user"]["name"], e["source"]["ip"], e["event"]["action"]
        if action == "login_success":
            if seen_success_ip[user] and ip not in seen_success_ip[user]:
                result.append(alert("TL-002", "medium", f"Successful login from new source IP {ip}",
                                    [e["event"]["id"]], user))
            seen_success_ip[user].add(ip)

    denied_by_user = defaultdict(list)
    for e in ordered:
        if (e["event"]["action"] == "order_view" and
            e.get("http", {}).get("response", {}).get("status_code") == 403 and
            e.get("order", {}).get("owner") != e["user"]["name"]):
            denied_by_user[e["user"]["name"]].append(e["event"]["id"])
    for user, ids in denied_by_user.items():
        if len(ids) >= 2:
            result.append(alert("TL-003", "high", "Repeated cross-tenant order access denied (IDOR probing)", ids, user))

    for e in ordered:
        user = e["user"]["name"]
        if e["event"]["action"] == "data_export" and e.get("export", {}).get("record_count", 0) >= 500:
            result.append(alert("TL-004", "critical", "Large export of >=500 records", [e["event"]["id"]], user))
        if (e["event"]["action"] == "role_change" and
            e.get("iam", {}).get("new_role") == "admin" and
            e.get("iam", {}).get("approved") is False):
            result.append(alert("TL-005", "critical", "Unapproved admin role assignment", [e["event"]["id"]], user))
    return sorted(result, key=lambda a: a["rule_id"])
