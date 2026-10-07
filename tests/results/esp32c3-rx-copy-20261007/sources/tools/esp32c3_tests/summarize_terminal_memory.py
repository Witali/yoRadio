"""Summarize natural-EOF recovery separately from an explicit Stop."""
import argparse
import json
from pathlib import Path
import statistics


def summarize(report):
    cases = {c['name']:c for c in report['cases']}
    result = dict(image=report['board']['app_elf_sha256'], streams={})
    for name in cases:
        if not name.endswith(':idle-before'): continue
        prefix = name[:-len('idle-before')]
        rows = {}
        for stage, suffix in [('before','idle-before'),('eof','idle-without-stop'),('stop','idle-after-stop')]:
            evidence = cases[prefix+suffix]['evidence']
            if evidence['explicit_stop'] != (stage != 'eof'):
                raise ValueError('Natural EOF checkpoint was masked with Stop')
            samples = evidence['samples']
            if len(samples)<2: raise ValueError('Missing settled heap samples')
            rows[stage]={key:statistics.median(s[key] for s in samples) for key in ('heap','largest','tasks')}
        rows['eof_heap_loss']=rows['before']['heap']-rows['eof']['heap']
        rows['eof_largest_loss']=rows['before']['largest']-rows['eof']['largest']
        rows['eof_result']=cases[prefix+'eof-recovery']['result']
        rows['stop_result']=cases[prefix+'stop-recovery']['result']
        rows['playback_result']=cases[prefix+'play-to-eof']['result']
        result['streams'][prefix[:-1]]=rows
    if not result['streams']: raise ValueError('No natural-EOF heap measurements')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=summarize(json.loads(args.report.read_text()))
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
