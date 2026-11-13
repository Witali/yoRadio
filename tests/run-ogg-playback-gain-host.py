"""Execute actual ogg_playback.h with explicit public-API host seams.

Every fresh ignored capture freezes sources, command logs and actual terminal
status. No vendor binary/MCU is executed by this host lifecycle qualification.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent if ROOT.parent.name == '.worktree' else ROOT
VENDOR = REPO / '.idf/esp-adf-libs/esp_audio_codec'
HARNESS = Path('tests/native/ogg_playback_gain_host.c')
MAIN = Path('idf/esp32-cyd2usb-native/main')
SHARED = Path('idf/components/native_stream/include')
INPUTS = [HARNESS, Path('tests/native/ogg_legacy_raw_unselected.c'),
          *[MAIN / n for n in ('ogg_playback.h','opus_family1_playback.h','opus_family1_decoder.h')],
          *[SHARED / n for n in ('ogg_page_input.h','opus_pcm_trim.h','ogg_opus_timeline.h','decoder_pending_input.h','pcm_header_gain.h',
             'opus_tags_stream.h','ogg_opus_audio_packets.h','opus_family1_mapping.h','opus_multistream_framing.h','pcm_channel_layout.h')]]
PUBLIC_HEADERS = ('esp_audio_types.h','decoder/esp_audio_dec.h','decoder/esp_audio_dec_reg.h',
                  'decoder/impl/esp_opus_dec.h','simple_dec/esp_audio_simple_dec.h')


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    need(out.is_relative_to(ROOT / '.build') and not out.exists(), 'fresh ignored capture required')
    out.mkdir(parents=True)
    report = dict(passed=False, state='preparing', sources=[], commands=[], actual_wrapper=True,
                  vendor_executed=False, production_selected=False, gain_metadata_only=True, output_render_qualified=False)

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def command(name, argv):
        full = (['wsl.exe','--exec'] if sys.platform == 'win32' else []) + argv
        row = dict(name=name, argv=full, state='starting', exit_status=None)
        report['commands'].append(row)
        start = time.monotonic()
        paths = {n: out / (name + '.' + n + '.log') for n in ('stdout','stderr')}
        with paths['stdout'].open('wb') as stdout, paths['stderr'].open('wb') as stderr:
            child = subprocess.Popen(full, stdout=stdout, stderr=stderr, shell=False)
            row.update(pid=child.pid, state='running')
            save()
            try:
                status = child.wait(timeout=120)
            except subprocess.TimeoutExpired:
                child.kill(); status = child.wait(); row['timed_out'] = True
            row.update(state='complete', exit_status=status, elapsed_seconds=round(time.monotonic()-start,3))
        for n, path in paths.items():
            row[n] = dict(path=path.name, bytes=path.stat().st_size, sha256=sha(path.read_bytes()))
        save()
        need(status == 0 and not row.get('timed_out'), 'native terminal zero required: ' + name)
        return paths['stdout'].read_bytes()

    save()
    try:
        for relative in [Path(__file__).resolve().relative_to(ROOT)] + INPUTS:
            body = (ROOT / relative).read_bytes()
            snapshot = out / 'sources' / relative
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_bytes(body)
            report['sources'].append(dict(path=relative.as_posix(), snapshot=snapshot.relative_to(out).as_posix(), bytes=len(body), sha256=sha(body)))
        for name in PUBLIC_HEADERS:
            original = VENDOR / 'include' / name
            body = original.read_bytes(); snapshot = out / 'sources/vendor/include' / name
            snapshot.parent.mkdir(parents=True, exist_ok=True); snapshot.write_bytes(body)
            report['sources'].append(dict(path=str(original.resolve()), snapshot=snapshot.relative_to(out).as_posix(), bytes=len(body), sha256=sha(body)))
        save()
        report['compiler_version'] = command('compiler-version',['/usr/bin/gcc','--version']).decode().splitlines()[0]
        compiler = command('compiler-realpath',['/usr/bin/readlink','-f','/usr/bin/gcc']).decode().strip()
        need(compiler.startswith('/usr/') and '\n' not in compiler, 'actual compiler path')
        report['compiler_identity'] = command('compiler-sha256',['/usr/bin/sha256sum',compiler]).decode().strip()
        binary = out / 'ogg-playback-gain-host'
        command('build',['/usr/bin/gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wpedantic','-Wshadow',
                         '-DCONFIG_YORADIO_TLS_STATIC_RX_RESERVE=1',
                         '-Wformat=2','-Wstrict-prototypes','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
                         *['-I'+host(out/'sources/vendor/include'/name) for name in ('','decoder','decoder/impl','simple_dec')],
                         '-I'+host(out/'sources'/MAIN),'-I'+host(out/'sources'/SHARED),
                         host(out/'sources'/HARNESS),host(out/'sources/tests/native/ogg_legacy_raw_unselected.c'),'-lm','-o',host(binary)])
        report['binary'] = dict(path=binary.name, bytes=binary.stat().st_size, sha256=sha(binary.read_bytes()), local_only=True)
        report['state'] = 'running'
        stdout = command('test',['/usr/bin/env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                                'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',host(binary)])
        rows = [json.loads(line) for line in stdout.decode().splitlines()]
        need(len(rows) >= 90 and all(row.get('passed') is True for row in rows), 'complete passing actual wrapper seam records')
        need(rows[-1]['suite'] == 'ogg-playback-gain-host' and rows[-1]['cases'] == len(rows)-1 and
             rows[-1]['actual_wrapper'] and not rows[-1]['vendor_executed'] and not rows[-1]['live_allocations'], 'full lifecycle and allocation summary')
        report['test_records'] = rows
        for row in report['sources']:
            need(sha((ROOT/row['path']).read_bytes()) == row['sha256'] == sha((out/row['snapshot']).read_bytes()), 'canonical/frozen source unchanged')
        report.update(passed=True, state='complete', all_source_bindings_unchanged=True)
        save()
        print(json.dumps(dict(capture=out.relative_to(ROOT).as_posix(), **rows[-1])))
        return 0
    except Exception as error:
        report.update(passed=False, state='nonpass', failure=dict(type=type(error).__name__, reason=str(error)))
        save()
        print(json.dumps(dict(passed=False,capture=out.relative_to(ROOT).as_posix(),failure=report['failure'])))
        return 1


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
