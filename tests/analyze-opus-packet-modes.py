"""Localize observed Opus differences without defining a conformance tolerance.

Ordinary consecutive frames, repeated/reordered complete coded frames and PLC
cases are separate. Full scalar/packet/frame metrics and a bounded alignment
observation are computed from unchanged complete creator/native PCM captures.
"""
import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import sys


def need(value, reason):
    if not value:
        raise ValueError(reason)


def pin(path):
    body = path.read_bytes()
    return dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())


def pcm(path):
    body = array('h'); body.frombytes(path.read_bytes())
    if sys.byteorder != 'little':
        body.byteswap()
    return body


def statistics(native, creator):
    need(len(native) == len(creator) and native, 'equal nonempty complete observation geometry')
    return dict(samples=len(native), max_abs_lsb=max(abs(x - y) for x, y in zip(native, creator)),
                rms_error_lsb=math.sqrt(sum((x - y) ** 2 for x, y in zip(native, creator)) / len(native)),
                native_peak=max(abs(x) for x in native), creator_peak=max(abs(x) for x in creator),
                native_clipped_samples=sum(x in (-32768, 32767) for x in native),
                creator_clipped_samples=sum(x in (-32768, 32767) for x in creator))


def alignment(native, creator, channels):
    count = min(len(native) // channels, 2400)
    observations = []
    for swapped in ([False, True] if channels == 2 else [False]):
        for lag in range(-8, 9):
            error = 0; samples = 0
            for frame in range(max(0, -lag), min(count, count - lag)):
                for channel in range(channels):
                    other = 1 - channel if swapped else channel
                    delta = native[(frame + lag) * channels + channel] - creator[frame * channels + other]
                    error += delta * delta; samples += 1
            observations.append(dict(lag_frames=lag, swapped_channels=swapped, scalar_samples=samples,
                                     mean_square_error=error / samples))
    return dict(checked_lag_min=-8, checked_lag_max=8, prefix_frames=count,
                best=min(observations, key=lambda row: row['mean_square_error']), observations=observations,
                interpretation='bounded waveform/alignment observation, not a conformance acceptance bound')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('native', 'reference', 'output'):
        parser.add_argument('--' + name, required=True, type=Path)
    args = parser.parse_args()
    need(not args.output.exists(), 'fresh numeric observation output')
    native = json.loads((args.native / 'report.json').read_bytes())
    creator = json.loads((args.reference / 'report.json').read_bytes())
    need(native['passed'] and native['completed'] and creator['passed'] and creator['completed'], 'terminal original captures')
    summary, details = {}, {}
    for index, (name, fixture) in enumerate(creator['cases'].items()):
        maps = fixture['accounting']['source_frame_map']; flattened = [source for packet in maps for source in packet]
        category = 'missing_coded_frames' if None in flattened else 'unaltered_consecutive_fully_coded' if flattened == list(range(len(flattened))) else 'nonconsecutive_or_repeated_fully_coded'
        row = native['measurements']['cases'][4 * index]
        need(row['name'] == name and row['measurements']['mode'] == row['measurements']['chunk'] == 0, 'actual first whole-stock case')
        native_file = args.native / row['complete_pcm']['raw']['path']; creator_file = args.reference / fixture['artifacts']['raw.pcm']['path']
        need(pin(native_file) == {key: row['complete_pcm']['raw'][key] for key in ('bytes', 'sha256')} and
             pin(creator_file) == {key: fixture['artifacts']['raw.pcm'][key] for key in ('bytes', 'sha256')}, 'complete original PCM byte identities')
        actual, reference = pcm(native_file), pcm(creator_file)
        measured = statistics(actual, reference)
        aggregate = summary.setdefault(category, dict(cases=0, max_abs_lsb=0, max_rms_error_lsb=0, clipped_native=0, clipped_creator=0, names=[]))
        aggregate['cases'] += 1
        aggregate['max_abs_lsb'] = max(aggregate['max_abs_lsb'], measured['max_abs_lsb'])
        aggregate['max_rms_error_lsb'] = max(aggregate['max_rms_error_lsb'], measured['rms_error_lsb'])
        aggregate['clipped_native'] += measured['native_clipped_samples']; aggregate['clipped_creator'] += measured['creator_clipped_samples']
        aggregate['names'].append(name)
        channels = fixture['accounting']['channels']; duration = fixture['case']['samples']; packet = duration * fixture['case']['count']
        per_packet = [statistics(actual[at:at + packet * channels], reference[at:at + packet * channels])
                      for at in range(0, len(actual), packet * channels)]
        per_frame = []
        for at in range(0, len(actual), duration * channels):
            record = statistics(actual[at:at + duration * channels], reference[at:at + duration * channels])
            record.update(frame=at // (duration * channels), packet=(at // channels) // packet,
                          packet_frame=(at // channels) % packet // duration)
            per_frame.append(record)
        details[name] = dict(category=category, statistics=measured, source_frame_map=maps, per_packet=per_packet,
                             per_frame=per_frame, first_different_scalar_sample=next((i for i, (x, y) in enumerate(zip(actual, reference)) if x != y), None),
                             channels=channels, sample_rate=48000,
                             alignment=alignment(actual[:packet * channels], reference[:packet * channels], channels))
    result = dict(classification_is_observation_not_conformance=True, new_tolerance_applied=False,
                  input_native_report=pin(args.native / 'report.json'), input_creator_report=pin(args.reference / 'report.json'),
                  summary=summary, cases=details)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(summary=summary, alignment_best=[dict(name=name, **row['alignment']['best']) for name, row in details.items()]), indent=2))


if __name__ == '__main__':
    main()
