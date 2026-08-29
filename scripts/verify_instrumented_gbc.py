"""Fail-closed reproduction and routing audit for instrumented clean-room GBC."""
from __future__ import annotations
import numpy as np
from baselines.gbc import GranularBallClassifier
from studies.purity_validity.core import sample_family
from studies.purity_validity.instrumented_gbc import InstrumentedGranularBallClassifier
def main():
 checks=[]
 for family in ('null_label','smooth_moderate','piecewise'):
  x,y=sample_family(family,400,1);a=GranularBallClassifier(.9,random_state=1).fit(x,y);b=InstrumentedGranularBallClassifier(.9,random_state=1).fit(x,y)
  exact=len(a.balls_)==len(b.balls_) and all(np.array_equal(u.members,v.members) and np.allclose(u.center,v.center) and np.isclose(u.radius,v.radius) and u.label==v.label and np.isclose(u.purity,v.purity) and np.array_equal(u.class_counts,v.class_counts) for u,v in zip(a.balls_,b.balls_)) and np.array_equal(a.predict(x),b.predict(x))
  construction=np.mean(b.route_construction(x)==np.array([next(i for i,n in enumerate(b.terminal_nodes_) if j in n.members) for j in range(len(x))]));native=np.mean(b.route_native(x)==np.array([next(i for i,n in enumerate(b.terminal_nodes_) if j in n.members) for j in range(len(x))]))
  checks.append({'family':family,'reproduction':bool(exact),'construction_self_routing_consistency':float(construction),'native_self_routing_consistency':float(native)})
 print({'GBC_REPRODUCTION':'PASS' if all(x['reproduction'] for x in checks) else 'FAIL','checks':checks})
if __name__=='__main__':main()
