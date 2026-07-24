#!/usr/bin/env python3
"""Audit live Identifiers.org namespaces against the complete Biobricks GitHub repo list."""
import csv,json,re
from pathlib import Path
from urllib.parse import urlparse
from difflib import SequenceMatcher

LEDGER=Path("/tmp/identifiers-ledger.json")
REPOS=Path("/tmp/biobricks-repos.tsv")
OUT=Path(__file__).parent
ROOTS=[Path("/mnt/raid2/biobricks"),Path("/home/insilica/git/com.toxindex")]
FILES=(".bb/brick.jsonld",".bb/source.jsonld","README.md","readme.md","dvc.yaml",
       "stages/01_download.py","stages/download.py","stages/fetch.py")
GENERIC={"github.com","raw.githubusercontent.com","doi.org","zenodo.org","figshare.com",
         "data.gov","catalog.data.gov","www.ncbi.nlm.nih.gov","ncbi.nlm.nih.gov",
         "ebi.ac.uk","www.ebi.ac.uk","ftp.ebi.ac.uk","ftp.ncbi.nlm.nih.gov",
         "purl.org","www.w3.org","w3.org","identifiers.org","www.identifiers.org"}
STOP={"database","data","resource","registry","information","project","protein","gene",
      "chemical","online","national","international","institute","center","centre",
      "archive","collection","repository","identifiers","identifier"}
STOP |= {"and","the","for","from","with","into","via","based","provides","contains",
         "human","species","system","analysis","research","results","molecular"}

def norm(s): return re.sub(r"[^a-z0-9]+"," ",(s or "").lower()).strip()
def toks(s): return {x for x in norm(s).split() if len(x)>=3 and x not in STOP}
def domains(ns):
    out=set()
    for r in ns.get("resources",[]):
        for k in ("urlPattern","resourceHomeUrl"):
            try:
                d=urlparse(r.get(k) or "").hostname
                if d: out.add(d.lower())
            except Exception: pass
    return out
def urls(ns):
    out=set()
    for r in ns.get("resources",[]):
        for k in ("urlPattern","resourceHomeUrl"):
            u=(r.get(k) or "").replace("{$id}","")
            if u: out.add(u.rstrip("/"))
    return out
def repo_index():
    rows=[]
    for line in REPOS.read_text().splitlines():
        p=line.split("\t")
        rows.append({"name":p[0],"description":p[1] if len(p)>1 else "",
                     "url":p[2] if len(p)>2 else "","branch":p[3] if len(p)>3 else ""})
    paths={}
    for root in ROOTS:
        for depth in ("*","*/*","*/*/*","*/*/*/*"):
            for p in root.glob(depth):
                if p.is_dir() and p.name not in paths: paths[p.name]=p
    for r in rows:
        p=paths.get(r["name"]); chunks=[r["description"]]
        evidence=[]
        if p:
            candidates=[p/rel for rel in FILES]
            candidates += list(p.glob("stages/*.py"))+list(p.glob("health/*.json"))
            candidates += list(p.glob("queries/*.rq"))+list(p.glob("src/**/*.*"))
            seen=set()
            for f in candidates:
                if f in seen:continue
                seen.add(f)
                if f.is_file() and f.stat().st_size<2_000_000:
                    try:
                        text=f.read_text(errors="replace")
                        chunks.append(text);evidence.append(str(f))
                    except OSError: pass
        r["path"]=str(p or "");r["text"]="\n".join(chunks).lower();r["files"]=evidence
        r["tokens"]=toks(r["name"]+" "+r["description"])
        r["metadata_tokens"]=toks(r["text"][:100000])
    return rows

def main():
    namespaces=json.loads(LEDGER.read_text())["payload"]["namespaces"]
    repos=repo_index()
    ns_by_prefix={n["prefix"].lower():n for n in namespaces}
    domain_index={}
    token_index={}
    url_index={}
    ns_tokens={}
    for ns in namespaces:
        pref=ns["prefix"];ns_tokens[pref]=toks(pref+" "+ns.get("name",""))
        for d in domains(ns):domain_index.setdefault(d,set()).add(pref)
        for t in ns_tokens[pref]:token_index.setdefault(t,set()).add(pref)
        for u in urls(ns):url_index.setdefault(u.lower(),set()).add(pref)
    confirmed=[];review=[];covered=set()
    for r in repos:
        text=r["text"]; rt=r["tokens"]|r["metadata_tokens"]; reasons={}
        # Direct Identifiers.org IRIs.
        for pref in set(re.findall(r"identifiers\.org/([a-z0-9_.-]+)(?:[/:\s\"<])",text)):
            if pref in ns_by_prefix:reasons.setdefault(pref,[]).append("direct Identifiers.org namespace IRI in repository metadata/source")
        # URLs and provider domains from metadata/source.
        found_urls=set(re.findall(r"https?://[^\s\"'<>]+",text))
        found_domains=set()
        for u in found_urls:
            try: found_domains.add(urlparse(u.rstrip(".,);]")).hostname)
            except ValueError: pass
        for u in found_urls:
            clean=u.rstrip("/.,);]").lower()
            for registered,prefs in url_index.items():
                try: path=urlparse(registered).path.strip("/")
                except ValueError: path=""
                if len(path)<2:continue
                if clean==registered or clean.startswith(registered+"/"):
                    for pref in prefs:
                        # A cited URL alone is not a dataset mapping: require namespace-specific repository metadata.
                        if ns_tokens[pref] & r["tokens"]:
                            reasons.setdefault(pref,[]).append("exact registry resource URL plus namespace-specific repository metadata: "+registered)
        for d in found_domains:
            if not d or d in GENERIC:continue
            for pref in domain_index.get(d.lower(),()):
                overlap=sorted(ns_tokens[pref]&r["tokens"])
                if overlap:reasons.setdefault(pref,[]).append("registry provider domain plus namespace-specific metadata token: "+d+"; "+overlap[0])
        for pref,why in reasons.items():
            ns=ns_by_prefix[pref];file_evidence=";".join(r["files"][:4]) or "GitHub repository description"
            confirmed.append([pref,ns.get("name",""),r["name"],r["url"],"|".join(dict.fromkeys(why)),file_evidence]);covered.add(pref)
        # Heuristic candidates only from shared namespace-specific tokens.
        candidates=set()
        for t in r["tokens"]:candidates.update(token_index.get(t,()))
        for pref in candidates:
            if pref in reasons:continue
            ns=ns_by_prefix[pref];a=norm(pref.replace("."," ")+" "+ns.get("name",""));b=norm(r["name"].replace("-"," ")+" "+r["description"])
            sim=SequenceMatcher(None,a,b).ratio();ov=ns_tokens[pref]&r["tokens"]
            if sim>=0.52 or (len(ov)>=2 and sim>=0.30):
                review.append([pref,ns.get("name",""),r["name"],r["url"],f"{sim:.3f}",",".join(sorted(ov)),"no exact source/metadata evidence"])
    confirmed.sort();review.sort(key=lambda x:(-float(x[4]),x[0],x[2]))
    with (OUT/"confirmed-mappings.tsv").open("w",newline="") as f:
        w=csv.writer(f,delimiter="\t");w.writerow(["namespace_prefix","namespace_name","repository","repository_url","confirmation_evidence","local_evidence_paths"]);w.writerows(confirmed)
    with (OUT/"heuristic-review.tsv").open("w",newline="") as f:
        w=csv.writer(f,delimiter="\t");w.writerow(["namespace_prefix","namespace_name","repository","repository_url","similarity","token_overlap","review_reason"]);w.writerows(review)
    uncovered=sorted((n["prefix"],n.get("name","")) for n in namespaces if n["prefix"] not in covered)
    with (OUT/"unmapped-namespaces.tsv").open("w",newline="") as f:
        w=csv.writer(f,delimiter="\t");w.writerow(["namespace_prefix","namespace_name"]);w.writerows(uncovered)
    summary={"ledger_namespaces":len(namespaces),"github_repositories":len(repos),
             "repositories_with_local_metadata":sum(bool(r["path"]) for r in repos),
             "confirmed_mapping_rows":len(confirmed),"confirmed_namespaces":len(covered),
             "confirmed_repositories":len({x[2] for x in confirmed}),
             "heuristic_review_rows":len(review),"unmapped_namespaces":len(uncovered),
             "inputs":{"ledger":str(LEDGER),"repositories":str(REPOS)},
             "outputs":{"confirmed":str(OUT/"confirmed-mappings.tsv"),"heuristic_review":str(OUT/"heuristic-review.tsv"),"unmapped":str(OUT/"unmapped-namespaces.tsv")}}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
