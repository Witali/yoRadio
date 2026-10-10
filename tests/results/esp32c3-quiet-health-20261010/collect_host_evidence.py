"""Copy completed host/build evidence without touching the physical runner."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for source, destination in (
    (Path('.build/production-health-native'), ROOT / 'native-health'),
    (Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-mpi-health/log'),
     ROOT / 'build-logs'),
):
    destination.mkdir(exist_ok=True)
    for path in source.iterdir():
        if not path.is_file() or path.name in ('health-0', 'health-1'):
            continue
        (destination / path.name).write_bytes(path.read_bytes())

for name in (
    'tests/test-production-health.py',
    'tests/test-production-health-native.py',
    'tests/native/production_health_test.c',
    'tests/test-file-playback-runtime.py',
):
    source = Path(name)
    destination = ROOT / 'host-test-sources' / source
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source.read_bytes())
print('Copied completed host tests and build logs')
