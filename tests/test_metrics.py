import pytest
from lab21.metrics import box_iou

def test_iou():
    assert box_iou([0,0,2,2],[0,0,2,2])==1
    assert box_iou([0,0,2,2],[2,2,3,3])==0
    assert box_iou([0,0,0,0],[0,0,0,0])==0
    assert box_iou([0,0,2,2],[1,1,3,3])==pytest.approx(1/7)
    with pytest.raises(ValueError):box_iou([2,0,1,1],[0,0,1,1])
