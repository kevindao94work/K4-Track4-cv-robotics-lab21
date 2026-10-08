"""Commit an accepted checkpoint and verify the private remote SHA."""
import argparse,json,subprocess
from pathlib import Path

def cmd(args):return subprocess.check_output(args,text=True).strip()
def main():
    p=argparse.ArgumentParser();p.add_argument('checkpoint');p.add_argument('message');p.add_argument('--evidence',nargs='+',required=True);a=p.parse_args()
    if cmd(['git','branch','--show-current'])!='main':raise RuntimeError('Expected main')
    repo=json.loads(cmd(['gh','repo','view','--json','visibility,nameWithOwner,url']))
    if repo['visibility']!='PRIVATE' or repo['nameWithOwner']!='kevindao94work/cv-robotics-lab21':raise RuntimeError('Unexpected remote identity/visibility')
    for evidence in a.evidence:
        if not Path(evidence).is_file():raise ValueError('Missing acceptance evidence '+evidence)
    log=Path('reports/checkpoints.json');states=json.loads(log.read_text()) if log.exists() else {}
    states[a.checkpoint]={'status':'PASS','evidence':a.evidence,'remote_status':'verification recorded in reports/push_verification.jsonl after commit'}
    log.write_text(json.dumps(states,indent=2))
    subprocess.run(['git','add','.'],check=True)
    names=cmd(['git','diff','--cached','--name-only']).splitlines()
    forbidden=['data/','weights/','.venv/','TrackEval/','.env']
    if any(any(n.startswith(x) for x in forbidden) or n.endswith(('.pt','.mp4','.zip')) for n in names):raise RuntimeError('Unsafe staged assets')
    subprocess.run(['git','diff','--cached','--check'],check=True)
    subprocess.run(['git','commit','-m',a.message],check=True)
    subprocess.run(['git','push','-u','origin','main'],check=True)
    local=cmd(['git','rev-parse','HEAD']);remote=cmd(['git','ls-remote','origin','refs/heads/main']).split()[0]
    if local!=remote:raise RuntimeError('SHA mismatch')
    with Path('reports/push_verification.jsonl').open('a') as f:f.write(json.dumps({'checkpoint':a.checkpoint,'commit':local,'remote_sha':remote,'status':'PUSHED'})+'\n')
    print(local,remote,'PUSHED')
if __name__=='__main__':main()
