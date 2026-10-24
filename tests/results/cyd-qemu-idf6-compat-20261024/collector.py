"""Create a compact, byte-preserving checkpoint of completed emulator work."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1]).resolve()
assert out.parent == root / '.build' and not out.exists()
groups = (
    'cyd-qemu-rebuild-20261024-01',
    'cyd-qemu-flash-trace-prep-01',
    'cyd-qemu-flash-trace-20261024-01',
    'cyd-qemu-flash-trace-audit-20261024-01',
    'cyd-qemu-production-observer-prep-02',
    'cyd-qemu-production-observer-review-20261024-01',
    'cyd-qemu-production-observation-20261024-02',
    'cyd-qemu-production-analysis-20261024-02',
    'cyd-qemu-idf6-compat-prep-01',
    'cyd-qemu-idf6-compat-review-20261024-01',
    'cyd-qemu-trace-portability-review-20261024-01',
    'cyd-qemu-production-observer-prep-03',
    'cyd-qemu-peripheral-filter-prep-01',
    'cyd-qemu-idf6-root-01',
    'cyd-qemu-idf6-build-01',
    'cyd-qemu-idf6-baseline-mmio-01',
    'cyd-qemu-idf6-baseline-mmio-02',
    'cyd-qemu-idf6-baseline-peripherals-01',
    'cyd-qemu-idf6-patched-mmio-01',
    'cyd-qemu-idf6-patched-peripherals-01',
    'cyd-qemu-production-observation-20261024-03',
    'cyd-qemu-idf6-build-02', 'cyd-qemu-idf6-build-03',
    'cyd-qemu-idf6-build-04', 'cyd-qemu-idf6-build-05',
    'cyd-qemu-idf6-sr2-control-mmio-01',
    'cyd-qemu-idf6-subbyte-control-mmio-01',
    'cyd-qemu-idf6-patched-mmio-02', 'cyd-qemu-idf6-patched-mmio-03',
    'cyd-qemu-idf6-patched-peripherals-02', 'cyd-qemu-idf6-patched-peripherals-03',
    'cyd-qemu-sr2-continuity-review-20261024-01',
    'cyd-qemu-subbyte-review-20261024-01',
    'cyd-qemu-input-delay-tests-prep-01', 'cyd-qemu-input-delay-primary-01',
    'cyd-qemu-input-delay-control-01', 'cyd-qemu-input-delay-control-02',
    'cyd-qemu-input-delay-0-01', 'cyd-qemu-input-delay-25-01',
    'cyd-qemu-idf6-final-mmio-01',
    'cyd-qemu-idf6-final-peripherals-0-01', 'cyd-qemu-idf6-final-peripherals-25-01',
    'cyd-qemu-production-observer-prep-04', 'cyd-qemu-production-observer-prep-05',
    'cyd-qemu-production-observer-prep-06',
    'cyd-qemu-production-observation-20261024-04',
    'cyd-qemu-production-observation-20261024-05',
    'cyd-qemu-production-observation-20261024-06',
)
plan = {}
omissions = []


def fact(path):
    raw = path.read_bytes()
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def add(target, source):
    assert target not in plan, target
    assert source.is_file() and not source.is_symlink(), str(source)
    plan[target] = source


for group in groups:
    base = root / '.build' / group
    assert base.is_dir(), str(base)
    for path in sorted(base.rglob('*')):
        if not path.is_file():
            continue
        if path.suffix.lower() in ('.exe', '.bin', '.img', '.elf', '.o', '.obj', '.pyc'):
            omissions.append(dict(source_path=str(path), **fact(path),
                                  reason='Tool or replaceable synthetic/snapshot medium body omitted'))
        else:
            add('evidence/' + group + '/' + path.relative_to(base).as_posix(), path)

qemu = Path('C:/Work/QEMU-ESP32/.worktree/cyd-idf6-compat')
source_files = (
    'hw/ssi/esp32_spi.c', 'include/hw/ssi/esp32_spi.h', 'hw/xtensa/esp32.c',
    'hw/misc/esp32_dport.c', 'include/hw/misc/esp32_dport.h', 'hw/block/m25p80.c',
    'trace/meson.build', 'scripts/tracetool/__init__.py',
    'scripts/tracetool/backend/log.py', 'scripts/tracetool/backend/ftrace.py',
    'scripts/tracetool/backend/syslog.py', 'tools/test_esp32_idf6_compat.py',
    'tools/test_esp_modules.py', 'tools/esp_board.py', 'tools/small_tv_vm.py',
    'tools/small_tv_network.py', 'tools/small_tv_web.py', 'tools/esp_services.py',
    'tools/test_esp32_spi_input_delay.py', 'docs/esp32-idf6-compat.md', '.gitattributes',
)
for relative in source_files:
    add('selected-qemu-source/' + relative, qemu / relative)
pins = root / 'tests/results/cyd-production-radio-boot-20261020/preparation/inputs.json'
add('original-production-context/inputs.json', pins)
original = json.loads(pins.read_bytes())
for role, row in original['profiles']['pdm']['files'].items():
    path = Path(row['path'])
    assert fact(path) == dict(bytes=row['bytes'], sha256=row['sha256']), str(path)
    if path.stat().st_size > 65536:
        omissions.append(dict(source_path=str(path), **fact(path), role=role,
                              reason='Original production body already identified by unchanged input inventory'))
    else:
        add('original-production-context/' + role + '/' + path.name, path)
for index, row in enumerate(original['source_evidence']):
    path = Path(row['path'])
    assert fact(path) == dict(bytes=row['bytes'], sha256=row['sha256']), str(path)
    add('original-production-context/source-evidence/' + str(index) + '/' + path.name, path)
add('verify.py', root / '.build/cyd-qemu-checkpoint-verify-01.py')
add('CHECKPOINT.md', root / '.build/cyd-qemu-checkpoint-note-01.md')
add('collector.py', Path(__file__).resolve())
add('peripheral-owned-runner.py', root / '.build/cyd-qemu-peripheral-run-01.py')
add('command-runner.py', root / '.build/cyd-vorbis-format-command-01.py')
out.mkdir()
for relative, source in plan.items():
    raw = source.read_bytes()
    target = out / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    assert target.read_bytes() == raw and source.read_bytes() == raw
(out / '.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n', encoding='ascii')
rows = [dict(path=p.relative_to(out).as_posix(), **fact(p))
        for p in sorted(out.rglob('*')) if p.is_file()]
manifest = dict(schema='cyd-qemu-idf6-compact-evidence-v1', files=rows,
                omitted_bodies=omissions, source_dependency_closure_claimed=False,
                new_guest_execution_by_collector=False, physical_qualification=False)
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(archive=str(out), indexed_files=len(rows),
                     bytes=sum(x['bytes'] for x in rows), omissions=len(omissions),
                     manifest_sha256=fact(out / 'manifest.json')['sha256']), indent=2))
