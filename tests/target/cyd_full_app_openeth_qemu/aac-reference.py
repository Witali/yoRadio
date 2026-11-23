"""Prepare and run an isolated complete public AAC PCM reference on LX6."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
REPO = ROOT.parent.parent if ROOT.parent.name == '.worktree' else ROOT
PROJECT = Path(__file__).with_name('aac_reference')
ARCHIVES = {'libesp_audio_codec.a': '92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58',
            'libesp_audio_simple_dec.a': 'ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6'}


def pin(path):
    body = path.read_bytes()
    return dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())


def fixtures():
    make = runpy.run_path(str(ROOT / 'tests/run-cyd-full-app-openeth.py'))['aac_fixture']
    return [(profile, make(profile)) for profile in ('lc', 'he')]


def validate_log(text, expected):
    if re.search(r'Guru Meditation|assert failed|abort\(\)|CORRUPT HEAP|watchdog.*triggered|stack overflow', text, re.I):
        raise ValueError('Reference logged a native fault')
    lines = [line for line in text.splitlines() if line.startswith('AAC_TLS_REFERENCE')]
    if len(lines) != 5 or lines[-1] != 'AAC_TLS_REFERENCE_COMPLETE cases=4 handles_closed=4 heap_integrity=1':
        raise ValueError('Incomplete reference case/handle census')
    rows = []
    keys = {'profile', 'plus', 'input', 'input_sha256', 'rate', 'channels', 'bits', 'frames',
            'pcm_bytes', 'pcm_sha256', 'calls', 'resizes', 'heap_before', 'heap_after',
            'stack_free', 'core', 'priority', 'drained'}
    for index, line in enumerate(lines[:-1]):
        fields = line.removeprefix('AAC_TLS_REFERENCE ').split()
        if any(field.count('=') != 1 for field in fields):
            raise ValueError('Malformed reference record')
        pairs = [field.split('=') for field in fields]
        row = dict(pairs)
        if len(pairs) != len(keys) or set(row) != keys:
            raise ValueError('Unexpected reference fields')
        for key in keys - {'profile', 'input_sha256', 'pcm_sha256'}:
            if not row[key].isdigit():
                raise ValueError('Invalid numeric reference observation')
            row[key] = int(row[key])
        profile = ('lc', 'he')[index // 2]
        plus = 1 - index % 2
        fixture = expected[profile]
        rate = 48000 if plus else fixture['core_rate']
        frames = fixture['adts_frames'] * 1024 * (rate // fixture['core_rate'])
        if not (row['profile'] == profile and row['plus'] == plus and row['core'] == 1 and row['priority'] == 3
                and row['input'] == fixture['input_bytes'] and row['input_sha256'] == fixture['input_sha256']
                and row['rate'] == rate and row['channels'] == 2 and row['bits'] == 16
                and row['frames'] == frames and row['pcm_bytes'] == frames * 4 and row['drained'] == 1
                and 0 < row['calls'] < fixture['adts_frames'] * 4 + 16
                and 0 < row['stack_free'] <= 16384 and row['heap_before'] > 0 and row['heap_after'] > 0
                and re.fullmatch('[a-f0-9]{64}', row['pcm_sha256'])):
            raise ValueError('Reference disagrees with complete input, PCM geometry or task contract')
        rows.append(row)
    if rows[0]['pcm_sha256'] != rows[1]['pcm_sha256']:
        raise ValueError('LC changed with AAC-Plus preference')
    if rows[2]['pcm_sha256'] == rows[3]['pcm_sha256']:
        raise ValueError('HE control failed to distinguish full-rate and core output')
    if any(row['heap_before'] != row['heap_after'] for row in rows[1:]):
        raise ValueError('Repeated reference handle retained heap')
    return rows


def validate_frame_log(text, expected, base_cases):
    lines = [line for line in text.splitlines() if line.startswith('AAC_TLS_FRAME_REFERENCE')]
    if len(lines) != 5 or lines[-1] != 'AAC_TLS_FRAME_REFERENCE_COMPLETE cases=4 handles_closed=4 heap_integrity=1':
        raise ValueError('Incomplete frame-input reference census')
    full = {row['profile']: row for row in base_cases if row['plus'] == 1}
    keys = set(base_cases[0]) | {'initial_capacity', 'empty_retries', 'encoded_frames', 'last_frame_eos'}
    rows = []
    for index, line in enumerate(lines[:-1]):
        fields = [field.split('=') for field in line.removeprefix('AAC_TLS_FRAME_REFERENCE ').split()]
        if any(len(field) != 2 for field in fields):
            raise ValueError('Malformed frame-input record')
        row = dict(fields)
        if len(fields) != len(keys) or set(row) != keys:
            raise ValueError('Unexpected frame-input fields')
        for key in keys - {'profile', 'input_sha256', 'pcm_sha256'}:
            if not row[key].isdigit():
                raise ValueError('Invalid frame-input observation')
            row[key] = int(row[key])
        profile = ('lc', 'he')[index // 2]
        capacity = (12288, 1024)[index % 2]
        fixture, baseline = expected[profile], full[profile]
        identity = ('input', 'input_sha256', 'rate', 'channels', 'bits', 'frames', 'pcm_bytes', 'pcm_sha256')
        if not (row['profile'] == profile and row['plus'] == 1 and row['initial_capacity'] == capacity
                and row['core'] == 1 and row['priority'] == 3 and row['last_frame_eos'] == 1
                and row['drained'] == 0 and row['encoded_frames'] == fixture['adts_frames']
                and all(row[key] == baseline[key] for key in identity)
                and 0 < row['calls'] < fixture['adts_frames'] * 4 + 16
                and 0 < row['stack_free'] <= 16384 and row['heap_before'] == row['heap_after'] > 0
                and 0 <= row['empty_retries'] <= row['resizes']
                and (capacity != 1024 or row['resizes'] > 0)):
            raise ValueError('Frame input differs from full PCM, input, retry or task contract')
        rows.append(row)
    return rows


def validate_buffer_log(text, expected, base_cases):
    lines = [line for line in text.splitlines() if line.startswith('AAC_TLS_BUFFER_REFERENCE')]
    if len(lines) != 3 or lines[-1] != 'AAC_TLS_BUFFER_REFERENCE_COMPLETE cases=2 handles_closed=2 heap_integrity=1':
        raise ValueError('Incomplete parsed-buffer reference census')
    full = {row['profile']: row for row in base_cases if row['plus'] == 1}
    rows = []
    for profile, line in zip(('lc', 'he'), lines[:-1]):
        pairs = [field.split('=') for field in line.removeprefix('AAC_TLS_BUFFER_REFERENCE ').split()]
        if any(len(pair) != 2 for pair in pairs):
            raise ValueError('Malformed parsed-buffer reference')
        row = dict(pairs)
        keys = set(base_cases[0]) | {'initial_capacity'}
        if len(pairs) != len(keys) or set(row) != keys:
            raise ValueError('Unexpected parsed-buffer fields')
        for key in keys - {'profile', 'input_sha256', 'pcm_sha256'}:
            if not row[key].isdigit():
                raise ValueError('Invalid parsed-buffer observation')
            row[key] = int(row[key])
        baseline = full[profile]
        if not (row['profile'] == profile and row['plus'] == 1 and row['initial_capacity'] == 1024
                and row['drained'] == 1 and row['core'] == 1 and row['priority'] == 3
                and row['heap_before'] == row['heap_after'] > 0 and row['resizes'] > 0
                and 0 < row['stack_free'] <= 16384 and 0 < row['calls'] < expected[profile]['adts_frames'] * 4 + 16
                and all(row[key] == baseline[key] for key in
                        ('input', 'input_sha256', 'rate', 'channels', 'bits', 'frames', 'pcm_bytes', 'pcm_sha256'))):
            raise ValueError('Parsed-buffer input differs from complete reference PCM or lifetime')
        rows.append(row)
    return rows


def validate_fragment_log(text, expected, base_cases):
    lines = [line for line in text.splitlines() if line.startswith('AAC_TLS_FRAGMENT_REFERENCE')]
    if len(lines) != 5 or lines[-1] != 'AAC_TLS_FRAGMENT_REFERENCE_COMPLETE cases=4 handles_closed=4 heap_integrity=1':
        raise ValueError('Incomplete fragmented-input reference census')
    full = {row['profile']: row for row in base_cases if row['plus'] == 1}
    rows = []
    keys = set(base_cases[0]) | {'initial_capacity', 'framed', 'chunk', 'encoded_frames', 'last_frame_eos'}
    for index, line in enumerate(lines[:-1]):
        pairs = [field.split('=') for field in line.removeprefix('AAC_TLS_FRAGMENT_REFERENCE ').split()]
        if any(len(pair) != 2 for pair in pairs):
            raise ValueError('Malformed fragmented-input reference')
        row = dict(pairs)
        if len(pairs) != len(keys) or set(row) != keys:
            raise ValueError('Unexpected fragmented-input fields')
        for key in keys - {'profile', 'input_sha256', 'pcm_sha256'}:
            if not row[key].isdigit():
                raise ValueError('Invalid fragmented-input observation')
            row[key] = int(row[key])
        profile, framed = ('lc', 'he')[index // 2], index % 2
        fixture, baseline = expected[profile], full[profile]
        if not (row['profile'] == profile and row['plus'] == 1 and row['framed'] == framed
                and row['initial_capacity'] == 8192 and row['chunk'] == 257
                and row['drained'] == 1 - framed and row['encoded_frames'] == (fixture['adts_frames'] if framed else 0)
                and row['last_frame_eos'] == framed and row['core'] == 1 and row['priority'] == 3
                and row['heap_before'] == row['heap_after'] > 0 and row['resizes'] == 0
                and 0 < row['stack_free'] <= 16384
                and 0 < row['calls'] < fixture['adts_frames'] * 4 + 16 + 2 * (fixture['input_bytes'] // 257 + 1)
                and all(row[key] == baseline[key] for key in
                        ('input', 'input_sha256', 'rate', 'channels', 'bits', 'frames', 'pcm_bytes', 'pcm_sha256'))):
            raise ValueError('Fragmented input differs from complete reference PCM or ownership')
        rows.append(row)
    return rows


def validate_memory_log(text, expectations, require_samples=False):
    lines = [line for line in text.splitlines() if line.startswith('AAC_TLS_MEMORY')]
    if len(lines) != len(expectations):
        raise ValueError('Incomplete live-memory census')
    rows = []
    keys = {'profile', 'plus', 'framed', 'initial_capacity', 'final_capacity', 'live_free'}
    sampled = {'chunk', 'min_live_free'}
    for line, (case, framed, initial, chunk) in zip(lines, expectations):
        pairs = [field.split('=') for field in line.removeprefix('AAC_TLS_MEMORY ').split()]
        if any(len(pair) != 2 for pair in pairs):
            raise ValueError('Malformed live-memory observation')
        row = dict(pairs)
        if len(pairs) != len(row) or set(row) not in (keys, keys | sampled):
            raise ValueError('Unexpected live-memory fields')
        if require_samples and set(row) != keys | sampled:
            raise ValueError('Missing sampled memory observations')
        for key in set(row) - {'profile'}:
            if not row[key].isdigit():
                raise ValueError('Invalid live-memory observation')
            row[key] = int(row[key])
        row.setdefault('chunk', 0)
        row.setdefault('min_live_free', None)
        if not (row['profile'] == case['profile'] and row['plus'] == case['plus']
                and row['framed'] == framed and row['initial_capacity'] == initial and row['chunk'] == chunk
                and row['final_capacity'] >= initial and 0 < row['live_free'] < case['heap_before']
                and (case['resizes'] > 0 or row['final_capacity'] == initial)
                and (row['min_live_free'] is None or 0 < row['min_live_free'] < case['heap_before'])):
            raise ValueError('Live memory differs from the completed case or buffer policy')
        rows.append(row)
    return rows


def main():
    if not __debug__:
        raise RuntimeError('Run the reference controller without Python -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'run'))
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--qemu', type=Path)
    parser.add_argument('--rom', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--frame-input', action='store_true', help='Prepare four additional complete-frame public API cases')
    parser.add_argument('--small-buffers', action='store_true', help='Prepare two parsed cases with forced public output growth')
    parser.add_argument('--fragmented-input', action='store_true', help='Prepare four 257-byte transport cases')
    args = parser.parse_args()
    campaign = args.campaign.resolve()
    if not campaign.is_relative_to(ROOT / '.build') or campaign == ROOT / '.build':
        raise ValueError('Use a task directory under .build')
    if args.action == 'prepare':
        campaign.mkdir(parents=True)
        project = campaign / 'project'
        shutil.copytree(PROJECT, project)
        if args.frame_input:
            cmake = project / 'main/CMakeLists.txt'
            with cmake.open('a', encoding='utf-8', newline='\n') as out:
                out.write('\ntarget_compile_definitions(${COMPONENT_LIB} PRIVATE AAC_REFERENCE_FRAME_INPUT=1)\n')
        if args.small_buffers:
            with (project / 'main/CMakeLists.txt').open('a', encoding='utf-8', newline='\n') as out:
                out.write('\ntarget_compile_definitions(${COMPONENT_LIB} PRIVATE AAC_REFERENCE_SMALL_BUFFER=1)\n')
        if args.fragmented_input:
            with (project / 'main/CMakeLists.txt').open('a', encoding='utf-8', newline='\n') as out:
                out.write('\ntarget_compile_definitions(${COMPONENT_LIB} PRIVATE AAC_REFERENCE_FRAGMENTED_INPUT=1)\n')
        seed = ROOT / 'tests/target/cyd_aac_public_config_qemu'
        shutil.copyfile(seed / 'partitions.csv', project / 'partitions.csv')
        config = (seed / 'sdkconfig.common.defaults').read_text()
        config += '\nCONFIG_IDF_TARGET="esp32"\nCONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_240=y\n# CONFIG_FREERTOS_UNICORE is not set\nCONFIG_ESP_TASK_WDT_TIMEOUT_S=5\n'
        (project / 'sdkconfig.defaults').write_text(config, encoding='utf-8', newline='\n')
        offset = 80
        entries, payloads, expected = [], [], {}
        for name, fixture in fixtures():
            body = fixture['data']
            entries.append(struct.pack('<8s6I', name.encode(), offset, len(body), fixture['adts_frames'],
                                       fixture['core_rate'], 2, 48000))
            payloads.append(body)
            offset += len(body)
            expected[name] = dict(input_bytes=len(body), input_sha256=hashlib.sha256(body).hexdigest(),
                                  adts_frames=fixture['adts_frames'], core_rate=fixture['core_rate'],
                                  pcm_frames=fixture['pcm_frames'], repetitions=fixture['repetitions'],
                                  source_sha256=fixture['source_sha256'])
        (project / 'main/fixtures.bin').write_bytes(struct.pack('<4I', 0x41414354, 1, 2, 32) + b''.join(entries + payloads))
        manifest = dict(schema=1, expected=expected, frame_input=args.frame_input, small_buffers=args.small_buffers,
                        fragmented_input=args.fragmented_input,
                        inputs={p.relative_to(project).as_posix(): pin(p)
                        for p in project.rglob('*') if p.is_file()}, archives=ARCHIVES,
                        preparer=pin(Path(__file__)))
        (campaign / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        print('Prepared two complete AAC inputs and an independent public-API reference project.')
        return 0
    if not args.qemu or not args.rom or not args.output:
        parser.error('run requires --qemu, --rom and --output')
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / '.build') or output == ROOT / '.build':
        raise ValueError('Use a fresh result directory under .build')
    output.mkdir(parents=True)
    manifest = json.loads((campaign / 'manifest.json').read_bytes())
    project, build = campaign / 'project', campaign / 'build'
    for name, expected in manifest['inputs'].items():
        assert pin(project / name) == expected, 'Frozen reference input changed'
    vendor = REPO / '.idf/esp-adf-libs/esp_audio_codec'
    for name, expected in ARCHIVES.items():
        assert pin(vendor / 'lib/esp32' / name)['sha256'] == expected, 'Vendor archive changed'
    recipe = json.loads((build / 'flasher_args.json').read_bytes())
    config = json.loads((build / 'config/sdkconfig.json').read_bytes())
    assert config['IDF_TARGET'] == 'esp32' and not config['FREERTOS_UNICORE']
    assert config['ESP_TASK_WDT_TIMEOUT_S'] == 5 and config['ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0'] and config['ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1']
    assert config['COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE'] and config['FREERTOS_CHECK_STACKOVERFLOW_CANARY']
    flash = bytearray(b'\xff' * (4 * 1024**2))
    parts = []
    end = 0
    for address, name in sorted((int(a, 0), n) for a, n in recipe['flash_files'].items()):
        source = (build / name).resolve(strict=True)
        assert source.is_relative_to(build)
        body = source.read_bytes()
        assert end <= address < address + len(body) <= len(flash)
        end = address + len(body)
        flash[address:end] = body
        parts.append(dict(offset=address, file=name, **pin(source)))
    assert {p['offset'] for p in parts} == {0x1000, 0x8000, 0x10000}
    flash_path = output / 'flash.bin'
    flash_path.write_bytes(flash)
    command = [str(args.qemu.resolve(strict=True)), '-M', 'esp32', '-smp', '2', '-L', str(args.rom.resolve(strict=True)),
               '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot', '-snapshot',
               '-nic', 'none', '-drive', 'file=' + str(flash_path).replace(',', ',,') + ',if=mtd,format=raw']
    description = json.loads((build / 'project_description.json').read_bytes())
    elf = build / description['app_elf']
    assert elf.read_bytes()[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', elf.read_bytes(), 18)[0] == 94
    paths = [Path(value).resolve() for value in description['build_component_paths']]
    assert vendor.resolve() in paths, 'The compiler used a different vendor component'
    link_map = elf.with_suffix('.map').read_text('utf-8', errors='replace').replace('\\', '/')
    assert all((vendor / 'lib/esp32' / name).as_posix() in link_map for name in ARCHIVES)
    assert '__wrap_esp_audio' not in link_map and 'aac_compact' not in link_map
    commands = json.loads((build / 'compile_commands.json').read_bytes())
    selected = [entry for entry in commands if Path(entry['file']).resolve() == project / 'main/main.c']
    assert len(selected) == 1 and '-UNDEBUG' in selected[0]['command']
    compiler = Path(description['c_compiler'])
    revisions = {}
    for name, directory, expected in (
            ('vendor', vendor.parent, '67b8d0e98f58c774b8652480893037273190e8dc'),
            ('sdk', REPO / '.idf/v6.0.2', '7101770dc6db2667b3c477cc31365dd1acd6db4e')):
        actual = subprocess.check_output(['git', '-C', str(directory), 'rev-parse', 'HEAD'], text=True).strip()
        assert actual == expected, 'Pinned source revision changed'
        assert not subprocess.check_output(['git', '-c', 'core.longpaths=true', '-C', str(directory),
                                            'status', '--porcelain', '--untracked-files=no'])
        revisions[name] = actual
    report = dict(passed=False, state='STARTING', scope='complete direct public AAC integration identity; not independent numerical conformance',
                  physical_tested=False, expected=manifest['expected'], archives=ARCHIVES,
                  qemu=pin(args.qemu), elf=pin(elf), flash_parts=parts, inputs=manifest['inputs'],
                  runner=pin(Path(__file__)), watchdog_seconds=5)
    report.update(revisions=revisions, compiler=pin(compiler),
                  compiled_reference_source=pin(project / 'main/main.c'),
                  compile_command_sha256=hashlib.sha256(selected[0]['command'].encode()).hexdigest())

    def save():
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    save()
    try:
        with (output / 'qemu.log').open('xb') as log:
            child = subprocess.Popen(command, cwd=output, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            report.update(state='RUNNING', pid=child.pid)
            save()
            try:
                child.wait(timeout=120)
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait()
                report['qemu_exit_status'] = child.returncode
        assert child.returncode == 0, 'Reference QEMU did not exit successfully'
        text = (output / 'qemu.log').read_text('utf-8', errors='replace')
        rows = validate_log(text, manifest['expected'])
        if manifest.get('small_buffers'):
            report['buffer_cases'] = validate_buffer_log(text, manifest['expected'], rows)
        if manifest.get('fragmented_input'):
            report['fragment_cases'] = validate_fragment_log(text, manifest['expected'], rows)
        if manifest.get('frame_input'):
            report['frame_cases'] = validate_frame_log(text, manifest['expected'], rows)
        if manifest.get('frame_input') or manifest.get('small_buffers') or manifest.get('fragmented_input'):
            expectations = [(case, 0, 12288, 0) for case in rows]
            expectations += [(case, 1, case['initial_capacity'], 0) for case in report.get('frame_cases', [])]
            expectations += [(case, 0, case['initial_capacity'], 0) for case in report.get('buffer_cases', [])]
            expectations += [(case, case['framed'], 8192, 257) for case in report.get('fragment_cases', [])]
            report['live_memory'] = validate_memory_log(text, expectations, require_samples=bool(manifest.get('fragmented_input')))
        report['handles_closed'] = 4 + 4 * bool(manifest.get('frame_input')) + 2 * bool(manifest.get('small_buffers')) + 4 * bool(manifest.get('fragmented_input'))
        report.update(passed=True, state='TERMINAL_PASS', cases=rows)
    except Exception as error:
        report.update(state='TERMINAL_NONPASS', failure_type=type(error).__name__)
        raise
    finally:
        report['log'] = pin(output / 'qemu.log') if (output / 'qemu.log').is_file() else None
        save()
    print(json.dumps(dict(passed=True, cases=4, frame_cases=len(report.get('frame_cases', [])),
                          buffer_cases=len(report.get('buffer_cases', [])), handles_closed=report['handles_closed'],
                          fragment_cases=len(report.get('fragment_cases', [])),
                          identities={r['profile']: r['pcm_sha256'] for r in rows if r['plus']})))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
