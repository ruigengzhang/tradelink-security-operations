"""End-to-end lab CLI (standard library only)."""
import argparse
import json
from pathlib import Path
from .generator import generate, read_jsonl, write_jsonl
from .detections import detect
from .report import write_report


def main():
    parser = argparse.ArgumentParser(description="TradeLink SOC reproducible scenario")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--input", type=Path, help="Use existing newline-delimited JSON telemetry")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    events = read_jsonl(args.input) if args.input else generate(args.seed)
    write_jsonl(out / "events.jsonl", events)
    alerts = detect(events)
    (out / "alerts.json").write_text(json.dumps(alerts, indent=2) + "\n", encoding="utf-8")
    write_report(out / "incident-report.md", events, alerts)
    print(f"Events: {len(events)} | Alerts: {len(alerts)}")
    for a in alerts:
        print(f"{a['rule_id']} {a['severity']}: {a['description']} [{a['user']}]")
    print(f"Artifacts: {out.resolve()}")


if __name__ == "__main__":
    main()
