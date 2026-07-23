import csv
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows():
    with (ROOT / "registry/namespace-repositories.tsv").open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def test_every_live_registry_namespace_is_accounted_for_once():
    expected = {
        item["prefix"]
        for item in json.loads(
            (ROOT / "registry/registry.json").read_text()
        )["payload"]["namespaces"]
    }
    actual = [row["prefix"] for row in rows()]
    assert len(actual) == len(set(actual)) == len(expected) == 861
    assert set(actual) == expected


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


def test_no_deprecated_namespace_is_queued_without_review():
    assert not [
        row
        for row in rows()
        if row["deprecated"] == "true" and row["status"] == "build-needed"
    ]
