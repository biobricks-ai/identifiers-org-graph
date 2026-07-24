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
    document = json.loads(MAPPINGS.read_text())
    mappings = document.get("namespaces", document)
    with LEDGER.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            delimiter="\t",
            lineterminator="\n",
            fieldnames=[
                "prefix",
                "name",
                "deprecated",
                "status",
                "repository",
                "repository_name",
                "submodule_path",
                "evidence",
                "evidence_source",
            ],
        )
        writer.writeheader()
        for namespace in sorted(namespaces, key=lambda item: item["prefix"]):
            prefix = namespace["prefix"]
            entries = mappings.get(prefix, [])
            if isinstance(entries, dict):
                entries = [entries]
            if not entries:
                entries = [{
                    "status": "deprecated" if namespace["deprecated"] else "build-needed",
                    "repository": "", "repository_name": "", "submodule_path": "",
                    "evidence": "No confirmed BioBricks graph mapping",
                    "evidence_source": "",
                }]
            for mapping in sorted(entries, key=lambda item: item.get("submodule_path", "")):
                writer.writerow(
                    {
                        "prefix": prefix,
                        "name": namespace["name"],
                        "deprecated": str(namespace["deprecated"]).lower(),
                        "status": mapping.get("status", "existing-submodule"),
                        "repository": mapping.get("repository", ""),
                        "repository_name": mapping.get("repository_name", ""),
                        "submodule_path": mapping.get("submodule_path", ""),
                        "evidence": mapping.get("evidence", ""),
                        "evidence_source": mapping.get("evidence_source", ""),
                    }
                )


if __name__ == "__main__":
    main()
