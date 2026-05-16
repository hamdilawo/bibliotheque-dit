"""
Exporte l'historique des emprunts depuis le service Emprunts vers data/loans.csv.

Usage:
    python scripts/export_loans.py
    python scripts/export_loans.py --url http://localhost:8008
"""
import argparse
import os
import sys
from pathlib import Path

import requests

DEFAULT_URL = os.getenv("SERVICE_EMPRUNTS_URL", "http://localhost:8008")


def export(base_url: str, output: str) -> None:
    url = f"{base_url}/api/emprunts/export-csv/"
    print(f"Fetching {url} ...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(resp.text)

    lines = resp.text.strip().split("\n")
    print(f"Exporté : {len(lines) - 1} emprunts → {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output", default="data/loans.csv")
    args = parser.parse_args()

    try:
        export(args.url, args.output)
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)
