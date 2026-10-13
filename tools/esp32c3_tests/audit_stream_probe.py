"""Recheck saved stream-probe gates without contacting a board."""
import argparse
import json
from pathlib import Path

from common import check_transitions, fixtures, matches, require, sha
from stream_probe_cases import validate_schedule


def check_decoder_faults(case, *, required=False):
    """Check every retained health row, including terminal/failure diagnostics."""
    samples = [case[key] for key in ('before', 'after', 'active_before',
               'active_after', 'failure_health') if key in case]
    samples.extend(case.get('transition_health', []))
    require(samples, case['name']+': missing health samples')
    checked = missing = 0
    for sample in samples:
        fault = sample.get('decoder_failure')
        if fault is None:
            missing += 1
            require(not required, case['name']+': missing decoder fault evidence')
            continue
        require(isinstance(fault, dict) and type(fault.get('sequence')) is int and
                fault['sequence'] == 0, case['name']+': decoder fault or invalid counter')
        checked += 1
    return dict(checked=checked, missing=missing)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results',type=Path,required=True)
    parser.add_argument('--controller',type=Path,required=True)
    parser.add_argument('--expected-cases',type=int,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--require-decoder-health',action='store_true',
                        help='Reject missing decoder counters as well as recorded faults')
    args=parser.parse_args()
    r=json.loads(args.results.read_text())
    require(sha(args.controller.read_bytes())==r['controller_sha256'],'Controller hash differs')
    require(r['installed']['app_elf_sha256']==r['candidate']['app_elf_sha256'],'Candidate differs')
    restored=r['restoration']
    require(restored['image']['app_elf_sha256']==r['initial']['app_elf_sha256'],'Original image not restored')
    require(not restored['status']['audio'],'Board not stopped after restoration')
    require(all(restored[k] is True for k in ('wifi_unchanged','playlist_unchanged','settings_unchanged')),
            'Private settings verification missing or failed')
    sources=validate_schedule(r,args.expected_cases)
    available=fixtures();rows=[]
    negative={'unknown':'unknown audio format','partial':'unknown audio format',
              'truncated-id3':'unknown audio format'}
    if r.get('startup_confirmation'):
        negative.update(partial='truncated audio frame',**{'truncated-id3':'truncated audio frame'})
    prefixes={'false-mp3-before-he-aac':'he-48000-stereo',
              'false-aac-before-mp3':'mp3-320',
              'false-large-adts-before-he-aac':'he-48000-stereo',
              'false-large-adts-before-mp3':'mp3-320'}
    previous=None
    for case in r['cases']:
        name=case['name'];require(case['result']=='PASS',name+': recorded failure')
        decoder_health=check_decoder_faults(case,required=args.require_decoder_health)
        source_name=sources[name]
        before,after=case['before'],case['after']
        if previous is not None:
            require(before['boot_id']==previous['boot_id'] and
                    before['uptime_ms']>=previous['uptime_ms'],name+': restart between cases')
        require(after['uptime_ms']>=before['uptime_ms'],name+': uptime decreased')
        previous=after
        for key in ('boot_id','allocation_failures','task_watchdog_events'):
            require(before[key]==after[key],name+': '+key+' changed')
        require(after['allocation_failures']==after['task_watchdog_events']==0,name+': runtime errors')
        events=[e for e in r['server'] if e.get('fixture')==name]
        if r['transport']=='https':
            events=[e for e in events if e.get('tls_version') and e.get('tls_cipher')]
            require(events,name+': TLS negotiation evidence missing')
        observations=case['observations']
        active=case.get('transition_health',[])
        if source_name in negative:
            require(observations and not observations[-1]['audio'] and
                    observations[-1]['format']==negative[source_name],name+': wrong rejection status')
        else:
            require(any(e.get('complete') is True and e['sent']==r['fixtures'][name]['bytes'] for e in events),
                    name+': complete body missing')
            base=prefixes.get(source_name,source_name.removesuffix('-id3'))
            spec=available[base]
            if 'sequence' in spec:
                check_transitions(observations,[available[n] for n in spec['sequence']])
            else:
                consecutive=best=0
                for state in observations:
                    consecutive=consecutive+1 if matches(state,spec) else 0
                    best=max(best,consecutive)
                require(best>=3,name+': missing stable expected format')
                active=[case['active_before'],case['active_after']]
            require(not case['eof']['audio'] and case['eof']['format']=='stream ended',name+': wrong EOF')
            require(len(active)>=2 and active[-1]['uptime_ms']>active[0]['uptime_ms'],name+': missing active interval')
            for sample in active:
                require(sample['boot_id']==before['boot_id'] and
                        sample['allocation_failures']==sample['task_watchdog_events']==0,name+': active runtime failure')
                require(sample['output']['available'] is True and sample['output']==active[0]['output'],
                        name+': active output counters changed')
        rows.append(dict(name=name,result='PASS',active_samples=len(active),
            decoder_health=decoder_health,
            sampled_min_heap=min((h['heap'] for h in active),default=None),
            sampled_min_largest=min((h['largest'] for h in active),default=None),
            idle_after_heap=after['heap'],idle_after_largest=after['largest'],
            completion_drops_whole_case=after['output']['completion_queue_drops']-before['output']['completion_queue_drops'],
            tls_versions=sorted({e['tls_version'] for e in events if e.get('tls_version')})))
    result=dict(passed=True,transport=r['transport'],cases=rows,restored=True,
        scope='Finite streams and sampled active output/heap counters. No acoustic, long-run or lifetime-zero-drop claim.')
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS offline audit:',len(rows),'cases;',r['transport'],'; firmware and private settings restored')


if __name__=='__main__':main()
