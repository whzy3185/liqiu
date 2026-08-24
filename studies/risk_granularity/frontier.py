"""Shared risk-resource frontier utilities."""
def pareto_front(points,cost_key='cost',risk_key='risk'):
 out=[]
 for i,p in enumerate(points):
  dominated=any(j!=i and q[cost_key]<=p[cost_key] and q[risk_key]<=p[risk_key] and (q[cost_key]<p[cost_key] or q[risk_key]<p[risk_key]) for j,q in enumerate(points))
  item=dict(p);item['pareto_dominated']=dominated
  if not dominated:out.append(item)
 return sorted(out,key=lambda x:(x[cost_key],x[risk_key]))
def best_risk_at_budget(points,budget,cost_key='cost',risk_key='risk'):
 feasible=[p for p in points if p[cost_key]<=budget];return min((p[risk_key] for p in feasible),default=None)
def frontier_regret(method_points,reference_points,cost_key='cost',risk_key='risk'):
 rows=[]
 for p in method_points:
  best=best_risk_at_budget(reference_points,p[cost_key],cost_key,risk_key);rows.append({**p,'best_observed_risk':best,'frontier_regret':None if best is None else p[risk_key]-best})
 return rows
def resource_regret(method_points,reference_points,risk_tolerance,cost_key='cost',risk_key='risk'):
 m=[p[cost_key] for p in method_points if p[risk_key]<=risk_tolerance];r=[p[cost_key] for p in reference_points if p[risk_key]<=risk_tolerance]
 return None if not m or not r else min(m)-min(r)
