"""Verify recovery after the original controller's final readiness timeout."""
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, require
from ota import image_info

root = Path(__file__).resolve().parent
out = root / 'physical'
log = (root / 'private/restoration-retry.log').read_text()
markers = [line.strip() for line in log.splitlines()
           if line.strip() == 'Hard resetting with a watchdog...'
           or line.strip() == 'Application verified: http://192.168.100.4/ returned HTTP 200.']
require(any('returned HTTP 200.' in line for line in markers), 'Retry HTTP check missing')
(out / 'restoration-retry.log').write_text('\n'.join(markers) + '\n')
recovery = dict(initial_controller_exit_code=1,
                initial_error='Expected application did not return',
                initial_readiness_timeout_seconds=45,
                retry_method='Skill script, watchdog reset; no Flash writes',
                retry_process_exit_code=0, retry_http_status=200)
(out / 'restoration-recovery.json').write_text(json.dumps(recovery, indent=2) + '\n')

board = Board('http://192.168.100.4')
initial = json.loads((out / 'initial.json').read_text())
flash = json.loads((out / 'flash-restoration.json').read_text())
previous = json.loads((out / 'qio-settings.json').read_text())
expected = image_info(Path('firmware/development/esp32c3-idf-6.1-compact-icy-quiet/app.bin').read_bytes())['app_elf_sha256']
identity = board.info()
require(identity['app_elf_sha256'] == expected == initial['identity']['app_elf_sha256'],
        'Original application identity not restored')
states = []
for _ in range(3):
    time.sleep(5)
    states.append(board.status())
final = dict(identity=identity, status=states,
             persistence=dict(nvs_bytes_equal_after_restore=flash['nvs_equal'],
                              spiffs_bytes_equal_after_restore=flash['spiffs_equal'],
                              last_pre_restore_webui_comparison_equal=all(previous.values())),
             persistence_basis='Exact NVS/SPIFFS comparison before the restore boot, plus the '
                 'successful in-memory WebUI snapshot comparison immediately before restoration. '
                 'The original controller exited before its final snapshot comparison; its '
                 'in-memory reference is unavailable after exit. No post-retry snapshot equality is claimed.',
             post_retry_snapshot_compared=False,
             playback_restored=all(s['audio'] == initial['status']['audio'] for s in states))
(out / 'final-board.json').write_text(json.dumps(final, indent=2) + '\n')
require(final['playback_restored'], 'Playback has not returned')
require(all(final['persistence'].values()) and flash['full_flash_equal'], 'Persistence evidence failed')
print('Original image identity, three playback observations and retained Flash/settings evidence: PASS')
