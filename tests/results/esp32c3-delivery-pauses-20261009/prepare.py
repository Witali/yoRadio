"""Prepare a fresh app-only OTA comparison using already audited integer images."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
OLD = Path('tests/results/esp32c3-flac-integer-20261009')
source = (OLD/'physical.py').read_text().replace('.build/c3-flac-integer-20261009', '.build/c3-delivery-pauses-20261009')
source = source.replace('Matched integer-clock FLAC queue comparison with app-only OTA restoration.', 'Matched byte-position pause comparison using saved integer-clock firmware.')
(ROOT/'physical.py').write_text(source)
trial = (OLD/'trial.py').read_text()
trial = trial.replace('from audio_test_server.server import Server', 'from audio_test_server.server import Server\n\nPAUSES = tuple((3000000*(i+1), (.05,.10,.20)[i%3]) for i in range(6))')
trial = trial.replace('delivery_stats=True, pacing_ratio=1.0) as server:', 'delivery_stats=True, pacing_ratio=1.0, delivery_pauses=PAUSES,\n                        send_buffer_bytes=4096) as server:')
trial = trial.replace("case('flac-heap-recovery',", "case('delivery-pause-schedule', lambda: verify_pauses(server.events))\n                case('flac-heap-recovery',")
insertion = '''
def verify_pauses(events):
    selected = [e for e in events if e.get('fixture') == name and e.get('mode') == 'file']
    require(len(selected) == 1, 'Exactly one FLAC response required')
    event = selected[0]
    expected = [dict(after_bytes=n, seconds=s) for n,s in PAUSES]
    require(event.get('pause_schedule') == expected, 'Wrong pause schedule')
    rows = event.get('pauses', [])
    require(len(rows) == len(PAUSES), 'Not all pauses executed')
    require(event.get('send_buffer_requested') == 4096 and 0 < event.get('send_buffer_actual', 0) <= 8192, 'Unexpected host send buffer')
    require(event.get('pacing_ratio') is None, 'Use unpaced catch-up')
    for row, (offset, seconds) in zip(rows, PAUSES):
        require(row['after_bytes'] == offset and row['requested_seconds'] == seconds, 'Pause position changed')
        require(row['completed'] and seconds-.002 <= row['elapsed_seconds'] <= seconds+.050, 'Interrupted or mistimed pause')
    require(event.get('delivery', {}).get('finished') and not event['delivery']['dropped_windows'], 'Delivery statistics incomplete')
    return dict(pauses=rows, send_buffer_actual=event['send_buffer_actual'],
        scope='Host API writes only; in-flight and receiver data can mask a pause')

'''
trial = trial.replace("with (a.output/'request-phases.jsonl')", insertion+"with (a.output/'request-phases.jsonl')")
(ROOT/'trial.py').write_text(trial)
for filename in ('build-audit.json','case-catalog.json','flow_windows.py'):
    shutil.copyfile(OLD/filename, ROOT/filename)
for filename in ('ca.pem','server.pem'):
    shutil.copyfile(Path('.build/c3-switch-owner-20261009/trust')/filename, ROOT/filename)
sources = {}
for directory in ('tools/esp32c3_tests','tools/audio_test_server'):
    for src in Path(directory).glob('*.py'):
        dest = ROOT/'sources'/src; dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(src.read_bytes())
        sources[src.as_posix()] = hashlib.sha256(src.read_bytes()).hexdigest()
support = Path('tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py')
dest = ROOT/'sources'/support; dest.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(support,dest)
shutil.copyfile('tests/test-audio-server-pauses.py',ROOT/'host/test-audio-server-pauses.py')
(ROOT/'sources.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'firmware-baseline.json').write_text(json.dumps(dict(archive=OLD.as_posix(),
    index_sha256=hashlib.sha256((OLD/'index.json').read_bytes()).hexdigest(),
    note='Firmware images and source snapshots are unchanged from the archived integer-clock experiment. New shared server is frozen separately.'),indent=2)+'\n')
# The six new tests passed in the interactive exec call; older-route logs are retained separately.
(ROOT/'host/new-tests-observation.json').write_text(json.dumps(dict(command='python tests/test-audio-server-pauses.py -v',
    result='PASS',tests=6,exit_code=0,observed_output='Ran 6 tests in 3.238s; OK',
    source_sha256=hashlib.sha256(Path('tests/test-audio-server-pauses.py').read_bytes()).hexdigest()),indent=2)+'\n')
