"""Run the evidence-selected configurations on all input frames."""
import argparse,json,os
from pathlib import Path
from lab21.pipeline import run
from lab21.reporting import sha256
p=argparse.ArgumentParser();p.add_argument('--lab-data-root',default=os.getenv('LAB_DATA'));a=p.parse_args()
if not a.lab_data_root:p.error('Dataset root required')
path=Path('reports/selected_configs.json');configs=json.loads(path.read_text())
for name,c in configs.items():
    mp=Path('runs/nop_bai')/f'{name}_metadata.json';tp=mp.with_name(f'{name}.txt')
    if mp.exists():
        m=json.loads(mp.read_text())
        if m['tracks_sha256']!=sha256(tp) or m['max_frames'] is not None or any(m[k]!=c[k] for k in ['tracker','conf','iou']):raise ValueError('Invalid existing final run')
    else:m=run(Path(a.lab_data_root)/name/'img1',name,c['tracker'],c['conf'],c['iou'],'runs/nop_bai',True)
    c['full_sequence_metadata']=str(mp)
    path.write_text(json.dumps(configs,ensure_ascii=False,indent=2))
