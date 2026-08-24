"""Clean-room paper-spec GBGC baseline with disclosed deterministic choices."""
from collections import deque
import heapq
import math
import numpy as np
from scipy.sparse.csgraph import connected_components,dijkstra
def quality(adj,nodes):
 nodes=np.asarray(nodes,int);n=len(nodes)
 if n<2:return 0.0
 A=adj[nodes][:,nodes].astype(np.float64);edges=A.nnz/2;degree=np.asarray(A.sum(1)).ravel();triples=np.sum(degree*(degree-1)/2);triangles=float((A@A@A).diagonal().sum()/6) if triples>0 else 0.;return float(edges/n+(3*triangles/triples if triples>0 else 0))
def initial_balls(adj):
 count,component=connected_components(adj,directed=False);degree=np.asarray(adj.sum(1)).ravel();balls=[]
 for c in range(count):
  members=np.flatnonzero(component==c);unassigned=set(map(int,members));cap=max(1,int(math.ceil(math.sqrt(len(members)))))
  while unassigned:
   center=max(unassigned,key=lambda i:(degree[i],-i));ball=[];queue=deque([center]);seen={center}
   while queue and len(ball)<cap:
    i=queue.popleft()
    if i in unassigned:ball.append(i);unassigned.remove(i)
    neighbors=adj.indices[adj.indptr[i]:adj.indptr[i+1]]
    for j in sorted(map(int,neighbors),key=lambda x:(-degree[x],x)):
     if j in unassigned and j not in seen:seen.add(j);queue.append(j)
   if not ball:i=min(unassigned);unassigned.remove(i);ball=[i]
   balls.append(np.array(ball,int))
 return balls
def split_ball(adj,nodes):
 nodes=np.asarray(nodes,int)
 if len(nodes)<2:return None
 sub=adj[nodes][:,nodes];deg=np.asarray(sub.sum(1)).ravel();centers=np.lexsort((np.arange(len(nodes)),-deg))[:2];dist=dijkstra(sub,directed=False,indices=centers,unweighted=True);assignment=np.argmin(dist,axis=0);a=nodes[assignment==0];b=nodes[assignment==1]
 return None if not len(a) or not len(b) else (a,b)
def gain(adj,nodes):
 children=split_ball(adj,nodes)
 return (-np.inf,None) if children is None else (quality(adj,children[0])+quality(adj,children[1])-quality(adj,nodes),children)
def _pack(adj,balls,meta):
 assignment=np.empty(adj.shape[0],int)
 for k,nodes in enumerate(balls):assignment[nodes]=k
 return assignment,meta
def adaptive_assignment(adj):
 balls=initial_balls(adj);initial=len(balls);i=0
 while i<len(balls):
  delta,children=gain(adj,balls[i])
  if children is not None and delta>1e-12:balls[i]=children[0];balls.append(children[1])
  else:i+=1
 return _pack(adj,balls,{'initial_balls':initial,'final_balls':len(balls),'mode':'adaptive','paper_deviations':['deterministic degree/BFS tie breaks','E/N uses undirected edge count','zero triples imply transitivity 0']})
def fixed_ratio_assignment(adj,ratio):
 target=max(1,int(round(adj.shape[0]*ratio)));initial_nodes=initial_balls(adj);initial=len(initial_nodes);balls={i:nodes for i,nodes in enumerate(initial_nodes)};heap=[];next_id=initial;splits=0
 def push(i):
  delta,children=gain(adj,balls[i])
  if children is not None:heapq.heappush(heap,(-delta,-len(balls[i]),i,children))
 for i in balls:push(i)
 while len(balls)<target and heap:
  _,_,i,children=heapq.heappop(heap)
  if i not in balls:continue
  balls[i]=children[0];j=next_id;next_id+=1;balls[j]=children[1];splits+=1;push(i);push(j)
 ordered=[balls[i] for i in sorted(balls)]
 return _pack(adj,ordered,{'initial_balls':initial,'target_balls':target,'final_balls':len(ordered),'splits':splits,'mode':'fixed_ratio_cleanroom','paper_deviations':['Algorithm 4 score/tie-break unspecified: use quality gain then size','continue even nonpositive gain to reach target','deterministic degree/BFS ties','E/N uses undirected edge count','zero triples imply transitivity 0']})
