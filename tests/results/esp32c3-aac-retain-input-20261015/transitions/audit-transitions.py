import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require,fixtures,check_transitions
from audit_stream_probe import check_decoder_faults
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
base=Path('.build/c3-aac-retain-input-20261015')
folder=sys.argv[1];p=base/folder;r=json.loads((p/'results.json').read_text())
require(hashlib.sha256(Path('tools/esp32c3_tests/stream_probe.py').read_bytes()).hexdigest()==r['controller_sha256'],'Controller changed')
restore=r['restoration'];require(restore['image']['app_elf_sha256']==r['initial']['app_elf_sha256'] and not restore['status']['audio'],'Original not restored stopped')
require(all(restore[k] for k in ('wifi_unchanged','playlist_unchanged','settings_unchanged')),'Settings changed')
expected=['changing'] if folder=='baseline-changing' else ['changing','implicit-sbr','mp3-he-mp3','aac-mp3-hev2']
require([c['name'] for c in r['cases']]==expected,'Incomplete matrix')
a=fixtures();out={'image':r['candidate'],'cases':[],'scope':'Independent replay preserves original failure; no analog or full qualification claim'}
for c in r['cases']:
    name=c['name'];spec=a[name]
    require(hashlib.sha256(spec['data']).hexdigest()==r['fixtures'][name]['sha256'],'Fixture differs')
    h=c['transition_health'];check_transitions(c['observations'],[a[n] for n in spec['sequence']])
    require(not c['eof']['audio'] and c['eof']['format']=='stream ended','Wrong EOF')
    rows=[c['before']]+h+[c['after']]
    require(len(h)>=3 and all(x['output'].get('available') is True for x in h),'Missing output counters')
    output={}
    for key in ('completion_queue_drops','write_errors'):
        values=[x['output'][key] for x in h]
        require(all(type(v) is int and v>=0 for v in values) and values==sorted(values),'Invalid/reset output counter')
        output[key]=values[-1]-values[0]
    require(len({x['boot_id'] for x in rows})==1,'Restart')
    out['cases'].append(dict(name=name,original_result=c['result'],original_failure=c.get('check'),
        transition_format_and_eof='PASS',decoder=check_decoder_faults(c,required=True),
        allocation_delta=c['after']['allocation_failures']-c['before']['allocation_failures'],
        watchdog_delta=c['after']['task_watchdog_events']-c['before']['task_watchdog_events'],
        output=output,minimum_sampled_heap=min(x['heap'] for x in rows),
        lifetime_minimum_heap=min(x['minimum_heap'] for x in rows),
        minimum_largest=min(x['largest'] for x in rows),
        last_failure=c['after'].get('last_allocation_failure'),
        resident_slots=sorted({x['input_queue']['resident'] for x in rows}),
        boot_id=rows[0]['boot_id'],health_samples=len(rows)))
(p/'audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
