import json
import pytest
from lab21.reporting import validate_submission

def test_missing_provenance_rejected(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):validate_submission(tmp_path)
