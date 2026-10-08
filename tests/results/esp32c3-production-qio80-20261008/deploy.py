"""Install matching QIO bootloader/application, preserve settings, run quiet smoke tests."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import time

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, require
from ota import image_info, snapshot, verify_snapshot

ROOT = Path('.build/c3-production-qio80-20261008')
OUT = ROOT / 'physical'
PRIVATE = ROOT / 'private'
ARTIFACT = Path('firmware/development/esp32c3-idf-6.1-r9a97-production-qio80')
BOARD = Board('http://192.168.100.4')
PORT = 'COM9'
PHASES = []

def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')

def run(name, command, private=False, required=True, timeout=180):
    start = time.monotonic()
    print('START', name, flush=True)
    with ((PRIVATE if private else OUT) / (name + '.log')).open('xb') as log:
        proc = subprocess.run(list(map(str, command)), stdout=log,
                              stderr=subprocess.STDOUT, timeout=timeout)
    PHASES.append(dict(name=name, code=proc.returncode, seconds=time.monotonic()-start))
    save(OUT / 'phases.json', PHASES)
    print('END', name, proc.returncode, flush=True)
    require(not required or proc.returncode == 0, 'Required phase failed: ' + name)
    return proc.returncode

def esp(name, *args):
    return run(name, [sys.executable, '-m', 'esptool', '--chip', 'esp32c3',
        '--port', PORT, '--before', 'usb-reset', '--after', 'no-reset', *args], private=True)

def reset(name):
    return run(name, ['pwsh.exe', '-NoProfile', '-File',
        '.agents/skills/flash-reset-esp32c3-oled/scripts/reset_esp32c3_oled.ps1',
        '-Port', PORT, '-PythonPath', sys.executable], private=True, timeout=60)

def ready(digest, timeout=45):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        try:
            info = BOARD.info()
            if info['app_elf_sha256'] == digest:
                BOARD.status()
                return info
        except (OSError, ValueError):
            pass
        time.sleep(.5)
    raise RuntimeError('Expected application did not return')

require(not OUT.exists() and not PRIVATE.exists(), 'Preserve previous evidence')
OUT.mkdir(); PRIVATE.mkdir()
identity = BOARD.info(); initial = BOARD.status(); before = snapshot(BOARD)
save(OUT / 'initial.json', dict(identity=identity, status=initial))
app = (ARTIFACT / 'app.bin').read_bytes()
boot = (ARTIFACT / 'bootloader.bin').read_bytes()
expected = image_info(app)['app_elf_sha256']
written = False
started = False
try:
    BOARD.stop()
    esp('backup', 'read-flash', '0', '0x400000', PRIVATE / 'original-flash.bin')
    original = (PRIVATE / 'original-flash.bin').read_bytes()
    require(len(original) == 0x400000, 'Incomplete backup')
    entries = {}
    for offset in range(0x8000, 0x9000, 32):
        raw = original[offset:offset+32]
        if raw[:2] != b'\xaaP': break
        _, kind, subtype, address, size, label, flags = struct.unpack('<HBBII16sI', raw)
        entries[label.split(b'\0')[0].decode()] = dict(address=address, size=size)
    require(entries['app0'] == dict(address=0x10000, size=0x1d0000) and
            entries['app1'] == dict(address=0x1e0000, size=0x1d0000) and
            entries['nvs'] == dict(address=0x9000, size=0x5000) and
            entries['spiffs'] == dict(address=0x3b0000, size=0x40000), 'Unexpected layout')
    slot = identity['partition']; address = entries[slot]['address']
    require(len(app) <= entries[slot]['size'] and len(boot) <= 0x8000, 'Images exceed regions')
    save(OUT / 'partition-layout.json', entries)
    (PRIVATE / 'old-boot.bin').write_bytes(original[:0x8000])
    (PRIVATE / 'old-ota-apps.bin').write_bytes(original[0xe000:0x3b0000])
    written = True
    esp('install', 'write-flash', '--flash-mode', 'keep', '--flash-freq', 'keep',
        '--flash-size', 'keep', '0x0', ARTIFACT / 'bootloader.bin', hex(address), ARTIFACT / 'app.bin')
    esp('readback', 'read-flash', '0', '0x400000', PRIVATE / 'installed-readback.bin')
    readback = (PRIVATE / 'installed-readback.bin').read_bytes()
    allowed = bytearray(original)
    for offset, length in ((0, len(boot)), (address, len(app))):
        end = offset + ((length + 4095) // 4096) * 4096
        allowed[offset:end] = readback[offset:end]
    verification = dict(bootloader_equal=readback[:len(boot)] == boot,
        app_equal=readback[address:address+len(app)] == app,
        only_programmed_sectors_changed=bytes(allowed) == readback,
        nvs_equal=original[0x9000:0xe000] == readback[0x9000:0xe000],
        spiffs_equal=original[0x3b0000:0x3f0000] == readback[0x3b0000:0x3f0000],
        partition_table_equal=original[0x8000:0x9000] == readback[0x8000:0x9000],
        otadata_equal=original[0xe000:0x10000] == readback[0xe000:0x10000])
    save(OUT / 'flash-verification.json', verification)
    require(all(verification.values()), 'Readback/preservation failed')
    resets = []
    for attempt in (1, 2):
        reset('start-' + str(attempt))
        try:
            current = ready(expected)
            resets.append(dict(attempt=attempt, result='PASS'))
            started = True
            break
        except RuntimeError:
            resets.append(dict(attempt=attempt, result='FAIL', reason='Readiness timeout, 45 seconds'))
    save(OUT / 'startup.json', dict(attempts=resets))
    require(started, 'Production image did not start after two resets')
    save(OUT / 'installed.json', dict(identity=current, settings=verify_snapshot(BOARD, before)))
    command = [sys.executable, '-X', 'utf8', 'tools/esp32c3_tests/run.py',
        '--board', BOARD.origin, '--host', '192.168.100.253', '--suite', 'http',
        '--output', OUT / 'http-smoke', '--sdkconfig', ARTIFACT / 'sdkconfig',
        '--unpaced-files', '--delivery-stats', '--leave-stopped']
    for name in ('mp3-320', 'flac-level8', 'vorbis-q10', 'opus-510',
                 'lc-48000-stereo', 'he-48000-stereo', 'hev2-44100-stereo'):
        command += ['--case', name]
    smoke_code = run('http-smoke', command, required=False, timeout=900)
    ota_code = run('ota-roundtrip', [sys.executable, '-X', 'utf8', 'tools/esp32c3_tests/ota.py',
        '--board', BOARD.origin, '--firmware', ARTIFACT / 'app.bin', '--suite', 'roundtrip',
        '--output', OUT / 'ota-roundtrip.json'], required=False, timeout=240)
    BOARD.reboot()
    final_identity = ready(expected)
    if not initial['audio']: BOARD.stop()
    states = []
    for _ in range(3):
        time.sleep(5); states.append(BOARD.status())
    final = dict(identity=final_identity, status=states, settings=verify_snapshot(BOARD, before),
        playback_restored=all(s['audio'] == initial['audio'] for s in states),
        http_smoke_passed=smoke_code == 0, ota_roundtrip_passed=ota_code == 0,
        scope='Quiet production configuration, HTTP format/EOF smoke, OTA roundtrip and settings. '
              'No serial CPU/heap diagnostics, HTTPS matrix or acoustic qualification.')
    save(OUT / 'final-board.json', final)
    require(final['playback_restored'], 'Stored station playback did not return')
    require(smoke_code == 0 and ota_code == 0, 'One or more production smoke tests failed')
finally:
    if not started:
        if written:
            esp('rollback', 'write-flash', '--flash-mode', 'keep', '--flash-freq', 'keep',
                '--flash-size', 'keep', '0x0', PRIVATE / 'old-boot.bin',
                '0xe000', PRIVATE / 'old-ota-apps.bin')
        reset('rollback-start')
        ready(identity['app_elf_sha256'])
    elif not (OUT / 'final-board.json').exists():
        BOARD.reboot()
        recovered = ready(expected)
        if not initial['audio']: BOARD.stop()
        save(OUT / 'interrupted-test-recovery.json',
             dict(identity=recovered, settings=verify_snapshot(BOARD, before)))
print('PRODUCTION_INSTALLED_AND_SMOKE_CHECKED', flush=True)
