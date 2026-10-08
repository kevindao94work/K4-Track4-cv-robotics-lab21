import cv2

def color(tid):
    return tuple(64+((int(tid)*p)%192) for p in (37,67,97))

def draw(frame,tracks,title=''):
    frame=frame.copy()
    scale=max(.5,min(1.0,frame.shape[1]/1500))
    for x1,y1,x2,y2,tid,conf,cls in tracks:
        c=color(tid);cv2.rectangle(frame,(int(x1),int(y1)),(int(x2),int(y2)),c,2)
        label=f'ID {int(tid)} {conf:.2f}';(tw,th),_=cv2.getTextSize(label,cv2.FONT_HERSHEY_SIMPLEX,scale,1)
        tx=max(0,int(x1));ty=max(th+4,int(y1)-3)
        cv2.rectangle(frame,(tx,ty-th-3),(tx+tw+3,ty+3),(0,0,0),-1)
        cv2.putText(frame,label,(tx+1,ty),cv2.FONT_HERSHEY_SIMPLEX,scale,c,1,cv2.LINE_AA)
    if title:
        (tw,th),_=cv2.getTextSize(title,cv2.FONT_HERSHEY_SIMPLEX,scale,1)
        cv2.rectangle(frame,(0,0),(min(frame.shape[1],tw+24),th+18),(0,0,0),-1)
        cv2.putText(frame,title,(10,th+8),cv2.FONT_HERSHEY_SIMPLEX,scale,(0,255,255),1,cv2.LINE_AA)
    return frame
