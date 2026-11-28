import hashlib, itertools, json, pathlib, runpy, sys
import numpy as np
root=pathlib.Path(sys.argv[1]); g=runpy.run_path(str(root/'control-namespace.py'))
for n,h in {'control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f'}.items():
 b=(root/n).read_bytes(); assert hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==h
u,old,naive,new,labels,info=g['build'](root)
# Independent tuple equality / multiplicities instead of upstream rank matching.
from collections import Counter, defaultdict
oldbody=defaultdict(list)
for i,w in enumerate(old): oldbody[tuple(w[:8])].append(i)
assert len(set(map(tuple,new)))==68204
assert len(set(map(tuple,naive)))==68204-2031
assert not any(j!=i for i,w in enumerate(new) for j in oldbody.get(tuple(w[:8]),[]))
# Independently evaluate every row from first four samples with modular Lagrange.
def interp(book,n):
 x=np.arange(4); weights=np.array([[int(np.prod([(k-j)%17 for j in x if j!=i]))*pow(int(np.prod([(i-j)%17 for j in x if j!=i]))%17,-1,17)%17 for k in range(n)] for i in x]);return book[:,:4]@weights%17
assert np.array_equal(interp(new,10),new)
assert np.array_equal(interp(old,8),old[:,:8])
# Incompatible cross pairs have d>=5 by body proof. Exactly five matches gives d=5.
counts=[]; witness=None
for mask in itertools.combinations(range(10),5):
 a=old[:,mask]@np.array([1,17,289,4913,83521]); b=new[:,mask]@np.array([1,17,289,4913,83521]); order=np.argsort(a); sa=a[order]; lo=np.searchsorted(sa,b,'left'); hi=np.searchsorted(sa,b,'right'); c=hi-lo; c[:len(old)]-=a==b[:len(old)]; assert np.all(c>=0); counts.append(int(c.sum()))
 if witness is None and c.max()>0:
  i=int(np.flatnonzero(c)[0]); j=next(int(j) for j in order[lo[i]:hi[i]] if j!=i); witness={'new_row':i,'tag_row':j,'new_identity':labels[i],'tag_identity':labels[j],'new_word':new[i].tolist(),'tag_word':old[j].tolist(),'distance':int(np.count_nonzero(new[i]!=old[j]))}
assert witness and witness['distance']==5
# Whole-menu legacy d=2 incompatible profiles; counts exact among equal bodies.
legacy=Counter(int(np.count_nonzero(old[i]!=old[j])) for ids in oldbody.values() for i,j in itertools.combinations(ids,2)); assert legacy[2]==2604
print(json.dumps({'new_rows':len(new),'naive_duplicate_rows':len(naive)-len(set(map(tuple,naive))),'interpolation_rows':len(old)+len(new),'cross_incompatible_d5_pairs':sum(counts),'cross_projection_masks':len(counts),'cross_minimum_distance':5,'witness':witness,'legacy_same_body_pair_distance_counts':dict(legacy)},indent=2))
