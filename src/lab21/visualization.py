import cv2

def color(tid):
    return tuple(64+((int(tid)*p)%192) for p in (37,67,97))

def draw(frame,tracks,title=''):
    frame=frame.copy()
    for x1,y1,x2,y2,tid,conf,cls in tracks:
        c=color(tid);cv2.rectangle(frame,(int(x1),int(y1)),(int(x2),int(y2)),c,2)
        cv2.putText(frame,f'ID {int(tid)} {conf:.2f}',(int(x1),max(15,int(y1)-4)),cv2.FONT_HERSHEY_SIMPLEX,.45,c,1)
    cv2.putText(frame,title,(15,25),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,255,255),2)
    return frame
