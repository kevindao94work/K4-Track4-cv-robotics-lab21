import argparse
from pathlib import Path
import cv2,numpy as np
from lab21.dataset import frames
from lab21.visualization import draw
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--left',required=True);p.add_argument('--right',required=True);p.add_argument('--frame',type=int,nargs='+',required=True);p.add_argument('--out',required=True);a=p.parse_args()
left=np.loadtxt(a.left,delimiter=',',ndmin=2);right=np.loadtxt(a.right,delimiter=',',ndmin=2);paths=frames(a.source);tiles=[]
for f in a.frame:
    pair=[]
    for rows,title in [(left,Path(a.left).parent.name),(right,Path(a.right).parent.name)]:
        r=rows[rows[:,0]==f];tracks=np.column_stack([r[:,2],r[:,3],r[:,2]+r[:,4],r[:,3]+r[:,5],r[:,1],r[:,6],np.zeros(len(r))])
        img=draw(cv2.imread(str(paths[f-1])),tracks,title+f' frame {f}');h,w=img.shape[:2];pair.append(cv2.resize(img,(640,round(h*640/w))))
    tiles.append(np.hstack(pair))
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);cv2.imwrite(str(out),np.vstack(tiles))
