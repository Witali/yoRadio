"""Keep original physical verdicts alongside paired receive-credit evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import sys

REPO = next(p for p in Path(__file__).resolve().parents if (p/'tools/esp32c3_tests/common.py').is_file())
sys.path.insert(0, str(REPO/'tools/esp32c3_tests'))
from heap_receive_correlation import inspect
from staged_dma import parse as parse_dma

source = REPO/'tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py'
spec = importlib.util.spec_from_file_location('sustained_evidence', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
root = Path(__file__).resolve().parent
summary = dict(cases=[], note='Same lab application, sequential 600 s HTTPS runs; '
    'rate100 first, rate102 second. Original gates unchanged. '
    'CPU is informational; no acoustic output capture.')
for label in ('rate100', 'rate102'):
    folder = root/'physical'/label
    paths = {n:folder/(n+'.json') for n in ('report','status','performance')}
    if not all(p.exists() for p in paths.values()):
        summary['cases'].append(dict(label=label, complete=False, reason='Run files unavailable'))
        continue
    data = {n:json.loads(p.read_text()) for n,p in paths.items()}
    hashes = {n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in paths.items()}
    batches = [b for b in data['status'] if b['case']=='load:hev2-44100-stereo']
    if len(batches)!=1:
        summary['cases'].append(dict(label=label, complete=False, reason='Missing unique load window'))
        continue
    item = module.summarize_batch(label, folder, batches[0], data, hashes)
    correlation = inspect(folder, 'hev2-44100-stereo')
    item['paired_memory'] = correlation['paired']
    item['server'] = correlation['server']
    dma = [p for row in data['performance'] if (p := parse_dma(row)) is not None
           and item['measured_start'] <= p['at'] <= item['measured_end']]
    item['dma_intervals'] = [dict(start=a['at'], end=b['at'],
        q_overruns=b['q_overruns']-a['q_overruns'],
        written_bytes=b['written_bytes']-a['written_bytes']) for a,b in zip(dma,dma[1:])]
    item['continuity_diagnostic'] = dict(
        complete=item['telemetry_complete'],
        zero_overruns=item.get('dma',{}).get('delta',{}).get('q_overruns') == 0,
        acoustic_continuity_qualified=False,
        note='Independent of original gates; nonzero queue overruns require investigation. '
             'Zero overruns alone does not qualify acoustic continuity.')
    reports = {c['name']:c for c in data['report']['cases']}
    item['idle'] = {}
    for phase,key in [('before','load-idle-baseline:hev2-44100-stereo'),
                      ('after','load-idle-recovery:hev2-44100-stereo')]:
        rows = reports.get(key,{}).get('evidence',{}).get('samples',[])
        item['idle'][phase] = ({k:statistics.median(r[k] for r in rows) for k in ('heap','largest','tasks')}
                              if rows else None)
    summary['cases'].append(item)
    print(label, 'original',item['original_gates_passed'], 'runtime',item['runtime_acceptance']['result'],
          'complete',item['telemetry_complete'],'cpu',item['cpu'].get('busy_mean_percent'),
          'heap',item.get('heap'),'DMA',item.get('dma',{}).get('delta'),flush=True)
for name in ('restoration','restoration-failure','controller-failure','phases'):
    path = root/'physical'/(name+'.json')
    if path.exists(): summary[name] = json.loads(path.read_text())
summary['sources_sha256'] = {str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in (source,Path(__file__),REPO/'tools/esp32c3_tests/heap_receive_correlation.py')}
(root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
