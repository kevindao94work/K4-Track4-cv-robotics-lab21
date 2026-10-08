import argparse,os,json
from pathlib import Path
import cv2,numpy as np
from lab21.dataset import frames
p=argparse.ArgumentParser();p.add_argument('--lab-data-root',default=os.getenv('LAB_DATA'));a=p.parse_args()
if not a.lab_data_root:p.error('Dataset root required')
out=Path('artifacts/scene_analysis');out.mkdir(parents=True,exist_ok=True)
for i in range(1,6):
    paths=frames(Path(a.lab_data_root)/f'video_{i}'/'img1'); tiles=[]
    for n in np.linspace(0,len(paths)-1,6,dtype=int):
        img=cv2.imread(str(paths[n]));h,w=img.shape[:2];tile=np.zeros((280,480,3),np.uint8)
        small=cv2.resize(img,(480,int(h*480/w)))
        if small.shape[0]>250:small=cv2.resize(img,(int(w*250/h),250))
        tile[30:30+small.shape[0],:small.shape[1]]=small
        cv2.putText(tile,f'video_{i} frame {n+1}',(10,21),cv2.FONT_HERSHEY_SIMPLEX,.6,(255,255,255),1);tiles.append(tile)
    cv2.imwrite(str(out/f'video_{i}.jpg'),np.vstack([np.hstack(tiles[:3]),np.hstack(tiles[3:])]))
