"""Actual streaming FLAC metadata EOF regressions and unchanged exact PCM.

Platform seams are the existing timer/log/FreeRTOS/Arduino host headers. The
production adapter and decoder compile unchanged, including every include.
No target scheduling, heap capacity, DMA or full FLAC conformance is claimed.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CORE = 'yoRadio/src/audioI2S/flac_decoder'
ADAPTER = 'idf/components/custom_flac'
LEGACY_ADAPTER = 'idf/esp32c3-oled-native/components/custom_flac'
TEST = 'tests/native/flac_stream_eof'


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def execute(command, log, expected=None):
    result = subprocess.run((['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + command,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    log.write_bytes(result.stdout)
    if expected is not None and result.returncode != expected:
        raise RuntimeError(f'{log.name}: exit={result.returncode}\n' + result.stdout.decode(errors='replace'))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline-revision', help='Compile this exact old adapter as an executable negative control')
    parser.add_argument('--probe', action='store_true', help='Run metadata cuts before editing; preserve actual failure status')
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__).relative_to(ROOT).as_posix(), TEST + '/main.cpp',
             CORE + '/flac_decoder.cpp', CORE + '/flac_decoder.h',
             ADAPTER + '/custom_flac_adapter.cpp', ADAPTER + '/custom_flac_adapter.h',
             'tools/audio_test_server/generate_flac_depths.py',
             'tests/native/flac_bounds/Arduino.h']
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'tests/native/flac_depths').rglob('*.h')]
    hashes = {}
    for name in files:
        data = (ROOT/name).read_bytes(); hashes[name] = hashlib.sha256(data).hexdigest()
        destination = out/'sources'/name; destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    frozen = out/'sources'
    spec = importlib.util.spec_from_file_location('fixtures', frozen/'tools/audio_test_server/generate_flac_depths.py')
    generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
    manifest = generator.generate(out/'fixtures')
    # Multiple legal metadata blocks cross internal 512-byte chunks. Verbatim
    # frames make the final split-resume call larger than one internal chunk.
    resume = next(s for s in manifest['fixtures'] if s['name'] == 'flac-24bit-mid-verbatim')
    original = (out/'fixtures'/resume['file']).read_bytes()
    metadata = bytearray(original[:42]); metadata[4] &= 0x7f
    metadata += b'\x01\x00\x04\x03' + bytes(1027)
    metadata += b'\x81\x00\x00\x00'  # last, zero-byte padding
    mixed = bytes(metadata) + original[42:]
    (out/'metadata.flac').write_bytes(mixed)
    metadata_pcm = subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(out/'metadata.flac'),
                                            '-f','s16le','-acodec','pcm_s16le','-'])
    assert len(metadata_pcm) == resume['pcm_bytes']
    assert hashlib.sha256(metadata_pcm).hexdigest() == resume['pcm_sha256']
    flags = ['g++', '-std=c++14', '-O2', '-g', '-Wall', '-Wextra',
             '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
             '-DFLAC_SEGMENTED_WORKSPACE=1', '-DFLAC_OUTPUT_FRAMES=512',
             '-I'+host(frozen/'tests/native/flac_bounds'), '-I'+host(frozen/'tests/native/flac_depths'),
             '-I'+host(frozen/CORE), '-I'+host(frozen/ADAPTER)]
    commands = []
    env = ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1', 'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '90']
    def build(name, adapter):
        command = flags + [host(frozen/CORE/'flac_decoder.cpp'), host(adapter),
                           host(frozen/TEST/'main.cpp'), '-o', host(out/name)]
        commands.append(command); execute(command, out/(name+'-build.log'), 0)
    def cut_run(name, expected):
        command = env + [host(out/name), 'cuts', host(out/'metadata.flac'), str(len(metadata))]
        commands.append(command); result = execute(command, out/(name+'-cuts.log'), expected)
        match = re.search(rb'RESULT groups=(\d+) failures=(\d+) metadata_bytes=(\d+)', result.stdout)
        assert match, result.stdout.decode(errors='replace')
        return dict(exit_code=result.returncode, groups=int(match[1]), failures=int(match[2]), metadata_bytes=int(match[3]))
    production = frozen/ADAPTER/'custom_flac_adapter.cpp'
    build('current', production)
    current = cut_run('current', None if args.probe else 0)
    report = dict(passed=current['failures'] == 0, source_sha256=hashes, sanitizers=['ASan','UBSan'],
                  current=current, commands=commands, scope=__doc__, valid_pcm=[],
                  metadata_sha256=hashlib.sha256(mixed).hexdigest(),
                  metadata_pcm_sha256=resume['pcm_sha256'],
                  ffmpeg=subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0],
                  compiler=execute(['g++','--version'], out/'compiler.log', 0).stdout.decode().splitlines()[0])
    if args.probe:
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps(current)); return current['exit_code']
    assert args.baseline_revision, 'A real old adapter revision is required for qualification'
    baseline_path = ADAPTER + '/custom_flac_adapter.cpp'
    if subprocess.run(['git','cat-file','-e',args.baseline_revision+':'+baseline_path], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        baseline_path = LEGACY_ADAPTER + '/custom_flac_adapter.cpp'
    baseline = subprocess.check_output(['git', 'show', args.baseline_revision+':'+baseline_path], cwd=ROOT)
    (out/'baseline-adapter.cpp').write_bytes(baseline)
    build('baseline', out/'baseline-adapter.cpp')
    report['baseline_adapter_path'] = baseline_path
    report['baseline_revision'] = subprocess.check_output(['git','rev-parse',args.baseline_revision],cwd=ROOT,text=True).strip()
    report['baseline_adapter_sha256'] = hashlib.sha256(baseline).hexdigest()
    report['baseline'] = cut_run('baseline', 1)
    assert report['baseline']['failures'] == 4 * len(metadata)
    fixture_list = out/'fixture-list.txt'
    fixture_list.write_bytes(''.join(s['file']+'\n' for s in manifest['fixtures']).encode('ascii'))
    for name in ['current', 'baseline']:
        destination = out/(name+'-pcm'); destination.mkdir()
        command = env + [host(out/name), 'matrix', host(fixture_list), host(out/'fixtures'), host(destination)]
        commands.append(command); execute(command, out/(name+'-matrix.log'), 0)
    # All complete files must retain exact PCM against both the executable old
    # adapter and independent FFmpeg/known encoder PCM, in three input schedules.
    for fixture in manifest['fixtures']:
        path = out/'fixtures'/fixture['file']
        reference = subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','s16le','-acodec','pcm_s16le','-'])
        assert len(reference) == fixture['pcm_bytes'] and hashlib.sha256(reference).hexdigest() == fixture['pcm_sha256']
        row = dict(name=fixture['name'], reference_sha256=fixture['pcm_sha256'], bytes=len(reference), runs=[])
        for name in ['current','baseline']:
            for mode in range(3):
                dest = out/(name+'-pcm')/(fixture['file']+f'-{mode}.pcm')
                assert dest.read_bytes() == reference, dest.name
                row['runs'].append(dict(variant=name,mode=mode,identical=True))
        report['valid_pcm'].append(row)
    report['passed'] = True
    report['valid_pcm_comparisons'] = len(report['valid_pcm']) * 6
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=True,current=current,baseline=report['baseline'],valid_pcm_comparisons=report['valid_pcm_comparisons'])))
    return 0


if __name__ == '__main__': raise SystemExit(main())
