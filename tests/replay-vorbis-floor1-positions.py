"""Retrospective floor1 evidence replay: read bytes only, never run a decoder.

The original reference NONPASS is retained. Header decisions and complete saved
target/Xiph PCM comparisons are separate finite results;2LSB is a project bound.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
BOUND = 2
DECODERS = ('vorbis', 'libvorbis')
INVALIDDATA = (-1094995529, 3199971767)


def need(ok, reason):
    if not ok: raise ValueError(reason)


def digest(data): return hashlib.sha256(data).hexdigest()


def safe(base, relative):
    path = (base/relative.replace('\\', '/')).resolve()
    need(path.is_relative_to(base), 'recorded path escapes evidence directory')
    return path


def metrics(a, b):
    need(len(a) == len(b) and len(a) % 2 == 0, 'equal complete PCM16 vectors')
    differences = [abs(x[0]-y[0]) for x, y in zip(struct.iter_unpack('<h', a), struct.iter_unpack('<h', b))]
    return dict(samples=len(differences), max_abs_error=max(differences, default=0),
                over_bound=sum(d > BOUND for d in differences), allowed=BOUND)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference-report', type=Path, required=True)
    p.add_argument('--target-report', type=Path, action='append', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); out = a.output.resolve(); build = (ROOT/'.build').resolve()
    reports = [a.reference_report.resolve()] + [x.resolve() for x in a.target_report]
    need(build.parent == ROOT and out != build and out.is_relative_to(build) and not out.exists(), 'fresh .build output')
    need(len(set(reports)) == len(reports) and all(x.is_relative_to(build) and not out.is_relative_to(x.parent) for x in reports), 'report/output boundary')
    out.mkdir(parents=True)
    r = dict(schema='floor1-retrospective-replay-v1', completed=False, passed=False,
             dual_reference_qualified=False, full_numeric_qualified=False, full_G6_qualified=False,
             target_executed=False, decoder_executed=False, production_changed=False,
             xiph_header_qualified=False, predeclared_max_abs_error=BOUND, inputs={}, tools={}, cases=[], targets=[], scope=__doc__)
    def save(): (out/'report.json').write_text(json.dumps(r, indent=2)+'\n', encoding='utf-8')
    def freeze(path):
        path = Path(path).resolve(); need(path.is_relative_to(ROOT), 'input outside checkout')
        data = path.read_bytes(); key = str(path)
        if key not in r['inputs']:
            dest = out/'sources'/path.relative_to(ROOT); dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open('xb') as stream: stream.write(data)
            r['inputs'][key] = dict(sha256=digest(data), bytes=len(data), snapshot=dest.relative_to(out).as_posix())
        need(digest(data) == r['inputs'][key]['sha256'], 'evidence changed during replay')
        return data
    def read_report(path):
        report = json.loads(freeze(path)); snapshots = {}
        for original, entry in report['inputs'].items():
            data = freeze(safe(path.parent, entry['snapshot']))
            need(digest(data) == entry['sha256'], 'executed input snapshot digest')
            snapshots[original] = data
        for tool, expected in report['tools'].items():
            present = Path(tool).is_file()
            if present: need(digest(Path(tool).read_bytes()) == expected, 'available recorded tool changed')
            r['tools'][tool] = dict(sha256=expected, currently_available=present, currently_verified=present)
        return report, snapshots
    def logs(report, path, reference):
        result = {}
        for command in report['commands']:
            name = command['name']; need(name not in result, 'duplicate recorded command')
            if reference:
                need(command['state'] == 'terminal' and command['reaped'] and not command.get('forced_stop'), 'reference actual terminal/reap')
            else:
                need(command['state'] == 'complete' and command['exit_status'] == 0, 'target actual command exit0')
            bodies = []
            for kind in ('stdout', 'stderr'):
                data = freeze(safe(path.parent, command.get(kind, name+'.'+kind+'.log')))
                need(digest(data) == command[kind+'_sha256'], 'recorded command log digest')
                bodies.append(data.decode('utf-8', errors='replace').replace('\r\n', '\n'))
            result[name] = (command, *bodies)
        return result
    try:
        save(); freeze(Path(__file__)); reference_path = reports[0]
        ref, ref_inputs = read_report(reference_path); reference_logs = logs(ref, reference_path, True)
        need(ref['result'] == 'NONPASS' and ref['passed'] is False, 'preserve original reference NONPASS')
        r['original_reference'] = dict(path=str(reference_path), sha256=digest(reference_path.read_bytes()), result=ref['result'])
        previous = ref_inputs[str(ROOT/'.build/cyd-vorbis-floor-presence-host-01/report.json')]
        need(digest(previous) == 'e1ac49a4283f37207c5de206946c6f402798f1fda4c78a0c88d825211b18a85b', 'original reference tool provenance')
        ffmpegs = [path for path in ref['tools'] if Path(path).name.lower() == 'ffmpeg.exe']
        need(len(ffmpegs) == 1 and ref['tools'][ffmpegs[0]] == json.loads(previous)['tools'][ffmpegs[0]], 'selected FFmpeg provenance pin')
        manifest_paths = [Path(path) for path in ref_inputs if Path(path).name == 'manifest.json']
        need(len(manifest_paths) == 1, 'one complete recorded corpus'); corpus = manifest_paths[0].parent
        generator = ROOT/'tests/vorbis_format_corpus/generate_floor1_positions.py'
        helper = ROOT/'tests/vorbis_block_matrix/generate_minimal.py'
        manifest = json.loads(ref_inputs[str(corpus/'manifest.json')])
        need(digest(freeze(generator)) == manifest['generator_sha256'] and digest(freeze(helper)) == manifest['helper']['sha256'], 'canonical pure construction source pins')
        need(ref_inputs[str(generator)] == generator.read_bytes() and ref_inputs[str(helper)] == helper.read_bytes(), 'recorded generator/helper bytes')
        spec = importlib.util.spec_from_file_location('floor1_replay_pure_construction', generator)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        expected = module.payloads()  # Pure construction only, never a decoder.
        need(all(ref_inputs[str(corpus/name)] == data for name, data in expected.items()), 'full canonical corpus bytes')
        matrix = json.loads(expected['matrix.json']); cases = matrix['cases']
        need(len(cases) == 14 and [c['expected_valid'] for c in cases] == [True]*8+[False]*6, 'complete14 cases')
        need([(c['index'],c['id'],c['expected_valid']) for c in ref['cases']] == [(i,c['id'],c['expected_valid']) for i,c in enumerate(cases)], 'complete ordered reference case declarations')
        info = expected['identification.bin']
        need(info[:7] == b'\x01vorbis' and info[11] == 2 and int.from_bytes(info[12:16], 'little') == 48000 and info[28] == 0xb8, 'actual stereo48k/S256L2048 header')
        need(set(reference_logs) == {f'case-{i:02d}-{d}' for i in range(14) for d in DECODERS}, 'all28 actual reference commands')
        xiph_pcm = {}; native_pcm = {}
        tool_error = re.compile(r'Unknown decoder|Decoder .*not found|Unrecognized option|No such file or directory|Permission denied|Error writing', re.I)
        codec_error = re.compile(r'\[(?:lib)?vorbis @ [^]]+\].*(?:header damaged|header.*corrupt|Duplicate value|rangebits value|Floor value)|Error while opening decoder: Invalid data found', re.I)
        for i, case in enumerate(cases):
            row = dict(index=i, id=case['id'], expected_valid=case['expected_valid'], decoders={}); r['cases'].append(row)
            for decoder in DECODERS:
                name = f'case-{i:02d}-{decoder}'; command, stdout, stderr = reference_logs[name]
                argv = command['argv']; need(argv[0] == ffmpegs[0] and argv.index('-c:a') < argv.index('-i') and argv[argv.index('-c:a')+1] == decoder, 'explicit pinned input decoder')
                need(not any(x in argv for x in ('-ar', '-ac', '-af', '-filter:a', '-ss', '-t', '-to')), 'unaltered reference PCM route')
                wav = reference_path.parent/(name+'.wav'); pcm = b''; meta = None
                if wav.exists():
                    freeze(wav)
                    with wave.open(str(wav), 'rb') as w:
                        meta = [w.getnchannels(), w.getframerate(), w.getsampwidth(), w.getnframes(), w.getcomptype()]
                        pcm = w.readframes(w.getnframes())
                    need(meta == [2, 48000, 2, 7040, 'NONE'] and len(pcm) == 28160 and any(pcm), 'complete stereo48k S16 reference WAV')
                rc = command['returncode']; error = codec_error.search(stderr)
                rejection = rc in (1, *INVALIDDATA) and error is not None and not tool_error.search(stderr) and not wav.exists() and not wav.with_suffix('.s16le').exists()
                output_error = stderr.find('Error opening output')
                if output_error >= 0: rejection = rejection and error is not None and output_error > error.start()
                decoded = rc == 0 and len(pcm) == 28160
                fact = dict(returncode=rc, decoded=decoded, codec_rejection=bool(rejection), pcm_bytes=len(pcm), pcm_sha256=digest(pcm), metadata=meta,
                            decision_matches_spec=decoded if i < 8 else bool(rejection), stderr=stderr)
                row['decoders'][decoder] = fact
                need(decoded or rejection, 'unclassified decoder/tool/crash outcome')
                if decoded:
                    recorded = ref['cases'][i]['decoded'][decoder]
                    need(recorded['pcm_sha256'] == digest(pcm), 'original recorded reference PCM digest')
                    if i < 8:
                        need(freeze(safe(reference_path.parent, recorded['pcm_path'])) == pcm, 'saved raw reference PCM')
                        (xiph_pcm if decoder == 'libvorbis' else native_pcm)[i] = pcm
            if i in xiph_pcm and i in native_pcm:
                row['cross_reference'] = metrics(xiph_pcm[i], native_pcm[i])
                need(row['cross_reference'] == ref['cases'][i]['cross_reference'], 'preserved original numeric outcomes')
        r['xiph_header_qualified'] = all(x['decoders']['libvorbis']['decision_matches_spec'] for x in r['cases'])
        need(len(xiph_pcm) == 8, 'complete eight Xiph PCM vectors')
        seen_targets = set()
        for target_path in reports[1:]:
            target, snapshots = read_report(target_path); target_logs = logs(target, target_path, False)
            platform = target['target']; need(platform in ('esp32', 'esp32c3') and platform not in seen_targets, 'distinct supported target')
            seen_targets.add(platform); core = 1 if platform == 'esp32' else 0
            need(target['completed'] and target['passed'] and target['control'] is None and target['result'] == 'FINITE_MATRIX_PASSED', 'complete target acceptance')
            need(target['corpus_manifest_sha256'] == digest(expected['manifest.json']), 'target manifest identity')
            need(all(snapshots[str(corpus/name)] == data for name, data in expected.items()), 'target full canonical corpus snapshot')
            main = ROOT/'tests/target/vorbis_floor1_positions_qemu/main/main.c'
            need(snapshots[str(main)] == freeze(main), 'canonical target metadata assertion source')
            need(all(token in snapshots[str(main)] for token in (b'a_info.sample_rate==48000 && b_info.sample_rate==48000', b'a_info.channel==2 && b_info.channel==2', b'a_info.bits_per_sample==16 && b_info.bits_per_sample==16', b'"public_metadata"')), 'bound metadata assertion')
            elf_names = [name for name in target['build_outputs'] if name.endswith('.elf')]
            need(len(elf_names) == 1, 'one recorded target ELF'); elf = freeze(safe(target_path.parent, elf_names[0]))
            need(digest(elf) == target['build_outputs'][elf_names[0]] and elf[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', elf, 18)[0] == (94 if core else 243), 'actual ELF machine')
            config = freeze(target_path.parent/'sdkconfig')
            need(digest(config) == target['build_outputs']['sdkconfig'] and (b'CONFIG_FREERTOS_UNICORE=y' in config) == (core == 0), 'recorded target core configuration')
            need(target['elf_machine'] == (94 if core else 243) and target['observed']['summary'] == ['8','6','112','225280',str(core)], 'target report architecture/summary')
            command, log, stderr = target_logs['qemu']
            need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|FLOOR1_FAILURE', log+stderr), 'target panic or semantic failure')
            need(re.findall(r'^FLOOR1_START coordinator=0 decoder=(\d+)$', log, re.M) == [str(core)] and log.count('FLOOR1_CONTROLLED_STOP') == 1, 'task cores/controlled terminal')
            need(re.findall(r'^FLOOR1_COMPLETE accepted=(\d+) rejected=(\d+) packets=(\d+) pcm=(\d+) core=(\d+)$', log, re.M) == [('8','6','112','225280',str(core))], 'target complete summary')
            need(re.findall(r'^FLOOR1_ACCEPT case=(\d+) name=(\S+) packets=14 pcm=28160 original_exact=1 core=(\d+)$', log, re.M) == [(str(i),cases[i]['id'],str(core)) for i in range(8)], 'all eight accepted original-exact cases')
            need(re.findall(r'^FLOOR1_REJECT case=(\d+) name=(\S+) result=-1 handle=0 core=(\d+)$', log, re.M) == [(str(i),cases[i]['id'],str(core)) for i in range(8,14)], 'all six rejected cases')
            opens = re.findall(r'^FLOOR1_OPEN case=(\d+) result=(-?\d+) handle=([01])$', log, re.M)
            need(opens == [(str(i),'0','1') if i < 8 else (str(i),'-1','0') for i in range(14)], 'exact public open outcomes')
            rows = re.findall(r'^FLOOR1_PCM case=(\d+) packet=(\d+) consumed=(\d+) bytes=(\d+) hex=([0-9a-f]*)$', log, re.M)
            need([(int(x[0]),int(x[1])) for x in rows] == [(i,j) for i in range(8) for j in range(14)], 'complete ordered112 PCM prefix')
            pins = {}
            for name, value in target['observed']['pcm'].items():
                normalized = name.replace('\\','/'); need(normalized not in pins, 'PCM key collision'); safe(target_path.parent, normalized); pins[normalized] = value
            need(set(pins) == {f'pcm/{i}.s16le' for i in range(8)}, 'exact raw eight PCM files')
            fact = dict(target=platform, report_sha256=digest(target_path.read_bytes()), core=core, metadata_assertion_coverage='Frozen canonical target asserts stereo48000Hz/S16 before every published PCM record; values are not separate telemetry.', pcm_bytes=0, cases=[])
            r['targets'].append(fact)
            for i in range(8):
                packets = []; comparisons = []; offset = 0
                for j, entry in enumerate(rows[i*14:(i+1)*14]):
                    pcm = bytes.fromhex(entry[4]); size = cases[i]['expected_packet_bytes'][j]
                    need(int(entry[2]) == matrix['offsets'][j+1]-matrix['offsets'][j] and int(entry[3]) == len(pcm) == size, 'each packet consumption/PCM size')
                    comparisons.append(dict(packet=j, **metrics(pcm, xiph_pcm[i][offset:offset+size]))); offset += size; packets.append(pcm)
                raw = b''.join(packets); saved = freeze(target_path.parent/f'pcm/{i}.s16le')
                need(len(raw) == 28160 and raw == saved and digest(raw) == pins[f'pcm/{i}.s16le'], 'full transcript/raw PCM/hash equality')
                fact['pcm_bytes'] += len(raw); fact['cases'].append(dict(index=i, raw_sha256=digest(raw), **metrics(raw,xiph_pcm[i]), packets=comparisons))
            need(fact['pcm_bytes'] == 225280, 'full225280 target PCM bytes')
            fact['xiph_pcm_qualified'] = all(not c['over_bound'] for c in fact['cases']); save()
        for path, entry in r['inputs'].items():
            need(digest(Path(path).read_bytes()) == entry['sha256'] == digest((out/entry['snapshot']).read_bytes()), 'replay evidence changed')
        for path, entry in r['tools'].items():
            if entry['currently_available']: need(digest(Path(path).read_bytes()) == entry['sha256'], 'available tool changed during replay')
        r.update(completed=True, result='ANALYSIS_COMPLETE_OVERALL_NONPASS', limitations='Read-only retrospective qualification of saved evidence. Native wide refusal/count acceptance/short-endpoint numeric failures remain. No runtime replay, QMP claim, full dependency closure, radio, hardware or full G6 qualification.')
        save(); print(json.dumps(dict(completed=True, passed=False, xiph_header_qualified=r['xiph_header_qualified'], targets=[dict(target=x['target'],xiph_pcm_qualified=x['xiph_pcm_qualified']) for x in r['targets']]))); return 0
    except BaseException as exc:
        r.update(completed=False, error=repr(exc), result='REPLAY_INCOMPLETE_NONPASS'); save(); raise


if __name__ == '__main__': sys.exit(main())
