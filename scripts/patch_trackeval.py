"""Replace removed NumPy scalar aliases in pinned upstream source, no metric logic changes."""
from pathlib import Path
import re
for p in Path('TrackEval/trackeval').rglob('*.py'):
    original=p.read_text();updated=re.sub(r'np\.(float|int|bool)\b',lambda m:m[1],original)
    if updated!=original:p.write_text(updated)
