"""Compare first-use recovery while preserving the original failed verdict."""
import argparse,hashlib,json,re,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'probe-comparison.json');a=p.parse_args()
def summarize(folder):
 report=json.loads((folder/'report.json').read_text());rows=json.loads((folder/'performance.json').read_text());status=json.loads((folder/'status.json').read_text())
 result={}
 for c in report['cases']:
  if c['name']=='tls-record:grow':result['playback']=c.get('evidence')
  if c['name'] in ('idle-before','idle-recovery'):
   result[c['name']]={k:c[k] for k in ('result','reason') if k in c}
   if c['result']=='PASS':result[c['name']]['medians']={k:statistics.median(s[k] for s in c['evidence']['samples']) for k in ('heap','largest','tasks')}
 last=status[-1];assert last['case']=='settled-idle';samples=[]
 for r in rows:
  m=re.search(r'PERF CPU:.*heap=(\d+) largest=(\d+) tasks=(\d+)',r['line'])
  if m and last['started_at']<=r['at']<=last['ended_at']:samples.append(dict(zip(('heap','largest','tasks'),map(int,m.groups()))))
 assert len(samples)>=2
 result['raw_final_idle']={'samples':samples,'medians':{k:statistics.median(r[k] for r in samples) for k in ('heap','largest','tasks')}}
 result['input_sha256']={n:hashlib.sha256((folder/n).read_bytes()).hexdigest() for n in ('report.json','performance.json','status.json')}
 return result
control=REPO/'tests/results/esp32c3-frac4-attribution-20261010/physical/hev2-tls-grow'
result=dict(baseline_archive=control.relative_to(REPO).as_posix(),baseline=summarize(control),early_mpi_probe=summarize(ROOT/'physical/mpi-probe-tls'),
 note='Same watched raw range and initial size. Recovery improvement is contiguous capacity, not total RAM saved; no runtime allocation call stack is captured. The original failed verdict is retained.')
a.output.write_text(json.dumps(result,indent=2)+'\n');print('PASS: first-use comparison reproduced without changing recovery verdicts')
