"""Optional upload of synthetic ECS-like telemetry to a *local* Elasticsearch instance."""
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen
from .generator import read_jsonl


def main():
    p = argparse.ArgumentParser(description="Ingest synthetic TradeLink events into local Elasticsearch")
    p.add_argument("--input", type=Path, default=Path("outputs/events.jsonl"))
    p.add_argument("--url", default="http://localhost:9200")
    p.add_argument("--index", default="tradelink-security-lab")
    args = p.parse_args()
    if not args.url.startswith("http://localhost:") and not args.url.startswith("http://127.0.0.1:"):
        p.error("For safety this example permits only loopback Elasticsearch endpoints")
    events = read_jsonl(args.input)
    payload = "".join(json.dumps({"index": {"_index": args.index}}) + "\n" +
                      json.dumps(e) + "\n" for e in events).encode()
    req = Request(args.url.rstrip("/") + "/_bulk?refresh=true", data=payload,
                  headers={"Content-Type": "application/x-ndjson"}, method="POST")
    with urlopen(req, timeout=30) as resp:
        result = json.load(resp)
    if result.get("errors"):
        raise SystemExit("Bulk ingest reported errors: " + json.dumps(result.get("items", [])[:2]))
    print(f"Indexed {len(events)} synthetic events into {args.index}")


if __name__ == "__main__":
    main()
