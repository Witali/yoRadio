"""Observe public raw Opus cadence/configuration beside stock Ogg decoding.

Creator float cadence is exact on these inputs; clipped creator int16 cadence
is not universally exact. All numeric relations here remain measurements.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent if ROOT.parent.name == '.worktree' else ROOT
PROJECT = ROOT / 'tests/target/cyd_opus_frame_control_qemu'
MODES = ROOT / 'tests/run-cyd-opus-packet-modes-qemu.py'
MODES_SHA = 'b6b12b0934630b24afb9f288881bfc7ba370e671f060276c0b366fe7a384b18a'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


need(sha(MODES) == MODES_SHA, 'unchanged reviewed mode-diagnostic closure helper')
spec = importlib.util.spec_from_file_location('frame_control_modes_helper', MODES)
modes = importlib.util.module_from_spec(spec); spec.loader.exec_module(modes)
common = modes.common


def parse_log(text, creator, control, parent, args):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack overflow', text, re.I), 'no actual target panic/assert/heap/watchdog failure')
    lines = [line for line in text.replace('\r\n', '\n').splitlines() if line.startswith('FC_')]
    need(lines[0] == 'FC_BEGIN sdk=6.0.2 coordinator=0 worker=1 priority=3 stack=16384 fixtures=4 cases=24', 'real worker profile')
    cases, calls, opens, closes, pcms = [], {}, {}, {}, {}
    for line in lines[1:-1]:
        parts = line.split(); tag = parts[0]; fields = dict(pair.split('=', 1) for pair in parts[1:])
        need(len(fields) == len(parts) - 1, 'unique exact observation fields')
        id = int(fields['id'])
        if tag == 'FC_PCM':
            need(set(fields) == {'id', 'offset', 'bytes', 'hex'}, 'exact complete PCM transport')
            body = pcms.setdefault(id, bytearray()); data = bytes.fromhex(fields['hex'])
            need(len(body) == int(fields['offset']) and len(data) == int(fields['bytes']) and 0 < len(data) <= 128, 'all actual PCM bytes in sequence')
            body.extend(data)
        elif tag == 'FC_CASE':
            cases.append({key: value if key == 'sha' else int(value) for key, value in fields.items()})
        elif tag == 'FC_CALL':
            calls.setdefault(id, []).append({key: int(value) for key, value in fields.items()})
        elif tag == 'FC_OPEN':
            opens.setdefault(id, []).append({key: value if value in ('na', 'ogg', 'raw') else int(value) for key, value in fields.items()})
        elif tag == 'FC_CLOSE':
            closes.setdefault(id, []).append({key: value if value == 'void' else int(value) for key, value in fields.items()})
        else:
            need(False, 'known actual public observation')
    need(len(cases) == 24 and [r['id'] for r in cases] == list(range(24)), 'all public control cases completed')
    names = list(control['cases']); outcomes = []; bodies = {}
    for id, row in enumerate(cases):
        fixture, mode = id // 6, id % 6; name = names[fixture]; account = creator['cases'][name]
        own, opened, closed = calls.get(id, []), opens.get(id, []), closes.get(id, [])
        need(row['fixture'] == fixture and row['mode'] == mode and len(opened) == 1 and
             row['open_status'] == opened[0]['result'] and row['opens'] == sum(r['result'] == 0 for r in opened) == row['closes'] == len(closed), 'real ordered open and exact cleanup')
        need(row['calls'] == len(own) and [r['call'] for r in own] == list(range(1, len(own) + 1)) and
             row['consumed'] == sum(r['consumed'] for r in own) and row['resizes'] == sum(r['result'] == -8 for r in own) and
             all(r['consumed'] <= r['len'] and r['decoded'] <= r['capacity'] for r in own), 'genuine complete public call/result accounting')
        expected_duration = (8 if account['accounting']['packet_samples'] == 5760 else 0) if mode in (1, 2) else 0 if mode == 4 else -1
        if mode:
            need(opened[0]['api'] == 'raw' and opened[0]['rate'] == 48000 and opened[0]['channels'] == 2 and
                 opened[0]['duration'] == expected_duration and opened[0]['self_delimited'] == 0 and
                 all(r['packet'] >= 0 for r in own) and all(isinstance(r['result'], int) for r in closed), 'documented real raw configuration, no PLC recovery requests')
        else:
            need(opened[0]['api'] == 'ogg' and all(r['packet'] == -1 for r in own) and
                 all(r['result'] == 'void' for r in closed), 'stock Ogg API has a void close result')
        need(row['core'] == 1 and row['priority'] == 3 and 0 < row['stack_free'] <= 16384 and
             row['before'] > 0 and row['after'] > 0 and row['heap_min'] > 0 and
             row['initial_capacity'] == (12288 if mode == 2 else 23040), 'actual worker/resource/output-capacity profile')
        data = bytes(pcms.get(id, b'')); bodies[id] = data
        need(len(data) == row['pcm_bytes'] and hashlib.sha256(data).hexdigest() == row['sha'], 'complete native PCM and independent hash')
        output = args.output / ('case' + str(id) + '.pcm'); output.write_bytes(data)
        expected_packets = 192 if mode >= 4 and name != 'm2-s120-code0' else 4
        if mode:
            file = args.control / control['cases'][name]['files']['elementary.packets' if mode >= 4 else 'input.packets']['path']
            transport = file.read_bytes(); payload_bytes = len(transport) - 28 - expected_packets * 4
        else:
            payload_bytes = account['artifacts']['complete.ogg']['bytes']
        complete = row['status'] == 0 and row['rate'] == 48000 and row['channels'] == 2 and row['bits'] == 16 and \
            len(data) == account['creator_decoding']['raw_bytes'] and row['consumed'] == payload_bytes and \
            (not mode or row['packets'] == expected_packets)
        comparisons = {}
        if data and len(data) == account['creator_decoding']['raw_bytes']:
            for filename in ('aggregate-s16.pcm', 'elementary-s16.pcm', 'aggregate-hard-s16.pcm', 'elementary-hard-s16.pcm',
                             'aggregate-soft-s16.pcm', 'elementary-soft-s16.pcm'):
                ref = args.control / control['cases'][name]['files'][filename]['path']
                comparisons[filename] = modes.compare_pcm(data, ref.read_bytes())
            previous = next(r for r in parent['measurements']['cases'] if r['name'] == name and r['measurements']['mode'] == 0 and r['measurements']['chunk'] == 0)
            prior = args.parent / previous['complete_pcm']['raw']['path']
            comparisons['previous-stock-ogg'] = modes.compare_pcm(data, prior.read_bytes())
        outcomes.append(dict(name=name, measurements=row, public_calls=own, public_opens=opened, public_closes=closed,
                             complete_expected_geometry=complete, comparisons=comparisons,
                             pcm=dict(path=output.name, bytes=len(data), sha256=sha(output), local_only=True)))
    for id, result in enumerate(outcomes):
        result['matches_current_stock_ogg'] = bool(bodies[id]) and bodies[id] == bodies[id // 6 * 6]
        result['matches_raw_aggregate_presized'] = bool(bodies[id]) and bodies[id] == bodies[id // 6 * 6 + 1]
    need(lines[-1].startswith('FC_COMPLETE '), 'actual complete terminal control record')
    terminal = {key: int(value) for key, value in (part.split('=', 1) for part in lines[-1].split()[1:])}
    need(terminal['cases'] == 24 and terminal['heap_integrity'] == 1 and terminal['core'] == 1 and terminal['priority'] == 3, 'real terminal ownership and heap integrity')
    return dict(cases=outcomes, terminal=terminal, reported_refusals=sum(r['measurements']['status'] != 0 for r in outcomes),
                geometry_gaps=sum(not r['complete_expected_geometry'] for r in outcomes), numeric_conformance_claim=False,
                numeric_tolerance_applied=False, creator_clipped_integer_cadence_equivalence=False)


class Campaign(modes.base.Campaign):
    def __init__(self, args, creator, control):
        super().__init__(args); self.creator = creator; self.control = control
        self.report.update(actual_wrapper=False, actual_audio_service_tu=False, actual_public_raw_opus=True,
                           production_selected=False, numeric_conformance_claim=False, numeric_tolerance_applied=False,
                           fixtures={name: dict(channels=creator['cases'][name]['accounting']['channels'],
                                                raw_frames=creator['cases'][name]['creator_decoding']['raw_frames'],
                                                aggregate_sha256=control['cases'][name]['files']['input.packets']['sha256'],
                                                elementary_sha256=control['cases'][name]['files']['elementary.packets']['sha256'])
                                     for name in control['cases']})

    def freeze_sources(self):
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file():
                self.freeze(path, Path('project') / path.relative_to(PROJECT), 'new public raw-frame diagnostic')
        for name in ('decoder_registration.c', 'decoder_registration.h', 'ogg_playback.h'):
            self.freeze(modes.MAIN / name, Path('project/main') / name, 'unchanged public registration and header-only pending owner')
        for name in ('ogg_page_input.h', 'opus_pcm_trim.h', 'ogg_opus_timeline.h', 'decoder_pending_input.h'):
            self.freeze(modes.SHARED / name, Path('project/main') / name, 'unchanged public owner headers; wrapper not called')
        for path in (MODES, modes.BASE, modes.base.COMMON, Path(__file__)):
            self.freeze(path, Path('sources/controllers') / path.name, 'reviewed unchanged closure/command helpers')
        for label, folder in (('creator', self.args.reference), ('control', self.args.control), ('parent', self.args.parent)):
            self.freeze(folder / 'report.json', Path('sources') / label / 'report.json', 'exact completed predecessor report')
        table, bodies, offset = [], [], 176
        for name, control in self.control['cases'].items():
            fixture = self.creator['cases'][name]; values = []
            for path in (self.args.reference / fixture['artifacts']['complete.ogg']['path'],
                         self.args.control / control['files']['input.packets']['path'], self.args.control / control['files']['elementary.packets']['path']):
                self.freeze(path, Path('sources/reference') / name / path.name, 'complete original encoded control bytes')
                body = path.read_bytes(); values += [offset, len(body)]; bodies.append(body); offset += len(body)
            values += [2, fixture['creator_decoding']['raw_frames'], 120, fixture['accounting']['packet_samples']]
            table.append(struct.pack('<10I', *values))
            for artifact in control['files'].values():
                path = self.args.control / artifact['path']
                need(sha(path) == artifact['sha256'] and path.stat().st_size == artifact['bytes'], 'exact completed creator control artifact')
                self.freeze(path, Path('sources/creator-control') / artifact['path'], 'independent complete reference; PCM/float stay local')
        blob = self.out / 'project/main/control.bin'; blob.write_bytes(struct.pack('<4I', 0x46434f50, 1, 4, 40) + b''.join(table) + b''.join(bodies))
        self.artifacts[blob.relative_to(self.out).as_posix()] = sha(blob)
        vendor = self.args.vendor; paths = {p for p in vendor.iterdir() if p.is_file()}
        for folder in ('include', 'src'):
            paths.update(p for p in (vendor / folder).rglob('*') if p.is_file())
        paths.update(vendor / 'lib/esp32' / name for name in common.ARCHIVE_PINS)
        for path in sorted(paths):
            self.freeze(path, Path('sources/vendor/esp_audio_codec') / path.relative_to(vendor), 'exact public vendor input')
        common.write_json(self.out / 'source-manifest.json', self.sources)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'reference', 'control', 'parent'):
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--build-timeout', type=int, default=1200)
    parser.add_argument('--qemu-timeout', type=int, default=600)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    for name in ('output', 'reference', 'control', 'parent'):
        setattr(args, name, getattr(args, name).resolve())
    need(sys.platform == 'win32' and args.output.is_relative_to(ROOT / '.build') and not args.output.exists(), 'fresh Windows local native capture')
    creator = json.loads((args.reference / 'report.json').read_bytes()); control = json.loads((args.control / 'report.json').read_bytes())
    parent = json.loads((args.parent / 'report.json').read_bytes())
    need(all(r['passed'] and r['completed'] for r in (creator, control, parent)) and len(control['cases']) == 4 and
         all(r['observations'][-1]['float_unequal_samples'] == 0 for r in control['cases'].values()), 'complete public float cadence equivalence prerequisite')
    need(sha(args.reference / 'report.json') == control['input_creator_report']['sha256'] and
         sha(args.parent / 'report.json') == control['input_native_report']['sha256'], 'exact unchanged predecessor reports')
    for report, folder in ((creator, args.reference), (control, args.control)):
        for row in report['sources']:
            need(sha(ROOT / row['path']) == sha(folder / row['snapshot']) == row['sha256'], 'current exact creator source bytes')
    need(sha(modes.MAIN / 'ogg_playback.h') == modes.WRAPPER_SHA, 'unchanged frozen application header')
    args.idf = REPO / '.idf/v6.0.2'; args.idf_tools = REPO / '.idf/tools-v6.0.2'
    args.idf_python = args.idf_tools / 'python_env/idf6.0_py3.12_env/Scripts/python.exe'
    args.vendor = REPO / '.idf/esp-adf-libs/esp_audio_codec'; args.qemu = ROOT / '.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
    args.rom = Path('C:/Work/QEMU-ESP32/pc-bios'); args.git = Path(shutil.which('git.exe') or shutil.which('git') or '')
    args.powershell = Path(shutil.which('pwsh.exe') or '')
    need(all(path.is_file() for path in (args.idf / 'tools/idf.py', args.idf_python, args.qemu, args.git, args.powershell, PROJECT / 'sdk-build.ps1')), 'installed dependencies only')
    need(sha(args.qemu) == common.QEMU_SHA and all(sha(args.vendor / 'lib/esp32' / name) == digest for name, digest in common.ARCHIVE_PINS.items()), 'pinned emulator and public archives')
    if args.preflight_only:
        print(json.dumps(dict(preflight=True, target_executed=False, cases=24))); return 0
    args.output.mkdir(parents=True); campaign = Campaign(args, creator, control)
    try:
        campaign.save(); campaign.verify_repositories(); campaign.freeze_sources()
        defaults = (args.output / 'project/sdkconfig.common.defaults').read_text()
        (args.output / 'project/sdkconfig.defaults').write_text('CONFIG_IDF_TARGET="esp32"\nCONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_240=y\n# CONFIG_FREERTOS_UNICORE is not set\n' + defaults)
        for path in (args.idf_python, args.qemu, args.git, args.powershell, *args.rom.glob('esp32-v3-rom*.bin')):
            campaign.bind_runtime(path)
        print('FROZEN public raw-control sources; starting SDK build', flush=True)
        campaign.run_command('build', [args.powershell, '-NoProfile', '-NonInteractive', '-File', args.output / 'project/sdk-build.ps1',
            '-Campaign', args.output, '-SdkDirectory', args.idf, '-ToolsDirectory', args.idf_tools, '-PythonExecutable', args.idf_python, '-Target', 'esp32'], args.build_timeout)
        flash = campaign.qualify(); print('SDK terminal zero; starting public raw Opus control', flush=True)
        log = campaign.run_command('qemu', [args.qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet', '-smp', '2', '-L', args.rom,
            '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic', 'none',
            '-drive', 'file=' + str(flash) + ',if=mtd,format=raw'], args.qemu_timeout)
        campaign.report['measurements'] = parse_log(log + '\n' + (args.output / 'qemu.stderr.log').read_text(errors='replace'), creator, control, parent, args)
        need(campaign.verify_inputs(), 'all consumed source/runtime/artifact bytes unchanged')
        campaign.report.update(passed=True, completed=True)
        print(json.dumps(dict(passed=True, diagnostic_only=True, cases=24, reported_refusals=campaign.report['measurements']['reported_refusals'],
                             geometry_gaps=campaign.report['measurements']['geometry_gaps'])))
        return 0
    except Exception as error:
        campaign.report.update(passed=False, completed=False, failure_type=type(error).__name__, failure=str(error))
        print(json.dumps(dict(passed=False, failure=str(error)))); return 1
    finally:
        campaign.save()


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
