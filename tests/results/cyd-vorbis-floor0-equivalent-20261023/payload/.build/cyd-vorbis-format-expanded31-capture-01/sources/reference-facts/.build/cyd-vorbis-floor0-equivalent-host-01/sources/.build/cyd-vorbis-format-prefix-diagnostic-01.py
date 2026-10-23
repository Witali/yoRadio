"""Measure a complete six-case prefix of a failed run; never qualify that run."""
from pathlib import Path
import array
import hashlib
import io
import json
import math
import re
import sys
import wave

root = Path(__file__).resolve().parent.parent
campaign = root / '.build/cyd-vorbis-format-corpus-capture-01'
hostdir = root / '.build/cyd-vorbis-format-corpus-host-01'
output = root / '.build/cyd-vorbis-format-prefix-diagnostic-01'
assert not output.exists()
sha = lambda data: hashlib.sha256(data).hexdigest()
report = json.loads((campaign / 'report.json').read_bytes())
terminal = json.loads((root / '.build/cyd-vorbis-format-corpus-capture-01-terminal.json').read_bytes())
assert terminal['exit_code'] == 1 and terminal['report_sha256'] == sha((campaign / 'report.json').read_bytes())
assert report['result'] == 'NONPASS' and report['completed'] is False
assert len(report['commands']) == 7 and all(r['exit_status'] == 0 and r['timed_out'] is False and r['interrupted'] is False for r in report['commands'])
hostbytes = (hostdir / 'report.json').read_bytes()
assert sha(hostbytes) == 'eaf3d8033406d5c6844f5dd6e3f42b26195d6e03b3293c27ea03353d6ca0ae29'
host = json.loads(hostbytes)
contractbytes = (campaign / 'sources/corpus/contract.json').read_bytes()
assert sha(contractbytes) == '6c95b8d52a7bd5a3ca8e2d1b519f5d0ec3172e7e76e83ade8c1e78d364fdd391'
cases = json.loads(contractbytes)['model']['cases']
logbytes = (campaign / 'qemu.stdout.log').read_bytes()
log = logbytes.decode(errors='strict')
assert 'CORRUPT HEAP:' in log and 'Fail to parse vorbis configuration' in log
lines = [line for line in log.splitlines() if line.startswith('CYD_VORBIS_CORPUS_')]
assert len(lines) == 188
assert lines[-1].startswith('CYD_VORBIS_CORPUS_CASE case=5 ')
wavs = {}
for path in hostdir.rglob('*.wav'):
    data = path.read_bytes()
    wavs.setdefault(sha(data), (path, data))
def fields(line):
    tokens = line.split(' ')
    assert all(token.count('=') == 1 for token in tokens[1:])
    result = dict(token.split('=', 1) for token in tokens[1:])
    assert len(result) == len(tokens) - 1
    return tokens[0].removeprefix('CYD_VORBIS_CORPUS_'), result
rows = []
for index, case in enumerate(cases[:6]):
    actual = bytearray()
    pairs = [fields(line)[1] for line in lines if line.startswith(f'CYD_VORBIS_CORPUS_PAIR case={index} ')]
    hexes = [fields(line)[1] for line in lines if line.startswith(f'CYD_VORBIS_CORPUS_PCM_HEX case={index} ')]
    assert len(pairs) == len(hexes) == 14
    for packet, (pair, raw) in enumerate(zip(pairs, hexes)):
        assert pair['packet'] == raw['packet'] == str(packet)
        assert pair['core'] == raw['core'] == '1'
        for key in ('vendor_rc', 'checked_rc'): assert pair[key] == '0'
        for key in ('vendor_consumed', 'checked_consumed', 'size'): assert pair[key] == str(case['sizes'][packet])
        for key in ('expected_pcm', 'vendor_pcm', 'checked_pcm'): assert pair[key] == str(case['pcm'][packet])
        for key in ('vendor_rate', 'checked_rate'): assert pair[key] == str(case['rate'])
        for key in ('vendor_channels', 'checked_channels'): assert pair[key] == '2'
        for key in ('vendor_bits', 'checked_bits'): assert pair[key] == '16'
        for key in ('equal', 'vendor_canary', 'checked_canary', 'vendor_first'): assert pair[key] == '1'
        assert raw['bytes'] == str(case['pcm'][packet])
        assert re.fullmatch('[0-9a-f]*', raw['hex']) and len(raw['hex']) == case['pcm'][packet] * 2
        actual.extend(bytes.fromhex(raw['hex']))
    reference = host['cases'][index]
    assert reference['id'] == f"0-{case['id']}"
    facts = reference['decoded']['libvorbis']
    path, encoded = wavs[facts['wav_sha256']]
    with wave.open(io.BytesIO(encoded), 'rb') as wav:
        assert (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) == (2, 2, case['rate'])
        expected = wav.readframes(wav.getnframes())
    assert len(expected) == len(actual) == case['total_pcm']
    assert sha(expected) == facts['pcm_sha256']
    a, b = array.array('h'), array.array('h')
    a.frombytes(actual); b.frombytes(expected)
    if sys.byteorder != 'little': a.byteswap(); b.byteswap()
    delta = [x-y for x, y in zip(a, b)]
    rows.append(dict(case=index, id=case['id'], pcm_bytes=len(actual), actual_pcm_sha256=sha(actual),
        reference_wav=str(path.relative_to(root)), reference_wav_sha256=facts['wav_sha256'],
        max_abs_error=max(map(abs, delta)), rms_error=math.sqrt(sum(x*x for x in delta)/len(delta)),
        signed_min_error=min(delta), signed_max_error=max(delta), differing_samples=sum(x != 0 for x in delta)))
result = dict(schema='failed-corpus-prefix-diagnostic-v1', completed_diagnostic=True,
    original_campaign_result='NONPASS', original_campaign_qualified=False, full_G6_qualified=False,
    capture_report_sha256=terminal['report_sha256'], qemu_stdout_sha256=sha(logbytes),
    complete_prefix_cases=6, complete_prefix_packets=84, numeric_policy_applied=False, cases=rows)
output.mkdir()
(output / 'report.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(result))
