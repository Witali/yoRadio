"""Time-weighted CPU saturation and LPC-order statistics for paired radio files.

CPU windows are about five seconds, not instantaneous peaks. Decoder task CPU,
elapsed FLAC call time and LPC order are deliberately reported separately.
"""
import argparse
import gzip
import json
from pathlib import Path
import re

from public_streams import no_runtime_faults

CPU_FIELDS = ('busy','idle','decode','stream','output','wifi','tcpip','web')


def read(path):
    data = path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes())
    return json.loads(data)


def cpu_intervals(rows, start, end):
    previous = None
    windows, malformed, gaps = [], [], []
    for row in rows:
        line = row['line']
        if 'PERF CPU:' not in line:
            continue
        match = re.search(r'\((\d+)\).*PERF CPU:', line)
        tick = int(match[1])/1000 if match else None
        duration = tick-previous if tick is not None and previous is not None else None
        previous = tick
        values = {key:float(value) for key,value in re.findall(r'(\w+)=([\d.]+)%', line)}
        valid = (all(k in values and 0 <= values[k] <= 100 for k in CPU_FIELDS)
                 and abs(values.get('busy', 0)+values.get('idle', 0)-100) < .3)
        if start <= row['at'] <= end and (not valid or tick is None):
            malformed.append(row)
        if duration is None or duration <= 0 or not valid:
            continue
        # Exclude partial warm-up/final intervals. Firmware timestamps give the
        # interval duration; host timestamps locate it inside the playback test.
        if row['at']-duration < start or row['at'] > end:
            continue
        if duration >= 10:
            gaps.append(dict(at=row['at'], seconds=duration,
                             note='Excluded: delayed sample or lost CPU log; interval attribution is uncertain'))
            continue
        windows.append(dict(at=row['at'], seconds=duration, **{k:values[k] for k in CPU_FIELDS}))
    return windows, malformed, gaps


def cpu_summary(windows):
    total = sum(w['seconds'] for w in windows)
    if not total:
        return dict(observed_seconds=0, windows=0)
    result = dict(observed_seconds=total, windows=len(windows), peak_percent=max(w['busy'] for w in windows))
    for key in CPU_FIELDS:
        result[key+'_mean_percent'] = sum(w[key]*w['seconds'] for w in windows)/total
    for threshold in (85,95,99.9):
        seconds = sum(w['seconds'] for w in windows if w['busy'] >= threshold)
        result['at_least_'+str(threshold)+'_percent'] = dict(seconds=seconds, observed_time_percent=100*seconds/total)
    return result


def decode_summary(rows, start, end):
    intervals = []
    for row in rows:
        match = re.search(r'PERF FLAC: window (\d+) ms, audio (\d+) ms, decode (\d+) ms', row['line'])
        if not match:
            continue
        window, audio, decode = map(int, match.groups())
        if row['at']-window/1000 >= start and row['at'] <= end:
            peak = re.search(r', max (\d+) us', row['line'])
            intervals.append(dict(window_ms=window, audio_ms=audio, decode_ms=decode,
                                  max_call_us=int(peak[1]) if peak else None))
    wall = sum(w['window_ms'] for w in intervals)
    audio = sum(w['audio_ms'] for w in intervals)
    decode = sum(w['decode_ms'] for w in intervals)
    peaks = [w['max_call_us'] for w in intervals if w['max_call_us'] is not None]
    return dict(windows=len(intervals), intervals=intervals, wall_ms=wall, audio_ms=audio, decode_ms=decode,
        max_call_us=max(peaks) if peaks else None,
        audio_wall_ratio=audio/wall if wall else None,
        audio_shortfall_percent=max(0,100*(1-audio/wall)) if wall else None,
        elapsed_decode_ms_per_audio_second=1000*decode/audio if audio else None,
        windows_decode_slower_than_audio=sum(w['decode_ms']>=w['audio_ms'] for w in intervals if w['audio_ms']))


def summarize(board_folder, manifest, analysis):
    report = read(board_folder/'report.json')
    rows = read(board_folder/'performance.json')
    status = read(board_folder/'status.json')
    specs = {s['name']:s for s in manifest['fixtures']}
    orders = {s['name']:s for s in analysis['cases']}
    original = {c['name']:c for c in report['cases']}
    cases, combined = [], {12:[],32:[]}
    for batch in status:
        if not batch['case'].startswith('load:'):
            continue
        name = batch['case'][5:]
        if 'cpu-under-http-load:'+name not in original:
            continue  # Case is still running or its outcome hasn't been saved.
        spec = specs[name]
        start, end = batch['started_at']+10, batch['ended_at']
        windows, malformed, gaps = cpu_intervals(rows,start,end)
        runtime = dict(result='PASS')
        try:
            no_runtime_faults([r for r in rows if batch['started_at']<=r['at']<=end])
        except AssertionError as error:
            runtime = dict(result='FAIL', reason=str(error))
        cpu = cpu_summary(windows)
        cpu['measurement_seconds'] = max(0,end-start)
        cpu['coverage_percent'] = 100*cpu['observed_seconds']/(end-start) if end>start else 0
        cpu['excluded_gap_seconds'] = sum(g['seconds'] for g in gaps)
        decoder = decode_summary(rows,start,end)
        observations = batch['samples']
        case = dict(name=name, station=spec['station'], max_lpc_order=spec['max_lpc_order'],
            file_bytes=spec['bytes'], pcm_sha256=spec['pcm_sha256'],
            original=original['cpu-under-http-load:'+name], runtime=runtime,
            measured_start=start, measured_end=end, cpu=cpu, decoder=decoder, predictor=orders[name],
            cpu_intervals=windows, malformed_cpu=malformed, suspected_gaps=gaps,
            max_http_ms=max(s['request_ms'] for s in observations),
            minimum_rssi=min(s['rssi'] for s in observations))
        cases.append(case)
        combined[spec['max_lpc_order']].extend(windows)
    aggregate = {}
    for limit, windows in combined.items():
        group = [c for c in cases if c['max_lpc_order']==limit]
        audio = sum(c['decoder']['audio_ms'] for c in group)
        wall = sum(c['decoder']['wall_ms'] for c in group)
        decode = sum(c['decoder']['decode_ms'] for c in group)
        samples = sum(c['predictor']['channel_samples'] for c in group)
        cpu = cpu_summary(windows)
        cpu['measurement_seconds'] = sum(c['cpu']['measurement_seconds'] for c in group)
        cpu['coverage_percent'] = 100*cpu['observed_seconds']/cpu['measurement_seconds'] if cpu['measurement_seconds'] else 0
        cpu['excluded_gap_seconds'] = sum(c['cpu']['excluded_gap_seconds'] for c in group)
        aggregate[str(limit)] = dict(cases=len(group), cpu=cpu,
            elapsed_decode_ms_per_audio_second=1000*decode/audio if audio else None,
            audio_wall_ratio=audio/wall if wall else None,
            bytes=sum(c['file_bytes'] for c in group),
            lpc32_percent_all=sum(c['predictor']['lpc32_percent_all']*c['predictor']['channel_samples'] for c in group)/samples if samples else None,
            above12_percent_all=sum(c['predictor']['above12_percent_all']*c['predictor']['channel_samples'] for c in group)/samples if samples else None,
            rolling_eligible_percent_lpc=sum(c['predictor']['rolling_eligible_percent_lpc']*c['predictor']['lpc_channel_samples'] for c in group)/sum(c['predictor']['lpc_channel_samples'] for c in group) if any(c['predictor']['lpc_channel_samples'] for c in group) else None,
            mean_order=sum(c['predictor']['mean_order_all_channel_samples']*c['predictor']['channel_samples'] for c in group)/samples if samples else None,
            original_gate_counts={result:sum(c['original']['result']==result for c in group) for result in ('PASS','FAIL','BLOCKED')},
            all_original_gates_pass=all(c['original']['result']=='PASS' for c in group) if group else None,
            all_runtime_gates_pass=all(c['runtime']['result']=='PASS' for c in group) if group else None)
    pairs = []
    for station in dict.fromkeys(s['station'] for s in specs.values()):
        pair = {c['max_lpc_order']:c for c in cases if c['station']==station}
        if set(pair) != {12,32}:
            continue
        if pair[12]['pcm_sha256'] != pair[32]['pcm_sha256']:
            raise ValueError('Mismatched PCM in comparison')
        cpu12, cpu32 = (pair[n]['cpu'].get('busy_mean_percent') for n in (12,32))
        decode12, decode32 = (pair[n]['decoder']['elapsed_decode_ms_per_audio_second'] for n in (12,32))
        pairs.append(dict(station=station,
            size_saving_percent=100*(1-pair[32]['file_bytes']/pair[12]['file_bytes']),
            cpu_change_percentage_points=cpu32-cpu12 if cpu12 is not None and cpu32 is not None else None,
            decode_change_percent=100*(decode32/decode12-1) if decode12 and decode32 is not None else None))
    return dict(board=report['board'], cases=cases, aggregate=aggregate, pairs=pairs,
        note='Full CPU means >=99.9% in observed complete ~5-second profiling intervals; not instantaneous peaks. Original failures retained. One broadcaster, ten short music excerpts, 24-bit PCM.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board-results',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--analysis',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    result = summarize(args.board_results,read(args.manifest),read(args.analysis))
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    for case in result['cases']:
        mean = case['cpu'].get('busy_mean_percent')
        print(case['name'], 'CPU',round(mean,2) if mean is not None else None,
              'peak',case['cpu'].get('peak_percent'),
              'full%',case['cpu'].get('at_least_99.9_percent',{}).get('observed_time_percent'),
              'decode ms/s',case['decoder']['elapsed_decode_ms_per_audio_second'],
              case['original']['result'], 'runtime',case['runtime']['result'])


if __name__ == '__main__':
    main()
