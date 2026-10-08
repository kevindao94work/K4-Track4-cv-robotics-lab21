import numpy as np
import pytest
from lab21.trackers import create_tracker,update_tracker,NAMES
@pytest.mark.parametrize('name',NAMES)
def test_tracker(name):
    t,reid=create_tracker(name)
    img=np.random.default_rng(42).integers(0,256,(240,320,3),dtype=np.uint8)
    d=np.array([[20,20,80,180,.9,0]],np.float32)
    for _ in range(4):r=update_tracker(t,d,img)
    assert r.shape[1]==7;assert len(r)==1;assert r[0,4]>=1
    assert reid==(name in ('botsort','strongsort','deepocsort'))
    r=update_tracker(t,np.empty((0,6)),img);assert r.shape[1]==7
