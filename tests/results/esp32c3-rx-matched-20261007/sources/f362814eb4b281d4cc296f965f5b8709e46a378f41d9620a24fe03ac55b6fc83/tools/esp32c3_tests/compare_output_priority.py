"""Compare matched scheduling experiments, retaining original load verdicts."""
import argparse
import json
from pathlib import Path

from pipeline_flow import summarize


def compare(control, candidate):
    before = json.loads((control/'report.json').read_text())
    after = json.loads((candidate/'report.json').read_text())
    if before['fixture_hashes'] != after['fixture_hashes']:
        raise ValueError('Scheduling comparison requires identical fixtures')
    if before['load_seconds'] != after['load_seconds']:
        raise ValueError('Scheduling comparison requires identical durations')
    summaries = [summarize(control), summarize(candidate)]
    indexed = [{c['name']: c for c in s['cases'] if c['name'].startswith('load:')}
               for s in summaries]
    if indexed[0].keys() != indexed[1].keys():
        raise ValueError('Scheduling comparison requires identical cases')
    verdicts = [{c['name']: c for c in r['cases']} for r in (before, after)]
    result = dict(control_image=before['board']['app_elf_sha256'],
        candidate_image=after['board']['app_elf_sha256'],
        fixtures=before['fixture_hashes'], cases=[],
        note='Complete windows after 10 s warm-up; scheduler wall times include preemption. '
             'Decoder CPU per audio second is an estimate from independent CPU/audio windows. '
             'Original gate failures remain failures; no acoustic continuity claim.')
    for name in indexed[0]:
        pair = []
        for cases, gates in zip(indexed, verdicts):
            c = cases[name]
            ratio = c['decoder']['audio_wall_ratio']
            pair.append(dict(original=gates[name], cpu=c['cpu'], decoder=c['decoder'],
                flow_decoder=c['flow_decoder'], flow_output=c['flow_output'],
                estimated_decoder_cpu_ms_per_audio_second=(
                    c['cpu']['decode_mean_percent']*10/ratio if ratio else None)))
        result['cases'].append(dict(name=name, control=pair[0], candidate=pair[1]))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--control', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = compare(args.control, args.candidate)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    for pair in result['cases']:
        print(pair['name'], {side: dict(
            cpu=pair[side]['cpu']['busy_mean_percent'],
            ratio=pair[side]['decoder']['audio_wall_ratio'],
            overruns=pair[side]['flow_output'].get('overruns'),
            original=pair[side]['original']['result']) for side in ('control', 'candidate')})
