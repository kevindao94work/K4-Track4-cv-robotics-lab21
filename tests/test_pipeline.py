import io
import numpy as np
from lab21.trackers import create_tracker,update_tracker
from lab21.mot_writer import write_frame,validate_rows

def test_motion_state_and_mot():
    t,_=create_tracker('bytetrack');img=np.zeros((240,320,3),np.uint8);f=io.StringIO()
    for n in range(1,6):
        tracks=update_tracker(t,np.array([[20+n,20,80+n,180,.9,0]],np.float32),img);write_frame(f,n,tracks)
    rows=validate_rows(np.loadtxt(io.StringIO(f.getvalue()),delimiter=',',ndmin=2));assert len(set(rows[:,1]))==1
    fresh,_=create_tracker('bytetrack');assert fresh.frame_count==0
