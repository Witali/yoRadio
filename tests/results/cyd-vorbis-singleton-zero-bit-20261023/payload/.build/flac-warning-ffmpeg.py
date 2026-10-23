from pathlib import Path
import hashlib
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from audio_test_server.generate_flac_depths import encode, crc

out = root / '.build/flac-warning-ffmpeg'
out.mkdir(exist_ok=False)
valid = encode([0] * 16, [0] * 16, 16, 'mono', 'constant', block=16)
invalid = bytearray(valid)
assert invalid[50] == 0
invalid[50] = 0x80
invalid[-2:] = crc(invalid[42:-2], 16, 0x8005).to_bytes(2, 'big')
report = dict(encoder='existing deterministic fixture generator',
              mutation='Set reserved subframe padding bit; recompute frame CRC16', cases={})
for name, data, expected_success in [('valid', valid, True), ('reserved', invalid, False)]:
    fixture = out / (name + '.flac')
    fixture.write_bytes(data)
    result = subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(fixture),
                             '-f', 's16le', '-acodec', 'pcm_s16le', '-'], capture_output=True)
    (out / (name + '.log')).write_bytes(result.stderr)
    assert (result.returncode == 0) == expected_success, result.stderr
    if expected_success: assert result.stdout == b'\0' * 32
    report['cases'][name] = dict(returncode=result.returncode,
                               pcm_bytes=len(result.stdout),
                               fixture_sha256=hashlib.sha256(data).hexdigest(),
                               expected_success=expected_success)
report['ffmpeg'] = subprocess.check_output(['ffmpeg', '-version'], text=True).splitlines()[0]
report['passed'] = True
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print('PASS independent FFmpeg: valid constant PCM exact; reserved padding rejected with valid frame CRC')
