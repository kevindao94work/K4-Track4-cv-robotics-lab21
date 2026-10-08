"""Download the assigned archive and extract safely; never substitute data."""
from pathlib import Path
import argparse, hashlib, json, shutil, stat, time, zipfile
URL='https://drive.google.com/file/d/1UeVPQd6j5pSzxoJDcKJrerT9SL3vJLDt/view'
def extract(archive, destination):
    destination=Path(destination).resolve()
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            target=(destination/member.filename).resolve()
            if not target.is_relative_to(destination) or stat.S_ISLNK(member.external_attr >> 16):
                raise ValueError('Unsafe archive entry: '+member.filename)
        bad=z.testzip()
        if bad: raise ValueError('Corrupt archive entry: '+bad)
        z.extractall(destination)
def main():
    import gdown
    p=argparse.ArgumentParser(); p.add_argument('--archive',type=Path,default=Path('data/data_lab21.zip')); a=p.parse_args()
    a.archive.parent.mkdir(parents=True,exist_ok=True)
    if not zipfile.is_zipfile(a.archive):
        for attempt in range(3):
            try:
                gdown.download(URL,str(a.archive),fuzzy=True,resume=True)
                if not zipfile.is_zipfile(a.archive): raise ValueError('Response is not a ZIP archive')
                break
            except Exception:
                if attempt==2: raise
                time.sleep(2*(attempt+1))
    root=Path('data/extracted')
    extract(a.archive,root)
    candidates=[p.parent for p in root.rglob('video_1') if all((p.parent/f'video_{i}'/'img1').is_dir() for i in range(1,6))]
    if len(candidates)!=1: raise ValueError(f'Expected one dataset root, found {candidates}')
    digest=hashlib.file_digest(a.archive.open('rb'),'sha256').hexdigest()
    Path('data/source.json').write_text(json.dumps({'url':URL,'sha256':digest,'root':str(candidates[0].resolve())},indent=2))
    print(candidates[0].resolve())
if __name__=='__main__': main()
