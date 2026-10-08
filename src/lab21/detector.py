from pathlib import Path
import numpy as np,torch
from ultralytics import YOLO
from .reporting import sha256

class Detector:
    def __init__(self,device=None):
        self.device=device or ('cuda:0' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
        self.model=YOLO('weights/yolo26n.pt')
        self.model_hash=sha256('weights/yolo26n.pt')
    def detect(self,frame,conf=.3,iou=.5):
        if not 0<=conf<=1 or not 0<=iou<=1:raise ValueError('Invalid thresholds')
        r=self.model.predict(frame,imgsz=640,classes=[0],conf=conf,iou=iou,device=self.device,nms=None,verbose=False)[0]
        d=r.boxes.data.cpu().numpy().astype(np.float32).reshape(-1,6)
        if len(d) and (not np.isfinite(d).all() or (d[:,2:4]<=d[:,:2]).any() or (d[:,5]!=0).any()):raise ValueError('Invalid detector output')
        return d
