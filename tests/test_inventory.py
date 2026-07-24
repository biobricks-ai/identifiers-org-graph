import csv
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows():
    with (ROOT / "registry/namespace-repositories.tsv").open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def test_every_live_registry_namespace_is_accounted_for():
    expected = {
        item["prefix"]
        for item in json.loads(
            (ROOT / "registry/registry.json").read_text()
        )["payload"]["namespaces"]
    }
    actual = {row["prefix"] for row in rows()}
    assert len(expected) == 861
    assert actual == expected


def test_confirmed_graphs_are_git_submodules():
    gitlinks = {
        line.split(maxsplit=3)[3]
        for line in subprocess.check_output(
            ["git", "ls-files", "--stage"], cwd=ROOT, text=True
        ).splitlines()
        if line.startswith("160000 ")
    }
    confirmed = {
        row["submodule_path"]
        for row in rows()
        if row["status"] == "existing-submodule"
    }
    assert confirmed
    assert confirmed == gitlinks


def test_multiple_repositories_use_deterministic_nested_paths():
    grouped = {}
    for row in rows():
        if row["status"] == "existing-submodule":
            grouped.setdefault(row["prefix"], []).append(row)
    for prefix, mappings in grouped.items():
        assert len({row["repository"] for row in mappings}) == len(mappings)
        if len(mappings) > 1:
            assert all(
                row["submodule_path"]
                == f"graphs/{prefix}/{row['repository_name']}"
                for row in mappings
            )
        else:
            assert mappings[0]["submodule_path"].startswith(f"graphs/{prefix}")


def test_audit_primary_sources_and_identifier_consumers_are_separate():
    primary = ROOT / "registry/audit/primary-source-mappings.tsv"
    consumers = ROOT / "registry/audit/identifier-consumer-coverage.tsv"
    with primary.open() as stream:
        primary_rows = list(csv.DictReader(stream, delimiter="\t"))
    with consumers.open() as stream:
        consumer_rows = list(csv.DictReader(stream, delimiter="\t"))
    primary_pairs = {
        (row["namespace_prefix"], row["repository"]) for row in primary_rows
    }
    consumer_pairs = {
        (row["namespace_prefix"], row["repository"]) for row in consumer_rows
    }
    assert primary_rows
    assert consumer_rows
    assert primary_pairs.isdisjoint(consumer_pairs)
    assert all(
        row["classification"] == "primary-registered-resource"
        for row in primary_rows
    )
    assert all(
        row["classification"] == "identifier-consumer"
        for row in consumer_rows
    )
    inventory_pairs = {
        (row["prefix"], row["repository_name"])
        for row in rows()
        if row["status"] == "existing-submodule"
    }
    assert primary_pairs <= inventory_pairs
    assert not (consumer_pairs - primary_pairs) & inventory_pairs


def test_no_deprecated_namespace_is_queued_without_review():
    assert not [
        row
        for row in rows()
        if row["deprecated"] == "true" and row["status"] == "build-needed"
    ]
