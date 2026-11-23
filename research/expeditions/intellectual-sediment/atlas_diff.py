#!/usr/bin/env python3
"""Compare two frozen MHAC-X004 atlas JSON snapshots transparently."""
from pathlib import Path
import argparse, json

def delta_map(before,after):
 keys=sorted(set(before)|set(after))
 return {k:after.get(k,0)-before.get(k,0) for k in keys if after.get(k,0)!=before.get(k,0)}

def style_deltas(before,after):
 out={}
 fams=sorted(set(before.get("style",{}).get("by_family",{}))|
             set(after.get("style",{}).get("by_family",{})))
 for fam in fams:
  b=before.get("style",{}).get("by_family",{}).get(fam,{})
  a=after.get("style",{}).get("by_family",{}).get(fam,{})
  markers={}
  for m in sorted(set(b)|set(a)):
   bv=b.get(m,{}).get("per_1000",0);av=a.get(m,{}).get("per_1000",0)
   if av!=bv:markers[m]=round(av-bv,6)
  if markers:out[fam]=markers
 return out

def motif_deltas(before,after):
 out={}
 bm=before.get("motifs",{});am=after.get("motifs",{})
 for name in sorted(set(bm)|set(am)):
  b=bm.get(name,{});a=am.get(name,{})
  row={"documents":a.get("documents",0)-b.get("documents",0),
       "family_count":a.get("family_count",0)-b.get("family_count",0)}
  bf=b.get("families",{});af=a.get("families",{})
  row["families"]=delta_map(bf,af)
  if row["documents"] or row["family_count"] or row["families"]:out[name]=row
 return out

def compare(before,after):
 bc=before.get("corpus",{});ac=after.get("corpus",{})
 bb={x["phrase"] for x in before.get("top_bridges",before.get("top_cross_family_lexical_bridges",[]))}
 ab={x["phrase"] for x in after.get("top_bridges",after.get("top_cross_family_lexical_bridges",[]))}
 bs={x["phrase"] for x in before.get("sparse_bridges",before.get("sparse_cross_family_phrases",[]))}
 ass={x["phrase"] for x in after.get("sparse_bridges",after.get("sparse_cross_family_phrases",[]))}
 return {"schema":"mhac-intellectual-sediment-diff-v1",
         "before_head":before.get("head_sha"),"after_head":after.get("head_sha"),
         "corpus":{"documents":ac.get("documents",ac.get("document_count",0))-bc.get("documents",bc.get("document_count",0)),
                   "words":ac.get("words",ac.get("word_count",0))-bc.get("words",bc.get("word_count",0)),
                   "families":delta_map(bc.get("families",bc.get("coarse_family_documents",{})),ac.get("families",ac.get("coarse_family_documents",{})))},
         "style_per_1000_deltas":style_deltas(before,after),
         "motif_deltas":motif_deltas(before,after),
         "bridges":{"new_top":sorted(ab-bb),"lost_top":sorted(bb-ab),
                    "new_sparse":sorted(ass-bs),"lost_sparse":sorted(bs-ass)},
         "limits":["differences reflect corpus and analyzer configuration together",
                   "a changed stoplist or motif lexicon can create apparent drift",
                   "new documents do not imply new independent contributors",
                   "lexical bridge churn is not conceptual innovation"]}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("before",type=Path);p.add_argument("after",type=Path);p.add_argument("--out",type=Path);a=p.parse_args()
 b=json.loads(a.before.read_text(encoding="utf-8"));c=json.loads(a.after.read_text(encoding="utf-8"));r=compare(b,c);s=json.dumps(r,indent=2,sort_keys=True)+"\n"
 if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(s,encoding="utf-8")
 else:print(s,end="")
if __name__=="__main__":main()
