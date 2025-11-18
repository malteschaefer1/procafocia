"""Simple CLI to review mapping decisions via the REST API."""
from __future__ import annotations

import argparse
import json
import sys

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch mapping review information for a product")
    parser.add_argument("product_id", help="Product identifier")
    parser.add_argument("--scenario-id", default="default", help="Scenario identifier")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()

    url = f"{args.base_url.rstrip('/')}/mapping/review/{args.product_id}"
    response = requests.get(url, params={"scenario_id": args.scenario_id}, timeout=10)
    if response.status_code != 200:
        print(f"Request failed: {response.status_code} {response.text}", file=sys.stderr)
        sys.exit(1)
    data = response.json()
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
