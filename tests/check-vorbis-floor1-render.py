"""Independent finite floor1 numeric qualification and libvorbis collection.

Compare every signed PCM16 sample at a fixed <=2 LSB bound, with no gain,
alignment, trimming, resampling or native-Vorbis oracle. Existing NONPASS records
are immutable inputs. SDK, QEMU and physical devices are never executed here.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
import wave

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BOUND = 2
FFMPEG_SHA = '09948d4cdd0650da6ff5a87577469f2a218dc2615ae379f8f734d24c49de0f73'
HELPER_SHA = '8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1'
GENERATORS = {
    'positions': '0248784f9baeb0c959bd1c63f56b958600d06c16f896c2c920b2cc88c442ca21',
    'slopes': '835158eac4bb5a6eebaa43a2ec45b331b93943f045d82e41abe31bf389dab37b',
}
BASELINES = {
    'esp32': '753c53375b29c4135f9c37844996c979c8d0f5bea8b509ec0d3a2d96840f764b',
    'esp32c3': '304e2b136ea69fa627b1eeab6792877cc3bd8a05e901a8e57d5a370c4182979f',
}
POSITION_REFERENCE = ROOT / '.build/vorbis-floor1-reference-01/report.json'
POSITION_REFERENCE_SHA = '183f3b8cfabe81021e0309a02de5674cfd264800a64d01ba2e75f0c7f0c26204'
INVALIDDATA = (1, -1094995529, 3199971767)
LIMIT = 32 * 1024 * 1024


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe(base, relative):
    path = (base / str(relative).replace('\\', '/')).resolve()
    need(path.is_relative_to(base) and path != base, 'evidence path escapes its directory')
    return path


def argument(argv, name):
    need(argv.count(name) == 1 and argv.index(name) + 1 < len(argv), 'one argument ' + name)
    return argv[argv.index(name) + 1]


def metrics(a, b):
    need(len(a) == len(b) and len(a) % 2 == 0, 'complete equal PCM16 vectors')
    errors = [abs(x[0] - y[0]) for x, y in zip(struct.iter_unpack('<h', a), struct.iter_unpack('<h', b))]
    return dict(samples=len(errors), max_abs_error=max(errors, default=0),
                over_bound=sum(e > BOUND for e in errors), allowed=BOUND)


class Checker:
    def __init__(self, out):
        self.out = out
        self.report = dict(schema='floor1-render-independent-check-v1', completed=False, passed=False,
            finite_renderer_qualified=False, both_architectures_qualified=False,
            full_G6_qualified=False, production_radio_integration=False, physical_device=False,
            sdk_or_target_executed=False, ffmpeg_executed=False, predeclared_max_abs_error=BOUND,
            inputs={}, tools={}, commands=[], references=[], targets=[], baselines=[], controls=[], failures=[],
            scope=__doc__)

    def save(self):
        (self.out / 'report.json').write_text(json.dumps(self.report, indent=2) + '\n', encoding='utf-8')

    def freeze(self, path):
        path = Path(path).resolve()
        need(path.is_relative_to(ROOT), 'snapshot input outside task checkout')
        raw = path.read_bytes(); key = str(path)
        if key not in self.report['inputs']:
            dest = self.out / 'sources' / path.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open('xb') as stream:
                stream.write(raw)
            self.report['inputs'][key] = dict(bytes=len(raw), sha256=digest(raw),
                                            snapshot=dest.relative_to(self.out).as_posix())
        need(digest(raw) == self.report['inputs'][key]['sha256'], 'input changed during qualification')
        return raw

    def tool(self, path, expected):
        path = Path(path).resolve(); present = path.is_file()
        if present:
            need(digest(path.read_bytes()) == expected, 'available recorded tool changed: ' + str(path))
        previous = self.report['tools'].get(str(path))
        need(previous is None or previous['sha256'] == expected, 'conflicting tool pins')
        self.report['tools'][str(path)] = dict(sha256=expected, currently_available=present)

    def current(self):
        for name, row in self.report['inputs'].items():
            need(digest(Path(name).read_bytes()) == row['sha256'] ==
                 digest(safe(self.out, row['snapshot']).read_bytes()), 'frozen input changed')
        for name, row in self.report['tools'].items():
            if row['currently_available']:
                need(digest(Path(name).read_bytes()) == row['sha256'], 'selected tool changed')

    def recorded(self, path):
        path = Path(path).resolve(); report = json.loads(self.freeze(path)); snapshots = {}
        for original, row in report['inputs'].items():
            raw = self.freeze(safe(path.parent, row['snapshot']))
            need(digest(raw) == row['sha256'] and ('bytes' not in row or len(raw) == row['bytes']),
                 'recorded input snapshot identity')
            snapshots[str(Path(original).resolve())] = raw
        for name, expected in report['tools'].items():
            self.tool(name, expected)
        return report, snapshots

    def logs(self, report, path, reference=False):
        rows = {}
        tools = {str(Path(name).resolve()) for name in report['tools']}
        for row in report['commands']:
            name = row['name']; need(name not in rows, 'duplicate command receipt')
            need(type(row.get('pid')) is int and row['pid'] > 0, 'actual owned command PID')
            if reference:
                need(row['state'] == 'terminal' and row['reaped'] is True and not row.get('forced_stop'),
                     'reference terminal/reap receipt')
            else:
                need(row['state'] == 'complete' and row['exit_status'] == 0,
                     'target command actual exit0')
            need(Path(row['cwd']).resolve() == path.parent, 'command working directory binding')
            need(row['argv'] and str(Path(row['argv'][0]).resolve()) in tools,
                 'actual command executable is one of the recorded pinned tools')
            bodies = []
            for kind in ('stdout', 'stderr'):
                raw = self.freeze(safe(path.parent, row.get(kind, name + '.' + kind + '.log')))
                need(digest(raw) == row[kind + '_sha256'], 'command log digest')
                bodies.append(raw.decode('utf-8', errors='replace').replace('\r\n', '\n'))
            rows[name] = (row, *bodies)
        return rows

    def generated(self, kind):
        source = ROOT / ('tests/vorbis_format_corpus/generate_floor1_' + kind + '.py')
        helper = ROOT / 'tests/vorbis_block_matrix/generate_minimal.py'
        need(digest(self.freeze(source)) == GENERATORS[kind] and digest(self.freeze(helper)) == HELPER_SHA,
             'reviewed ordinary construction source pins')
        spec = importlib.util.spec_from_file_location('render_checker_' + kind, source)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module.payloads()  # Pinned pure construction; no runner/decoder import.

    def corpus(self, corpus, expected):
        actual = {p.relative_to(corpus).as_posix() for p in corpus.rglob('*') if p.is_file()}
        need(actual == set(expected), 'exact generated corpus file inventory')
        need(all(self.freeze(safe(corpus, name)) == raw for name, raw in expected.items()),
             'complete canonical corpus bytes')
        matrix = json.loads(expected['matrix.json'])
        need(len(matrix['cases']) == 14 and [c['expected_valid'] for c in matrix['cases']] == [True]*8+[False]*6,
             'full fourteen-case validity matrix')
        need(matrix['expected_valid_pcm_bytes'] == 225280 and matrix['valid_raw_packet_count'] == 112,
             'complete valid corpus PCM accounting')
        return matrix

    def bound_corpus(self, report, snapshots, expected):
        manifest_sha = digest(expected['manifest.json'])
        need(report['corpus_manifest_sha256'] == manifest_sha, 'reported corpus manifest identity')
        origins = [Path(name).parent for name, raw in snapshots.items()
                   if Path(name).name == 'manifest.json' and digest(raw) == manifest_sha]
        need(len(origins) == 1, 'one complete recorded canonical corpus')
        origin = origins[0]
        need(all(snapshots.get(str((origin / name).resolve())) == raw for name, raw in expected.items()),
             'full generated corpus snapshots, including fixture and audits')
        return origin

    def target(self, path, expected, role='candidate'):
        report, snapshots = self.recorded(path); logs = self.logs(report, path)
        matrix = json.loads(expected['matrix.json']); cases = matrix['cases']
        self.bound_corpus(report, snapshots, expected)
        expected_kind = 'slopes' if matrix['schema'] == 'vorbis-floor1-slopes-v1' else 'positions'
        need(report.get('corpus_kind', 'positions') == expected_kind, 'declared target corpus kind')
        platform = report['target']; need(platform in ('esp32', 'esp32c3'), 'supported target architecture')
        core, machine = (1, 94) if platform == 'esp32' else (0, 243)
        need(report['completed'] is True, 'complete target capture')
        if role == 'baseline':
            need(digest(path.read_bytes()) == BASELINES[platform] and report['passed'] is True and
                 report['result'] == 'FINITE_MATRIX_PASSED' and report['control'] is None,
                 'pinned frozen baseline acceptance')
        else:
            need(report['target_capture_completed'] is True and report['renderer'] == 'on' and
                 report['passed'] is False and report['numerical_reference_qualified'] is False and
                 report['result'] == 'RENDER_CAPTURED' and
                 report['control'] == ('old-tail' if role == 'old-tail' else None),
                 'renderer capture pending independent numerical qualification')
        for key in ('full_G6_qualified', 'production_radio_integration', 'physical_device'):
            need(report[key] is False, 'finite target scope')
        for group in ('build_outputs', 'variant_sources', 'project_sources'):
            normalized = {}
            for name, expected_sha in report[group].items():
                normalized_name = name.replace('\\', '/')
                need(normalized_name not in normalized, 'normalized output pin collision')
                raw = self.freeze(safe(path.parent, name))
                need(digest(raw) == expected_sha, 'recorded ' + group + ' digest')
                normalized[normalized_name] = raw
            if group == 'build_outputs':
                outputs = normalized
            elif group == 'project_sources':
                project = normalized
        for name, raw in project.items():
            relative = name.removeprefix('project/')
            if relative == 'main/fixture.h':
                original = expected['fixture.h']
            elif relative in ('sdkconfig.defaults', 'partitions.csv'):
                original = self.freeze(safe(path.parent, 'sources/' + relative))
            else:
                original = self.freeze(safe(path.parent, 'sources/project/' + relative))
            need(raw == original, 'actual build project matches frozen sources/generated fixture')
        elf_names = [name for name in outputs if name.endswith('.elf')]
        need(len(elf_names) == 1, 'one target ELF')
        elf = outputs[elf_names[0]]
        need(elf[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', elf, 18)[0] == machine == report['elf_machine'],
             'actual ELF architecture')
        config = outputs['sdkconfig']
        need((b'CONFIG_FREERTOS_UNICORE=y' in config) == (core == 0) and
             ('CONFIG_IDF_TARGET="' + platform + '"').encode() in config, 'target/core SDK config')
        required = {'sdk-head', 'sdk-clean', 'build', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after'}
        need(required.issubset(logs), 'complete owned target command receipts')
        build_argv = logs['build'][0]['argv']
        need(argument(build_argv, '-Target') == platform and
             Path(argument(build_argv, '-Campaign')).resolve() == path.parent and
             Path(argument(build_argv, '-File')).resolve() == safe(path.parent, 'sources/project/sdk-build.ps1'),
             'owned SDK build command/campaign/source binding')
        need(logs['sdk-head'][1].strip() == logs['sdk-head-after'][1].strip() and
             not logs['sdk-clean'][1].strip() and not logs['sdk-clean-after'][1].strip(), 'SDK before/after evidence')
        qargv = logs['qemu'][0]['argv']
        need(argument(qargv, '-M') == platform and argument(qargv, '-smp') == ('2' if core else '1') and
             argument(qargv, '-nic') == 'none' and all(x in qargv for x in ('-no-reboot', '-snapshot')),
             'recorded target machine/core isolation')
        need(str(safe(path.parent, 'qemu-flash.bin')) in argument(qargv, '-drive'), 'QEMU flash binding')
        symbols = logs['symbols'][1]
        for symbol in ('__wrap_esp_vorbis_dec_open', '__wrap_esp_vorbis_dec_decode',
                       'esp_vorbis_dec_decode', *(() if role == 'baseline' else ('__wrap_floor1_inverse2',))):
            need(re.search(r'\b' + symbol + r'$', symbols, re.M), 'actual linked wrapper symbol')
        need(str(safe(path.parent, elf_names[0])) in logs['symbols'][0]['argv'], 'symbols/ELF command binding')
        rows = report['compile_rows']
        need(len(rows) == 2 and {Path(row['file']).name for row in rows} == {'setup.c', 'output.c'} and
             all(Path(row['file']).resolve().is_relative_to(path.parent / 'variant') for row in rows),
             'actual variant compilation rows')
        dispatch = report.get('dispatch', 'direct')
        need(dispatch in ('direct', 'registered'), 'known raw API dispatch')
        reset_cycles = report.get('reset_cycles', False)
        need(type(reset_cycles) is bool and (not reset_cycles or dispatch == 'registered'),
             'known public raw reset selection')
        need(dispatch != 'registered' or role == 'candidate', 'registered dispatch candidate only')
        source_name = 'main.c' if role == 'baseline' else 'registered.c' if dispatch == 'registered' else 'render.c'
        source = project['project/main/' + source_name]
        if role == 'baseline':
            tokens = (b'a_info.sample_rate==48000 && b_info.sample_rate==48000',
                      b'a_info.channel==2 && b_info.channel==2',
                      b'a_info.bits_per_sample==16 && b_info.bits_per_sample==16', b'"public_metadata"')
        else:
            need(argument(logs['build'][0]['argv'], '-Renderer') == 'on', 'explicit renderer build selection')
            need(b'--wrap=floor1_inverse2' in project['project/main/CMakeLists.txt'], 'renderer link contract')
            tokens = (b'info.sample_rate==48000 && info.channel==2 && info.bits_per_sample==16',
                      b'guard();', b'"output_canaries"', b'ESP_AUDIO_ERR_FAIL && !checked',
                      b'"invalid_setup_rejected"', b'"public_metadata"', b'"rejected_heap_integrity"')
            if dispatch == 'registered':
                need(argument(build_argv, '-Dispatch') == 'registered' and
                     argument(build_argv, '-BindingControl') == 'none' and
                     report['registered_callbacks_qualified'] is True, 'registered public API build/capture')
                compile_commands = json.loads(outputs['build/compile_commands.json'])
                compiled = [row for row in compile_commands
                            if Path(row['file']).resolve() == path.parent/'project/main/registered.c']
                need(len(compiled) == 1 and compiled == report['harness_compile_rows'],
                     'actual compiled registered fixture binding')
                if reset_cycles:
                    need(argument(build_argv, '-ResetCycles') == 'on' and
                         re.search(r'(?:^|\s)-DVORBIS_RESET_CYCLES=1(?:\s|$)', compiled[0]['command']) and
                         report['raw_reset_behavior_qualified'] is True and
                         re.search(r'\besp_audio_dec_reset$', symbols, re.M),
                         'actual reset-enabled compilation and public API symbol')
                    need(b'#include "reset_cycles.h"' in source and
                         b'esp_audio_dec_reset(' in project['project/main/reset_cycles.h'] and
                         b'#define VORBIS_RESET_SKIP_CONTROL 0' in project['project/main/reset_cycles.h'],
                         'unaltered public reset caller source')
                tokens = (b'esp_audio_dec_open(', b'esp_audio_dec_process(', b'esp_audio_dec_get_info(',
                          b'esp_audio_dec_close(', b'esp_audio_dec_unregister(', b'guard();',
                          b'"output_canaries"', b'"invalid_setup_rejected"', b'"public_metadata"')
                for symbol in ('__wrap_esp_vorbis_dec_register', 'esp_audio_dec_get_ops', 'esp_audio_dec_open',
                               'esp_audio_dec_process', 'esp_audio_dec_get_info', 'esp_audio_dec_close'):
                    need(re.search(r'\b' + symbol + r'$', symbols, re.M), 'registered public API linked symbol')
            for name in report['variant_sources']:
                relative = name.replace('\\', '/').removeprefix('variant/')
                original = self.freeze(safe(path.parent, 'sources/main/' + relative))
                actual = self.freeze(safe(path.parent, name))
                if role == 'old-tail' and relative == 'vorbis_repair/floor1_render.h':
                    anchor = b'out[j] = repair_floor1_multiply(out[j], repair_floor1_from_db[ly]);'
                    need(original.count(anchor) == 1 and actual == original.replace(
                        anchor, b'out[j] = repair_floor1_multiply(out[j], ly * 32768);', 1),
                        'exact single old-tail control mutation')
                else:
                    need(actual == original, 'unchanged executed variant source')
        need(all(token in source for token in tokens), 'frozen guard/null/metadata assertion coverage')
        log, stderr = logs['qemu'][1:]
        need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|FLOOR1_FAILURE', log + stderr),
             'no target panic or semantic failure')
        if dispatch == 'registered':
            protocol = ROOT / 'tests/vorbis_registered_protocol.py'
            need(self.freeze(protocol) == snapshots.get(str(protocol.resolve())), 'executed registered protocol source')
            from vorbis_registered_protocol import validate_log
            actual = validate_log(log, matrix, platform, returncode=logs['qemu'][0]['exit_status'],
                                  timed_out=logs['qemu'][0]['state'] != 'complete', interrupted=False)
            need(actual == report['observed_registry'], 'independent registered protocol replay')
            if reset_cycles:
                reset_protocol = ROOT / 'tests/vorbis_reset_protocol.py'
                need(self.freeze(reset_protocol) == snapshots.get(str(reset_protocol.resolve())),
                     'executed public raw reset protocol source')
                from vorbis_reset_protocol import validate_log as validate_reset
                reset_facts = validate_reset(log, matrix, platform, returncode=logs['qemu'][0]['exit_status'],
                                            timed_out=False, interrupted=False)
                need(reset_facts == report['observed_reset'], 'independent ordered raw reset replay')
        need(re.findall(r'^FLOOR1_START coordinator=0 decoder=(\d+)$', log, re.M) == [str(core)] and
             log.count('FLOOR1_CONTROLLED_STOP') == 1, 'coordinator/decoder cores and controlled terminal')
        summary = ['8', '6', '112', '225280', str(core)]
        need(report['observed']['summary'] == summary and
             re.findall(r'^FLOOR1_COMPLETE accepted=(\d+) rejected=(\d+) packets=(\d+) pcm=(\d+) core=(\d+)$', log, re.M) == [tuple(summary)],
             'complete finite target summary')
        marker = 'original_exact=1' if role == 'baseline' else 'renderer_repair=1'
        accepted = re.findall(r'^FLOOR1_ACCEPT case=(\d+) name=(\S+) packets=14 pcm=28160 ' + marker + r' core=(\d+)$', log, re.M)
        rejected = re.findall(r'^FLOOR1_REJECT case=(\d+) name=(\S+) result=-1 handle=0 core=(\d+)$', log, re.M)
        opens = re.findall(r'^FLOOR1_OPEN case=(\d+) result=(-?\d+) handle=([01])$', log, re.M)
        need(accepted == [(str(i), cases[i]['id'], str(core)) for i in range(8)] and
             rejected == [(str(i), cases[i]['id'], str(core)) for i in range(8, 14)] and
             opens == [(str(i), '0', '1') if i < 8 else (str(i), '-1', '0') for i in range(14)],
             'exact complete ordered accepts, rejects and null-handle outcomes')
        need(report['observed']['accepted'] == [list(x) for x in accepted] and
             report['observed']['rejected'] == [list(x) for x in rejected] and
             report['observed']['opens'] == [list(x) for x in opens], 'observed/transcript decision binding')
        pcm_rows = re.findall(r'^FLOOR1_PCM case=(\d+) packet=(\d+) consumed=(\d+) bytes=(\d+) hex=([0-9a-f]*)$', log, re.M)
        need([(int(x[0]), int(x[1])) for x in pcm_rows] == [(i, j) for i in range(8) for j in range(14)],
             'all ordered 112 PCM packet records')
        pins = {name.replace('\\', '/'): value for name, value in report['observed']['pcm'].items()}
        need(len(pins) == len(report['observed']['pcm']) and set(pins) == {f'pcm/{i}.s16le' for i in range(8)},
             'complete raw PCM file pins')
        pcm = {}
        for i in range(8):
            parts = []
            for j, row in enumerate(pcm_rows[i * 14:(i + 1) * 14]):
                raw = bytes.fromhex(row[4]); offsets = cases[i]['offsets']
                need(int(row[2]) == offsets[j + 1] - offsets[j] and
                     int(row[3]) == len(raw) == cases[i]['expected_packet_bytes'][j],
                     'per-case packet consumption and PCM length')
                parts.append(raw)
            raw = b''.join(parts); saved = self.freeze(safe(path.parent, f'pcm/{i}.s16le'))
            need(raw == saved and len(raw) == 28160 and any(raw) and digest(raw) == pins[f'pcm/{i}.s16le'],
                 'complete transcript/raw PCM/hash equality')
            pcm[i] = raw
        need(sum(map(len, pcm.values())) == 225280, 'complete target PCM byte count')
        if reset_cycles:
            need(reset_facts['baseline_pcm_sha256'] == {str(i): digest(raw) for i, raw in pcm.items()},
                 'all reset replay vectors bind the numerically compared full baseline')
        return dict(target=platform, core=core, role=role, dispatch=dispatch,
                    registered_callbacks_qualified=dispatch == 'registered',
                    raw_reset_behavior_qualified=reset_cycles,
                    report=str(path), report_sha256=digest(path.read_bytes()),
                    pcm_bytes=225280, pcm_sha256={str(i): digest(raw) for i, raw in pcm.items()},
                    metadata_evidence='Frozen executable harness checks stereo48k/S16 and canaries before PCM publication.'), pcm

    def wav(self, path):
        if not path.exists():
            return None, b'', None
        raw = self.freeze(path)
        if not raw:
            return digest(raw), b'', None
        with wave.open(str(path), 'rb') as stream:
            meta = dict(channels=stream.getnchannels(), sample_rate=stream.getframerate(),
                        sample_bytes=stream.getsampwidth(), frames=stream.getnframes(), compression=stream.getcomptype())
            pcm = stream.readframes(stream.getnframes())
            need(len(pcm) == meta['frames'] * meta['channels'] * meta['sample_bytes'] and not stream.readframes(1),
                 'complete WAV PCM payload')
        return digest(raw), pcm, meta

    def reference_outcome(self, command, stderr, wav, case):
        codec = re.search(r'\[libvorbis @ [^]]+\].*(?:header.*(?:damaged|corrupt|invalid)|floor.*(?:invalid|error))|'
                          r'\[dec:libvorbis @ [^]]+\] Error while opening decoder: Invalid data found', stderr, re.I)
        tool_error = re.search(r'Unknown decoder|Decoder .*not found|Unrecognized option|Option .*not found|'
                              r'No such file or directory|Permission denied|Error writing|Unable to find.*output format', stderr, re.I)
        need(command['state'] == 'terminal' and command['reaped'] is True and not command.get('forced_stop'),
             'normal reaped reference command required')
        need(not tool_error, 'tool/configuration/I/O error is not codec rejection')
        wav_sha, pcm, meta = self.wav(wav)
        if case['expected_valid']:
            need(command['returncode'] == 0 and meta == dict(channels=2, sample_rate=48000,
                 sample_bytes=2, frames=7040, compression='NONE') and len(pcm) == 28160 and any(pcm),
                 'complete nonzero unaltered stereo48k/S16 libvorbis reference')
        else:
            lines = stderr.splitlines()
            output_indices = [i for i, line in enumerate(lines) if line.startswith('Error opening output')]
            output_is_codec_consequence = not output_indices
            if len(output_indices) == 2:
                first, second = output_indices
                path_line = 'Error opening output file ' + str(wav) + '.'
                output_is_codec_consequence = (
                    second == first + 1 and lines[first] == path_line and
                    lines[second] == 'Error opening output files: Invalid data found when processing input' and
                    codec is not None and stderr.find(path_line) > codec.end())
            need(type(command.get('returncode')) is int and command['returncode'] in INVALIDDATA and
                 codec is not None and not pcm and output_is_codec_consequence,
                 'actual normal codec refusal with zero PCM; crash/timeout is not a rejection')
            raw_path = wav.with_suffix('.s16le')
            need(not raw_path.exists() or not self.freeze(raw_path), 'invalid carrier produced raw PCM')
        return pcm, dict(returncode=command['returncode'], decoded=case['expected_valid'],
                         codec_rejection=not case['expected_valid'], pcm_bytes=len(pcm),
                         pcm_sha256=digest(pcm), wav_sha256=wav_sha, metadata=meta)

    @staticmethod
    def ffmpeg_argv(ffmpeg, ogg, wav):
        return list(map(str, [ffmpeg, '-nostdin', '-n', '-hide_banner', '-loglevel', 'error', '-xerror',
            '-c:a', 'libvorbis', '-i', ogg, '-map', '0:a:0', '-map_metadata', '-1',
            '-fflags', '+bitexact', '-flags:a', '+bitexact', '-c:a', 'pcm_s16le', '-f', 'wav', wav]))

    def retained_reference(self, path, expected):
        need(digest(path.read_bytes()) == POSITION_REFERENCE_SHA, 'frozen original positions reference pin')
        report, snapshots = self.recorded(path); logs = self.logs(report, path, reference=True)
        origin = self.bound_corpus(report, snapshots, expected)
        need(report['result'] == 'NONPASS' and report['passed'] is False, 'preserved original overall NONPASS')
        ffmpegs = [name for name, value in report['tools'].items()
                   if Path(name).name.lower() == 'ffmpeg.exe' and value == FFMPEG_SHA]
        need(len(ffmpegs) == 1 and set(logs) == {f'case-{i:02d}-{d}' for i in range(14) for d in ('vorbis', 'libvorbis')},
             'pinned FFmpeg and complete original twenty-eight command receipts')
        cases = json.loads(expected['matrix.json'])['cases']
        need([(c['index'], c['id'], c['expected_valid']) for c in report['cases']] ==
             [(i, c['id'], c['expected_valid']) for i, c in enumerate(cases)], 'original reference case declarations')
        # Validate every advertised WAV/raw hash, including the unused native
        # oracle's retained NONPASS output, without promoting its numeric result.
        for item in report['cases']:
            for decoder, row in item['decoded'].items():
                if row.get('wav_sha256') is not None:
                    command = logs[row['command']][0]
                    wav = Path(command['argv'][-1]).resolve()
                    need(wav.is_relative_to(path.parent), 'recorded reference WAV boundary')
                    sha, pcm, meta = self.wav(wav)
                    need(sha == row['wav_sha256'] and digest(pcm) == row['pcm_sha256'] and
                         len(pcm) == row['pcm_bytes'] and meta == row['metadata'], 'advertised reference WAV/PCM binding')
                    if row.get('pcm_path'):
                        need(self.freeze(safe(path.parent, row['pcm_path'])) == pcm, 'advertised raw reference PCM')
        result, evidence = {}, dict(kind='retained_positions', report=str(path),
            report_sha256=digest(path.read_bytes()), original_result=report['result'], cases=[])
        self.report['references'].append(evidence)
        for i, case in enumerate(cases):
            name = f'case-{i:02d}-libvorbis'; command, stdout, stderr = logs[name]
            wav = path.parent / (name + '.wav')
            need(command['argv'] == self.ffmpeg_argv(ffmpegs[0], origin / case['ogg'], wav),
                 'exact unaltered retained libvorbis command route')
            pcm, fact = self.reference_outcome(command, stderr, wav, case)
            if i < 8:
                saved = report['cases'][i]['decoded']['libvorbis']
                need(digest(pcm) == saved['pcm_sha256'] and
                     self.freeze(safe(path.parent, saved['pcm_path'])) == pcm, 'Xiph reference saved PCM binding')
                fact['pcm_path'] = str(safe(path.parent, saved['pcm_path']))
                result[i] = pcm
            evidence['cases'].append(dict(index=i, id=case['id'], wav_path=str(wav), **fact))
        need(len(result) == 8, 'all eight retained libvorbis vectors')
        return result

    def run_ffmpeg(self, name, argv):
        self.current(); so = self.out / (name + '.stdout.log'); se = self.out / (name + '.stderr.log')
        row = dict(name=name, argv=argv, cwd=str(self.out), state='starting', stdout=so.name, stderr=se.name)
        self.report['commands'].append(row); self.save(); child = None; start = time.monotonic()
        try:
            with so.open('xb') as stdout, se.open('xb') as stderr:
                child = subprocess.Popen(argv, cwd=self.out, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                row['pid'] = child.pid; self.save()
                while child.poll() is None:
                    need(time.monotonic() - start < 30, 'reference child thirty-second bound')
                    need(so.stat().st_size <= LIMIT and se.stat().st_size <= LIMIT, 'reference log size bound')
                    wav = Path(argv[-1])
                    need(not wav.exists() or wav.stat().st_size <= LIMIT, 'reference WAV size bound')
                    try:
                        child.wait(timeout=0.1)
                    except subprocess.TimeoutExpired:
                        pass
                row.update(state='terminal', returncode=child.returncode)
        except BaseException as exc:
            row.update(state='tool_or_timeout_nonpass', error=repr(exc))
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
        finally:
            try:
                if child is not None:
                    if child.poll() is None:
                        child.kill(); row['forced_stop'] = True
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        child.kill(); child.wait(timeout=5)
            finally:
                row.update(reaped=child is not None and child.poll() is not None,
                           elapsed_seconds=time.monotonic() - start,
                           stdout_sha256=digest(so.read_bytes()) if so.exists() else None,
                           stderr_sha256=digest(se.read_bytes()) if se.exists() else None)
                self.save()
        return row, se.read_text(encoding='utf-8', errors='replace') if se.exists() else ''

    def fresh_reference(self, ffmpeg, corpus, matrix):
        need(ffmpeg.is_file() and digest(ffmpeg.read_bytes()) == FFMPEG_SHA, 'explicit pinned FFmpeg executable')
        self.tool(ffmpeg, FFMPEG_SHA); self.report['ffmpeg_executed'] = True
        evidence = dict(kind='fresh_libvorbis', ffmpeg=str(ffmpeg), ffmpeg_sha256=FFMPEG_SHA, cases=[])
        self.report['references'].append(evidence); result = {}
        for i, case in enumerate(matrix['cases']):
            name = f'case-{i:02d}-libvorbis'; wav = self.out / (name + '.wav')
            command, stderr = self.run_ffmpeg(name, self.ffmpeg_argv(ffmpeg, safe(corpus, case['ogg']), wav))
            item = dict(index=i, id=case['id'], expected_valid=case['expected_valid'],
                        wav_path=str(wav), qualified=False)
            evidence['cases'].append(item)
            try:
                pcm, fact = self.reference_outcome(command, stderr, wav, case)
                item.update(fact, qualified=True)
                if i < 8:
                    raw = self.out / (name + '.s16le')
                    with raw.open('xb') as stream:
                        stream.write(pcm)
                    self.freeze(raw); item['pcm_path'] = str(raw); result[i] = pcm
            except Exception as exc:
                item['error'] = repr(exc)
                self.report['failures'].append(dict(reference_case=i, error=repr(exc)))
            self.save()
        need(len(self.report['commands']) == 14, 'all fourteen fresh libvorbis command attempts')
        need(len(result) == 8 and all(row['qualified'] for row in evidence['cases']),
             'all eight valid references and six actual normal codec refusals')
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True)
    parser.add_argument('--target-report', type=Path, action='append', required=True)
    parser.add_argument('--old-tail-report', type=Path)
    parser.add_argument('--baseline-report', type=Path, action='append', default=[])
    parser.add_argument('--reference-report', type=Path)
    parser.add_argument('--ffmpeg', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out, corpus, build = args.output.resolve(), args.corpus.resolve(), (ROOT / '.build').resolve()
    targets = [p.resolve() for p in args.target_report]
    baselines = [p.resolve() for p in args.baseline_report]
    old_tail = args.old_tail_report.resolve() if args.old_tail_report else None
    retained = args.reference_report.resolve() if args.reference_report else POSITION_REFERENCE.resolve()
    reports = targets + baselines + ([old_tail] if old_tail else []) + [retained]
    need(build.parent == ROOT and out != build and out.is_relative_to(build) and not out.exists(), 'fresh .build output')
    need(corpus.is_relative_to(build) and corpus.is_dir() and not out.is_relative_to(corpus), 'corpus/output boundary')
    need(len(targets) == len(set(targets)) and len(baselines) == len(set(baselines)) and
         all(p.is_relative_to(build) and not out.is_relative_to(p.parent) for p in reports), 'report/output boundary')
    out.mkdir(parents=True); checker = Checker(out); r = checker.report
    try:
        checker.save(); checker.freeze(Path(__file__))
        supplied_matrix = json.loads(checker.freeze(corpus / 'matrix.json'))
        kind = 'slopes' if supplied_matrix['schema'] == 'vorbis-floor1-slopes-v1' else 'positions'
        need(supplied_matrix['schema'] == 'vorbis-floor1-' + kind + '-v1', 'recognized complete corpus schema')
        expected = checker.generated(kind); matrix = checker.corpus(corpus, expected)
        r.update(corpus_kind=kind, corpus_manifest_sha256=digest(expected['manifest.json']))
        positional_expected = expected if kind == 'positions' else None
        positional_reference = None
        if kind == 'positions' or old_tail:
            positional_expected = positional_expected or checker.generated('positions')
            positional_reference = checker.retained_reference(retained, positional_expected)
        reference = positional_reference if kind == 'positions' else checker.fresh_reference(
            args.ffmpeg.resolve() if args.ffmpeg else Path('missing-explicit-ffmpeg'), corpus, matrix)
        baseline_pcm = {}
        for path in baselines:
            positional_expected = positional_expected or checker.generated('positions')
            fact, pcm = checker.target(path, positional_expected, role='baseline')
            need(fact['target'] not in baseline_pcm, 'distinct baseline architectures')
            baseline_pcm[fact['target']] = pcm; r['baselines'].append(fact)
        seen = set()
        for path in targets:
            fact, pcm = checker.target(path, expected)
            need(fact['target'] not in seen, 'distinct candidate architectures'); seen.add(fact['target'])
            fact['cases'] = []
            for i in range(8):
                comparisons = []; offset = 0
                for j, size in enumerate(matrix['cases'][i]['expected_packet_bytes']):
                    comparisons.append(dict(packet=j, **metrics(pcm[i][offset:offset + size], reference[i][offset:offset + size])))
                    offset += size
                row = dict(index=i, id=matrix['cases'][i]['id'], raw_sha256=digest(pcm[i]),
                           **metrics(pcm[i], reference[i]), packets=comparisons)
                fact['cases'].append(row)
                if row['over_bound']:
                    r['failures'].append(dict(target=fact['target'], case=i, reason='predeclared complete-vector 2LSB bound'))
            if kind == 'positions' and fact['target'] in baseline_pcm:
                fact['ordinary_baseline_byte_exact'] = all(pcm[i] == baseline_pcm[fact['target']][i] for i in range(3, 8))
                need(fact['ordinary_baseline_byte_exact'], 'positions cases3..7 changed from pinned baseline')
            fact['numerically_qualified'] = all(row['over_bound'] == 0 for row in fact['cases'])
            r['targets'].append(fact); checker.save()
        if old_tail:
            need(positional_expected is not None and positional_reference is not None, 'old-tail positions oracle')
            fact, pcm = checker.target(old_tail, positional_expected, role='old-tail')
            need(fact['target'] in baseline_pcm, 'old-tail needs matching pinned frozen baseline')
            fact['all_eight_frozen_baseline_byte_exact'] = all(pcm[i] == baseline_pcm[fact['target']][i] for i in range(8))
            fact['cases'] = [dict(index=i, **metrics(pcm[i], positional_reference[i])) for i in range(8)]
            need(fact['all_eight_frozen_baseline_byte_exact'] and
                 [row['max_abs_error'] for row in fact['cases'][:3]] == [65535] * 3 and
                 all(row['over_bound'] > 0 for row in fact['cases'][:3]) and
                 all(row['max_abs_error'] == 1 and row['over_bound'] == 0 for row in fact['cases'][3:]),
                 'specific old-tail failure must reproduce baseline all8, three65535 failures and five1LSB normals')
            fact['specific_old_tail_control_effective'] = True; r['controls'].append(fact)
        checker.current()
        qualified = not r['failures'] and bool(r['targets']) and all(x['numerically_qualified'] for x in r['targets'])
        r.update(completed=True, passed=qualified, finite_renderer_qualified=qualified,
                 both_architectures_qualified=qualified and seen == {'esp32', 'esp32c3'},
                 result='FINITE_RENDERER_NUMERICALLY_QUALIFIED' if qualified else 'FINITE_RENDERER_NUMERIC_NONPASS',
                 limitations='Finite saved raw API evidence and Xiph libvorbis only; fixed2LSB policy, no signal transforms. '
                             'Native overall NONPASS remains unchanged. No fullG6, production radio, Ogg adapter, RF or physical qualification.')
        checker.save(); print(json.dumps({key: r[key] for key in ('completed', 'passed', 'result', 'both_architectures_qualified')}))
        return 0 if qualified else 1
    except BaseException as exc:
        r.update(completed=False, passed=False, finite_renderer_qualified=False,
                 both_architectures_qualified=False, result='RENDER_CHECK_INCOMPLETE_NONPASS', error=repr(exc))
        try:
            checker.current()
            r['inputs_unchanged_on_error'] = True
        except BaseException as audit:
            r['preservation_error'] = repr(audit)
        checker.save(); raise


if __name__ == '__main__':
    sys.exit(main())
