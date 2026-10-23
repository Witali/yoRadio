"""Preserve frozen time/private-Wi-Fi evidence without replacing earlier bytes."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
groups = {
    'time-backend-initial': 'native-time-qualified-01',
    'time-backend-final': 'native-time-foreign-ip-qualified-01',
    'time-cyd': 'cyd-time-qualified-02',
    'time-settings-c3': 'c3-time-settings-qualified-final',
    'time-service-c3': 'c3-time-service-qualified-final-03',
    'time-lifetime-c3': 'c3-time-lifetime-qualified-final-03',
    'time-lifetime-final-c3': 'c3-time-lifetime-foreign-ip-qualified-01',
    'time-http-cyd': 'cyd-web-time-qualified-final',
    'time-wire-cyd': 'cyd-time-wire-qualified-01',
    'time-startup-events': 'cyd-time-events-qualified-01',
    'wifi-store': 'native-wifi-store-02',
    'wifi-json': 'native-wifi-json-01',
    'wifi-store-c3': 'c3-wifi-private-store-02',
    'wifi-store-cyd': 'cyd-wifi-private-store-qualified-02',
    'wifi-reader-cyd': 'cyd-wifi-private-reader-qualified-01',
    'wifi-http-io': 'native-wifi-shared-io-03',
    'wifi-http-final': 'native-wifi-legacy-io-qualified',
    'wifi-wire-cyd-http': 'native-wifi-wire-qualified-cyd-plain',
    'wifi-wire-cyd-tls': 'native-wifi-wire-qualified-cyd-tls',
    'wifi-wire-c3': 'native-wifi-wire-qualified-c3',
    'legacy-uploads': 'cyd-upload-wifi-final01',
    'multipart-final': 'multipart-wifi-final01',
    'production-wrapper': 'cyd-runtime-production-wrapper-final',
    'lint-cyd': 'lint-cyd-runtime-transfer-full',
    'lint-c3-original': 'lint-c3-runtime-transfer-full',
    'lint-c3-resumed': 'lint-c3-runtime-transfer-resumed-02',
    'lint-c3-final': 'lint-c3-runtime-transfer-complete-01',
    'json-lint-grammar': 'native-wifi-json-lint-triage-01',
    'json-lint-boundaries': 'native-wifi-json-boundary-lint-01',
    'lint-review': 'runtime-lint-review-campaign',
    'clients': 'native-runtime-client-tests',
    'web-start-c3': 'c3-web-start-wifi-01',
    'web-start-static-cyd': 'cyd-web-static-private-qualified-01',
    'web-page-cyd': 'cyd-native-page-qualified-final',
    'ws-status-c3': 'c3-websocket-status-qualified-01',
}
source = (root / '.build/archive-native-web.py').read_text()
source = source.replace('native-web-transfer-20261018', 'native-runtime-transfer-20261018')
source, count = re.subn(r'groups=\{.*?\n\}', 'groups=' + repr(groups), source, count=1, flags=re.S)
assert count == 1
source = source.replace("reports=list(source.glob('*report.json')) or list(source.glob('results.json'))",
                        "reports=([source/'report.json'] if (source/'report.json').is_file() else list(source.glob('results.json')))")
source = source.replace('assert reports, source', "assert reports or name == 'lint-c3-original', source")
source = source.replace("file.name!='.clang-tidy'", "file.name not in {'.clang-tidy', 'sdkconfig'}")
source = source.replace("'.yaml','.md','.gz'", "'.yaml','.md','.gz','.defaults','.projbuild'")
exec(compile(source, __file__, 'exec'))
