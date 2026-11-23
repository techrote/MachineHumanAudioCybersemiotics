#!/usr/bin/env python3
"""MHAC-X004: extract candidate epistemic distinctions with file/line provenance.

The miner is intentionally lexical. It surfaces statements for human/agent review;
it does NOT decide that the extracted left/right spans are philosophically valid,
complete, symmetric, or independent.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import argparse, json, re, sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import sediment_atlas as atlas  # noqa:E402

PAIR_PATTERNS=[
 ("distinguish_from",re.compile(r"\bdistinguish(?:es|ed|ing)?\s+(.{2,100}?)\s+from\s+(.{2,100}?)(?=[.;:]|$)",re.I)),
 ("separate_from",re.compile(r"\bseparat(?:e|es|ed|ing)\s+(.{2,100}?)\s+from\s+(.{2,100}?)(?=[.;:]|$)",re.I)),
 ("not_same_as",re.compile(r"(.{2,90}?)\s+(?:is|are)\s+not\s+(?:the\s+same\s+as|equivalent\s+to)\s+(.{2,90}?)(?=[.;:]|$)",re.I)),
]
BOUNDARY_PATTERNS=[
 ("does_not_establish",re.compile(r"\bdoes\s+not\s+(?:establish|prove|validate|imply|mean)\b",re.I)),
 ("not_evidence",re.compile(r"\bnot\s+(?:an?\s+)?(?:evidence|proof|finding|validation)\b",re.I)),
 ("do_not_conflate",re.compile(r"\bdo\s+not\s+(?:conflate|collapse|equate|identify)\b",re.I)),
 ("keep_distinct",re.compile(r"\bkeep\b.{0,80}\bdistinct\b",re.I)),
 ("rather_than",re.compile(r"\brather\s+than\b",re.I)),
]
MARKDOWN=re.compile(r"[*_#>|~]+")
LINK=re.compile(r"\[([^\]]+)\]\([^)]+\)")
CODE=re.compile(r"\x60([^\x60]+)\x60")

def line_clean(line):
 line=LINK.sub(r"\1",line);line=CODE.sub(r"\1",line);line=MARKDOWN.sub("",line)
 return " ".join(line.split())

def clip(s,n=180):
 s=" ".join(s.strip(" -–—,:;()[]").split())
 return s[:n]

def mine_file(path,root):
 rel=path.relative_to(root).as_posix();records=[]
 try:lines=path.read_text(encoding="utf-8").splitlines()
 except UnicodeDecodeError:return []
 for lineno,raw in enumerate(lines,1):
  line=line_clean(raw)
  if not line or line.startswith("| ---"):continue
  for kind,pat in PAIR_PATTERNS:
   for m in pat.finditer(line):
    records.append({"path":rel,"line":lineno,"family":atlas.family(rel),"kind":kind,
                    "left":clip(m.group(1),100),"right":clip(m.group(2),100),
                    "excerpt":clip(line),"paired":True})
  for kind,pat in BOUNDARY_PATTERNS:
   if pat.search(line):
    records.append({"path":rel,"line":lineno,"family":atlas.family(rel),"kind":kind,
                    "left":None,"right":None,"excerpt":clip(line),"paired":False})
 return records

def build(root):
 root=root.resolve();records=[]
 for p in sorted(root.rglob("*.md")):
  rel=p.relative_to(root).as_posix()
  if not atlas.eligible(rel):continue
  records.extend(mine_file(p,root))
 unique=[];seen=set()
 for r in records:
  key=(r["path"],r["line"],r["kind"],r["left"],r["right"])
  if key not in seen:seen.add(key);unique.append(r)
 records=unique
 kinds=Counter(r["kind"] for r in records);families=Counter(r["family"] for r in records)
 paired=[r for r in records if r["paired"]]
 term_counts=Counter()
 for r in paired:
  for side in (r["left"],r["right"]):
   for t in atlas.tokens(side or ""):
    if t not in atlas.STOP and len(t)>=4:term_counts[t]+=1
 return {"schema":"mhac-distinction-ledger-v1","head_sha":atlas.head(root),
         "records":records,"summary":{"records":len(records),"paired_records":len(paired),
         "kinds":dict(sorted(kinds.items())),"families":dict(sorted(families.items())),
         "paired_term_frequency":dict(term_counts.most_common(40))},
         "limits":["regex candidates require contextual reading","left/right spans may contain clauses rather than atomic concepts","absence does not mean no conceptual distinction","frequency is not importance","repository instructions can deliberately induce distinction language"]}

def markdown(result,limit=160):
 out=["# MHAC distinction ledger","","Generated lexical candidates; review context before reuse.","",
      f"Head: {result['head_sha']}  ",f"Candidates: {result['summary']['records']}  ",f"Parsed pairs: {result['summary']['paired_records']}","","| Kind | Left | Right | Source |","| --- | --- | --- | --- |"]
 for r in result["records"][:limit]:
  if not r["paired"]:continue
  left=(r["left"] or "").replace("|","/");right=(r["right"] or "").replace("|","/")
  out.append(f"| {r['kind']} | {left} | {right} | {r['path']}:{r['line']} |")
 out+=["","## Boundary-only candidates",""]
 for r in [x for x in result["records"] if not x["paired"]][:80]:
  out.append(f"- {r['path']}:{r['line']} — {r['kind']}: {r['excerpt']}")
 out+=["","## Limits",""]+[f"- {x}" for x in result["limits"]]
 return "\n".join(out)+"\n"

def main():
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path("."));p.add_argument("--json",type=Path);p.add_argument("--markdown",type=Path);p.add_argument("--print-ci-summary",action="store_true");a=p.parse_args();r=build(a.root)
 if a.json:a.json.parent.mkdir(parents=True,exist_ok=True);a.json.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 if a.markdown:a.markdown.parent.mkdir(parents=True,exist_ok=True);a.markdown.write_text(markdown(r),encoding="utf-8")
 if a.print_ci_summary:print("MHAC_X004_DISTINCTIONS="+json.dumps(r["summary"],sort_keys=True))
 elif not a.json and not a.markdown:print(markdown(r))
if __name__=="__main__":main()
