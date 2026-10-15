"""Re-evaluate saved finite playback without rewriting original test verdicts."""
import argparse
import json
from pathlib import Path

from common import check_recovery_heap, require, sha
from production_health import check_decoder_health, output_window
from public_file_acceptance import check_finite_playback
from sustained_output import check_memory, check_output


def review(directory):
    inputs = {name: (directory/name).read_bytes() for name in ('report.json','status.json','health.json')}
    report, states, health = (json.loads(inputs[n]) for n in ('report.json','status.json','health.json'))
    require(any(c['name']=='all-decoder-health' for c in report['cases']), 'Campaign incomplete')
    result = dict(image=report['image'], input_sha256={k:sha(v) for k,v in inputs.items()},
        original_cases=[{k:c[k] for k in ('name','result','reason') if k in c} for c in report['cases']],
        scope='Retrospective checks on original playback boundaries; original report remains unchanged. '
              'Finite observations do not prove absence of slower leaks or acoustic continuity.', files=[])
    for batch in states:
        name=batch['case']
        if not name.startswith('https:'):continue
        codec=name.split(':')[1]
        row=dict(case=name,checks={});result['files'].append(row)
        def check(label,fn):
            try:
                evidence=fn();row['checks'][label]=dict(result='PASS',evidence=evidence)
                return evidence
            except Exception as error:
                row['checks'][label]=dict(result='FAIL',reason=str(error))
        playback=check('playback',lambda:check_finite_playback(batch['samples'],report['references']['sources'][codec]['spec']))
        if playback is None:continue
        start=batch['started_at']
        selected=[h for h in health if start+playback['first_playback_seconds']+3<=h['at']<=
                  start+playback['first_stopped_seconds']-1]
        require(len(selected)>=10,'Sparse playback health')
        row['window']=dict(first_at=selected[0]['at'],last_at=selected[-1]['at'],samples=len(selected))
        for label,fn in (('memory',check_memory),('decoder',check_decoder_health),
                         ('output_measurement',output_window),('output',check_output)):
            check(label,lambda f=fn:f(selected))
        def recovery():
            stopped=[h for h in health if start+playback['first_stopped_seconds']+2<=h['at']<=batch['ended_at']]
            require(len(stopped)>=3,'Missing pre-Stop EOF recovery')
            check_recovery_heap(report['idle']['initial'],stopped[-3:])
            return dict(samples=stopped[-3:],before_explicit_stop=True)
        check('natural_eof_recovery',recovery)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    require(not args.output.exists(),'Preserve earlier review')
    result=review(args.directory)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    for row in result['files']:
        print(row['case'], {k:v['result'] for k,v in row['checks'].items()})
