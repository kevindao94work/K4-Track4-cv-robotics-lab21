import importlib.metadata,json,time
from pathlib import Path
import cv2,numpy as np,torch
from .dataset import frames
from .detector import Detector
from .trackers import create_tracker,update_tracker
from .mot_writer import write_frame,validate_rows
from .visualization import draw
from .reporting import sha256

def run(source,seq_name,tracker='bytetrack',conf=.30,iou=.50,out='runs/thu_nhanh',save_video=False,max_frames=None,start_frame=1,device=None,cache_root='data/detection_cache'):
    np.random.seed(42);torch.manual_seed(42)
    paths=frames(source)
    if not 1<=start_frame<=len(paths):raise ValueError('Invalid start frame')
    end=len(paths) if max_frames is None else min(len(paths),start_frame+max_frames-1)
    paths=paths[start_frame-1:end];out=Path(out);out.mkdir(parents=True,exist_ok=True)
    target=out/f'{seq_name}.txt';meta_path=out/f'{seq_name}_metadata.json'
    if target.exists() or meta_path.exists():raise FileExistsError(f'Refusing overwrite: {target}')
    det=Detector(device=device);t,reid=create_tracker(tracker,'cpu');start=time.perf_counter();writer=None
    cache=Path(cache_root)/det.model_hash/f'{seq_name}_conf{conf:.2f}_iou{iou:.2f}_640_nms';cache.mkdir(parents=True,exist_ok=True)
    try:
        with target.open('w') as handle:
            for index,path in enumerate(paths,start_frame):
                img=cv2.imread(str(path))
                if img is None:raise ValueError(f'Unreadable frame {path}')
                frame_hash=sha256(path);cp=cache/f'{index}_{frame_hash}.npy'
                if cp.exists():d=np.load(cp,allow_pickle=False)
                else:
                    d=det.detect(img,conf,iou);np.save(cp,d)
                tracks=update_tracker(t,d,img)
                write_frame(handle,index,tracks)
                if save_video:
                    rendered=draw(img,tracks,f'{seq_name} {tracker} c={conf:.2f} iou={iou:.2f} frame={index}')
                    if writer is None:
                        h,w=img.shape[:2];writer=cv2.VideoWriter(str(out/f'{seq_name}_preview.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),25,(w,h))
                        if not writer.isOpened():raise RuntimeError('Video writer unavailable')
                    writer.write(rendered)
                if index%50==0:print(f'{seq_name} {tracker}: {index}/{end}',flush=True)
    finally:
        if writer:writer.release()
    elapsed=time.perf_counter()-start
    validate_rows(np.loadtxt(target,delimiter=',',ndmin=2))
    metadata={'sequence':seq_name,'tracker':tracker,'conf':conf,'iou':iou,'source':str(Path(source).resolve()),'input_frames':len(frames(source)),'frames_processed':len(paths),'frame_range':[start_frame,end],'start_frame':start_frame,'max_frames':max_frames,'model':'yolo26n.pt','model_sha256':det.model_hash,'imgsz':640,'classes':[0],'nms_mode':'one-to-many; nms=None','device':det.device,'reid_device':'cpu' if reid else None,'reid_enabled':bool(reid and t.generates_embeddings and t._reid_encoder is not None),'reid_sha256':sha256('weights/osnet_x0_25_msmt17.pt') if reid else None,'elapsed_seconds':elapsed,'fps':len(paths)/elapsed,'tracks_sha256':sha256(target),'versions':{k:importlib.metadata.version(k) for k in ['torch','ultralytics','boxmot','numpy']},'seed':42,'completed_at':time.strftime('%Y-%m-%dT%H:%M:%S%z')}
    meta_path.write_text(json.dumps(metadata,indent=2));return metadata
