"""Compare complete all-codec CPU/audio windows without hiding failed gates."""
import argparse
import json
from pathlib import Path
import re

from summarize_radio_flac import cpu_intervals, cpu_summary


def summarize(folder):
    report = json.loads((folder/'report.json').read_text())
    rows = json.loads((folder/'performance.json').read_text())
    batches = json.loads((folder/'status.json').read_text())
    cases = []
    for batch in batches:
        if not batch['case'].startswith('load:'):
            continue
        start, end = batch['started_at']+10, batch['ended_at']
        windows, malformed, gaps = cpu_intervals(rows, start, end)
        cpu = cpu_summary(windows)
        decoded = []
        for row in rows:
            match = re.search(r'PERF (AAC|MP3|FLAC|OGG): window (\d+) ms, audio (\d+) ms, decode (\d+) ms', row['line'])
            if not match:
                continue
            codec, window, audio, decode = match.groups()
            window, audio, decode = map(int, (window, audio, decode))
            if start <= row['at']-window/1000 and row['at'] <= end:
                decoded.append(dict(codec=codec, window=window, audio=audio, decode=decode))
        wall = sum(d['window'] for d in decoded)
        audio = sum(d['audio'] for d in decoded)
        elapsed = sum(d['decode'] for d in decoded)
        ratio = audio/wall if wall else None
        name = batch['case'].split(':', 1)[1]
        original = next(c for c in report['cases'] if c['name'] == 'cpu-under-http-load:'+name)
        cases.append(dict(name=name, original=original, cpu=cpu, cpu_malformed=malformed,
            cpu_gaps=gaps, decoder_windows=decoded, audio_wall_ratio=ratio,
            elapsed_decode_ms_per_audio_second=elapsed*1000/audio if audio else None,
            estimated_decoder_cpu_ms_per_audio_second=(
                cpu['decode_mean_percent']*10/ratio if ratio and 'decode_mean_percent' in cpu else None),
            minimum_rssi=min(s['rssi'] for s in batch['samples']),
            maximum_http_ms=max(s['request_ms'] for s in batch['samples'])))
    return dict(image=report['board']['app_elf_sha256'], priority=report['output_priority'],
        cases=cases, original_checks=report['cases'])


def compare(control, candidate):
    reports = [json.loads((p/'report.json').read_text()) for p in (control, candidate)]
    if reports[0]['fixture_hashes'] != reports[1]['fixture_hashes'] or reports[0]['load_seconds'] != reports[1]['load_seconds']:
        raise ValueError('Different fixture hashes or load duration')
    result = dict(control=summarize(control), candidate=summarize(candidate),
        note='Independent complete CPU/audio windows after 10 s warm-up. Wall decode time includes preemption. '
             'Original thresholds and verdicts retained; short tests do not prove acoustic or one-hour stability.')
    if [c['name'] for c in result['control']['cases']] != [c['name'] for c in result['candidate']['cases']]:
        raise ValueError('Different load cases/order')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--control', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = compare(args.control, args.candidate)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    for before, after in zip(result['control']['cases'], result['candidate']['cases']):
        print(before['name'], 'CPU', before['cpu'].get('busy_mean_percent'), after['cpu'].get('busy_mean_percent'),
              'audio/wall', before['audio_wall_ratio'], after['audio_wall_ratio'],
              'gates', before['original']['result'], after['original']['result'])
