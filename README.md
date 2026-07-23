# identifiers-org-graph

Umbrella BioBrick for the complete data surface published by Identifiers.org.
Its Git submodules remain independently buildable and independently loadable:

| Component | Scope |
|---|---|
| `registry-data` | Live resolver dataset plus the official versioned Git mirror |
| `registry-rdf` | One metadata graph per registered namespace |
| `sparql-rdf` | Verbatim official DCAT/VoID/idot registry projection |
| `resolutions-rdf` | Every registered sample identifier and every resolver candidate |
| `statistics-rdf` | Trial namespace usage statistics, when the experimental API responds |

The current live registry has 861 namespaces and 1,033 provider resources.
Together the components define 2,584 independently addressable graph slots.

## Identifier-population boundary

Identifiers.org is a registry and meta-resolver. It publishes identifier
patterns and one sample identifier per namespace, but it does not provide an
API or dump enumerating every accession assigned by PubMed, UniProt, ChEBI,
NCBI Taxonomy, GO, and the other upstream databases. Those populations must be
integrated from their authoritative providers under provider-specific licenses
and release processes.

This brick records that limitation for every namespace. It does not infer
accessions from regexes, probe random values, scrape provider sites, or claim
that usage counts are namespace sizes.

```bash
python stages/catalog.py
pytest -q
```
