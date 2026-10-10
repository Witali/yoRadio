"""Review early-MPI allocation recovery and preserve every original failure."""
import argparse,hashlib,json,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'test-sources/tools/esp32c3_tests'))
from heap_fragment import analyze as owners
from public_streams import no_runtime_faults
from staged_dma import summarize as dma
from web_tcp import window as tcp_window

def verdict(fn):
    try:return dict(result='PASS',evidence=fn())
    except (AssertionError,ValueError,KeyError) as error:return dict(result='FAIL',reason=str(error))
def heap(samples):return {k:statistics.median(r[k] for r in samples) for k in ('heap','largest','tasks')}
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'review.json');a=p.parse_args()
initial=json.loads((ROOT/'physical/initial.json').read_text());result=dict(phases={})
for phase in json.loads((ROOT/'physical/phases.json').read_text()):
    label=phase['name'];folder=ROOT/'physical'/label
    report=json.loads((folder/'report.json').read_text());rows=json.loads((folder/'performance.json').read_text());status=json.loads((folder/'status.json').read_text())
    assert report['board']['app_elf_sha256']==phase['image']['app_elf_sha256']
    assert report['test_sources_sha256']==initial['test_sources_sha256']
    item=dict(controller=phase,passed=sum(c['result']=='PASS' for c in report['cases']),total=len(report['cases']),
        original_cases=report['cases'],runtime=verdict(lambda:no_runtime_faults(rows)),heaps={},observations=[])
    if label.endswith('-tls'):
        for c in report['cases']:
            if c['name'] in ('idle-before','idle-recovery') and c['result']=='PASS':item['heaps'][c['name']]=heap(c['evidence']['samples'])
        for b in status:
            if b['case'].startswith('tls-record:'):
                start,end=b['started_at'],b['ended_at']
                v=dict(seconds=end-start,interrupted=b.get('interrupted',False),dma=verdict(lambda:dma(rows,start,end)),
                       dma_after_10_seconds=verdict(lambda:dma(rows,start+10,end)))
                if label.startswith('mpi-probe'):v['tcp']=verdict(lambda:tcp_window(rows,start,end))
                item['observations'].append(v)
        trace=ROOT/'physical'/(label+'-request-phases.jsonl')
    else:
        item['heaps']={k:heap(v) for k,v in report['idle'].items()}
        trace=folder/'request-phases.jsonl'
    if label.startswith('mpi-probe'):item['owners']=verdict(lambda:owners(rows))
    connections=[json.loads(s) for s in trace.read_text().splitlines() if json.loads(s)['phase']=='connect']
    item['connections']=len(connections);item['failed_connections']=[c for c in connections if c['result']!='PASS']
    item['input_sha256']={n:hashlib.sha256((folder/n).read_bytes()).hexdigest() for n in ('report.json','performance.json','status.json')}
    result['phases'][label]=item
restore=ROOT/'physical/restoration.json';result['restoration']=json.loads(restore.read_text()) if restore.exists() else None
a.output.write_text(json.dumps(result,indent=2)+'\n')
for name,item in result['phases'].items():
    o=item.get('owners',{});snaps=o.get('evidence',{}).get('snapshots',[])
    print(json.dumps(dict(phase=name,gates=[item['passed'],item['total']],failures=[c for c in item['original_cases'] if c['result']!='PASS'],
        heaps=item['heaps'],connections=item['connections'],failed_connections=item['failed_connections'],
        owners_result=o.get('result'),owner_endpoints=[snaps[0],snaps[-1]] if snaps else [],
        dma=[v['dma'] for v in item['observations']]),ensure_ascii=True),flush=True)
