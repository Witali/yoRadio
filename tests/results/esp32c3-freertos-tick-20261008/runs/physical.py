"""Run only the two heavy cases, restoring the quiet image after each variant."""
import json
from pathlib import Path
import subprocess
import sys

root = Path('.build/c3-tick-20261008')
template = Path('.build/c3-staged-dma-profile-20261008/physical.py').read_text()
for tick in (2, 5):
    image = Path('firmware/development') / (
        'esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof-tick'+str(tick))
    manifest = json.loads((image/'manifest.json').read_text())
    assert manifest['scheduler_tick_ms'] == tick
    recipe = template.replace('.build/c3-staged-dma-profile-20261008/physical',
        str(root.as_posix())+'/tick'+str(tick)+'/physical')
    recipe = recipe.replace('rx6-reserve-rxonly-dmaprof/app.bin',
        'rx6-reserve-rxonly-dmaprof-tick'+str(tick)+'/app.bin')
    script = root/('tick'+str(tick))/'physical.py'
    assert not script.exists(), 'Preserve earlier controller'
    script.write_text(recipe)
    print('VARIANT_START', tick, flush=True)
    status = subprocess.run([sys.executable, '-X', 'utf8', str(script)]).returncode
    if status:
        raise SystemExit(status)
    final = json.loads((script.parent/'physical/final-board.json').read_text())
    assert final['result'] == 'PASS'
    print('VARIANT_END', tick, flush=True)
print('TICK_PHYSICAL_COMPLETE', flush=True)
