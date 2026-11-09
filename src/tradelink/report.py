"""Generate a reviewable case report; recommendations are not executed automatically."""
from collections import Counter
from pathlib import Path


def report_markdown(events, alerts):
    counts = Counter(a["severity"] for a in alerts)
    ids = {eid for a in alerts for eid in a["event_ids"]}
    timeline = [e for e in events if e["event"]["id"] in ids]
    timeline.sort(key=lambda e: e["@timestamp"])
    lines = ["# TradeLink — Synthetic Incident Investigation",
             "", "**Case:** TL-IR-001 | **Environment:** Isolated demo / synthetic telemetry",
             "", "## Executive summary", "",
             f"Generated {len(alerts)} rule alerts from {len(events)} simulated events. "
             "This is a lab scenario, not a verified real-world compromise.",
             f"Severity breakdown: {dict(sorted(counts.items()))}.", "",
             "## Alert triage", "",
             "| Rule | Severity | Principal | Evidence | Reason |",
             "|---|---|---|---|---|"]
    for a in alerts:
        lines.append(f"| {a['rule_id']} | {a['severity']} | {a['user']} | "
                     f"{', '.join(a['event_ids'])} | {a['description']} |")
    lines.extend(["", "## Evidence timeline (UTC)", "",
                  "| Timestamp | Event | Principal | Source IP | Outcome |",
                  "|---|---|---|---|---|"])
    for e in timeline:
        lines.append(f"| {e['@timestamp']} | {e['event']['action']} ({e['event']['id']}) | "
                     f"{e['user']['name']} | {e['source']['ip']} | {e['event']['outcome']} |")
    lines += ["", "## Analyst assessment", "",
              "**Hypothesis:** Credentials for `supplier_alpha` were used from an unfamiliar source after failed logins. "
              "Subsequent denied cross-tenant order access, bulk export and unapproved role elevation warrant escalation.",
              "", "**Observed vs inferred:** The export event indicates a completed synthetic data export; "
              "it does not prove transmission to an external destination. 403 responses demonstrate blocked access, "
              "not successful unauthorized disclosure.",
              "", "## Recommended containment and remediation", "",
              "1. Revoke active sessions and reset affected credentials; enforce MFA.",
              "2. Remove unauthorized admin role and review IAM audit trails.",
              "3. Review export authorization, apply rate limits and alert on sensitive bulk exports.",
              "4. Validate server-side tenant ownership checks for all order endpoints.",
              "5. Preserve immutable logs; determine scope, and confirm whether notification is required.",
              "", "## Limitations and follow-up", "",
              "- All users, addresses and records are synthetic; no third-party systems were targeted.",
              "- Source-IP novelty can trigger on travel, VPN or NAT; enrich with device/user context.",
              "- Real incident decisions require verified identity, endpoint, audit and cloud evidence.",
              "- Run regression tests for alerts and examine benign export/role-change cases for false positives.", ""]
    return "\n".join(lines)


def write_report(path, events, alerts):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(report_markdown(events, alerts), encoding="utf-8")
