#!/usr/bin/env python3
"""Build isolated unchanged/fixed model relays from exact retained inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import struct
import subprocess

OUT = Path(__file__).resolve().parent
WORK = OUT.parent.parent
QEMU = Path('C:/Work/QEMU-ESP32')
BUILD = QEMU / 'build'
MINGW = Path('C:/Work/HLV-codec/local_tools/msys2/msys64/mingw64/bin')
GCC = MINGW / 'gcc.exe'
SELECTED = WORK / '.build/cyd-openeth-ota-lifecycle-20261116/qemu-system-xtensa.exe'
RELAY = WORK / '.build/cyd-openeth-ota-lifecycle-20261116/link.rsp'
MODEL = WORK / '.build/cyd-pdm-dma-qemu-20261113/esp32_i2s_dac.c'
OBJECT = MODEL.with_suffix('.obj')
EXPECTED_EXE = 'eb88d36f5bea48f547615ee147cf01985f9adf301112e2954ad90b8ca461ed02'
EXPECTED_MODEL = 'a05e52b1cfa0f4c5a1d74bed70efb8761d8a54cf18a120b10c45f1887cd3c286'
EXPECTED_OBJECT = '30be297358d6fef894223208a70d3e7d5ee0a35c99d3d4c5521b60fa28f9eb86'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def record(path):
    path = path.resolve(strict=True)
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def git_state():
    def git(*args):
        return subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.longpaths=true',
                                        *args], cwd=WORK, text=True).strip()
    index = Path(git('rev-parse', '--git-path', 'index'))
    if not index.is_absolute():
        index = WORK / index
    return {'head': git('rev-parse', 'HEAD'),
            'tracked_status': git('status', '--porcelain', '--untracked-files=no'),
            'index_sha256': sha(index)}


def pe(path):
    raw = path.read_bytes()
    off = struct.unpack_from('<I', raw, 0x3c)[0]
    assert raw[off:off + 4] == b'PE\x00\x00'
    section_count, timestamp = struct.unpack_from('<HI', raw, off + 6)
    opt_size = struct.unpack_from('<H', raw, off + 20)[0]
    section_offset = off + 24 + opt_size
    sections = []
    sections_without_link_timestamps = []
    normalized = bytearray(raw)
    for n in range(section_count):
        p = section_offset + 40 * n
        name, virtual_size, rva, size, data = struct.unpack_from('<8sIIII', raw, p)
        sections.append({'name': name.rstrip(b'\0').decode('ascii'),
                         'virtual_size': virtual_size, 'rva': rva, 'raw_bytes': size,
                         'sha256': hashlib.sha256(raw[data:data + size]).hexdigest()})
        section_bytes = bytearray(raw[data:data + size])
        if name.rstrip(b'\0') == b'.edata':
            # IMAGE_EXPORT_DIRECTORY.TimeDateStamp duplicates the link timestamp.
            section_bytes[4:8] = bytes(4)
            normalized[data + 4:data + 8] = bytes(4)
        sections_without_link_timestamps.append({**sections[-1],
            'sha256': hashlib.sha256(section_bytes).hexdigest()})
    normalized[off + 8:off + 12] = bytes(4)
    # Checksum may incorporate the timestamp, so report this normalization separately.
    checksum = off + 24 + 64
    normalized[checksum:checksum + 4] = bytes(4)
    return {'file': record(path), 'coff_timestamp': timestamp, 'sections': sections,
            'sections_without_link_timestamps': sections_without_link_timestamps,
            'coff_export_timestamps_and_checksum_zero_sha256': hashlib.sha256(normalized).hexdigest()}


def compare(left, right):
    a, b = pe(left), pe(right)
    return {'left': a, 'right': b, 'section_tables_and_bytes_identical': a['sections'] == b['sections'],
            'sections_identical_except_export_timestamp': a['sections_without_link_timestamps'] ==
                                                         b['sections_without_link_timestamps'],
            'normalized_whole_image_identical': a['coff_export_timestamps_and_checksum_zero_sha256'] ==
                                               b['coff_export_timestamps_and_checksum_zero_sha256'],
            'different_section_names': [x['name'] for x, y in zip(a['sections'], b['sections']) if x != y]}


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def run(args, label):
    env = dict(os.environ, PATH=str(MINGW) + os.pathsep + os.environ['PATH'])
    with (OUT / (label + '-stdout.log')).open('wb') as stdout, \
         (OUT / (label + '-stderr.log')).open('wb') as stderr:
        result = subprocess.run(args, cwd=BUILD, env=env, stdout=stdout, stderr=stderr,
                                timeout=240, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    if result.returncode:
        raise RuntimeError(f'{label} failed with {result.returncode}; see private stderr log')


def link(label, obj):
    text = RELAY.read_text()
    old_output = '-o "' + SELECTED.as_posix() + '"'
    old_object = '"' + OBJECT.as_posix() + '"'
    assert text.count(old_output) == 1
    assert text.count(old_object) == 1
    directory = OUT / label
    directory.mkdir()
    target = directory / 'qemu-system-xtensa.exe'
    assert not target.exists()
    text = text.replace(old_output, '-o "' + target.as_posix() + '"', 1)
    text = text.replace(old_object, '"' + obj.as_posix() + '"', 1)
    rsp = OUT / (label + '.rsp')
    rsp.write_text(text, newline='\n')
    run([str(GCC), '-m64', '@' + rsp.as_posix()], label + '-link')
    return target


def compile_model(source, label, command):
    args = shlex.split(command)
    obj = OUT / (label + '.obj')
    for switch, value in (('-MQ', str(obj)), ('-MF', str(obj) + '.d'), ('-o', str(obj))):
        args[args.index(switch) + 1] = value.replace('\\', '/')
    original = '../hw/audio/esp32_i2s_dac.c'
    assert args.count(original) == 1
    args[args.index(original)] = source.as_posix()
    write_json(label + '-compile-argv.json', [str(GCC), *args[1:]])
    run([str(GCC), *args[1:]], label + '-compile')
    return obj


def inspect_inputs():
    for path, digest in ((SELECTED, EXPECTED_EXE), (MODEL, EXPECTED_MODEL), (OBJECT, EXPECTED_OBJECT)):
        assert sha(path) == digest, str(path)
    state = git_state()
    assert state['head'] == 'b65437a1bc59c9d269ce7bece597efddc70cea58'
    assert not state['tracked_status']
    db = json.loads((BUILD / 'compile_commands.json').read_text())
    entry, = [x for x in db if x['file'] == '../hw/audio/esp32_i2s_dac.c']
    tokens = shlex.split(RELAY.read_text())
    paths = [SELECTED, RELAY, MODEL, OBJECT, GCC, BUILD / 'compile_commands.json']
    for token in tokens[2:]:
        if token.startswith('-'):
            continue
        path = Path(token.lstrip('@'))
        if not path.is_absolute():
            path = BUILD / path
        if path.is_file():
            paths.append(path)
    unique = sorted({str(x.resolve()): x for x in paths}.values(), key=lambda x: str(x))
    manifest = {'state_before': state, 'compiler_record': entry,
                'inputs': [record(path) for path in unique],
                'scope': 'Private relays only. No QEMU repository, production source, index, or firmware writes.'}
    write_json('input-manifest.json', manifest)
    return manifest, entry


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('relink', 'compile'))
    args = p.parse_args()
    manifest, entry = inspect_inputs()
    if args.mode == 'relink':
        target = link('baseline-matched-name', OBJECT)
        comparison = compare(SELECTED, target)
        write_json('baseline-matched-name-pe-comparison.json', comparison)
        print(json.dumps({'mode': args.mode, 'output': str(target),
                          'input_count': len(manifest['inputs']),
                          'sections_identical': comparison['section_tables_and_bytes_identical'],
                          'normalized_image_identical': comparison['normalized_whole_image_identical'],
                          'different_sections': comparison['different_section_names']}))
    else:
        baseline = compile_model(MODEL, 'baseline-recompiled', entry['command'])
        base_exe = link('baseline-recompiled', baseline)
        write_json('baseline-recompiled-pe-comparison.json', compare(SELECTED, base_exe))
        raw = MODEL.read_bytes()
        old = b's->regs[address / 4] = val & ~I2S_OUT_LINK_PARK;'
        new = b's->regs[address / 4] = val & ~(I2S_OUT_LINK_PARK | I2S_OUT_LINK_START);'
        assert raw.count(old) == 1
        fixed = OUT / 'esp32_i2s_dac.c'
        fixed.write_bytes(raw.replace(old, new, 1))
        (OUT / 'retained_model.c').write_bytes(raw)
        obj = compile_model(fixed, 'fixed-self-clear', entry['command'])
        fixed_exe = link('fixed-self-clear', obj)
        write_json('output-manifest.json', {'state_after': git_state(),
                   'baseline_source': record(MODEL), 'private_baseline_copy': record(OUT / 'retained_model.c'),
                   'fixed_source': record(fixed), 'baseline_object': record(baseline),
                   'fixed_object': record(obj), 'baseline_exe': record(base_exe),
                   'fixed_exe': record(fixed_exe),
                   'patch': {'old': old.decode(), 'new': new.decode()}})
        print(json.dumps({'mode': args.mode, 'baseline': str(base_exe), 'fixed': str(fixed_exe),
                          'sections_identical_for_recompiled_baseline':
                          compare(SELECTED, base_exe)['section_tables_and_bytes_identical']}))
    state_after = git_state()
    assert state_after == manifest['state_before'], 'Repository state changed during private build'


if __name__ == '__main__':
    main()
