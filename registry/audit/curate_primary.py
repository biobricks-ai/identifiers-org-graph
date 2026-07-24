#!/usr/bin/env python3
import csv,json
from pathlib import Path

ROOT=Path(__file__).parent
rows=list(csv.DictReader((ROOT/"confirmed-mappings.tsv").open(),delimiter="\t"))
false_namespaces={"arxiv","broad","geogeo","go_ref","gsso","iao","inchi","mondo","obi","ro"}
exclude_repos={
 "bindingdb-info","nih-bindingdb-in-2024-a-fair-knowledgeb",
 "go-chembl-a-large-scale-bioactivi","en-comptox-chemicals-dashboard",
 "go-drugbank-online-database-for-d","go-drugbank-release-version-5-1-1",
 "cosmetic-inci-glossary","hsdb-pubchem","hsdb-pubchem-rdf",
 "medium-downloading-pubchem-bioassays","mckee","pdbbind-opt-rdf","plas-20k-rdf",
}
primary=[];consumers=[];rejected=[]
for r in rows:
    evidence=r["confirmation_evidence"]
    provider=("registry resource URL plus" in evidence or "registry provider domain plus" in evidence)
    direct="direct Identifiers.org namespace IRI" in evidence
    if direct and not provider:
        r["classification"]="identifier-consumer"
        consumers.append(r);continue
    if not provider:
        r["classification"]="insufficient-primary-source-evidence"
        rejected.append(r);continue
    if r["namespace_prefix"] in false_namespaces or r["repository"] in exclude_repos:
        r["classification"]="related-or-derived-not-namespace-resource"
        rejected.append(r);continue
    r["classification"]="primary-registered-resource"
    primary.append(r)

fields=["namespace_prefix","namespace_name","repository","repository_url",
        "classification","confirmation_evidence","local_evidence_paths"]
for name,data in (("primary-source-mappings.tsv",primary),
                  ("identifier-consumer-coverage.tsv",consumers),
                  ("rejected-context-matches.tsv",rejected)):
    with (ROOT/name).open("w",newline="") as f:
        w=csv.DictWriter(f,delimiter="\t",lineterminator="\n",fieldnames=fields)
        w.writeheader();w.writerows({k:r.get(k,"") for k in fields} for r in sorted(data,key=lambda x:(x["namespace_prefix"],x["repository"])))
summary={"primary_rows":len(primary),"primary_namespaces":len({r["namespace_prefix"] for r in primary}),
         "primary_repositories":len({r["repository"] for r in primary}),
         "identifier_consumer_rows":len(consumers),"rejected_context_rows":len(rejected)}
(ROOT/"curation-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary,indent=2))
