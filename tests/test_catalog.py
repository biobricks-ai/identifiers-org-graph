import json
from pathlib import Path

from stages.catalog import catalog


def test_catalog_exposes_every_layer_and_population_limit(tmp_path):
    namespaces = [{"prefix": "go", "pattern": "^GO:\\d{7}$", "sampleId": "0008150"}]
    report = catalog(namespaces, tmp_path)
    assert report["graph_slots"] == 4
    assert report["identifier_population_status_coverage"] == 1.0
    assert report["enumerable_complete_populations_from_identifiers_org"] == 0
    graphs = (tmp_path / "graphs.tsv").read_text()
    assert "identifiers-org/go" in graphs
    assert "identifiers-org-resolution/go" in graphs
    assert "identifiers-org-statistics/go" in graphs


def test_contract_and_submodules():
    root = Path(__file__).parents[1]
    deps = set((root / ".bb/dependencies.txt").read_text().splitlines())
    assert deps == {
        "identifiers-org-registry-rdf",
        "identifiers-org-sparql-rdf",
        "identifiers-org-resolutions-rdf",
        "identifiers-org-statistics-rdf",
    }
    for component in ("registry-rdf", "sparql-rdf", "resolutions-rdf", "statistics-rdf"):
        assert (root / "components" / component / ".git").is_file()
    assert json.loads((root / "health/ontology-policy.json").read_text())["passed"]
