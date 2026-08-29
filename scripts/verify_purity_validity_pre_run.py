"""Pre-outcome checks available before the full v1.1 purity-validity grid."""
from __future__ import annotations
import numpy as np
from studies.purity_validity.core import XOnlyMaximalGranulationTree, _cut_geometry, _route_tree, sample_family
def signature(node):
 return (tuple(node.indices.tolist()), tuple(np.round(node.center,12)), node.depth, tuple(signature(c) for c in node.children))
def main():
 x,y=sample_family('smooth_moderate',400,1); y2=np.random.default_rng(7).permutation(y)
 a=XOnlyMaximalGranulationTree(random_state=1).fit(x); b=XOnlyMaximalGranulationTree(random_state=1).fit(x)
 invariant=signature(a.root)==signature(b.root)
 leaves=_cut_geometry(a.root,y,.9); routed=_route_tree(a.root,leaves,x)
 membership={index:ball for ball,node in enumerate(leaves) for index in node.indices}
 consistency=float(np.mean([routed[i]==membership[i] for i in range(len(x))]))
 print({'LABEL_INVARIANT_MAXIMAL_TREE':invariant,'train_routing_consistency':consistency,'depth_populated':all(node.depth is not None for node in leaves),'note':'label permutation was intentionally not passed to X-only fit'})
if __name__=='__main__':main()
