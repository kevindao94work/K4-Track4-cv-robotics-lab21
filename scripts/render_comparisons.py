"""Regenerate synchronized contact sheets for completed controlled runs."""
from pathlib import Path
import subprocess,sys
for i in range(1,6):
    v=f'video_{i}';base=Path('runs/experiments')/v;c='015' if i<=2 else '030'
    pairs=[('trackers','bytetrack_conf030_iou050_f1_150','botsort_conf030_iou050_f1_150',[1,75,150]),('confidence','bytetrack_conf015_iou050_f1_150','bytetrack_conf050_iou050_f1_150',[50,100,150]),('iou',f'bytetrack_conf{c}_iou040_f1_150',f'bytetrack_conf{c}_iou070_f1_150',[50,100,150]),('verification',f'bytetrack_conf{c}_iou050_f301_150',f'botsort_conf{c}_iou050_f301_150',[301,375,450])]
    for name,left,right,frames in pairs:
        subprocess.run([sys.executable,'scripts/compare_runs.py','--source',f'data/extracted/data_lab21/{v}/img1','--left',str(base/left/f'{v}.txt'),'--right',str(base/right/f'{v}.txt'),'--frame',*map(str,frames),'--out',f'artifacts/comparisons/{v}_{name}.jpg'],check=True)
