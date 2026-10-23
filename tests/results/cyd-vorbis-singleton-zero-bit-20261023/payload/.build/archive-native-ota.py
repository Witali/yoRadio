"""Archive OTA evidence without altering previous campaign snapshots."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
groups = {
    'sink-cyd': 'native-ota-sink-602-qualified',
    'sink-c3': 'native-ota-sink-611-qualified',
    'image-cyd': 'native-ota-images-602-probe4',
    'image-c3': 'native-ota-images-611-probe',
    'reboot': 'reboot-leases-01',
    'reboot-regressions': 'reboot-leases-existing-uploads',
    'output-pause-initial': 'cyd-output-pause-final',
    'http-initial': 'ota-http-qualified-02',
    'multipart-current': 'ota-multipart-current-01',
    'static-startup-cyd': 'cyd-web-ota-start-qualified',
    'maintenance-cyd': 'cyd-maintenance-state-qualified-final',
    'maintenance-lifecycle': 'cyd-maintenance-state-lifecycle-final',
    'output-pause-final': 'cyd-output-pause-qualified-final',
    'output-gain': 'cyd-maintenance-output-gain-final',
    'transport-prepare-close': 'native-web-ota-prepare-close',
    'tls-cyd': 'native-tls-ota-602',
    'tls-c3': 'native-tls-ota-611',
    'lint-cyd': 'lint-cyd-ota-transfer-full',
    'lint-c3': 'lint-c3-ota-transfer-full',
    'maintenance-publication-cyd': 'cyd-maintenance-pause-publication',
    'audio-lint-publication-cyd': 'ota-audio-lint-cyd-publication',
    'audio-lint-publication-c3': 'ota-audio-lint-c3-publication',
    'output-pause-c3': 'c3-output-pause-2',
    'commands-c3': 'c3-maintenance-commands-final',
    'state-c3': 'c3-maintenance-state-regression-final',
    'output-boundaries-c3': 'c3-maintenance-output-boundaries-final',
    'output-gain-c3': 'c3-maintenance-output-regression-1',
    'eof-rtc-c3': 'c3-maintenance-eof-rtc-final',
    'maintenance-c3': 'c3-maintenance-qualified-final',
    'http-final': 'ota-http-c3-maintenance-01',
    'wire': 'ota-wire-qualified-02',
    'wss-regression': 'wss-ota-transport-regression',
}
source = (root / '.build/archive-native-web.py').read_text(encoding='utf-8')
source = source.replace('native-web-transfer-20261018', 'native-ota-transfer-20261018')
source, count = re.subn(r'groups=\{.*?\n\}', 'groups=' + repr(groups), source, count=1, flags=re.S)
assert count == 1
exec(compile(source, __file__, 'exec'))
