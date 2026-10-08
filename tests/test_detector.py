import numpy as np,torch
from lab21.detector import Detector
from ultralytics.utils.nms import non_max_suppression

def test_detector():
    d=Detector();r=d.detect(np.zeros((320,320,3),np.uint8));assert r.shape[1]==6
    assert not d.model.predictor.model.end2end

def test_nms_iou_changes_overlap():
    # Two overlapping xywh boxes; IoU 0.6, same person class.
    pred=torch.zeros((1,5,2));pred[0,:4,:]=torch.tensor([[50,60],[50,50],[40,40],[40,40]])
    pred[0,4,:]=torch.tensor([.9,.8])
    low=non_max_suppression(pred.clone(),conf_thres=.1,iou_thres=.4,nc=1)
    high=non_max_suppression(pred.clone(),conf_thres=.1,iou_thres=.7,nc=1)
    assert len(low[0])==1;assert len(high[0])==2
