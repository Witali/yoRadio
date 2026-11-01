"""Observe 49 complete public Opus streams, stock Ogg first and wrapper separately.

Exact public arguments/results and all decoded PCM are captured locally. Real
refusals and geometry differences remain observations, without an invented
numeric tolerance or a claim that a legal unsupported packet may be rejected.
This diagnostic does not run the full audio_service or physical output.
"""
import argparse
from array import array
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent if ROOT.parent.name == '.worktree' else ROOT
PROJECT = ROOT / 'tests/target/cyd_opus_packet_modes_qemu'
BASE = ROOT / 'tests/run-cyd-ogg-playback-qemu.py'
BASE_SHA = '6c1ffd611c7c10982d8c3ad6eb2b633c26139355d1996096ec9d2b4a0b120dfd'
WRAPPER_SHA = '2090861f891aa299fac3a90f4e35d13a6e6412f63b7293c4ed56bbd43d7482a6'
MAIN = ROOT / 'idf/esp32-cyd2usb-native/main'
SHARED = ROOT / 'idf/components/native_stream/include'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


need(sha(BASE) == BASE_SHA, 'pinned reviewed compiler-closure and native-command helper')
spec = importlib.util.spec_from_file_location('packet_modes_reviewed_native_helper', BASE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
common = base.common


def compare_pcm(actual, reference):
    need(len(actual) == len(reference) and len(actual) > 0 and len(actual) % 2 == 0, 'equal complete measured PCM geometry')
    a, b = array('h'), array('h')
    a.frombytes(actual); b.frombytes(reference)
    if sys.byteorder != 'little':
        a.byteswap(); b.byteswap()
    error = sum((x - y) ** 2 for x, y in zip(a, b))
    energy = sum(y * y for y in b)
    return dict(samples=len(a), equal_bytes=actual == reference, max_absolute_lsb=max(abs(x - y) for x, y in zip(a, b)),
                rms_error_lsb=math.sqrt(error / len(a)), reference_energy=energy, error_energy=error,
                signal_to_error_db=10 * math.log10(energy / error) if error and energy else None,
                new_tolerance_applied=False, numeric_conformance_claim=False)


def parse_log(text, fixtures, reference, out):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack overflow', text, re.I),
         'no actual panic/assertion/heap/watchdog/stack failure')
    lines = [line for line in text.replace('\r\n', '\n').splitlines() if line.startswith('PM_')]
    need(lines and lines[0] == 'PM_BEGIN sdk=6.0.2 coordinator=0 worker=1 priority=3 stack=16384 initial_capacity=12288 fixtures=49', 'actual known diagnostic worker')
    cases, calls, opens, closes, infos, pcms = [], {}, {}, {}, {}, {}
    keys = {'PM_CALL': {'id', 'call', 'len', 'consumed', 'capacity', 'needed', 'decoded', 'eos', 'result'},
            'PM_OPEN': {'id', 'result', 'handle'}, 'PM_CLOSE': {'id'},
            'PM_INFO': {'id', 'result', 'rate', 'channels', 'bits'}}
    for line in lines[1:-1]:
        parts = line.split(); tag = parts[0]
        fields = dict(pair.split('=', 1) for pair in parts[1:])
        need(len(fields) == len(parts) - 1, 'unique complete fields')
        if tag == 'PM_PCM':
            need(set(fields) == {'id', 'kind', 'offset', 'bytes', 'hex'} and fields['kind'] in ('raw', 'output'), 'exact PCM transport fields')
            data = bytes.fromhex(fields['hex']); key = (int(fields['id']), fields['kind'])
            body = pcms.setdefault(key, bytearray())
            need(0 < len(data) <= 128 and len(data) == int(fields['bytes']) and len(body) == int(fields['offset']), 'all exact PCM bytes in order')
            body.extend(data)
        elif tag == 'PM_CASE':
            cases.append({k: v if k.endswith('_sha') else int(v) for k, v in fields.items()})
        else:
            need(tag in keys and set(fields) == keys[tag], 'known exact public-call record')
            row = {k: int(v) for k, v in fields.items()}
            lookup = {'PM_CALL': calls, 'PM_OPEN': opens, 'PM_CLOSE': closes, 'PM_INFO': infos}[tag]
            lookup.setdefault(row['id'], []).append(row)
    need(len(cases) == 196 and [r['id'] for r in cases] == list(range(196)), 'all 49 complete stock/wrapper/split cases')
    fixture_rows = list(fixtures.items())
    outcomes, captured = [], {}
    for id, row in enumerate(cases):
        fixture_id, mode, chunk = id // 4, id % 4 // 2, 257 if id % 2 else 0
        name, fixture = fixture_rows[fixture_id]
        account, creator = fixture['accounting'], fixture['creator_decoding']
        need((row['fixture'], row['mode'], row['chunk'], row['fixture_bytes'], row['encoded_channels']) ==
             (fixture_id, mode, chunk, fixture['artifacts']['complete.ogg']['bytes'], account['channels']), 'exact complete source and stock-first order')
        own, open_rows, close_rows = calls.get(id, []), opens.get(id, []), closes.get(id, [])
        need(len(open_rows) == 1 and row['opens'] == sum(r['result'] == 0 for r in open_rows) == row['closes'] == len(close_rows) and
             row['open_status'] == open_rows[0]['result'] and row['calls'] == len(own) and
             row['consumed'] == sum(r['consumed'] for r in own) and [r['call'] for r in own] == list(range(1, len(own) + 1)),
             'authentic open/process/close/result accounting')
        need(row['resizes'] == sum(r['result'] == -8 for r in own) and
             row['data_eos'] == sum(r['eos'] and r['len'] > 0 for r in own) and
             row['empty_eos'] == sum(r['eos'] and r['len'] == 0 for r in own) and
             all(r['consumed'] <= r['len'] and r['decoded'] <= r['capacity'] for r in own), 'real capacities/resize/consumption/EOS')
        need(0 < row['offered'] <= row['fixture_bytes'] and row['consumed'] <= row['fixture_bytes'] and
             row['core'] == 1 and row['priority'] == 3 and 0 < row['stack_free'] <= 16384 and
             0 < row['heap_min'] <= row['after'] and row['before'] > 0, 'actual input/resource bounds')
        result = dict(name=name, measurements=row, public_calls=own, info=infos.get(id, []),
                      complete_pcm={}, creator_comparisons={}, exact_vendor_window=None,
                      real_zero_coded_frame_case=creator['zero_length_coded_frames'] > 0)
        for kind in ('raw', 'output'):
            data = bytes(pcms.get((id, kind), b'')); captured[(id, kind)] = data
            need(len(data) == row[kind + '_bytes'] and hashlib.sha256(data).hexdigest() == row[kind + '_sha'], 'entire native PCM bytes and independent hash')
            path = out / ('case' + str(id) + '-' + kind + '.pcm'); path.write_bytes(data)
            result['complete_pcm'][kind] = dict(path=path.name, bytes=len(data), sha256=sha(path), local_only=True)
            if data and row['channels'] == account['channels']:
                key = 'raw.pcm' if kind == 'raw' else 'playback.pcm'
                expected = (reference / fixture['artifacts'][key]['path']).read_bytes()
                if len(data) == len(expected):
                    result['creator_comparisons'][kind] = dict(complete_geometry=True, **compare_pcm(data, expected))
                else:
                    result['creator_comparisons'][kind] = dict(complete_geometry=False, actual_bytes=len(data), expected_bytes=len(expected),
                                                               numeric_comparison_performed=False)
        if row['status'] == 0:
            need(row['drained'] == 1 and row['offered'] == row['consumed'] == row['fixture_bytes'] and
                 row['data_eos'] > 0 and row['empty_eos'] > 0, 'genuine full input and EOS drain on success')
            result['complete_expected_geometry'] = row['channels'] == account['channels'] and row['bits'] == 16 and row['rate'] == 48000 and \
                row['raw_bytes'] == creator['raw_bytes'] and (not mode or row['output_bytes'] == creator['trim_bytes'])
            result['observed_behavior'] = 'complete_public_decode' if result['complete_expected_geometry'] else 'reported_success_with_geometry_gap'
        else:
            need(row['cause'] != 0 and row['drained'] == 0, 'authentic reported refusal')
            result.update(observed_behavior='reported_refusal_requires_assessment', standards_compliant_refusal=None, complete_expected_geometry=False)
        outcomes.append(result)
    exact_windows = 0
    for id, result in enumerate(outcomes):
        row = result['measurements']; fixture = fixture_rows[id // 4][1]; account = fixture['accounting']
        first = captured[(id // 4 * 4, 'raw')]
        if result['complete_expected_geometry'] and first:
            result['raw_matches_stock_whole'] = captured[(id, 'raw')] == first
            if row['mode']:
                frame_bytes = account['channels'] * 2; begin = account['pre_skip'] * frame_bytes
                window = first[begin:begin + account['logical_frames'] * frame_bytes]
                result['exact_vendor_window'] = captured[(id, 'output')] == window
                exact_windows += result['exact_vendor_window']
    terminal = lines[-1].split(); need(terminal[0] == 'PM_COMPLETE', 'actual terminal diagnostic completion')
    complete = {k: int(v) for k, v in (part.split('=', 1) for part in terminal[1:])}
    need(complete['cases'] == 196 and complete['core'] == 1 and complete['priority'] == 3 and complete['heap_integrity'] == 1,
         'all cases completed with real worker and heap integrity')
    return dict(cases=outcomes, terminal=complete, reported_refusals=sum(r['measurements']['status'] != 0 for r in outcomes),
                geometry_gaps=sum(r['measurements']['status'] == 0 and not r['complete_expected_geometry'] for r in outcomes),
                exact_vendor_windows=exact_windows, no_numeric_tolerance_applied=True,
                all_complete_playback_geometry=all(r['complete_expected_geometry'] for r in outcomes),
                numeric_conformance_claim=False)


class Campaign(base.Campaign):
    def __init__(self, args, fixtures):
        super().__init__(args); self.fixtures = fixtures
        self.report.update(fixtures=fixtures, actual_audio_service_tu=False, actual_wrapper=True,
                           stock_public_vendor_measured_first=True, standard_mode_matrix_playback_qualified=False)

    def freeze_sources(self):
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file():
                self.freeze(path, Path('project') / path.relative_to(PROJECT), 'new independent packet-mode diagnostic')
        for name in ('decoder_registration.c', 'decoder_registration.h', 'ogg_playback.h'):
            self.freeze(MAIN / name, Path('project/main') / name, 'unchanged actual public wrapper/registration')
        for name in ('ogg_page_input.h', 'opus_pcm_trim.h', 'ogg_opus_timeline.h', 'decoder_pending_input.h'):
            self.freeze(SHARED / name, Path('project/main') / name, 'unchanged actual shared owner')
        for path in (BASE, base.COMMON, Path(__file__)):
            self.freeze(path, Path('sources/controllers') / path.name, 'pinned reviewed controller source')
        for path in sorted((self.args.reference / 'sources').rglob('*')):
            if path.is_file():
                self.freeze(path, Path('sources/creator-sources') / path.relative_to(self.args.reference / 'sources'), 'exact creator host source')
        self.freeze(self.args.reference / 'report.json', Path('sources/reference/report.json'), 'original complete creator process report')
        table, bodies, offset = [], [], 16 + 49 * 32
        for index, (name, fixture) in enumerate(self.fixtures.items()):
            account, decoded = fixture['accounting'], fixture['creator_decoding']
            ogg = self.args.reference / fixture['artifacts']['complete.ogg']['path']
            table.append(struct.pack('<8I', account['channels'], offset, ogg.stat().st_size, decoded['raw_frames'],
                                     account['logical_frames'], account['pre_skip'], fixture['case']['mode'], index))
            bodies.append(ogg.read_bytes()); offset += ogg.stat().st_size
            for artifact in fixture['artifacts'].values():
                source = self.args.reference / artifact['path']
                need(sha(source) == artifact['sha256'] and source.stat().st_size == artifact['bytes'], 'exact creator input/output artifact')
                self.freeze(source, Path('sources/reference') / artifact['path'], 'full encoded source/independent reference; PCM stays local')
        blob = self.out / 'project/main/modes.bin'
        blob.write_bytes(struct.pack('<4I', 0x504d4f47, 1, 49, 32) + b''.join(table) + b''.join(bodies))
        self.artifacts[blob.relative_to(self.out).as_posix()] = sha(blob)
        vendor = self.args.vendor; paths = {p for p in vendor.iterdir() if p.is_file()}
        for folder in ('include', 'src'):
            paths.update(p for p in (vendor / folder).rglob('*') if p.is_file())
        paths.update(vendor / 'lib/esp32' / name for name in common.ARCHIVE_PINS)
        for path in sorted(paths):
            self.freeze(path, Path('sources/vendor/esp_audio_codec') / path.relative_to(vendor), 'exact public vendor input')
        common.write_json(self.out / 'source-manifest.json', self.sources)

    def qualify(self):
        flash = super().qualify()
        closure = json.loads((self.out / 'actual-compiler-closure.json').read_bytes())
        need('pcm_header_gain.h' not in {Path(p).name for p in closure['dependencies']}, 'metadata-only wrapper preserves raw synthesis')
        return flash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--build-timeout', type=int, default=1200)
    parser.add_argument('--qemu-timeout', type=int, default=1200)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args(); args.output = args.output.resolve(); args.reference = args.reference.resolve()
    need(sys.platform == 'win32' and args.output.is_relative_to(ROOT / '.build') and not args.output.exists(), 'fresh Windows native capture')
    need(args.reference.is_relative_to(ROOT / '.build') and 1 <= args.build_timeout <= 1200 and 1 <= args.qemu_timeout <= 1200,
         'local reference and bounded process deadlines')
    reference = json.loads((args.reference / 'report.json').read_bytes())
    need(reference['passed'] and reference['completed'] and reference['all_source_bindings_current'] and
         not reference['native_vendor_executed'] and len(reference['cases']) == 49, 'complete creator corpus prerequisite')
    for row in reference['sources']:
        need(sha(ROOT / row['path']) == sha(args.reference / row['snapshot']) == row['sha256'], 'current exact creator source binding')
    need(sha(MAIN / 'ogg_playback.h') == WRAPPER_SHA, 'frozen current metadata-only wrapper')
    args.idf = REPO / '.idf/v6.0.2'; args.idf_tools = REPO / '.idf/tools-v6.0.2'
    args.idf_python = args.idf_tools / 'python_env/idf6.0_py3.12_env/Scripts/python.exe'
    args.vendor = REPO / '.idf/esp-adf-libs/esp_audio_codec'; args.qemu = ROOT / '.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
    args.rom = Path('C:/Work/QEMU-ESP32/pc-bios')
    args.git = Path(shutil.which('git.exe') or shutil.which('git') or '')
    args.powershell = Path(shutil.which('pwsh.exe') or '')
    need(all(path.is_file() for path in (args.idf / 'tools/idf.py', args.idf / 'export.ps1', args.idf_python, args.qemu,
         args.git, args.powershell, PROJECT / 'sdk-build.ps1')), 'installed native dependencies only')
    need(sha(args.qemu) == common.QEMU_SHA and all(sha(args.vendor / 'lib/esp32' / name) == pin for name, pin in common.ARCHIVE_PINS.items()),
         'pinned LX6 public archives and emulator')
    if args.preflight_only:
        print(json.dumps(dict(preflight=True, target_executed=False, complete_creator_streams=49, planned_native_cases=196)))
        return 0
    args.output.mkdir(parents=True); campaign = Campaign(args, reference['cases'])
    try:
        campaign.save(); campaign.verify_repositories(); campaign.freeze_sources()
        defaults = (args.output / 'project/sdkconfig.common.defaults').read_text()
        (args.output / 'project/sdkconfig.defaults').write_text('CONFIG_IDF_TARGET="esp32"\nCONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_240=y\n# CONFIG_FREERTOS_UNICORE is not set\n' + defaults, encoding='utf-8')
        for path in (args.idf_python, args.qemu, args.git, args.powershell, *args.rom.glob('esp32-v3-rom*.bin')):
            campaign.bind_runtime(path)
        print('FROZEN packet-mode sources; starting SDK build', flush=True)
        campaign.run_command('build', [args.powershell, '-NoProfile', '-NonInteractive', '-File', args.output / 'project/sdk-build.ps1',
            '-Campaign', args.output, '-SdkDirectory', args.idf, '-ToolsDirectory', args.idf_tools, '-PythonExecutable', args.idf_python, '-Target', 'esp32'], args.build_timeout)
        flash = campaign.qualify(); print('SDK terminal zero; starting public packet-mode playback observations', flush=True)
        log = campaign.run_command('qemu', [args.qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet', '-smp', '2', '-L', args.rom,
            '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic', 'none',
            '-drive', 'file=' + str(flash) + ',if=mtd,format=raw'], args.qemu_timeout)
        campaign.report['measurements'] = parse_log(log + '\n' + (args.output / 'qemu.stderr.log').read_text(errors='replace'), reference['cases'], args.reference, args.output)
        need(campaign.verify_inputs(), 'all consumed source/runtime/artifact bindings unchanged')
        campaign.report.update(passed=True, completed=True)
        print(json.dumps(dict(passed=True, diagnostic_only=True, cases=196, capture=args.output.relative_to(ROOT).as_posix(),
                             reported_refusals=campaign.report['measurements']['reported_refusals'],
                             geometry_gaps=campaign.report['measurements']['geometry_gaps'])))
        return 0
    except Exception as error:
        campaign.report.update(passed=False, completed=False, failure_type=type(error).__name__, failure=str(error))
        print(json.dumps(dict(passed=False, failure=str(error))))
        return 1
    finally:
        campaign.save()


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
