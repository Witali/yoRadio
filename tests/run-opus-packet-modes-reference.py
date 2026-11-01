"""Prepare bounded complete Opus mode/framing streams using creator public APIs.

All original encoded packets and full independent PCM references remain in the
fresh local capture. No production source, SDK build, board or private ABI is
used. Successful creator checks are not Espressif synthesis coverage.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OGG = 'idf/components/native_vorbis_xiph/upstream/libogg'
CONFIG = 'idf/components/native_vorbis_xiph/platform'
SOURCES = ['tests/native/opus_packet_modes_public.h', 'tests/native/opus_packet_modes_encode.c',
           'tests/native/opus_packet_modes_reference.c', 'tests/native/opus_packet_modes_ogg.c',
           'tests/fixtures/opus_packet_modes/generate.py', 'tests/run-opus-packet-modes-reference.py',
           'tests/test-opus-packet-modes.py',
           OGG + '/include/ogg/ogg.h', OGG + '/include/ogg/os_types.h', OGG + '/COPYING', CONFIG + '/ogg/config_types.h']


def need(value, reason):
    if not value:
        raise ValueError(reason)


def pin(path):
    data = Path(path).read_bytes()
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def ogg_packets(body, generate):
    at, packets, current, pages = 0, [], bytearray(), 0
    while at < len(body):
        need(at + 27 <= len(body) and body[at:at + 5] == b'OggS\0', 'existing complete Ogg header')
        count = body[at + 26]; payload = at + 27 + count
        need(payload <= len(body), 'existing complete lacing')
        lace = body[at + 27:payload]; end = payload + sum(lace)
        need(end <= len(body), 'existing complete page')
        page = bytearray(body[at:end]); stored = struct.unpack_from('<I', page, 22)[0]; page[22:26] = bytes(4)
        need(generate.crc(page) == stored, 'existing actual page CRC')
        need(bool(page[5] & 1) == bool(current) or count == 0, 'existing continued packet')
        offset = payload
        for length in lace:
            current.extend(body[offset:offset + length]); offset += length
            if length < 255:
                packets.append(bytes(current)); current.clear()
        at = end; pages += 1
    need(not current and len(packets) >= 3 and packets[0][:8] == b'OpusHead' and packets[1][:8] == b'OpusTags', 'existing complete Opus stream')
    return packets[2:], pages


def inventory(generate):
    paths = sorted((ROOT / 'tests/fixtures/opus_native').rglob('*.opuspkt'))
    paths += sorted((ROOT / 'tests/fixtures/opus_native').glob('*.opus'))
    paths += sorted((ROOT / 'tests/fixtures/opus_native/through192').glob('*.opus'))
    paths += sorted((ROOT / 'tests/fixtures/opus_local_radio').glob('*.opus'))
    paths += [ROOT / 'tests/fixtures/esp32c3_calibration/opus-510.ogg',
              ROOT / 'tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg']
    result = []
    for path in paths:
        body = path.read_bytes(); row = dict(path=path.relative_to(ROOT).as_posix(), **pin(path))
        if body.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
            result.append(dict(row, available=False, reason='local LFS pointer; no download requested'))
            continue
        packets = []
        if path.suffix == '.opuspkt':
            at = 0
            while at < len(body):
                need(at + 2 <= len(body), 'existing packet length')
                size = struct.unpack_from('<H', body, at)[0]; at += 2
                need(size > 0 and at + size <= len(body), 'existing complete encoded packet')
                packets.append(body[at:at + size]); at += size
            row['complete_container'] = False
        else:
            packets, row['pages'] = ogg_packets(body, generate)
            row['complete_container'] = True
        parsed = [generate.parse_packet(packet) for packet in packets]
        row.update(available=True, packet_count=len(parsed),
                   modes=dict(Counter(r['mode'] for r in parsed)),
                   configs=dict(Counter(str(r['config']) for r in parsed)),
                   packet_samples=dict(Counter(str(r['samples']) for r in parsed)),
                   codes=dict(Counter(str(r['code']) for r in parsed)),
                   zero_length_coded_frames=sum(r['sizes'].count(0) for r in parsed),
                   padded_packets=sum(r['padding'] > 0 for r in parsed),
                   coverage='complete packet/framing metadata audit; no new vendor synthesis claimed')
        result.append(row)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); out = args.output.resolve()
    need(out.is_relative_to(ROOT / '.build') and not out.exists(), 'fresh ignored local capture')
    out.mkdir(parents=True)
    report = dict(passed=False, completed=False, commands=[], sources=[], cases={},
                  native_vendor_executed=False, physical_hardware=False, private_abi_used=False,
                  numerical_conformance_claim=False, production_sources_changed=False)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    def command(name, arguments, timeout=120):
        argv = (['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + list(map(str, arguments))
        row = dict(name=name, argv=argv, state='starting', timeout_seconds=timeout)
        report['commands'].append(row); save(); started = time.monotonic()
        with (out / (name + '.stdout.log')).open('xb') as stdout, (out / (name + '.stderr.log')).open('xb') as stderr:
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
            row.update(pid=child.pid, state='running'); save()
            try:
                status = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                child.kill(); status = child.wait(); row['timed_out'] = True
            row.update(state='complete', exit_status=status, elapsed_seconds=round(time.monotonic() - started, 3))
        for stream in ('stdout', 'stderr'):
            path = out / (name + '.' + stream + '.log')
            row[stream] = dict(path=path.name, **pin(path))
        save(); need(status == 0 and not row.get('timed_out'), 'actual terminal zero: ' + name)
        return (out / (name + '.stdout.log')).read_bytes()
    save()
    try:
        for name in SOURCES:
            path = ROOT / name; destination = out / 'sources' / name
            destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(path.read_bytes())
            report['sources'].append(dict(path=name, snapshot=destination.relative_to(out).as_posix(), **pin(destination)))
        path = out / 'sources/tests/fixtures/opus_packet_modes/generate.py'
        spec = importlib.util.spec_from_file_location('frozen_packet_modes_writer', path)
        generate = importlib.util.module_from_spec(spec); spec.loader.exec_module(generate)
        report['existing_inventory'] = inventory(generate)
        report['compiler_version'] = command('compiler-version', ['/usr/bin/gcc', '--version']).decode().splitlines()[0]
        compiler = command('compiler-path', ['readlink', '-f', '/usr/bin/gcc']).decode().strip()
        report['compiler_identity'] = command('compiler-sha', ['sha256sum', compiler]).decode().strip()
        library = command('libopus-path', ['readlink', '-f', '/lib/x86_64-linux-gnu/libopus.so.0']).decode().strip()
        libogg = command('libogg-path', ['readlink', '-f', '/lib/x86_64-linux-gnu/libogg.so.0']).decode().strip()
        need(library.startswith('/usr/lib/') and libogg.startswith('/usr/lib/'), 'installed creator libraries only')
        report['libopus_identity'] = command('libopus-sha', ['sha256sum', library]).decode().strip()
        report['libogg_identity'] = command('libogg-sha', ['sha256sum', libogg]).decode().strip()
        command('data-framing-tests', ['/usr/bin/python3', '-B', '-X', 'utf8',
                                     host(out / 'sources/tests/test-opus-packet-modes.py')])
        flags = ['-std=c11', '-O2', '-g', '-Wall', '-Wextra', '-Werror', '-Wpedantic', '-Wformat=2',
                 '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie']
        for name in ('encode', 'reference'):
            command(name + '-build', ['/usr/bin/gcc', *flags,
                host(out / ('sources/tests/native/opus_packet_modes_' + name + '.c')), library, '-lm', '-o', host(out / name)])
            report[name + '_executable'] = dict(path=name, local_only=True, **pin(out / name))
        command('ogg-build', ['/usr/bin/gcc', *flags, '-I' + host(out / 'sources' / OGG / 'include'),
                '-I' + host(out / 'sources' / CONFIG), host(out / 'sources/tests/native/opus_packet_modes_ogg.c'),
                libogg, '-o', host(out / 'ogg')])
        report['ogg_executable'] = dict(path='ogg', local_only=True, **pin(out / 'ogg')); save()
        env = ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1', 'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1']
        for index, case in enumerate(generate.cases()):
            name = case['name']; folder = out / name; folder.mkdir()
            original = folder / 'original.packets'; encoded_rows = folder / 'encoded.jsonl'
            encoded = json.loads(command(name + '-encode', [*env, host(out / 'encode'), str(case['mode']),
                str(case['samples']), str(int(case['vbr'])), str(case['count'] * 4), host(original), host(encoded_rows)]))
            need(encoded['input_signal_frames'] > 0 and encoded['input_silent_frames'] >= case['samples'] * case['count'],
                 'real encoded silent quarter distinct from absent-frame PLC')
            framed, accounting = generate.reframe(original.read_bytes(), case)
            transport = folder / 'framed.packets'; transport.write_bytes(framed)
            ogg = folder / 'complete.ogg'; ogg.write_bytes(generate.make_ogg(framed, 0x504d0000 + index))
            raw, trim, decoded_rows = folder / 'raw.pcm', folder / 'playback.pcm', folder / 'decoded.jsonl'
            decoded = json.loads(command(name + '-reference', [*env, host(out / 'reference'), host(transport), host(raw), host(trim), host(decoded_rows)]))
            creator_rows = [json.loads(line) for line in decoded_rows.read_text().splitlines()]
            need(len(creator_rows) == 4 and all(r['code'] == case['code'] and r['repacketize_pad_unpad_frames_exact'] and
                 r['decoded_pcm_exact'] and r['sizes'] == expected['sizes'] and r['samples'] == expected['samples']
                 for r, expected in zip(creator_rows, accounting['observations'])), 'independent creator framing and real synthesis')
            checks = [json.loads(line) for line in command(name + '-ogg', [*env, host(out / 'ogg'), host(ogg), host(transport)]).decode().splitlines()]
            need(len(checks) == 3 and all(row['pages'] == 6 and row['audio_packets'] == 4 and row['exact_complete_packets'] and
                 row['eos'] and row['sync_errors'] == row['packet_holes'] == 0 for row in checks), 'creator libogg exact complete stream')
            need(decoded['packets'] == 4 and decoded['logical_frames'] == accounting['logical_frames'] and
                 decoded['raw_bytes'] == raw.stat().st_size and decoded['trim_bytes'] == trim.stat().st_size and
                 decoded['three_full_decodes_exact'] and decoded['nonzero_samples'] > 0, 'full decoded/raw/window references')
            record = dict(case=case, creator_encoding=encoded, accounting=accounting, creator_decoding=decoded,
                          container_checks=checks, artifacts={})
            for artifact in (original, encoded_rows, transport, ogg, raw, trim, decoded_rows):
                record['artifacts'][artifact.name] = dict(path=artifact.relative_to(out).as_posix(),
                    local_only=artifact.suffix == '.pcm', **pin(artifact))
            report['cases'][name] = record; save()
            print(name + ': creator complete-stream PASS', flush=True)
        need(len(report['cases']) == 49, 'all bounded complete synthesis cases')
        need(command('libopus-post-sha', ['sha256sum', library]).decode().strip() == report['libopus_identity'], 'creator libopus unchanged')
        need(command('libogg-post-sha', ['sha256sum', libogg]).decode().strip() == report['libogg_identity'], 'creator libogg unchanged')
        need(command('compiler-post-sha', ['sha256sum', compiler]).decode().strip() == report['compiler_identity'], 'compiler unchanged')
        for row in report['sources']:
            need(pin(ROOT / row['path']) == pin(out / row['snapshot']) == dict(bytes=row['bytes'], sha256=row['sha256']), 'all source bytes unchanged')
        report.update(passed=True, completed=True, all_source_bindings_current=True)
        print(json.dumps(dict(passed=True, complete_streams=49, capture=out.relative_to(ROOT).as_posix(), native_vendor_executed=False)))
        return 0
    except Exception as error:
        report['failure'] = dict(type=type(error).__name__, reason=str(error))
        print(json.dumps(dict(passed=False, failure=report['failure'])))
        return 1
    finally:
        save()


if __name__ == '__main__':
    raise SystemExit(main())
