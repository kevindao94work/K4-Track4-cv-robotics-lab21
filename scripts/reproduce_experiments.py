"""Replay every recorded experiment configuration on the assigned real dataset."""
import argparse,json,os
from pathlib import Path
from run_experiments import execute

def main():
    p=argparse.ArgumentParser();p.add_argument('--lab-data-root',default=os.getenv('LAB_DATA'));a=p.parse_args()
    if not a.lab_data_root:p.error('Dataset root required')
    for m in json.loads(Path('artifacts/experiment_manifest.json').read_text()):
        execute(a.lab_data_root,m['sequence'],m['tracker'],m['conf'],m['iou'],m['start_frame'],m['max_frames'])
if __name__=='__main__':main()
