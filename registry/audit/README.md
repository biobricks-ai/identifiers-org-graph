# Identifiers.org × Biobricks repository audit

This audit compares the live Identifiers.org resolver ledger (861 namespaces,
retrieved 2026-07-23) with all 2,254 repositories returned by the Biobricks
GitHub organization API.

`confirmed-mappings.tsv` is the first-pass evidence ledger. It records exact
source/provider evidence and direct identifier use. It is not itself the
submodule allowlist. Confirmation in that first-pass ledger requires one of:

1. an exact `identifiers.org/<namespace>` IRI in repository metadata,
   transformation source, health contracts, queries, or source code;
2. an exact non-root Identifiers.org registry resource URL plus a
   namespace-specific token in the repository name or GitHub description; or
3. a non-generic registry provider domain plus a namespace-specific token in
   the repository name or GitHub description.

The semantic curation pass then separates:

- `primary-source-mappings.tsv`: the repository's primary records are the
  registered namespace resource; these are eligible for submodules.
- `identifier-consumer-coverage.tsv`: the repository consumes canonical
  Identifiers.org IRIs but is not a graph of that registered resource.
- `rejected-context-matches.tsv`: related papers, downstream datasets, imported
  ontologies, or generic provider context that must not label a submodule.

Only `primary-source-mappings.tsv` feeds the hub mapping. The evidence column
states the rule and the paths column identifies inspected local
metadata/source. GitHub descriptions are explicitly identified when no local
checkout was available.

`heuristic-review.tsv` is deliberately separate. It contains lexical candidates
that lacked exact source/metadata evidence and must not be treated as mappings.
`unmapped-namespaces.tsv` lists ledger namespaces with no confirmed mapping.

Generic hosting and aggregation domains (GitHub, DOI, NCBI/EBI roots, PURL,
W3C, Data.gov, Zenodo, and Figshare) cannot confirm a provider mapping by
themselves. Paper citations alone are not considered dataset mappings.

The audit script is reproducible from the captured live ledger and GitHub
repository inventory paths recorded in `summary.json`. It does not modify the
KG root or the Identifiers.org hub repositories.
