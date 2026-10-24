"""Finite floor1 host reference qualification; no SDK, target or radio execution.

Both named FFmpeg decoders process every carrier. Optional saved target PCM is
compared sample-for-sample under the predeclared project bound of2 LSB, without
alignment, gain, resampling or trimming. This does not establish full Vorbis/G6.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
import wave

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT / '.build/cyd-vorbis-floor-presence-host-01/report.json'
PREVIOUS_SHA = 'e1ac49a4283f37207c5de206946c6f402798f1fda4c78a0c88d825211b18a85b'
BOUND = 2  # Project PCM16 qualification policy, not a normative Vorbis tolerance.
DECODERS = ('vorbis', 'libvorbis')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def need(ok, message):
    if not ok: raise ValueError(message)


def compare(a, b):
    need(len(a) == len(b) == 28160, 'complete equally-sized PCM required')
    errors = [abs(x[0] - y[0]) for x, y in zip(struct.iter_unpack('<h', a), struct.iter_unpack('<h', b))]
    return dict(samples=len(errors), max_abs_error=max(errors),
                over_bound=sum(e > BOUND for e in errors), allowed=BOUND)


def wav_pcm(path):
    if not path.exists(): return b'', None
    with wave.open(str(path), 'rb') as w:
        meta = dict(channels=w.getnchannels(), sample_rate=w.getframerate(),
                    sample_bytes=w.getsampwidth(), frames=w.getnframes(), compression=w.getcomptype())
        pcm = w.readframes(w.getnframes())
        need(len(pcm) == meta['frames'] * meta['channels'] * meta['sample_bytes'], 'complete WAV data')
        return pcm, meta


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--corpus', type=Path, required=True)
    p.add_argument('--ffmpeg', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--target-report', type=Path, action='append', default=[])
    a = p.parse_args(); corpus, ffmpeg, out = a.corpus.resolve(), a.ffmpeg.resolve(), a.output.resolve()
    build = (ROOT / '.build').resolve()
    need(build.parent == ROOT and out != build and out.is_relative_to(build) and not out.exists(), 'fresh .build output required')
    need(corpus.is_relative_to(build) and corpus.is_dir() and not out.is_relative_to(corpus)
         and not corpus.is_relative_to(out), 'corpus/output boundary')
    targets = [x.resolve() for x in a.target_report]
    need(len(set(targets)) == len(targets) and all(not out.is_relative_to(x.parent) for x in targets), 'target/output boundary')
    out.mkdir(parents=True)
    r = dict(schema='floor1-positions-reference-v1', completed=False, passed=False,
             dual_reference_qualified=False, target_pcm_qualified=False, target_executed=False,
             full_G6_qualified=False, production_changed=False, scope=__doc__, max_abs_error_allowed=BOUND,
             inputs={}, tools={}, commands=[], cases=[], targets=[], failures=[])
    pcm_by_case = {}
    def save(): (out/'report.json').write_text(json.dumps(r, indent=2)+'\n', encoding='utf-8')
    def freeze(path):
        path = Path(path).resolve(); need(path.is_relative_to(ROOT), 'frozen input outside checkout')
        data = path.read_bytes(); digest = hashlib.sha256(data).hexdigest()
        if str(path) not in r['inputs']:
            dest = out/'sources'/path.relative_to(ROOT); dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open('xb') as stream: stream.write(data)
            r['inputs'][str(path)] = dict(sha256=digest, bytes=len(data), snapshot=dest.relative_to(out).as_posix())
        need(digest == r['inputs'][str(path)]['sha256'], 'input changed while freezing')
        return data
    def current():
        need(all(sha(path) == row['sha256'] == sha(out/row['snapshot']) for path, row in r['inputs'].items()), 'input changed')
        need(all(sha(path) == digest for path, digest in r['tools'].items()), 'selected tool changed')
    def run(name, argv):
        current(); so, se = out/(name+'.stdout.log'), out/(name+'.stderr.log')
        row = dict(name=name, argv=list(map(str, argv)), cwd=str(out), state='starting',
                   stdout=so.name, stderr=se.name)
        r['commands'].append(row); save(); child = None; start = time.monotonic()
        try:
            with so.open('xb') as stdout, se.open('xb') as stderr:
                child = subprocess.Popen(row['argv'], cwd=out, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                row['pid'] = child.pid; save()
                try:
                    child.wait(timeout=30); row.update(state='terminal', returncode=child.returncode)
                except subprocess.TimeoutExpired:
                    row['state'] = 'timeout_nonpass'
        except Exception as exc:
            row.update(state='tool_error_nonpass', error=repr(exc))
        finally:
            if child is not None and child.poll() is None:
                child.kill(); child.wait(timeout=5); row['forced_stop'] = True
            row.update(elapsed_seconds=time.monotonic()-start, reaped=child is not None and child.poll() is not None,
                stdout_sha256=sha(so) if so.exists() else None, stderr_sha256=sha(se) if se.exists() else None)
            save()
        return row, se.read_text(encoding='utf-8', errors='replace') if se.exists() else ''
    try:
        save(); need(sha(PREVIOUS) == PREVIOUS_SHA, 'pinned reference provenance report changed')
        previous = json.loads(freeze(PREVIOUS))
        pins = {Path(path).resolve(): digest for path, digest in previous['tools'].items()}
        need(ffmpeg.name.lower() == 'ffmpeg.exe' and ffmpeg in pins and sha(ffmpeg) == pins[ffmpeg], 'pinned FFmpeg executable required')
        r['tools'] = {str(ffmpeg): sha(ffmpeg), str(Path(sys.executable).resolve()): sha(sys.executable)}
        freeze(Path(__file__))
        generator = ROOT/'tests/vorbis_format_corpus/generate_floor1_positions.py'
        helper = ROOT/'tests/vorbis_block_matrix/generate_minimal.py'
        manifest = json.loads(freeze(corpus/'manifest.json'))
        need(manifest['generator_sha256'] == hashlib.sha256(freeze(generator)).hexdigest(), 'corpus generator identity')
        need(manifest['helper']['sha256'] == hashlib.sha256(freeze(helper)).hexdigest(), 'corpus helper identity')
        names = [row['path'] for row in manifest['files']]
        need(len(names) == len(set(names)), 'duplicate manifest body')
        for row in manifest['files']:
            path = (corpus/row['path']).resolve(); need(path.is_relative_to(corpus), 'corpus body escape')
            data = freeze(path)
            need(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], 'corpus body identity')
        need({x.relative_to(corpus).as_posix() for x in corpus.rglob('*') if x.is_file()} == set(names)|{'manifest.json'}, 'corpus file closure')
        matrix = json.loads(freeze(corpus/'matrix.json')); cases = matrix['cases']
        need(len(cases) == 14 and [c['expected_valid'] for c in cases] == [True]*8+[False]*6, 'complete14 case validity')
        need(matrix['expected_valid_pcm_bytes'] == 225280 and len({c['id'] for c in cases}) == 14, 'finite corpus accounting')
        r['corpus_manifest_sha256'] = sha(corpus/'manifest.json')
        environment_error = re.compile(r'Unknown decoder|Decoder .*not found|Unrecognized option|Option .*not found|'
            r'No such file or directory|Permission denied|Error opening output|Error writing|Unable to find.*output format', re.I)
        for index, case in enumerate(cases):
            item = dict(index=index, id=case['id'], expected_valid=case['expected_valid'], decoded={})
            r['cases'].append(item)
            for decoder in DECODERS:
                name = f'case-{index:02d}-{decoder}'; wav = out/(name+'.wav')
                row, stderr = run(name, [ffmpeg, '-nostdin', '-n', '-hide_banner', '-loglevel', 'error', '-xerror',
                    '-c:a', decoder, '-i', corpus/case['ogg'], '-map', '0:a:0', '-map_metadata', '-1',
                    '-fflags', '+bitexact', '-flags:a', '+bitexact', '-c:a', 'pcm_s16le', '-f', 'wav', wav])
                result = dict(command=name, qualified=False, stderr_excerpt=stderr[:2000])
                item['decoded'][decoder] = result
                try:
                    need(row['state'] == 'terminal' and row['reaped'] and not row.get('forced_stop'), 'actual bounded terminal required')
                    need(not environment_error.search(stderr), 'tool/configuration/output error is not codec rejection')
                    pcm, meta = wav_pcm(wav)
                    result.update(wav_sha256=sha(wav) if wav.exists() else None, pcm_bytes=len(pcm), metadata=meta,
                                  pcm_sha256=hashlib.sha256(pcm).hexdigest())
                    if case['expected_valid']:
                        need(row['returncode'] == 0, 'valid carrier decode refused')
                        need(meta == dict(channels=2, sample_rate=48000, sample_bytes=2, frames=7040, compression='NONE'), 'unaltered stereo48k S16 metadata')
                        need(len(pcm) == 28160 and any(pcm), 'complete nonzero valid PCM')
                        path = out/(name+'.s16le'); path.write_bytes(pcm)
                        result['pcm_path'] = path.relative_to(out).as_posix(); pcm_by_case[index, decoder] = pcm
                    else:
                        need(type(row['returncode']) is int and 0 < row['returncode'] <= 255 and stderr.strip() and not pcm,
                             'invalid carrier requires real decoder rejection and zero PCM')
                    result['qualified'] = True
                except Exception as exc:
                    result['error'] = repr(exc); r['failures'].append(dict(case=index, decoder=decoder, error=repr(exc)))
                save()
        for index in range(8):
            if all((index, d) in pcm_by_case for d in DECODERS):
                metric = compare(*(pcm_by_case[index, d] for d in DECODERS))
                r['cases'][index]['cross_reference'] = metric
                if metric['over_bound']: r['failures'].append(dict(case=index, error='cross-reference project2LSB bound'))
        r['dual_reference_qualified'] = not r['failures'] and len(pcm_by_case) == 16 and len(r['commands']) == 28
        for report_path in targets:
            target = json.loads(freeze(report_path)); folder = report_path.parent
            need(target['completed'] and target['passed'] and target['control'] is None, 'completed target acceptance required')
            need(target['corpus_manifest_sha256'] == r['corpus_manifest_sha256'], 'target corpus manifest binding')
            core = '1' if target['target'] == 'esp32' else '0'
            need(target['target'] in ('esp32', 'esp32c3') and target['observed']['summary'] == ['8', '6', '112', '225280', core], 'target complete finite summary')
            fact = dict(report=str(report_path), report_sha256=sha(report_path), target=target['target'], inputs={}, pcm={}, comparisons=[])
            r['targets'].append(fact)
            # Verify every advertised target corpus snapshot, never importing its runner.
            for path in (corpus/'manifest.json', *(corpus/name for name in names)):
                entry = target['inputs'][str(path.resolve())]; snapshot = (folder/entry['snapshot']).resolve()
                need(snapshot.is_relative_to(folder), 'target snapshot boundary')
                need(sha(path) == entry['sha256'] == hashlib.sha256(freeze(snapshot)).hexdigest(), 'target corpus input identity')
                fact['inputs'][str(path)] = entry['sha256']
            pcm_pins = {}
            for original, digest in target['observed']['pcm'].items():
                name = original.replace('\\', '/')
                need(name not in pcm_pins, 'normalized target PCM key collision')
                need((folder/name).resolve().is_relative_to(folder), 'target PCM path escape')
                pcm_pins[name] = digest
            need(set(pcm_pins) == {f'pcm/{i}.s16le' for i in range(8)}, 'full exact target PCM set')
            total = 0
            for index in range(8):
                name = f'pcm/{index}.s16le'; path = folder/name; pcm = freeze(path)
                need(sha(path) == pcm_pins[name] and len(pcm) == 28160 and any(pcm), 'target full raw PCM identity')
                fact['pcm'][name] = dict(bytes=len(pcm), sha256=sha(path)); total += len(pcm)
                for decoder in DECODERS:
                    need((index, decoder) in pcm_by_case, 'target comparison needs complete reference PCM')
                    metric = compare(pcm, pcm_by_case[index, decoder]); fact['comparisons'].append(dict(case=index, decoder=decoder, **metric))
                    if metric['over_bound']: r['failures'].append(dict(target=target['target'], case=index, decoder=decoder, error='target project2LSB bound'))
            need(total == 225280, 'full target225280 byte count'); fact['pcm_bytes'] = total; save()
        current()
        r['target_pcm_qualified'] = bool(targets) and r['dual_reference_qualified'] and not r['failures']
        r.update(completed=not r['failures'], passed=not r['failures'],
                 result='FINITE_REFERENCE_QUALIFIED' if not r['failures'] else 'NONPASS',
                 limitations='Finite floor1 corpus only. Saved target PCM replay is not target execution. No full dependency, radio, Ogg adapter, physical or full G6 acceptance.')
        save(); print(json.dumps({k:r[k] for k in ('completed', 'passed', 'dual_reference_qualified', 'target_pcm_qualified', 'result')}))
        return 0 if r['passed'] else 1
    except BaseException as exc:
        r.update(completed=False, passed=False, dual_reference_qualified=False, target_pcm_qualified=False, result='NONPASS', error=repr(exc))
        save(); raise


if __name__ == '__main__': sys.exit(main())
