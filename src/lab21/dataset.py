from pathlib import Path
import cv2, hashlib, json, configparser
import numpy as np

def frames(source):
    paths=list(Path(source).glob('*.jpg'))
    if not paths or any(not p.stem.isdigit() for p in paths): raise ValueError('Missing frames or nonnumeric filenames')
    paths.sort(key=lambda p:int(p.stem))
    ids=[int(p.stem) for p in paths]
    if len(set(ids))!=len(ids) or ids!=list(range(1,len(ids)+1)): raise ValueError('Frames must be contiguous and 1-based')
    return paths

def inspect(root):
    result={}
    for i in range(1,6):
        name=f'video_{i}'; folder=Path(root)/name; paths=frames(folder/'img1'); sizes=set(); h=hashlib.sha256()
        for p in paths:
            raw=p.read_bytes(); h.update(p.name.encode()); h.update(raw)
            img=cv2.imread(str(p))
            if img is None: raise ValueError(f'Unreadable frame: {p}')
            sizes.add(tuple(img.shape[:2]))
        gt=list(folder.rglob('gt.txt'))
        if i==1 and len(gt)!=1: raise ValueError(f'Expected one real GT file, found {gt}')
        info=configparser.ConfigParser(); info.read(folder/'seqinfo.ini')
        fps=info.getfloat('Sequence','frameRate',fallback=None)
        labels=None
        if i==1:
            a=np.loadtxt(gt[0],delimiter=',',ndmin=2)
            if a.shape[1]!=9 or not np.isfinite(a).all() or (a[:,4:6]<=0).any():raise ValueError('Invalid original MOT17 GT')
            if a[:,0].min()!=1 or a[:,0].max()!=len(paths):raise ValueError('GT range differs from frames')
            labels={'columns':9,'frame_range':[int(a[:,0].min()),int(a[:,0].max())],'annotated_frames':len(set(a[:,0])),'classes':{str(int(k)):int((a[:,7]==k).sum()) for k in np.unique(a[:,7])},'valid_person_rows':int(((a[:,6]==1)&(a[:,7]==1)).sum()),'coordinate_convention':'MOTChallenge left/top/width/height; 1-based frames; original GT retained','preprocessing':'MOT17 distractors and zero-marked boxes handled by TrackEval'}
        result[name]={'fps':fps,'gt_inspection':labels,'source':str(folder.resolve()),'frames':len(paths),'dimensions':sorted(sizes),'frame_sha256':h.hexdigest(),'gt':[str(p.resolve()) for p in gt]}
    return result
