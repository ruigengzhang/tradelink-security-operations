# Analyst playbook — TL-IR-001

## Hypothesis

A supplier account is accessed from an unfamiliar source after repeated failures. The same principal subsequently attempts blocked cross-tenant order access, executes a large synthetic export and receives an unapproved administrator role.

## Hands-on investigation

1. Run `tradelink-soc` and inspect `outputs/alerts.json`. Decide which two alerts deserve immediate triage.
2. Search `outputs/events.jsonl` for the earliest suspicious event and preceding legitimate login.
3. Explain why HTTP 403 suggests attempted IDOR rather than confirmed successful IDOR.
4. Explain why `data_export` does not by itself establish external network exfiltration.
5. Propose containment actions and assess business disruption.
6. Tune one detector to reduce a plausible false positive and add a regression test.
7. Compare your narrative with the generated `outputs/incident-report.md`.

## Interview questions

- What is the difference between an anomaly, a detection and a confirmed incident?
- Why can a novel source IP be benign?
- How do authorization enforcement and alerting differ?
- Which raw evidence would you preserve before disabling an account?
- What would it take to productionize this detection in Elastic Security or Sentinel?
