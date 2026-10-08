import argparse
from pathlib import Path
from lab21.reporting import validate_submission
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=Path('runs/nop_bai'));a=p.parse_args();validate_submission(a.input);print('PASS: five full-sequence files and provenance')
