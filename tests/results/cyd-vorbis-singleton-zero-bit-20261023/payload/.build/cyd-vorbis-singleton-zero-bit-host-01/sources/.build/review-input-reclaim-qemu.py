"""Independently inspect the completed target campaign and immutable ELF bytes."""
from pathlib import Path
import hashlib
import json
import re
import struct

root = Path.cwd()
base = root / '.build/cyd-input-reclaim-qemu-05'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
load = lambda path: json.loads(Path(path).read_text())
report = load(base / 'report.json')
assert report['passed'] and report['actual_cases'] == 5 and report['exact_semantic_controls'] == 4
expected = dict(canonical=None, **{'skip-first-real': 'real_allocator_failed_before_release',
                                 'skip-reclaim': 'recovery_after_real_null',
                                 'omit-pin': 'detach_busy_while_pinned', 'extend-budget': 'fixed_initial_budget'})
assert set(report['variants']) == set(expected)
assert report['all_bound_inputs_current'] and all(report['live_source_verification'].values())
sources = load(base / 'source-manifest.json')
for original, value in sources.items():
    assert sha(original) == value['sha256'] == sha(base / value['snapshot']), original
for original, digest in report['runtime_sha256'].items():
    assert sha(original) == digest, original
for row in report['commands']:
    assert row['exit_status'] == 0 and not row['timed_out'], row['name']
    assert sha(base / (row['name'] + '.log')) == row['sha256'], row['name']
details = {}
for name, marker in expected.items():
    variant = base / 'variants' / name
    bundle = load(variant / 'execution-bundle.json')
    assert sha(variant / 'execution-bundle.json') == report['variants'][name]['bundle_sha256']
    for key in ('frozen_input_sha256', 'artifact_sha256'):
        assert all(sha(base / relative) == digest for relative, digest in bundle[key].items())
    selected = Path(bundle['actual_module_command']['file']).resolve()
    assert selected == (base / 'sources/variants' / name / 'native_input_reclaim.c').resolve()
    log = (base / (name + '-qemu.log')).read_text().replace('\r\n', '\n')
    assert not re.search(r'Guru Meditation|assert failed|panic.ed|abort\(\)|Backtrace|watchdog.*triggered|stack smashing|CORRUPT HEAP', log, re.I)
    if marker is None:
        assert re.findall(r'^CYD_INPUT_RECLAIM_CASE id=(R\d)\b', log, re.M) == ['R0', 'R1', 'R2', 'R3', 'R4']
        assert log.count('CYD_INPUT_RECLAIM_COMPLETE cases=5 actual_module=1 real_sdk_allocator=1 real_oom=1 dualcore=1 hardware=0') == 1
    else:
        assert re.findall(r'^CYD_INPUT_RECLAIM_FAILURE (.+)$', log, re.M) == [marker]
        assert log.count('CYD_INPUT_RECLAIM_CONTROLLED_STOP') == 1
    elf_names = [relative for relative in bundle['artifact_sha256'] if relative.endswith('.elf')]
    assert len(elf_names) == 1
    raw = (base / elf_names[0]).read_bytes()
    assert raw[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', raw, 18)[0] == 94
    phoff = struct.unpack_from('<I', raw, 28)[0]
    phsize, phcount = struct.unpack_from('<HH', raw, 42)
    segments = [struct.unpack_from('<8I', raw, phoff + index * phsize) for index in range(phcount)]
    symbols = {}
    for line in (base / (name + '-nm.log')).read_text().splitlines():
        fields = line.split()
        if len(fields) == 4:
            symbols[fields[3]] = int(fields[0], 16)
    proof = load(variant / 'sdk-platform-pointer-proof.json')
    for pointer, target in [('mbedtls_calloc_func', '__wrap_esp_mbedtls_mem_calloc'), ('mbedtls_free_func', 'esp_mbedtls_mem_free')]:
        address = symbols[pointer]
        segment = next(row for row in segments if row[0] == 1 and row[2] <= address < row[2] + row[4])
        value = struct.unpack_from('<I', raw, segment[1] + address - segment[2])[0]
        assert value == symbols[target] == proof[pointer]['initial_value']
    details[name] = dict(expected_failure=marker, bundle_sha256=sha(variant / 'execution-bundle.json'),
                         elf_sha256=hashlib.sha256(raw).hexdigest(), pointer_words_independently_checked=True)
out = root / '.build/cyd-input-reclaim-qemu-root-review-01'
out.mkdir(exist_ok=False)
(out / 'review.json').write_text(json.dumps(dict(passed=True, actual_cases=5, exact_controls=4,
    report_sha256=sha(base / 'report.json'), current_sources=len(sources), command_count=len(report['commands']),
    variants=details, physical_tested=False,
    scope='Read-only independent current-source/log/bundle/ELF-pointer review. Not a new SDK build or emulator run.'), indent=2) + '\n')
print('PASS actual SDK campaign: 5 cases, 4 exact controls, ' + str(len(sources)) + ' current frozen inputs and five actual ELF pointer initializers')
