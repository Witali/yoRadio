"""Summarize quiet-image checks without converting failed gates into passes."""
import argparse,json,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'test-sources/tools/esp32c3_tests'))
from common import check_playback
from production_health import check_health
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'review.json');a=p.parse_args()
result=dict(campaigns={},production_qualified=False)
def median(rows):return {key:statistics.median(r[key] for r in rows) for key in ('heap','largest','tasks')}
for campaign in ('physical','physical-local'):
    folder=ROOT/campaign
    if not (folder/'phases.json').exists():continue
    initial=json.loads((folder/'initial.json').read_text())
    phases=json.loads((folder/'phases.json').read_text())
    item=dict(phases={},restoration=json.loads((folder/'restoration.json').read_text()) if (folder/'restoration.json').exists() else None)
    for phase in phases:
        label=phase['name']
        report=json.loads((folder/('ota.json' if label=='ota' else label+'/report.json')).read_text())
        assert report['board']['app_elf_sha256']==initial['candidate']['app_elf_sha256']
        summary=dict(controller=phase,passed=sum(c['result']=='PASS' for c in report['cases']),total=len(report['cases']),
                     failures=[c for c in report['cases'] if c['result']!='PASS'])
        if label!='ota':
            assert report['test_sources_sha256']==initial['test_sources_sha256']
            health=json.loads((folder/label/'health.json').read_text())
            try:summary['health']=dict(result='PASS',evidence=check_health(health))
            except AssertionError as error:summary['health']=dict(result='FAIL',reason=str(error))
            summary['idle']={n:median(rows) for n,rows in report['idle'].items()}
            requests=[json.loads(s) for s in (folder/label/'request-phases.jsonl').read_text().splitlines()]
            connect=[r for r in requests if r['phase']=='connect']
            summary['connections']=len(connect);summary['connection_failures']=[r for r in connect if r['result']!='PASS']
            summary['max_connect_ms']=max(r['ms'] for r in connect)
            summary['max_headers_ms']=max(r['ms'] for r in requests if r['phase']=='response_headers')
            if label=='public':
                status=json.loads((folder/label/'status.json').read_text());observations={}
                for name,reference in report.get('references',{}).items():
                    batch=next(b for b in status if b['case']=='https:'+name)
                    stable=[h for h in health if batch['started_at']+15<=h['at']<=batch['ended_at']]
                    try:playback=dict(result='PASS',evidence=check_playback(batch['samples'],reference['spec'],minimum=27,warmup=15))
                    except AssertionError as error:playback=dict(result='FAIL',reason=str(error))
                    observations[name]=dict(spec=reference['spec'],format_check=playback,
                        minimum_heap=min(h['heap'] for h in stable),minimum_largest=min(h['largest'] for h in stable),
                        maximum_status_and_health_ms=max(s['request_ms'] for s in batch['samples']))
                summary['observations']=observations
        item['phases'][label]=summary
    result['campaigns'][campaign]=item
a.output.write_text(json.dumps(result,indent=2)+'\n')
for name,campaign in result['campaigns'].items():
    for label,phase in campaign['phases'].items():
        print(json.dumps(dict(campaign=name,phase=label,gates=[phase['passed'],phase['total']],failures=phase['failures'],
            idle=phase.get('idle'),health=phase.get('health'),connections=phase.get('connections'),
            connection_failures=phase.get('connection_failures'))))
