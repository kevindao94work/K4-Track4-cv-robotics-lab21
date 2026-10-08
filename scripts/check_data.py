import argparse,json,os
from pathlib import Path
from lab21.dataset import inspect
p=argparse.ArgumentParser();p.add_argument('--lab-data-root',default=os.getenv('LAB_DATA'));a=p.parse_args()
if not a.lab_data_root: p.error('--lab-data-root or LAB_DATA required')
r=inspect(a.lab_data_root); out=Path('artifacts/scene_analysis/dataset_metadata.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
