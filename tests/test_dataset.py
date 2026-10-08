import zipfile
import pytest
from lab21.dataset import frames
from scripts.download_data import extract

def test_numeric_order(tmp_path):
    for n in range(1,12):(tmp_path/f'{n}.jpg').touch()
    assert [int(p.stem) for p in frames(tmp_path)]==list(range(1,12))
    (tmp_path/'2.jpg').unlink()
    with pytest.raises(ValueError): frames(tmp_path)
def test_zip_slip(tmp_path):
    p=tmp_path/'bad.zip'
    with zipfile.ZipFile(p,'w') as z:z.writestr('../escape.txt','no')
    with pytest.raises(ValueError):extract(p,tmp_path/'out')
    assert not (tmp_path/'escape.txt').exists()
