import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
paths = [
    'idf/esp32-cyd2usb-native/main/' + name for name in [
        'CMakeLists.txt', 'app_main.c', 'network_runtime.c', 'network_status.h',
        'web_pages.cpp', 'web_service.c', 'web_network_settings.c', 'web_network_settings.h']
] + [
    'tests/cyd-native-page.test.js', 'tests/native/cyd_time_events_test.c',
    'tests/native/cyd_web_start_test.c', 'tests/native/cyd_web_network_settings_test.c',
    *['tests/native/cyd_network_runtime/' + name for name in ['README.md', 'platform.c', 'platform.h', 'test.c']],
    *['tests/' + name for name in ['run-cyd-native-page.py', 'run-cyd-network-http.py',
        'run-cyd-network-runtime.py', 'run-cyd-time-events.py', 'run-cyd-web-static.py',
        'run-cyd-web-network-settings.py']]
]
assert len(paths) == len(set(paths)) == 22
for relative in ['n5-runtime-final-03', 'n5-http-02', 'n5-page-02', 'n5-startup-02',
                 'n5-web-start-final-03', 'n5-network-http-regression-01', 'n5-websocket-regression-01',
                 'n5-settings-persistence-01']:
    report = json.loads((root / '.build' / relative / 'report.json').read_text(encoding='utf-8'))
    assert report['passed'], relative
    for path, expected in report.get('source_sha256', {}).items():
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected, (relative, path)
lint = json.loads((root / '.build/lint-cyd-network-n5-01/report.json').read_text(encoding='utf-8'))
assert lint['complete'] and lint['errors'] == 0 and lint['all_inputs_unchanged_after_analysis']
assert not subprocess.check_output(['git', '-c', 'core.longpaths=true', 'diff', '--cached', '--name-only'], cwd=root).strip()
subprocess.run(['git', '-c', 'core.longpaths=true', 'add', '--', *paths], cwd=root, check=True)
staged = subprocess.check_output(['git', '-c', 'core.longpaths=true', 'diff', '--cached', '--name-only'], cwd=root, text=True).splitlines()
assert set(staged) == set(paths), staged
subprocess.run(['git', '-c', 'core.longpaths=true', 'diff', '--cached', '--check'], cwd=root, check=True)
subprocess.run(['git', '-c', 'core.longpaths=true', 'commit', '--quiet', '-m',
                'Apply CYD hostname and guarded AP timeout settings'], cwd=root, check=True)
print(subprocess.check_output(['git', 'log', '-1', '--format=%h %s'], cwd=root, text=True).strip())
