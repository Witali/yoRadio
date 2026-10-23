from pathlib import Path
import json
import subprocess

root = Path(__file__).resolve().parents[1]
audio = json.loads((root / '.build/audio-power-owned-paths.json').read_text(encoding='utf-8'))
owned = [
    'idf/components/native_network_power/CMakeLists.txt',
    'idf/components/native_network_power/native_network_power.c',
    'idf/components/native_network_power/include/native_network_power.h',
    'idf/esp32-cyd2usb-native/CMakeLists.txt', 'idf/esp32-cyd2usb-native/main/CMakeLists.txt',
    'idf/esp32c3-oled-native/CMakeLists.txt', 'idf/esp32c3-oled-native/main/CMakeLists.txt',
    'idf/esp32-cyd2usb-native/main/network_runtime.c', 'idf/esp32-cyd2usb-native/main/network_status.h',
    'idf/esp32-cyd2usb-native/main/network_service.c', 'idf/esp32-cyd2usb-native/main/network_service.h',
    'idf/esp32-cyd2usb-native/main/web_service.c',
    'idf/esp32c3-oled-native/main/network_service.c', 'idf/esp32c3-oled-native/main/network_service.h',
    'tests/run-cyd-network-runtime.py', 'tests/native/cyd_network_runtime/README.md',
    'tests/native/cyd_network_runtime/platform.c', 'tests/native/cyd_network_runtime/platform.h',
    'tests/native/cyd_network_runtime/test.c', 'tests/run-cyd-network-http.py',
    'tests/native/cyd_network_http_test.c', 'tests/run-cyd-websocket.py',
]
paths = sorted(set(audio + owned))
git = ['git', '-c', 'core.longpaths=true']
assert not subprocess.check_output(git + ['diff', '--cached', '--name-only'], cwd=root).strip()
subprocess.run(git + ['add', '--', *paths], cwd=root, check=True)
staged = subprocess.check_output(git + ['diff', '--cached', '--name-only', '-z'], cwd=root).decode().split('\0')
assert set(filter(None, staged)) == set(paths), staged
subprocess.run(git + ['diff', '--cached', '--check'], cwd=root, check=True)
subprocess.run(git + ['commit', '-m', 'Qualify Wi-Fi audio power intent by command generation'], cwd=root, check=True)
