import numpy as np

def box_iou(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    if a.shape!=(4,) or b.shape!=(4,) or not np.isfinite([a,b]).all() or (a[2:]<a[:2]).any() or (b[2:]<b[:2]).any(): raise ValueError('Invalid xyxy box')
    inter=np.maximum(0,np.minimum(a[2:],b[2:])-np.maximum(a[:2],b[:2])).prod()
    union=np.prod(a[2:]-a[:2])+np.prod(b[2:]-b[:2])-inter
    return float(inter/union) if union>0 else 0.
