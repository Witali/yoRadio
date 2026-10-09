"""Reuse verified app-only OTA helpers; generate a bounded comparison controller."""
from pathlib import Path
root=Path('.build/c3-staged-flow-20261009')
source=Path('tests/results/esp32c3-tls-final-gates-20261009/physical.py').read_text()
prefix=source.split("require(not OUT.exists(),")[0]
prefix=prefix.replace('c3-tls-final-gates-20261009','c3-staged-flow-20261009')
prefix=prefix.replace('def install(path, clock_mode=None):','def install(path, clock_mode=None, label=None):')
prefix=prefix.replace("save(clock_mode+'-clock.json'", "save((label or clock_mode)+'-clock.json'")
body=(root/'controller_body.txt').read_text()
(root/'physical.py').write_text(prefix+body)
