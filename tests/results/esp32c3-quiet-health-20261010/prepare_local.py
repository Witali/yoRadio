"""Continue independent local/OTA qualification, retaining public failures."""
from pathlib import Path
root=Path(__file__).resolve().parent
source=(root/'physical.py').read_text()
assert source.count("OUT=ROOT/'physical'")==1
source=source.replace("OUT=ROOT/'physical'", "OUT=ROOT/'physical-local'")
line="    run_phase('public',[*common,'--suite','public','--aac-reference-command',reference,'--output',OUT/'public'],900)\n"
assert line in source
source=source.replace(line,'')
source=source.replace('Install the exact quiet candidate, test it, and restore the listened image.',
    'Continue local and OTA tests after preserved public failures; restore the listened image.')
assert not (root/'physical-local.py').exists()
(root/'physical-local.py').write_text(source)
print('Prepared independent local/OTA campaign; public evidence remains unchanged')
