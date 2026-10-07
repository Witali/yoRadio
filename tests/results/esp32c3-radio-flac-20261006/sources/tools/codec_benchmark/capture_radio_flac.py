"""Capture finite public broadcasts and make matched FLAC LPC32/LPC12 files.

Audio stays in a caller-selected local directory (normally ignored .build).
Preserve native sample rate/channels; use 24-bit PCM as the common input.
LPC32 is allowed, never forced. Both variants use FFmpeg compression level 12.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import urlsplit
from urllib.request import urlopen


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public(url):
    value = urlsplit(url)
    if value.scheme != 'https' or not value.hostname or value.username or value.password or value.query or value.fragment:
        raise ValueError('Expected public credential-free HTTPS URL')
    return url


def command(args, log, timeout):
    with log.open('wb') as output:
        result = subprocess.run(args, stdout=output, stderr=subprocess.STDOUT, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'Command failed ({result.returncode}); see {log.name}')


def capture(station, folder, seconds):
    started = datetime.now(timezone.utc).isoformat()
    with urlopen(public(station['playlist']), timeout=20) as response:
        playlist = response.read(65536).decode('utf-8')
    candidates = re.findall(r'^File\d+=(https://\S+)\s*$', playlist, re.M)
    if not candidates:
        raise ValueError('Playlist contains no secure public stream')
    record = dict(station=station, started_utc=started, attempts=[])
    for index, candidate in enumerate(candidates[:3]):
        url = public(candidate)
        target = folder / f"{station['id']}-capture-{index}.aac"
        args = ['ffmpeg', '-n', '-hide_banner', '-nostdin', '-loglevel', 'warning',
                '-rw_timeout', '20000000', '-tls_verify', '1', '-icy', '0', '-i', url,
                '-t', str(seconds), '-map', '0:a:0', '-vn', '-c:a', 'copy', '-f', 'adts', str(target)]
        attempt = dict(url=url, command=args)
        record['attempts'].append(attempt)
        try:
            command(args, folder / f"{station['id']}-capture-{index}.log", seconds+60)
            probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
                'stream=codec_name,profile,sample_rate,channels', '-of', 'json', str(target)]))['streams'][0]
            record.update(file=target.name, sha256=sha(target), probe=probe, ended_utc=datetime.now(timezone.utc).isoformat())
            attempt['result'] = 'PASS'
            (folder / f"{station['id']}-capture.json").write_text(json.dumps(record, indent=2)+'\n')
            return record
        except (RuntimeError, subprocess.SubprocessError) as error:
            attempt.update(result='FAIL', error=str(error))
            (folder / f"{station['id']}-capture.json").write_text(json.dumps(record, indent=2)+'\n')
    raise RuntimeError(f"No complete capture for {station['id']}")


def encode(record, folder, seconds):
    station = record['station']['id']
    source = folder / record['file']
    pcm = folder / f'{station}-source24.wav'
    command(['ffmpeg','-n','-hide_banner','-nostdin','-v','error','-xerror','-i',str(source),
             '-t',str(seconds),'-map','0:a:0','-map_metadata','-1','-c:a','pcm_s24le',str(pcm)],
            folder / f'{station}-pcm.log', 120)
    reference = subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(pcm),
                                         '-f','s16le','-acodec','pcm_s16le','-'])
    source_info = record['probe']
    channels, rate = int(source_info['channels']), int(source_info['sample_rate'])
    actual_seconds = len(reference) / (channels * rate * 2)
    if actual_seconds < seconds - .05:
        raise ValueError(f'{station}: truncated capture ({actual_seconds}s)')
    results = []
    # Same level, precision and channel search; only the maximum LPC order differs.
    for order in (32, 12):
        name = f'radio-{station}-lpc{order}'
        path = folder / (name+'.flac')
        options = ['-c:a','flac','-compression_level','12','-max_prediction_order',str(order),
                   '-sample_fmt','s32','-bits_per_raw_sample','24']
        command(['ffmpeg','-n','-hide_banner','-nostdin','-v','error','-i',str(pcm),
                 '-map_metadata','-1',*options,str(path)], folder / (name+'-encode.log'), 300)
        decoded = subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(path),
                                          '-f','s16le','-acodec','pcm_s16le','-'])
        # Also compare full 24-bit PCM, not just the firmware's 16-bit output.
        raw24 = subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(pcm),'-f','s24le','-'])
        flac24 = subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','s24le','-'])
        if decoded != reference or raw24 != flac24:
            raise ValueError('Lossless encode round trip differs')
        results.append(dict(name=name, file=path.name, station=station, codec='flac', profile='flac',
            mime='audio/flac', rate=rate, channels=channels, bits=24, seconds=actual_seconds,
            max_lpc_order=order, encoder_options=options, sha256=sha(path), bytes=path.stat().st_size,
            pcm_sha256=hashlib.sha256(reference).hexdigest(), pcm_bytes=len(reference),
            pcm24_sha256=hashlib.sha256(raw24).hexdigest(), pcm24_bytes=len(raw24),
            source_capture_sha256=record['sha256']))
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', type=Path, default=Path(__file__).with_name('radio_flac_sources.json'))
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--seconds', type=int, default=120)
    p.add_argument('--jobs', type=int, default=5)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    sources = json.loads(args.sources.read_text())
    report = dict(sources=sources, seconds=args.seconds,
        ffmpeg=subprocess.check_output(['ffmpeg','-version'], text=True).splitlines()[0],
        generator_sha256=sha(Path(__file__)), captures=[], fixtures=[], failures=[])
    def save():
        (args.output/'manifest.json').write_text(json.dumps(report, indent=2)+'\n')
    save()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        tasks = {pool.submit(capture, s, args.output, args.seconds): s for s in sources['stations']}
        for task in as_completed(tasks):
            station = tasks[task]
            try:
                result = task.result()
                report['captures'].append(result)
                print('Captured', station['id'], flush=True)
            except Exception as error:
                report['failures'].append(dict(station=station['id'], stage='capture', error=str(error)))
                print('Capture failed', station['id'], type(error).__name__, flush=True)
            save()
    with ThreadPoolExecutor(max_workers=min(args.jobs, 3)) as pool:
        tasks = {pool.submit(encode, c, args.output, args.seconds): c for c in report['captures']}
        for task in as_completed(tasks):
            station = tasks[task]['station']['id']
            try:
                report['fixtures'].extend(task.result())
                print('Encoded pair', station, flush=True)
            except Exception as error:
                report['failures'].append(dict(station=station, stage='encode', error=str(error)))
                print('Encode failed', station, type(error).__name__, flush=True)
            save()
    positions = {s['id']: i for i,s in enumerate(sources['stations'])}
    report['captures'].sort(key=lambda c: positions[c['station']['id']])
    report['fixtures'].sort(key=lambda c: (positions[c['station']], -c['max_lpc_order']))
    save()
    return bool(report['failures']) or len(report['fixtures']) != 2*len(sources['stations'])


if __name__ == '__main__':
    raise SystemExit(main())
