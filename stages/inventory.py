"""Build the complete namespace-to-graph-repository ledger."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "registry.json"
MAPPINGS = ROOT / "registry" / "confirmed-repositories.json"
LEDGER = ROOT / "registry" / "namespace-repositories.tsv"


def main() -> None:
    namespaces = json.loads(REGISTRY.read_text())["payload"]["namespaces"]
    mappings = json.loads(MAPPINGS.read_text())
    with LEDGER.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            delimiter="\t",
            fieldnames=[
                "prefix",
                "name",
                "deprecated",
                "status",
                "repository",
                "submodule_path",
                "evidence",
            ],
        )
        writer.writeheader()
        for namespace in sorted(namespaces, key=lambda item: item["prefix"]):
            prefix = namespace["prefix"]
            mapping = mappings.get(prefix)
            if mapping:
                status = "existing-submodule"
                repository = mapping["repository"]
                path = f"graphs/{prefix}"
                evidence = mapping["evidence"]
            else:
                status = "deprecated" if namespace["deprecated"] else "build-needed"
                repository = path = ""
                evidence = "No confirmed BioBricks graph mapping"
            writer.writerow(
                {
                    "prefix": prefix,
                    "name": namespace["name"],
                    "deprecated": str(namespace["deprecated"]).lower(),
                    "status": status,
                    "repository": repository,
                    "submodule_path": path,
                    "evidence": evidence,
                }
            )


if __name__ == "__main__":
    main()
