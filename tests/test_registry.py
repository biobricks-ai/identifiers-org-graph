from rdflib import RDF, URIRef
from rdflib.namespace import DCAT, VOID

from stages.build_registry import IDOT, build, transform_namespace

FIXTURE = {
    "id": 1, "prefix": "gene.test", "mirId": "MIR:1", "name": "Test genes",
    "pattern": "^G[0-9]+$", "description": "fixture", "created": "2024-01-01",
    "modified": "2024-01-02", "sampleId": "G1",
    "namespaceEmbeddedInLui": False, "deprecated": False,
    "deprecationDate": None, "deprecationOfflineDate": None,
    "renderDeprecatedLanding": False, "deprecationStatement": None,
    "infoOnPostmortemAccess": None, "successor": None,
    "resources": [{
        "id": 2, "mirId": "MIR:2", "urlPattern": "https://example.org/{$id}",
        "name": "Provider", "description": "Provider", "official": True,
        "providerCode": "ex", "sampleId": "G1",
        "resourceHomeUrl": "https://example.org",
        "institution": {"id": 3, "name": "Institute",
                        "homeUrl": "https://example.org", "description": "Institute",
                        "rorId": None, "location": {"countryCode": "GB",
                                                   "countryName": "United Kingdom"}},
        "location": {"countryCode": "GB", "countryName": "United Kingdom"},
        "deprecated": False, "deprecationDate": None,
        "deprecationOfflineDate": None, "renderDeprecatedLanding": False,
        "deprecationStatement": None, "protectedUrls": False,
        "renderProtectedLanding": False, "authHelpUrl": None,
        "authHelpDescription": None,
    }],
}


def test_namespace_metadata_preserves_provider_and_sample():
    graph, metrics = transform_namespace(FIXTURE)
    namespace = URIRef("http://identifiers.org/gene.test")
    assert (namespace, RDF.type, DCAT.Dataset) in graph
    assert (
        namespace,
        VOID.exampleResource,
        URIRef("https://identifiers.org/gene.test:G1"),
    ) in graph
    assert (namespace, IDOT.identifierPopulationEnumerationStatus, None) in graph
    assert metrics["resources"] == metrics["sample"] == 1


def test_registry_build_emits_one_independent_graph_per_namespace(tmp_path):
    report = build({"payload": {"namespaces": [FIXTURE]}}, tmp_path)
    assert report["record_count_coverage"] == 1.0
    assert report["field_disposition_coverage"] == 1.0
    assert report["namespace_graphs"] == 1
    assert "gene.test" in (tmp_path / "graphs.tsv").read_text()
    assert (tmp_path / "namespaces/gene.test.nt").is_file()
