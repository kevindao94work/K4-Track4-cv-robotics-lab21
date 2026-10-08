"""One-time correction of pre-final development runs to MOT's (1,1) origin.

Does not alter tracking assignments, confidence, width/height or frame mapping.
Metadata flags ensure the translation cannot accidentally be applied twice.
"""
from pathlib import Path
import json,numpy as np
from lab21.reporting import sha256
for mp in Path('runs').rglob('*_metadata.json'):
    m=json.loads(mp.read_text())
    if m.get('bbox_origin')=='one-based':continue
    tp=mp.with_name(m['sequence']+'.txt');r=np.loadtxt(tp,delimiter=',',ndmin=2);r[:,2:4]+=1
    with tp.open('w') as f:
        for frame,tid,x,y,w,h,c,*_ in r:f.write(f'{int(frame)},{int(tid)},{x:.3f},{y:.3f},{w:.3f},{h:.3f},{c:.6f},-1,-1,-1\n')
    m['bbox_origin']='one-based';m['tracks_sha256']=sha256(tp);m['format_correction']='Translate pre-final zero-based left/top by +1 to conform to MOTChallenge; assignments unchanged.'
    mp.write_text(json.dumps(m,indent=2))
    print(tp)
