# identifiers-org-graph

This repository is the hub between the Identifiers.org registry and BioBricks
knowledge graphs.

Identifiers.org-level material lives directly in this repository:

- `registry/registry.json` is the complete live registry response.
- `brick/registry.nt` and `brick/registry-namespaces/` are its RDF projection.
- `registry/namespace-repositories.tsv` accounts for every registered namespace.

Dataset graphs are separate, independently buildable repositories. A confirmed
graph is linked at `graphs/<identifiers.org prefix>` as a Git submodule. A row
is not promoted to a submodule based only on a similar repository name: the
mapping must identify the same namespace/database.

The ledger statuses are:

- `existing-submodule`: a confirmed graph repository is linked here.
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
