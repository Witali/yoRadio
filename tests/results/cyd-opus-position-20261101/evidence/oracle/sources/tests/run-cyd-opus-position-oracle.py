"""Compare complete CYD public-vendor PCM to an independent public libopus decode.

The new native PCM capture must already have completed successfully. Every
possible full-playback-length vendor window is compared; no selected interior
window, fitted gain or resampling is used. PCM and executable bytes stay local.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path('tests/results/cyd-opus-position-20261101/source/reference.c')
NATIVE_READER = Path('tests/run-cyd-opus-position-qemu.py')
FIXTURES = {
    'F20': ('tests/fixtures/esp32c3_calibration/opus-510.ogg',
            '53b3ee1b3c883d4a282fa88d0ad42361a8d00eddb5d4ebe9e50657336c5b2a11', 528960),
    'F120': ('tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg',
             'b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679', 529920),
}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def file_pin(path):
    path = Path(path)
    return dict(bytes=path.stat().st_size, sha256=sha(path.read_bytes()))


def host(path):
    path = Path(path).resolve().as_posix()
    return '/mnt/' + path[0].lower() + path[2:] if sys.platform == 'win32' else path


def packets(body):
    """Independent complete Ogg reassembly, CRC/continuation and serial checks."""
    at = 0
    pending = bytearray()
    complete, granules = [], []
    sequence, serial = 0, None
    while at < len(body):
        need(body[at:at+5] == b'OggS\0' and at + 27 <= len(body), 'complete Ogg v0 page')
        n = body[at+26]
        need(at+27+n <= len(body), 'complete lacing table')
        lace = body[at+27:at+27+n]
        end = at+27+n+sum(lace)
        need(end <= len(body), 'complete page payload')
        page = bytearray(body[at:end])
        stored = int.from_bytes(page[22:26], 'little')
        page[22:26] = bytes(4)
        crc = 0
        for byte in page:
            crc ^= byte << 24
            for _ in range(8):
                crc = ((crc << 1) ^ (0x04c11db7 if crc & 0x80000000 else 0)) & 0xffffffff
        need(crc == stored, 'every original page CRC')
        current = int.from_bytes(page[14:18], 'little')
        if serial is None:
            serial = current
        flags = page[5]
        need(current == serial and int.from_bytes(page[18:22], 'little') == sequence,
             'one consecutive original logical stream')
        need(bool(flags & 1) == bool(pending) and not flags & ~7,
             'continued packets agree with lacing')
        need(bool(flags & 2) == (sequence == 0) and bool(flags & 4) == (end == len(body)),
             'actual complete BOS/EOS boundaries')
        pos = 27+n
        before = len(complete)
        for size in lace:
            pending.extend(page[pos:pos+size])
            pos += size
            if size < 255:
                complete.append(bytes(pending))
                pending.clear()
        granules.append(dict(sequence=sequence, granule=int.from_bytes(page[6:14], 'little'),
                             packet_begin=before, packet_end=len(complete), eos=bool(flags & 4)))
        sequence += 1
        at = end
    need(not pending and len(complete) > 2, 'all original packets complete')
    head = complete[0]
    need(len(head) == 19 and head[:9] == b'OpusHead\1' and head[9] == 2 and
         head[16:19] == bytes(3) and complete[1].startswith(b'OpusTags'),
         'stereo family-zero zero-gain Opus headers')
    return complete[2:], int.from_bytes(head[10:12], 'little'), granules


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-capture', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out, native = args.output.resolve(), args.native_capture.resolve()
    need(out.is_relative_to(ROOT / '.build') and not out.exists(), 'fresh ignored capture required')
    need(native.is_relative_to(ROOT / '.build') and native.is_dir(), 'actual local native capture required')
    out.mkdir(parents=True)
    report = dict(schema=1, passed=False, completed=False, metadata_only=False,
                  numeric_conformance_claim=False, production_trim_implemented=False,
                  physical_hardware=False, sources=[], commands=[], native_capture=native.relative_to(ROOT).as_posix())

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def command(name, argv, timeout=180):
        full = (['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + list(map(str, argv))
        row = dict(name=name, argv=full, state='starting', exit_status=None)
        report['commands'].append(row)
        stdout_path, stderr_path = out / (name+'.stdout.log'), out / (name+'.stderr.log')
        start = time.monotonic()
        with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
            child = subprocess.Popen(full, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL)
            row.update(pid=child.pid, state='running')
            save()
            try:
                status = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                child.kill()
                status = child.wait()
                row['timed_out'] = True
            row.update(state='complete', exit_status=status, elapsed_seconds=round(time.monotonic()-start, 3))
        row['stdout'] = dict(path=stdout_path.name, **file_pin(stdout_path))
        row['stderr'] = dict(path=stderr_path.name, **file_pin(stderr_path))
        save()
        need(status == 0 and not row.get('timed_out'), 'actual command terminal zero: '+name)
        return stdout_path.read_bytes()

    save()
    try:
        for relative in [Path(__file__).resolve().relative_to(ROOT), REFERENCE, NATIVE_READER,
                         *[Path(row[0]) for row in FIXTURES.values()]]:
            path = ROOT / relative
            snapshot = out / 'sources' / relative
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_bytes(path.read_bytes())
            report['sources'].append(dict(path=relative.as_posix(), snapshot=snapshot.relative_to(out).as_posix(), **file_pin(path)))
        native_report = json.loads((native / 'report.json').read_bytes())
        need(native_report['passed'] and native_report['completed'] and native_report['target_executed'] and
             native_report['all_bound_inputs_current'], 'actual completed native PCM capture')
        expected_commands = ['vendor-head', 'vendor-clean', 'sdk-head', 'sdk-clean', 'build', 'symbols', 'merge', 'qemu']
        need([row['name'] for row in native_report['commands']] == expected_commands, 'all original native commands')
        for row in native_report['commands']:
            need(row['state'] == 'complete' and row['pid'] > 0 and row['exit_status'] == 0, 'native command terminal status')
            for stream in ('stdout', 'stderr'):
                need(sha((native / (row['name']+'.'+stream+'.log')).read_bytes()) == row[stream+'_sha256'], 'actual original native log bytes')
        child = json.loads((native / 'sdk-child.json').read_text('utf-8-sig'))
        need(child['pid'] > 0 and child['exit_status'] == 0, 'actual SDK driver child exit')
        for original, pin in native_report['inputs'].items():
            need(file_pin(original) == dict(bytes=pin['bytes'], sha256=pin['sha256']) and
                 file_pin(native / pin['snapshot']) == dict(bytes=pin['bytes'], sha256=pin['sha256']), 'all native original/frozen source bindings')
        for name, digest in native_report['build_outputs'].items():
            need(sha((native / name).read_bytes()) == digest, 'actual bound image/build artifact identity')
        module_path = out / 'sources' / NATIVE_READER
        need(module_path.read_bytes() == (native / 'sources/controller.py').read_bytes(), 'executed native controller is the current frozen reader')
        spec = importlib.util.spec_from_file_location('new_public_pcm_capture', module_path)
        reader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reader)
        measured = reader.validate_log((native / 'qemu.stdout.log').read_text('utf-8') + '\n' +
                                       (native / 'qemu.stderr.log').read_text('utf-8'), 'esp32', out)
        need(measured == native_report['measurements'], 'independently recover all full PCM records and original raw/window digests')
        report['native_report'] = dict(path=(native / 'report.json').relative_to(ROOT).as_posix(), **file_pin(native / 'report.json'))
        report['native_measurements'] = measured
        (out / 'native-report.json').write_bytes((native / 'report.json').read_bytes())
        save()
        version = command('compiler-version', ['/usr/bin/gcc', '--version']).decode().splitlines()[0]
        compiler = command('compiler-realpath', ['readlink', '-f', '/usr/bin/gcc']).decode().strip()
        report['compiler'] = dict(version=version, identity=command('compiler-sha256', ['sha256sum', compiler]).decode().strip())
        library = command('libopus-path', ['/usr/bin/gcc', '-print-file-name=libopus.so.0']).decode().strip()
        need(library.startswith('/usr/') and '\n' not in library, 'installed public reference library')
        library = command('libopus-realpath', ['readlink', '-f', library]).decode().strip()
        library_identity = command('libopus-sha256', ['sha256sum', library]).decode().strip()
        report['libopus_identity'] = library_identity
        binary = out / 'reference'
        command('reference-build', ['/usr/bin/gcc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-Wpedantic',
                                     '-Wformat=2', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                                     '-fno-pie', '-no-pie', host(out / 'sources' / REFERENCE), '-l:libopus.so.0', '-lm', '-o', host(binary)])
        report['reference_executable'] = dict(path=binary.name, local_only=True, **file_pin(binary))
        report['fixtures'] = {}
        for name, (relative, digest, raw_frames) in FIXTURES.items():
            encoded = (ROOT / relative).read_bytes()
            need(sha(encoded) == digest, 'complete unchanged encoded fixture')
            audio, preskip, pages = packets(encoded)
            eos = pages[-1]['granule']
            need(preskip == 312 and eos == 528312, 'actual timeline, no globally substituted production constants')
            packet_path = out / (name+'.packets')
            transport = struct.pack('<8sIIQQI', b'OPPK01\0\0', 2, preskip, eos, raw_frames, len(audio))
            transport += b''.join(struct.pack('<I', len(packet))+packet for packet in audio)
            packet_path.write_bytes(transport)
            ref_raw, ref_logical = out / (name+'-libopus-raw.pcm'), out / (name+'-libopus-playback.pcm')
            result = json.loads(command(name+'-reference', ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                                                            'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',
                                                            host(binary), host(packet_path), host(out / (name+'-vendor-raw.pcm')),
                                                            host(ref_raw), host(ref_logical)]))
            need(result['reference'].startswith('libopus ') and result['raw_frames'] == raw_frames and result['packets'] == len(audio) and
                 result['logical_frames'] == 528000 and result['samples_per_candidate'] == 1056000 and
                 result['best_offset'] == preskip and result['best_ties'] == 1 and result['second_squared_error'] > result['best_squared_error'] and
                 result['candidate_windows'] == raw_frames-528000+1 and result['unique_sample_position_observed'] and not result['numeric_conformance_claim'],
                 'independent complete decode and exhaustive unique full-length sample-position check')
            report['fixtures'][name] = dict(encoded=dict(path=relative, bytes=len(encoded), sha256=digest), pages=pages,
                packet_transport=dict(path=packet_path.name, **file_pin(packet_path)), comparison=result,
                vendor_raw=dict(path=name+'-vendor-raw.pcm', **file_pin(out / (name+'-vendor-raw.pcm'))),
                reference_raw=dict(path=ref_raw.name, **file_pin(ref_raw)), reference_playback=dict(path=ref_logical.name, **file_pin(ref_logical)))
            save()
        need(command('libopus-post-sha256', ['sha256sum', library]).decode().strip() == library_identity, 'unchanged reference library during execution')
        for row in report['sources']:
            need(file_pin(ROOT / row['path']) == dict(bytes=row['bytes'], sha256=row['sha256']) == file_pin(out / row['snapshot']), 'unchanged source snapshots')
        report.update(passed=True, completed=True, all_source_bindings_unchanged=True)
        save()
        print(json.dumps(dict(passed=True, capture=out.relative_to(ROOT).as_posix(),
                             comparisons={name:value['comparison'] for name, value in report['fixtures'].items()})))
        return 0
    except Exception as error:
        report.update(passed=False, completed=False, failure=dict(type=type(error).__name__, reason=str(error)))
        save()
        print(json.dumps(dict(passed=False, failure=report['failure'])))
        return 1


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
