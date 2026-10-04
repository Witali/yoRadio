#!/usr/bin/env python3
"""Compare complete recording PCM without alignment, resampling or skipped samples."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct

from compare_aac_late_sbr_pcm import read_log
from run_aac_recording_capture import parse_recording


def summarize(histogram):
    samples = sum(histogram.values())
    return dict(channel_samples=samples, different=samples-histogram[0],
                max_error_lsb=max(map(abs, histogram)),
                over_three=sum(n for error, n in histogram.items() if abs(error)>3),
                rms_error_lsb=math.sqrt(sum(error*error*n for error, n in histogram.items())/samples),
                mean_error_lsb=sum(error*n for error, n in histogram.items())/samples,
                signed_histogram={str(e): n for e, n in sorted(histogram.items())})


def compare(reference_log, candidate_log, data):
    a, left = parse_recording(reference_log, data)
    b, right = parse_recording(candidate_log, data)
    for key in ('bytes', 'rate', 'channels', 'frames', 'channel_samples', 'calls'):
        if a[key] != b[key]:
            raise ValueError('Changed PCM shape or input processing: ' + key)
    total = Counter(); channels = [Counter() for _ in range(a['channels'])]; frames = []
    for x, y in zip(left, right):
        if x['bytes'] != y['bytes']:
            raise ValueError('Different PCM frame size')
        hist = Counter()
        for index, ((before,), (after,)) in enumerate(zip(struct.iter_unpack('<h', x['pcm']), struct.iter_unpack('<h', y['pcm']))):
            error = after-before
            hist[error] += 1; channels[index % a['channels']][error] += 1
        total.update(hist)
        frames.append(dict(frame=x['frame'], **summarize(hist)))
    result = summarize(total)
    result.update(rate=a['rate'], channels=a['channels'], input_bytes=len(data),
                  input_sha256=hashlib.sha256(data).hexdigest(), frame_count=len(frames),
                  precision_limit_lsb=3, precision_pass=result['max_error_lsb']<=3,
                  reference_pcm_sha256=a['pcm_sha256'], candidate_pcm_sha256=b['pcm_sha256'],
                  frames=frames, per_channel=[dict(channel=i, **summarize(h)) for i, h in enumerate(channels)],
                  scope=__doc__, production_qualified=False)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-log', type=Path, required=True)
    parser.add_argument('--candidate-log', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = compare(read_log(args.reference_log), read_log(args.candidate_log), args.input.read_bytes())
    result['log_sha256'] = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in
                           (('reference', args.reference_log), ('candidate', args.candidate_log))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('frames', 'per_channel', 'signed_histogram')}, indent=2))
    raise SystemExit(0 if result['precision_pass'] else 2)
