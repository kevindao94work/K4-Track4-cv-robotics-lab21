"""Verify the installed environment, weights, all five trackers and video codec."""
import importlib.metadata,json,platform,subprocess,tempfile
from pathlib import Path
import cv2,numpy as np,torch,trackeval
from lab21.detector import Detector
from lab21.trackers import NAMES,create_tracker,update_tracker
from lab21.reporting import sha256

def main():
    torch.set_num_threads(4)
    d=Detector();d.detect(np.zeros((320,320,3),np.uint8))
    trackers={};img=np.random.default_rng(42).integers(0,256,(240,320,3),dtype=np.uint8)
    for name in NAMES:
        t,reid=create_tracker(name)
        for _ in range(4):r=update_tracker(t,np.array([[20,20,80,180,.9,0]],np.float32),img)
        if not len(r):raise RuntimeError(f'{name} smoke produced no tracks')
        trackers[name]={'output_shape':list(r.shape),'reid_enabled':bool(reid and t.generates_embeddings and t._reid_encoder is not None)}
    with tempfile.TemporaryDirectory() as tmp:
        p=str(Path(tmp)/'codec.mp4');w=cv2.VideoWriter(p,cv2.VideoWriter_fourcc(*'mp4v'),25,(320,240))
        if not w.isOpened():raise RuntimeError('Video codec unavailable')
        w.write(img);w.release();cap=cv2.VideoCapture(p);ok,_=cap.read();cap.release()
        if not ok:raise RuntimeError('Cannot decode written video')
    subprocess.run(['.venv/bin/python','-m','ipykernel','install','--prefix',str(Path('.venv').resolve()),'--name','cv_robotics_lab21'],check=True)
    m={'python':platform.python_version(),'platform':platform.platform(),'detector_device':d.device,'reid_device':'cpu','torch':torch.__version__,'cuda_available':torch.cuda.is_available(),'mps_available':torch.backends.mps.is_available(),'versions':{k:importlib.metadata.version(k) for k in ['ultralytics','boxmot','numpy','opencv-python','trackeval']},'trackeval_commit':subprocess.check_output(['git','-C','TrackEval','rev-parse','HEAD'],text=True).strip(),'weights':{p.name:sha256(p) for p in Path('weights').glob('*.pt')},'trackers':trackers,'codec':'mp4v write/read passed'}
    Path('artifacts/environment.json').write_text(json.dumps(m,indent=2));print(json.dumps(m,indent=2))
if __name__=='__main__':main()
