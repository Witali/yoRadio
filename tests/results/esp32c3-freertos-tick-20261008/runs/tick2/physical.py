import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, require
from ota import snapshot, verify_snapshot

root = Path('.build/c3-tick-20261008/tick2/physical')
require(not root.exists(), 'Keep prior measurements')
root.mkdir(parents=True)
board = Board('http://192.168.100.4')
initial = board.status()
settings = snapshot(board)
require(board.info()['app_elf_sha256'] ==
        'da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0',
        'Previous controller must restore the quiet image first')
image = Path('firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof-tick2/app.bin')
trust = Path('.build/c3-tls-records-20261007/trust')
phases = []

def run(name, script, arguments, required=False):
    command = [sys.executable, '-X', 'utf8', script, *map(str, arguments)]
    print('START', name, flush=True)
    started = time.monotonic()
    with (root/(name+'.log')).open('xb') as log:
        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=900)
    phases.append(dict(name=name, command=command, code=completed.returncode,
                       seconds=time.monotonic()-started))
    (root/'phases.json').write_text(json.dumps(phases, indent=2)+'\n')
    print('END', name, completed.returncode, flush=True)
    require(not required or completed.returncode == 0, 'Required phase failed: '+name)

try:
    run('install', '.build/idf-upgrade/install.py',
        ['--firmware', image, '--output', root/'install.json'], True)
    run('flac-https-60', 'tools/esp32c3_tests/trace_transport.py', [
        '--runner', 'diagnostic', '--', 'run', '--board', board.origin,
        '--host', '192.168.100.253', '--serial-port', 'COM9', '--suite', 'load',
        '--load-seconds', '60', '--load-idle-recovery',
        '--case', 'stress-flac-48000-2ch-16bit-610s',
        '--fixture-manifest', '.build/c3-reserve-soak-20261008/fixtures/manifest.json',
        '--sustained-protocol', 'https', '--unpaced-files', '--delivery-stats', '--leave-stopped',
        '--https-origin', 'https://192.168.100.253:8771', '--tls-cert', trust/'server.pem',
        '--tls-key', trust/'server.key', '--sdkconfig', image.with_name('sdkconfig'),
        '--output', root/'flac-https-60'])
    run('aac-alternate-90', 'tools/esp32c3_tests/trace_transport.py', [
        '--runner', 'tls_records', '--', '--board', board.origin, '--host', '192.168.100.253',
        '--serial-port', 'COM9', '--firmware', image, '--ca', trust/'ca.pem',
        '--cert', trust/'server.pem', '--key', trust/'server.key', '--mode', 'alternate',
        '--seconds', '90', '--output', root/'aac-alternate-90'])
finally:
    run('restore', '.build/idf-upgrade/install.py', [
        '--firmware', 'firmware/development/esp32c3-idf-6.1-compact-icy-quiet/app.bin',
        '--output', root/'restore.json'], True)
    identity = board.info()
    require(identity['app_elf_sha256'] ==
            'da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0',
            'Wrong restored image')
    if not initial['audio']:
        board.stop()
    samples = []
    for _ in range(3):
        time.sleep(5)
        samples.append(board.status())
    state_matches = all(sample['audio'] == initial['audio'] for sample in samples)
    final = dict(result='PASS' if state_matches else 'FAIL', info=identity, status=samples,
                 persistence=verify_snapshot(board, settings), playback_state_restored=state_matches)
    (root/'final-board.json').write_text(json.dumps(final, indent=2)+'\n')
    require(state_matches, 'Initial playback state was not restored')

for case in ('flac-https-60', 'aac-alternate-90'):
    run('summarize-'+case, 'tools/esp32c3_tests/staged_dma.py',
        ['--input', root/case, '--output', root/(case+'-dma.json')])
print('STAGED_DMA_PHYSICAL_COMPLETE', flush=True)
