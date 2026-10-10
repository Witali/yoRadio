"""Replay FIR/control performance and exact rational EOF submissions."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'test-sources/tools/esp32c3_tests'))
from common import require,sha,check_recovery_heap
from pcm_tail import check_submission,terminal_records
from public_streams import no_runtime_faults
from staged_dma import summarize as dma_summary
from tls_records import record_evidence
from flow_windows import helper,strict_flow

def verdict(function):
    try:return dict(result='PASS',evidence=function())
    except (AssertionError,ValueError,KeyError) as error:return dict(result='FAIL',reason=str(error))

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=ROOT/'review.json')
args=parser.parse_args()
phases=json.loads((ROOT/'physical/phases.json').read_text())
initial=json.loads((ROOT/'physical/initial.json').read_text())
result=dict(phases={},missing=[],note='Driver queue events are not an acoustic gap count. CPU has no acceptance ceiling.')
for label in ('control-flac','fir-tails','fir-flac','fir-tls-grow'):
    phase=next((p for p in phases if p['name']==label),None)
    if not phase:result['missing'].append(label);continue
    folder=ROOT/'physical'/label
    data={n:json.loads((folder/(n+'.json')).read_text()) for n in ('report','status','performance')}
    report,batches,rows=data['report'],data['status'],data['performance']
    require(report['board']['app_elf_sha256']==phase['image']['app_elf_sha256'],'Unexpected image')
    require(report['test_sources_sha256']==initial['test_sources_sha256'],'Changed test helpers')
    require(report['host_clock']==initial['host_clock'],'Changed clock')
    hashes={n:sha((folder/(n+'.json')).read_bytes()) for n in data}
    item=dict(controller=phase,original=report['cases'],passed=sum(c['result']=='PASS' for c in report['cases']),
              total=len(report['cases']),runtime=verdict(lambda:no_runtime_faults(rows)),input_sha256=hashes)
    result['phases'][label]=item
    if label=='fir-tails':
        specs={s['name']:s for s in report['fixtures']}
        require(report['resampler_output_rate']=='625000/13','Wrong tail mode')
        require(len(specs)==30,'Wrong fixtures')
        terminals=terminal_records(rows)
        require(terminals==[b['terminal'] for b in batches],'Raw terminal evidence differs')
        item['complete']=len(batches)==61
        item['checks']=[]
        for previous,current in zip(batches,batches[1:]):
            spec=specs[current['name']]
            item['checks'].append(dict(name=current['name'],protocol=current['protocol'],
                **verdict(lambda p=previous,c=current,s=spec:check_submission(p['terminal'],c['terminal'],s['frames'],s['rate'],Fraction(625000,13)))))
        continue
    sustained=[b for b in batches if b['case'].startswith(('load:','tls-record:'))]
    require(len(sustained)==1,'Missing/extra sustained observations')
    batch=sustained[0]
    item['observation_interrupted']=bool(batch.get('interrupted'))
    item['requested_seconds']=600 if label=='fir-tls-grow' else 90
    item['observation_seconds']=batch['ended_at']-batch['started_at']
    measured=helper.summarize_batch(label,folder,batch,data,hashes)
    start,end=measured['measured_start'],measured['measured_end']
    measured.update(flow_decoder=strict_flow(rows,start,end,'DEC'),flow_output=strict_flow(rows,start,end,'STAGED_OUT'),
                    whole_dma=verdict(lambda:dma_summary(rows,batch['started_at'],batch['ended_at'])))
    measured['zero_dma_events']=bool(measured.get('dma',{}).get('coverage_complete') and
        not measured['dma']['delta']['q_overruns'] and not measured['dma']['delta']['errors'])
    measured['digital_acceptance']=bool(not item['observation_interrupted'] and measured['acceptance_passed'] and measured['zero_dma_events'] and
        measured['flow_decoder']['complete'] and measured['flow_output']['complete'])
    item['sustained']=measured
    if label=='fir-tls-grow':
        item['records']=verdict(lambda:record_evidence(report['record_observations']['grow']['events'],'grow'))
        original={c['name']:c for c in report['cases']}
        def recovery():
            require(original['idle-before']['result']=='PASS','Missing qualified initial idle')
            require(original['idle-recovery']['result']=='PASS','Original recovery gate failed')
            return check_recovery_heap(original['idle-before']['evidence']['samples'],original['idle-recovery']['evidence']['samples'])
        item['heap_recovery']=verdict(recovery)
        trace=ROOT/'physical'/(label+'-request-phases.jsonl')
    else:
        item['heap_recovery']=verdict(lambda:check_recovery_heap(report['idle']['before'],report['idle']['after-flac']))
        trace=folder/'request-phases.jsonl'
    requests=[json.loads(line) for line in trace.read_text().splitlines()]
    connections=[r for r in requests if r['phase']=='connect']
    item.update(connections=len(connections),connection_failures=[r for r in connections if r['result']!='PASS'])
restore=ROOT/'physical/restoration.json'
result['restoration']=json.loads(restore.read_text()) if restore.exists() else None
args.output.write_text(json.dumps(result,indent=2)+'\n')
for name,item in result['phases'].items():
    s=item.get('sustained',{})
    print(json.dumps(dict(phase=name,gates=[item['passed'],item['total']],runtime=item['runtime'],
        cpu=s.get('cpu',{}).get('busy_mean_percent'),output_cpu=s.get('cpu',{}).get('output_mean_percent'),
        audio_wall=s.get('decoded_audio_wall_ratio'),dma=s.get('dma',{}).get('delta'),
        heap=s.get('heap'),accepted=s.get('digital_acceptance'),
        tail_checks=len(item.get('checks',[])),tail_failures=[c for c in item.get('checks',[]) if c['result']!='PASS'],
        connection_failures=item.get('connection_failures'))))
