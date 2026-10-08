import numpy as np

def validate_rows(rows):
    rows=np.asarray(rows,dtype=float)
    if rows.ndim!=2 or rows.shape[1]!=10 or not len(rows): raise ValueError('Expected nonempty 10-column MOT rows')
    if not np.isfinite(rows).all(): raise ValueError('Nonfinite MOT values')
    if (rows[:,:2]<1).any() or (rows[:,:2]!=np.floor(rows[:,:2])).any(): raise ValueError('Invalid frame/ID')
    if (rows[:,4:6]<=0).any() or ((rows[:,6]<0)|(rows[:,6]>1)).any(): raise ValueError('Invalid bbox/confidence')
    if (np.diff(rows[:,0])<0).any(): raise ValueError('Unsorted frames')
    if len(set(map(tuple,rows[:,:2])))!=len(rows): raise ValueError('Duplicate frame/ID')
    if (rows[:,7:]!=-1).any(): raise ValueError('Invalid MOT sentinel')
    return rows

def write_frame(handle,frame,tracks):
    rows=[]
    for x1,y1,x2,y2,tid,conf,cls in tracks:
        rows.append([frame,tid,x1,y1,x2-x1,y2-y1,conf,-1,-1,-1])
    if rows:
        rows=validate_rows(rows)
        for f,tid,x,y,w,h,c,*_ in rows: handle.write(f'{int(f)},{int(tid)},{x:.3f},{y:.3f},{w:.3f},{h:.3f},{c:.6f},-1,-1,-1\n')
