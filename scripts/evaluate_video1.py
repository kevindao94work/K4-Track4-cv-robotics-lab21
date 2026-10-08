import argparse,csv,json,os
from pathlib import Path
from lab21.evaluation import evaluate
from lab21.reporting import sha256
p=argparse.ArgumentParser();p.add_argument('--lab-data-root',default=os.getenv('LAB_DATA'));p.add_argument('--prediction',default='runs/nop_bai/video_1.txt');p.add_argument('--out',default='artifacts/metrics');a=p.parse_args()
if not a.lab_data_root:p.error('Dataset root required')
m=json.loads(Path('artifacts/scene_analysis/dataset_metadata.json').read_text())['video_1'];out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
r=evaluate(m['gt'][0],a.prediction,Path('data/evaluation')/sha256(a.prediction),length=m['frames'])
with (out/'video_1_metrics.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(r));w.writeheader();w.writerow(r)
(out/'video_1_evaluation.md').write_text('# Đánh giá video_1 bằng TrackEval\n\nĐơn vị HOTA, DetA, AssA, MOTA, IDF1: phần trăm. MOT17 preprocessing bật; loại distractors theo GT gốc.\n\n'+ '\n'.join(f'- {k}: {v}' for k,v in r.items())+'\n\nPrediction SHA256: '+sha256(a.prediction)+'\nGT SHA256: '+sha256(m['gt'][0]))
print(r)
