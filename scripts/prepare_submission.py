import hashlib,shutil,zipfile
from pathlib import Path
from lab21.reporting import validate_submission

def main():
    validate_submission(Path('runs/nop_bai'))
    report=Path('reports/BAO_CAO_LAB21.md')
    if not report.is_file():raise ValueError('Missing report')
    files=[Path(f'runs/nop_bai/video_{i}.txt') for i in range(1,6)]+[report]
    out=Path('submission');out.mkdir(exist_ok=True)
    for f in files:shutil.copy2(f,out/f.name)
    with zipfile.ZipFile('submission.zip','w',zipfile.ZIP_DEFLATED) as z:
        for f in files:z.write(out/f.name,'submission/'+f.name)
    with zipfile.ZipFile('submission.zip') as z:
        assert z.testzip() is None
        assert set(z.namelist())=={'submission/'+f.name for f in files}
        for f in files:assert z.read('submission/'+f.name)==f.read_bytes()
    print('Validated submission.zip')
if __name__=='__main__':main()
