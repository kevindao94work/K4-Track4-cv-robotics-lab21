import io
import numpy as np
import pytest
from lab21.mot_writer import validate_rows,write_frame

def test_write_and_validate():
    f=io.StringIO();write_frame(f,1,[[1,2,11,22,3,.8,0]])
    a=np.loadtxt(io.StringIO(f.getvalue()),delimiter=',',ndmin=2)
    assert a.shape==(1,10);assert a[0,4:6].tolist()==[10,20];validate_rows(a)
@pytest.mark.parametrize('change', ['duplicate','nan','negative','fractional','confidence','sentinel'])
def test_reject(change):
    a=np.array([[1,1,0,0,10,20,.8,-1,-1,-1]],float)
    if change=='duplicate':a=np.repeat(a,2,axis=0)
    elif change=='nan':a[0,2]=np.nan
    elif change=='negative':a[0,4]=-1
    elif change=='fractional':a[0,0]=1.5
    elif change=='confidence':a[0,6]=2
    else:a[0,9]=0
    with pytest.raises(ValueError):validate_rows(a)
