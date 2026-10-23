"""Check an exact named open rejection against the complete fixed25 prefix."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--role', choices=('wide', 'single'), required=True)
p.add_argument('--session-id', type=int, required=True)
p.add_argument('--terminal-chunk-id', required=True)
a = p.parse_args()
root = Path(__file__).resolve().parent.parent
expected = {
    'wide': (8, 'sparse_explicit_d16_seq0', '5444e4f7c1dd6bfcf85e8ae53b8af4bb2e5b6a3fe165013a528db6b668fa2160'),
    'single': (12, 'single_explicit_d2_seq0', 'c81c799d00616a5aa5cc80b7d2f9854b42bd1fcb9b9902598fdf044eca2506cc'),
}
index, name, source_sha = expected[a.role]
base_name = 'cyd-vorbis-map2-' + a.role + '-control-01'
base = root / '.build' / base_name
report_bytes = (base / 'report.json').read_bytes()
report = json.loads(report_bytes)
assert a.session_id > 0 and a.terminal_chunk_id
terminal = dict(schema='direct-exec-tool-terminal-v1', session_id=a.session_id,
    terminal_chunk_id=a.terminal_chunk_id, exit_code=1,
    report_sha256=hashlib.sha256(report_bytes).hexdigest(),
    entrypoint_sha256='74ab64118cd8cd29e5fb376bc687a2b9eba703140c98b45474de7202d50e409f')
terminal_path = root / '.build' / (base_name + '-terminal.json')
assert not terminal_path.exists()
terminal_path.write_text(json.dumps(terminal, indent=2) + '\n', encoding='utf-8')
assert report['completed'] is False and report['result'] == 'NONPASS'
assert [r['name'] for r in report['commands']] == ['sdk-head', 'sdk-clean', 'build', 'setup-macros', 'symbols', 'merge', 'qemu']
for command in report['commands']:
    assert command['state'] == 'complete' and command['exit_status'] == 0
    assert command['timed_out'] is False and command['interrupted'] is False
    for stream in ('stdout', 'stderr'):
        data = (base / (command['name'] + '.' + stream + '.log')).read_bytes()
        assert hashlib.sha256(data).hexdigest() == command[stream + '_sha256']
qemu = (base / 'qemu.stdout.log').read_bytes() + b'\n' + (base / 'qemu.stderr.log').read_bytes()
assert not any(t in qemu for t in (b'CORRUPT HEAP', b'Guru Meditation', b'Backtrace:', b'assert failed'))
prefix = 'CYD_VORBIS_CHECKED_CORPUS_'
events = lambda data: [line for line in data.decode().splitlines() if line.startswith(prefix)]
fixed = events((root / '.build/cyd-vorbis-format-expanded25-capture-02/qemu.stdout.log').read_bytes())
observed = events(qemu)
prior = 2 + 31 * index
assert len(observed) == prior + 2 and observed[:prior] == fixed[:prior]
assert observed[prior] == f'{prefix}OPEN case={index} id={name} checked_rc=-1 checked_handle=0 core=1'
assert observed[prior + 1] == f'{prefix}FAILURE case={index} packet=0 reason=checked_public_open core=1'
assert sum(line.startswith(prefix + 'CASE ') for line in observed) == index
assert sum(line.startswith(prefix + 'PACKET ') for line in observed) == index * 14
variants = {key.replace('\\', '/'): value for key, value in report['variant_sources'].items()}
assert variants['variant/vorbis_repair/setup.c'] == source_sha
result = dict(schema='cyd-map2-focused-negative-witness-v1', role=a.role,
    control_expected_failure_observed=True, control_acceptance_passed=False,
    original_campaign_result='NONPASS', report_sha256=terminal['report_sha256'], source_sha256=source_sha,
    fixed_prefix_byte_equal=True, completed_prerequisite_cases=index,
    completed_prerequisite_packets=index * 14, completed_prerequisite_pcm_bytes=index * 28160,
    failure_case=index, failure_id=name, failure_phase='checked_public_open', failure_packet=0,
    checked_rc=-1, checked_handle=0, core=1, panic=False, owned_commands_completed_zero=7)
out = root / '.build' / (base_name + '-witness.json')
assert not out.exists()
out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result))
