from pathlib import Path
import numpy as np
import boxmot
NAMES=('bytetrack','ocsort','botsort','strongsort','deepocsort')
APPEARANCE=('botsort','strongsort','deepocsort')

def create_tracker(name,device='cpu',reid_model='weights/osnet_x0_25_msmt17.pt'):
    if name not in NAMES:raise ValueError(f'Unknown tracker {name}')
    enabled=name in APPEARANCE
    from boxmot.trackers.specs import TrackerSpec
    from boxmot.reid.specs import ReIDEncoderSpec
    from .reporting import sha256
    tracker=boxmot.create_tracker(TrackerSpec(name))
    if enabled:
        tracker.configure_reid(ReIDEncoderSpec(backend='pytorch',artifact=str(Path(reid_model).resolve()),artifact_sha256=sha256(reid_model),device=device,precision='fp32',preprocessing='resize'))
    if enabled and not tracker.generates_embeddings:raise RuntimeError("Re-ID is disabled")
    return tracker,enabled

def update_tracker(tracker,detections,frame):
    detections=np.asarray(detections,dtype=np.float32).reshape(-1,6)
    output=np.asarray(tracker.update(detections,frame),dtype=float)
    if not output.size:return np.empty((0,7))
    if output.ndim!=2 or output.shape[1]!=8:raise ValueError(f'Unexpected BoxMOT output {output.shape}')
    tracks=output[:,:7].copy()
    tracks[:,4]+=1  # BoxMOT 25 uses zero-based IDs; MOT submission requires positive IDs.
    if tracker.generates_embeddings and getattr(tracker,"_reid_encoder",None) is None:raise RuntimeError("No live Re-ID encoder")
    if not np.isfinite(tracks).all() or (tracks[:,2:4]<=tracks[:,:2]).any():raise ValueError('Invalid tracker boxes')
    if not (tracks[:,6]==0).all():raise ValueError('Non-person track')
    if len(set(tracks[:,4]))!=len(tracks):raise ValueError('Duplicate IDs')
    return tracks
