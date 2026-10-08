"""Evaluate only real video_1 full-sequence experiments with MOT17 preprocessing."""
import csv,json
from pathlib import Path
from lab21.evaluation import evaluate
from lab21.reporting import sha256
m=json.loads(Path('artifacts/scene_analysis/dataset_metadata.json').read_text())['video_1'];rows=[]
for mp in sorted(Path('runs/experiments/video_1').glob('*/*_metadata.json')):
    meta=json.loads(mp.read_text())
    if meta['max_frames'] is not None:continue
    if meta['bbox_origin']!='one-based':raise ValueError('MOT origin must be corrected before evaluation')
    tp=mp.with_name('video_1.txt')
    scores=evaluate(m['gt'][0],tp,Path('data/evaluation')/sha256(tp),length=m['frames'])
    rows.append({'experiment_id':mp.parent.name,'tracker':meta['tracker'],'conf':meta['conf'],'iou':meta['iou'],**scores,'tracks_sha256':sha256(tp)})
Path('artifacts/metrics/video_1_candidates.json').write_text(json.dumps(rows,indent=2))
with Path('artifacts/metrics/video_1_candidates.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
print(json.dumps(rows,indent=2))
