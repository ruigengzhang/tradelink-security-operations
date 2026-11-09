# Detection catalog

These rules are implemented in Python. They are **not** deployed Elastic or Sigma alerts.

| ID | Detection | Trigger | Common false positive |
|---|---|---|---|
| TL-001 | Brute force | >=5 login failures by user/source IP within 10 minutes | Incorrect saved credentials |
| TL-002 | New login source | Successful login from IP not seen in earlier successes for that principal | VPN, travel, ISP change |
| TL-003 | Cross-tenant access attempts | >=2 denied order reads targeting another owner | Stale links or broken client |
| TL-004 | Unusual bulk export | Successful export >=500 records | Legitimate scheduled report |
| TL-005 | Privilege escalation | Admin role assignment with approved=false | Missing change-ticket metadata |

## Investigation workflow

1. Check timestamps, completeness and source quality.
2. Confirm each alert using original evidence IDs.
3. Separate **attempted** access from successful unauthorized disclosure.
4. Correlate an export with storage and network telemetry before calling it confirmed exfiltration.
5. Record containment decision, approval, impact and post-remediation verification.

## Future refinements

Add device/MFA context and a longer baseline for TL-002, approval-ticket evidence for TL-005, tailored export thresholds, entity risk scores and native SIEM detections.
