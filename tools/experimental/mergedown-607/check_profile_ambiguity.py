"""#607 independent projection oracle for #443 at 0a298d30 and #453 at 7773a123.
Requires NumPy; accepts native upstream receipt.json, never imports upstream code.
Synthetic clean-erasure catalogue accounting, not physical error probabilities.
"""
import itertools, json, sys
from pathlib import Path
import numpy as np


def catalogue():
    # Generate all grammatical prefixes recursively, rather than scan pending slots.
    def expressions(n):
        if n < 1:
            return
        if n == 1:
            yield from ((x,) for x in (0, 1, 2, 3, 14))
        for x in range(4, 11):
            for a in expressions(n-1):
                yield (x,) + a
        for x in (11, 12):
            for k in range(1, n-1):
                for a in expressions(k):
                    for b in expressions(n-1-k):
                        yield (x,) + a + b
    radix = 17 ** np.arange(3, -1, -1)
    legal = {int(np.dot(a+(13,)*(4-n), radix)) for n in range(1, 5) for a in expressions(n)}
    free = np.array([i for i in range(4913, 13*4913) if i not in legal])
    assert len(free) == 55858
    # Enumerate coefficient vectors and invert by sorting systematic projections.
    coefficients = (np.arange(17**4)[:, None] // radix) % 17
    x = np.arange(8)
    universe = (coefficients @ (x[None, :] ** np.arange(4)[:, None])) % 17
    indices = universe[:, [0, 1, 4, 5]] @ radix
    all_words = universe[np.argsort(indices)]
    legal_indices = np.concatenate((np.arange(3840), 14*4913+np.arange(3840), free[36480:40320], free[:36480]))
    old = all_words[legal_indices]
    group = np.concatenate([k*192 + np.repeat(np.arange(192), n) for k,n in enumerate((20,20,20,190))])
    matched = np.flatnonzero(group % 192 < 16)
    c = (np.arange(4000)[:, None] // (17 ** np.arange(2,-1,-1))) % 17
    new = c @ (x[None,:] ** np.arange(3)[:,None]) % 17
    assert len(old)==48000 and len(matched)==len(new)==4000
    h=g=0
    for v in old.flat:
        h=(h*31+int(v)+1)%1000000007
        g=(g*37+int(v)+1)%1000000009
    assert (h,g)==(95787044,408117442)
    return old,new,group,matched


def counts(keys, query):
    s=np.sort(keys)
    return np.searchsorted(s,query,'right')-np.searchsorted(s,query,'left')


def inspect(old,new,group,matched,pos):
    weights=17**np.arange(len(pos)-1,-1,-1,dtype=np.int64)
    a,b=old[:,pos]@weights,new[:,pos]@weights
    keys=np.concatenate((a,b))
    ids=np.concatenate((np.arange(len(a)),matched))
    # A duplicate semantic identity counts only once when both profiles project equally.
    duplicate=a[matched]==b
    keep=np.concatenate((np.ones(len(a),dtype=bool),~duplicate))
    distinct=keys[keep]
    distinct_ids=ids[keep]
    uniq=counts(distinct,keys)
    # Group by projection and kind/address to count oracle-filtered candidates.
    stride=768
    scoped=counts(distinct*stride+group[distinct_ids],keys*stride+group[ids])
    na,nb=counts(a,keys),counts(b,keys)
    sa=np.argsort(a); sb=np.argsort(b)
    ia=np.minimum(np.searchsorted(a[sa],keys),len(a)-1)
    ib=np.minimum(np.searchsorted(b[sb],keys),len(b)-1)
    ga=np.where((na==1)&(len(pos)>=4),sa[ia],-1)
    gb=np.where(nb==1,matched[sb[ib]],-1)
    lf=np.where(ga>=0,ga,gb); pf=np.where(gb>=0,gb,ga)
    totals={}
    for name,sel in [('legacy',np.arange(len(a))),('legacy_matched',matched),('protected',len(a)+np.arange(len(b)))]:
        u=uniq[sel]
        d={'trials':len(sel),'both_profiles':int(np.sum((na[sel]>0)&(nb[sel]>0))),
           'semantic_singleton':int(np.sum(u==1)),'semantic_ambiguity':int(np.sum(u>1)),
           'same_kind_address_singleton':int(np.sum(scoped[sel]==1)),
           'candidate_sum':int(np.sum(u)),'max_candidates':int(np.max(u))}
        for label,got in [('legacy_first',lf[sel]),('protected_first',pf[sel])]:
            d[label+'_correct']=int(np.sum(got==ids[sel]))
            d[label+'_wrong']=int(np.sum((got>=0)&(got!=ids[sel])))
            d[label+'_abstain']=int(np.sum(got<0))
        totals[name]=d
    return totals


def main(path):
    receipt=json.loads(Path(path).read_text())
    assert receipt['source_commit']=='7773a123a29881a22d7c1893df1dd609c4ef25d1'
    old,new,group,matched=catalogue()
    expected=[p for n in (8,4,3) for p in itertools.combinations(range(8),n)]
    assert [tuple(r['surviving']) for r in receipt['rows']]==expected
    checked=0; total=0
    for p,row in zip(expected,receipt['rows']):
        observed=inspect(old,new,group,matched,p)
        for name,d in observed.items():
            actual=row['counts'][name]
            assert set(actual)<=set(d), (p,name,set(actual)-set(d))
            for k,v in d.items():
                assert actual.get(k,0)==v,(p,name,k,v,actual.get(k,0))
                checked+=1
            total+=d['trials']
    # Separate complete-codeword witness check; semantic label differs, same waveform.
    full=receipt['rows'][0]['counts']['protected']
    assert full['both_profiles']==2604 and full['semantic_ambiguity']==2603
    print(json.dumps({'masks':len(expected),'metric_cells':checked,'source_configurations_including_matched_subset':total,'full_protected':full},sort_keys=True))

if __name__=='__main__': main(sys.argv[1])
