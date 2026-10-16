"""Deterministic geometry conversion in model-local millimetres."""
import math

def arc_points(start,mid,end,tolerance=.025):
 """Approximate a circular arc through three points, preserving endpoints."""
 x1,y1=start;x2,y2=mid;x3,y3=end
 det=2*(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2))
 if abs(det)<1e-10:raise ValueError('Degenerate circular arc')
 a=x1*x1+y1*y1;b=x2*x2+y2*y2;c=x3*x3+y3*y3
 cx=(a*(y2-y3)+b*(y3-y1)+c*(y1-y2))/det
 cy=(a*(x3-x2)+b*(x1-x3)+c*(x2-x1))/det
 radius=math.hypot(x1-cx,y1-cy)
 angles=[math.atan2(y-cy,x-cx) for x,y in [start,mid,end]]
 sweep=(angles[2]-angles[0])%(2*math.pi)
 if (angles[1]-angles[0])%(2*math.pi)>sweep:sweep-=2*math.pi
 step=2*math.acos(max(-1,min(1,1-tolerance/radius)))
 count=max(2,math.ceil(abs(sweep)/step))
 points=[[round(cx+radius*math.cos(angles[0]+sweep*i/count),6),round(cy+radius*math.sin(angles[0]+sweep*i/count),6)] for i in range(count+1)]
 points[0]=start;points[-1]=end
 return points

def outline_polygon(edges):
 """Order one closed Edge.Cuts loop; never rely on file serialization order."""
 if not edges:raise ValueError('Missing board outline')
 pending=list(edges[1:]);points=list(edges[0])
 while pending:
  matches=[(i,b if a==points[-1] else a) for i,(a,b) in enumerate(pending) if a==points[-1] or b==points[-1]]
  if len(matches)!=1:raise ValueError('Outline is open, branched or has multiple loops')
  i,nxt=matches[0];pending.pop(i);points.append(nxt)
 if points[-1]!=points[0]:raise ValueError('Outline is not closed')
 return points[:-1]
