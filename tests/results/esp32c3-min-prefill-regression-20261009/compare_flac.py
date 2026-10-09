"""Compare retained heavy-FLAC runs; distinguish association from causation."""
import argparse
import json
from pathlib import Path
import re
from flow_windows import helper, sha

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--summary',type=Path,default=ROOT/'summary.json')
parser.add_argument('--output',type=Path,default=ROOT/'flac-comparison.json')
args=parser.parse_args()
current=json.loads(args.summary.read_text())['sustained'][0]
old_folder=ROOT/'control-flac'
old={n:json.loads((old_folder/(n+'.json')).read_text()) for n in ('report','status','performance')}
batch=next(b for b in old['status'] if b['case'].startswith('load:'))
baseline=helper.summarize_batch('control-heavy-flac',old_folder,batch,old,
    {n:sha(old_folder/(n+'.json')) for n in old})
new=json.loads((ROOT/'physical/heavy-flac/report.json').read_text())
assert old['report']['fixture_hashes']==new['fixture_hashes']
assert old['report']['server_options']==new['server_options']
assert old['report']['sustained_protocol']==new['sustained_protocol']=='https'
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
old_config=config(old_folder/'sdkconfig')
candidate=ROOT/'candidate/sdkconfig'
if not candidate.exists():
    repo=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
    candidate=repo/'firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250/sdkconfig'
new_config=config(candidate)
diff={k:dict(before=old_config.get(k),after=new_config.get(k))
      for k in sorted(old_config.keys()|new_config.keys()) if old_config.get(k)!=new_config.get(k)}
result=dict(scope='Sequential runs, different profiling/minimum-prefill settings; no single-change causality or acoustic gap count.',
    configuration_differences=diff,compared={},candidate_event_context=[])
for label,c in (('previous_pcm_tail',baseline),('minimum_prefill',current)):
    result['compared'][label]=dict(identity=c['board'],original=c['original_acceptance'],
        telemetry_complete=c['telemetry_complete'],cpu_busy=c['cpu']['busy_mean_percent'],
        cpu_peak=c['cpu']['peak_percent'],heap=c['heap'],dma=c['dma']['delta'],
        dma_seconds=c['dma']['observed_seconds'],audio_wall_ratio=c['decoded_audio_wall_ratio'],
        rssi_median=c['median_rssi'],rssi_min=c['minimum_rssi'],maximum_http_ms=c['maximum_http_ms'])
delivery=new['tls_events'][0]['delivery']
assert not delivery['dropped_windows']
decoder=current['flow_decoder']['intervals'];output=current['flow_output']['intervals']
for e in current['whole_observed_dma_events']:
    # Keep the neighbouring complete windows; serial logs are periodic,
    # so their endpoints cannot establish sample-accurate temporal order.
    windows=[w for w in delivery['windows'] if w['started_at']<e['end'] and w['ended_at']>e['start']]
    def adjacent(rows):return [r for r in rows if r['at']>=e['end'] and r['at']<e['end']+2]
    result['candidate_event_context'].append(dict(event=e,delivery_windows=windows,
        decoder_windows=adjacent(decoder),output_windows=adjacent(output),
        maximum_host_write_seconds=max(w['max_write_seconds'] for w in windows)))
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(config=diff,comparison={n:dict(cpu=v['cpu_busy'],dma_events=v['dma']['q_overruns'],rssi=v['rssi_median'])
    for n,v in result['compared'].items()},events=[dict(overruns=c['event']['overruns'],
        host_write_max=c['maximum_host_write_seconds'],input_timeouts=[r['input_timeouts'] for r in c['decoder_windows']])
        for c in result['candidate_event_context']]),indent=2))
