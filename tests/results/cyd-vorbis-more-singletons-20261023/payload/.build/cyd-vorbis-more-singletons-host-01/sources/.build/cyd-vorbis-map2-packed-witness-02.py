"""Validate the exact named packed-skip negative; never relabel its NONPASS."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent.parent
base = root / '.build/cyd-vorbis-map2-packed-control-01'
raw = (base / 'report.json').read_bytes()
d = json.loads(raw)
assert not d['completed'] and d.get('result') == 'NONPASS'
assert [c['name'] for c in d['commands']] == ['sdk-head', 'sdk-clean', 'build', 'setup-macros', 'symbols', 'merge', 'qemu']
for c in d['commands']:
    assert c['state'] == 'complete' and c['exit_status'] == 0 and c['timed_out'] is False and c['interrupted'] is False
    for stream in ('stdout', 'stderr'):
        data = (base / (c['name'] + '.' + stream + '.log')).read_bytes()
        assert hashlib.sha256(data).hexdigest() == c[stream + '_sha256']
q = (base / 'qemu.stdout.log').read_bytes() + b'\n' + (base / 'qemu.stderr.log').read_bytes()
assert not any(t in q for t in (b'CORRUPT HEAP', b'Guru Meditation', b'Backtrace:', b'assert failed'))


def events(data):
    return [line for line in data.decode().splitlines() if line.startswith('CYD_VORBIS_CHECKED_CORPUS_')]


a = events((root / '.build/cyd-vorbis-format-corpus-checked-acceptance-01/qemu.stdout.log').read_bytes())
b = events(q)
assert len(b) == 190 and b[:188] == a[:188]
assert b[188] == 'CYD_VORBIS_CHECKED_CORPUS_OPEN case=6 id=sparse_explicit_d4_seq0 checked_rc=-1 checked_handle=0 core=1'
assert b[189] == 'CYD_VORBIS_CHECKED_CORPUS_FAILURE case=6 packet=0 reason=checked_public_open core=1'
assert len([x for x in b if x.startswith('CYD_VORBIS_CHECKED_CORPUS_PACKET ')]) == 84
assert len([x for x in b if x.startswith('CYD_VORBIS_CHECKED_CORPUS_CASE ')]) == 6
variants = {key.replace('\\', '/'): value for key, value in d['variant_sources'].items()}
assert variants['variant/vorbis_repair/setup.c'] == 'dd216d11f54d8cbe8419b04b74b1bcf8ae5be223834285624fa824a2defd5feb'
terminal = dict(schema='direct-exec-tool-terminal-v1', session_id=69232, terminal_chunk_id='5b0f31', exit_code=1,
    report_sha256=hashlib.sha256(raw).hexdigest(), entrypoint_sha256=hashlib.sha256((root /
    '.build/cyd-vorbis-format-corpus-checked-prep-02/run-cyd-vorbis-format-corpus-checked-qemu.py').read_bytes()).hexdigest())
result = dict(schema='cyd-map2-packed-focused-negative-witness-v1', control_expected_failure_observed=True,
    control_acceptance_passed=False, original_campaign_result='NONPASS', report_sha256=terminal['report_sha256'],
    source_sha256=variants['variant/vorbis_repair/setup.c'], prefix_exact_to_fixed_capture=True,
    completed_prerequisite_cases=6, completed_prerequisite_packets=84, completed_prerequisite_pcm_bytes=168960,
    failure_case=6, failure_id='sparse_explicit_d4_seq0', failure_phase='checked_public_open', failure_packet=0,
    checked_rc=-1, checked_handle=0, core=1, panic=False, owned_commands_completed_zero=7)
for name, value in (('cyd-vorbis-map2-packed-control-01-terminal.json', terminal),
                    ('cyd-vorbis-map2-packed-control-01-witness.json', result)):
    path = root / '.build' / name
    assert not path.exists()
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result))
