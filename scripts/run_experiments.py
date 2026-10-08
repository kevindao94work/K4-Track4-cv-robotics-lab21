"""Run controlled experiments, resuming only verified matching outputs."""
import argparse,csv,json,os
from pathlib import Path
from lab21.pipeline import run
from lab21.reporting import sha256
FIELDS=['video','experiment_id','tracker','conf','iou','frames','frame_range','reid_enabled','device','elapsed_seconds','fps','observations','decision','reason','status']
def execute(root,video,tracker,conf,iou,start,count):
    eid=f'{tracker}_conf{round(conf*100):03}_iou{round(iou*100):03}_f{start}_{count}'
    out=Path('runs/experiments')/video/eid;mp=out/f'{video}_metadata.json';tp=out/f'{video}.txt'
    if mp.exists():
        m=json.loads(mp.read_text())
        if m['tracks_sha256']!=sha256(tp) or any(m[k]!=v for k,v in [('tracker',tracker),('conf',conf),('iou',iou),('start_frame',start),('max_frames',count)]):raise ValueError('Resume metadata mismatch')
    else:m=run(Path(root)/video/'img1',video,tracker,conf,iou,out,True,count,start)
    log=Path('reports/experiment_log.csv');rows=[]
    if log.exists():
        with log.open() as f:rows=list(csv.DictReader(f))
    if not any(r['video']==video and r['experiment_id']==eid for r in rows):
        rows.append(dict(video=video,experiment_id=eid,tracker=tracker,conf=conf,iou=iou,frames=m['frames_processed'],frame_range=str(m['frame_range']),reid_enabled=m['reid_enabled'],device=m['device'],elapsed_seconds=m['elapsed_seconds'],fps=m['fps'],observations='Awaiting visual review',decision='pending',reason='Requires observed evidence',status='completed'))
        with log.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    return m

def main():
    p=argparse.ArgumentParser();p.add_argument('--lab-data-root',default=os.getenv('LAB_DATA'));p.add_argument('--video',nargs='+',default=[f'video_{i}' for i in range(1,6)]);p.add_argument('--phase',choices=['tracker','conf','iou','verify'],required=True);p.add_argument('--tracker',default='bytetrack');p.add_argument('--conf',type=float,default=.3);p.add_argument('--frames',type=int,default=150);p.add_argument('--start',type=int,default=1);a=p.parse_args()
    if not a.lab_data_root:p.error('Dataset root required')
    for v in a.video:
        if a.phase=='tracker':configs=[(t,.3,.5) for t in ['bytetrack','botsort']]
        elif a.phase=='conf':configs=[(a.tracker,c,.5) for c in [.15,.3,.5]]
        elif a.phase=='iou':configs=[(a.tracker,a.conf,i) for i in [.4,.5,.7]]
        else:configs=[(a.tracker,a.conf,.5)]
        for t,c,i in configs:execute(a.lab_data_root,v,t,c,i,a.start,a.frames)
if __name__=='__main__':main()
