import numpy as np
import pytest
from lab21.evaluation import evaluate

def test_real_evaluator_regression(tmp_path):
    gt=np.array([[1,1,0,0,20,40,1,1,1],[2,1,0,0,20,40,1,1,1],[3,1,0,0,20,40,1,1,1],[4,1,0,0,20,40,1,1,1]])
    g=tmp_path/'gt.txt';np.savetxt(g,gt,delimiter=',')
    pred=np.column_stack([gt[:,:6],np.ones(4),-np.ones((4,3))]);p=tmp_path/'p.txt';np.savetxt(p,pred,delimiter=',')
    r=evaluate(g,p,tmp_path/'perfect',length=4)
    for k in ['HOTA','MOTA','IDF1']:assert r[k]==pytest.approx(100)
    pred[2:,1]=2;np.savetxt(p,pred,delimiter=',');r=evaluate(g,p,tmp_path/'switch',length=4);assert r['IDSW']==1;assert r['IDF1']<100
    np.savetxt(p,pred[:2],delimiter=',');r=evaluate(g,p,tmp_path/'missing',length=4);assert r['FN']==2;assert r['MOTA']<100
    with pytest.raises(ValueError):evaluate(g,p,tmp_path/'wrong',length=5)
