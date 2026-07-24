# identifiers-org-graph

This repository is the hub between the Identifiers.org registry and BioBricks
knowledge graphs.

Identifiers.org-level material lives directly in this repository:

- `registry/registry.json` is the complete live registry response.
- `brick/registry.nt` and `brick/registry-namespaces/` are its RDF projection.
- `registry/namespace-repositories.tsv` accounts for every registered namespace.

Dataset graphs are separate, independently buildable repositories. A namespace
may have more than one confirmed graph repository. Single legacy mappings may
remain at `graphs/<prefix>`; multiple mappings always use the deterministic
path `graphs/<prefix>/<repository-name>`.

A repository is promoted only when its primary source records are the resource
registered for that namespace. Merely minting or consuming an
`identifiers.org/<prefix>` IRI is not sufficient. Those joins are recorded
separately in `registry/audit/identifier-consumer-coverage.tsv`. Lexical
candidates are retained in `registry/audit/heuristic-review.tsv` and are never
submodules.

The ledger statuses are:

- `existing-submodule`: a primary-source-equivalent graph repository is linked.
- `build-needed`: no confirmed BioBricks graph is known yet.
- `deprecated`: the registry namespace is deprecated and has no confirmed graph.

Identifiers.org is a registry and resolver, not a dump of every identifier in
every registered database. Population graphs therefore come from the
authoritative upstream database and remain subject to its license and release
process.

```bash
python stages/inventory.py
pytest -q
git submodule update --init --recursive
```
