import hashlib,json
from pathlib import Path
import numpy as np
from .mot_writer import validate_rows
from .dataset import frames

def sha256(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def validate_submission(folder):
    selected=json.loads(Path('reports/selected_configs.json').read_text())
    dataset=json.loads(Path('artifacts/scene_analysis/dataset_metadata.json').read_text())
    for i in range(1,6):
        name=f'video_{i}';p=folder/f'{name}.txt';m=json.loads((folder/f'{name}_metadata.json').read_text());c=selected[name]
        if not c.get('reason') or not c.get('evidence'):raise ValueError('Missing selection evidence')
        for evidence in c['evidence']:
            if not Path(evidence).is_file():raise ValueError('Missing evidence artifact')
        if Path(c['full_sequence_metadata']).resolve()!=(folder/f'{name}_metadata.json').resolve():raise ValueError('Wrong selected metadata path')
        rows=validate_rows(np.loadtxt(p,delimiter=',',ndmin=2))
        if m['bbox_origin']!='one-based':raise ValueError('Wrong MOT coordinate convention')
        if m['sequence']!=name or m['max_frames'] is not None or m['start_frame']!=1:raise ValueError('Partial/wrong sequence')
        if m['frames_processed']!=dataset[name]['frames'] or m['frames_processed']!=len(frames(m['source'])):raise ValueError('Incomplete sequence')
        if rows[:,0].max()>m['frames_processed']:raise ValueError('Out-of-range frame')
        for key in ('tracker','conf','iou'):
            if m[key]!=c[key]:raise ValueError('Configuration mismatch')
        if m['model']!='yolo26n.pt' or m['imgsz']!=640 or m['classes']!=[0]:raise ValueError('Wrong model settings')
        if m['dataset_frame_sha256']!=dataset[name]['frame_sha256']:raise ValueError('Dataset fingerprint mismatch')
        if m['model_sha256']!=sha256('weights/yolo26n.pt'):raise ValueError('Model hash mismatch')
        if m['reid_enabled'] and m['reid_sha256']!=sha256('weights/osnet_x0_25_msmt17.pt'):raise ValueError('Re-ID hash mismatch')
        if m['tracks_sha256']!=sha256(p):raise ValueError('Modified output')
        if str(Path(m['source']).parent.resolve())!=dataset[name]['source']:raise ValueError('Wrong source')
        if m['tracker'] in ('botsort','strongsort','deepocsort') and not m['reid_enabled']:raise ValueError('Re-ID disabled')
