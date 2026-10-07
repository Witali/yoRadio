"""Retain QEMU fault results and compare subsequent PCM with the prior PC19 run."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil

from compare_aac_late_sbr_pcm import parse_capture, read_log
from compare_aac_sbr_gap_pcm import parse_gaps
from run_aac_faults import parse_log

ROOT = Path(__file__).resolve().parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8', newline='\n')


def save(args):
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    raw = (args.run/'qemu.log').read_bytes()
    log = read_log(args.run/'qemu.log')
    result = json.loads((args.run/'result.json').read_text())
    parsed = parse_log(log)
    # The parser may gain stricter validation without rerunning an unchanged ELF.
    for key, value in result.items():
        if key in parsed:
            assert parsed[key] == value, key
    result.update(parsed)
    for name, key in (('sdkconfig', 'sdkconfig_sha256'),
                      ('yoradio_esp32c3_oled_native.elf', 'elf_sha256')):
        assert sha((args.build/name).read_bytes()) == result['provenance'][key]
    assert sha(raw) == result['provenance']['qemu_log_sha256']
    save_json(output/'result.json', result)
    diagnostics = '\n'.join(line for line in log.splitlines()
                            if not re.match(r'AAC_(?:GAP|LATE|RECORD)_PCM_DATA ', line))+'\n'
    (output/'diagnostics.log').write_text(diagnostics, encoding='utf-8', newline='\n')
    shutil.copyfile(args.build/'sdkconfig', output/'sdkconfig')
    comparisons = []
    for kind, parser in (('gaps', parse_gaps), ('late', parse_capture)):
        pcm = b''.join(row['pcm'] for row in parser(log))
        baseline = ROOT/'tests/results/esp32c3-aac-metadata-20261004/pc19'/(kind+'.pcm.gz')
        previous = gzip.decompress(baseline.read_bytes())
        assert pcm == previous, kind+' PCM changed after fault/recovery tests'
        (output/(kind+'.pcm.gz')).write_bytes(gzip.compress(pcm, mtime=0))
        comparisons.append(dict(case=kind, channel_samples=len(pcm)//2,
                                different=0, max_error_lsb=0, pcm_sha256=sha(pcm),
                                baseline=baseline.relative_to(ROOT).as_posix()))
    save_json(output/'pcm-comparison.json', comparisons)
    initial = output/'initial-contract-failure'
    initial.mkdir()
    shutil.copyfile(args.initial/'qemu.log', initial/'qemu.log')
    shutil.copyfile(args.initial/'sdkconfig', initial/'sdkconfig')
    shutil.copyfile(args.initial/'sources/qemu_aac_faults.c', initial/'qemu_aac_faults.c')
    save_json(initial/'provenance.json', dict(
        elf_sha256=sha((args.initial/'firmware.elf').read_bytes()),
        explanation='Test expected a public error; SDK safely skipped header-only frame with no PCM. '
                    'This assertion failure was in the initial test, not a codec crash.'))
    sources = [
        *['idf/esp32c3-oled-native/main/'+name for name in (
            'CMakeLists.txt', 'qemu_aac_test.c', 'qemu_aac_faults.c',
            'native_aac_decoder.c', 'aac_compact_owner.c', 'aac_pointer_audit.c')],
        *['tools/codec_benchmark/'+name for name in (
            'generate_aac_faults.py', 'run_aac_faults.py', 'save_aac_faults_evidence.py')],
        'tests/test-aac-faults.py', 'tests/fixtures/aac_faults/manifest.json',
    ]
    for name in sources:
        target = output/'sources'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, target)
    save_json(output/'manifest.json', dict(raw_log_sha256=sha(raw), raw_log_bytes=len(raw),
        files={p.relative_to(output).as_posix(): sha(p.read_bytes())
               for p in sorted(output.rglob('*')) if p.is_file()}))
    print(json.dumps(dict(faults=parsed, pcm=comparisons), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('run', 'build', 'initial', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    save(parser.parse_args())
