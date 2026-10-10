"""Replay flash-mode comparison without replacing original acceptance outcomes."""
import argparse, hashlib, importlib.util, json, re
from pathlib import Path

MODES=('dio','qio')
FIXTURES={'mp3-320':'mp3','flac-level8':'flac','vorbis-q10':'vorbis','opus-510':'opus','aac-lc-320':'aac','lc-44100-stereo':'aac','lc-22050-mono':'aac','lc-48000-stereo':'aac','he-44100-stereo':'aac','he-48000-stereo':'aac','hev2-44100-stereo':'aac'}
EXPECTED_MATRIX={f'{p}:{n}:{h}' for p in ('http','https') for n,c in FIXTURES.items() for h in ('auto',c)}
PHASES=('matrix','transitions-faults-websocket','switch','heavy-flac','hev2-ten-minutes','boot-ready')

def summarize(root):
    root=Path(root); physical=root/'physical'
    spec=importlib.util.spec_from_file_location('retained_sustained',root/'sustained_summary.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    from ota_diagnostic import serial_health
    variants={};missing=[]
    def read(path):
        if not path.exists():missing.append(path.relative_to(root).as_posix());return None
        return json.loads(path.read_text())
    for mode in MODES:
        reports={};runtime={};performance=[]
        for label in PHASES:
            folder=physical/mode/label
            report=read(folder/'report.json')
            if report is None:continue
            reports[label]=report
            telemetry=read(folder/'performance.json')
            status=read(folder/'status.json') if label!='boot-ready' else []
            if telemetry is not None:
                if label == 'boot-ready':
                    runtime[label]={'result':'NOT_APPLIED','reason':'Intentional resets; retain per-case readiness gates and raw capture'}
                elif label == 'transitions-faults-websocket':
                    health=serial_health(telemetry)
                    serious=[r for r in telemetry if re.search(r'allocation failed|^(ESP-ROM:|rst:|waiting for download)',r['line'])]
                    runtime[label]={'result':'PASS' if health['result']=='PASS' and not serious else 'FAIL','serial_health':health,'unexpected_reboots_or_allocations':serious,'scope':'Decoder errors during deliberately malformed streams retain per-case recovery checks'}
                else:
                    runtime[label]=helper.runtime_acceptance(telemetry,False)[0]
            if label in ('heavy-flac','hev2-ten-minutes') and telemetry is not None and status is not None:
                batches=[s for s in status if s['case'].startswith('load:')]
                if len(batches)!=1:missing.append(mode+'/'+label+': expected one sustained window')
                for batch in batches:
                    data={'report':report,'status':status,'performance':telemetry}
                    hashes={name:hashlib.sha256((folder/(name+'.json')).read_bytes()).hexdigest() for name in data}
                    performance.append(helper.summarize_batch(mode,folder,batch,data,hashes))
        ota=read(physical/(mode+'-ota.json'))
        if ota is not None:reports['ota']=ota
        boots=[read(physical/(mode+'-boot-'+str(i)+'.json')) for i in (1,2)]
        persistence=read(physical/(mode+'-settings.json'))
        failures=[{'suite':name,**case} for name,r in reports.items() for case in r['cases'] if case['result']!='PASS']
        matrix=[c for c in reports.get('matrix',{}).get('cases',[]) if c['name'].startswith(('http:','https:'))]
        actual_names=[c['name'] for c in matrix]
        matrix_complete=len(actual_names)==len(EXPECTED_MATRIX) and set(actual_names)==EXPECTED_MATRIX
        if not matrix_complete:missing.append(mode+': incomplete or duplicated finite-file matrix')
        counts={protocol:{result:sum(c['name'].startswith(protocol+':') and c['result']==result for c in matrix)
                          for result in ('PASS','FAIL','BLOCKED')} for protocol in ('http','https')}
        variants[mode]=dict(reports=reports,matrix_counts=counts,failures=failures,boot_probes=boots,
            runtime=runtime,persistence=persistence,performance=performance,
            matrix_complete=matrix_complete,
            original_gates_passed=(matrix_complete and len(reports)==7 and not failures),
            runtime_passed=bool(runtime) and all(r['result'] in ('PASS','NOT_APPLIED') for r in runtime.values()))
    phases=read(physical/'phases.json')
    expected_phases={'flash-status-before','backup','restore','readback','flash-status-after','restore-start'} | {m+'-'+n for m in MODES for n in ('install','start','repeat')} | {m+'/'+n for m in MODES for n in (*PHASES,'ota')}
    phases_complete=bool(phases and len(phases)==len(expected_phases) and {p['name'] for p in phases}==expected_phases)
    final=read(physical/'final-board.json');flash=read(physical/'flash-restoration.json')
    flash_status=read(physical/'flash-status-restoration.json')
    recovery=read(physical/'restoration-recovery.json')
    restored=bool(final and flash and final['playback_restored'] and
        all(final['persistence'].values()) and flash['full_flash_equal'] and
        flash_status and flash_status['before']==flash_status['after'])
    complete=not missing and all(all(b and b['result']=='PASS' for b in v['boot_probes']) for v in variants.values())
    for mode,v in variants.items():
        own_phases=[p for p in (phases or []) if p['name'].startswith((mode+'/',mode+'-'))]
        v['qualified_within_scope']=bool(complete and restored and phases_complete and
            own_phases and all(p['code']==0 for p in own_phases) and
            v['persistence'] and all(v['persistence'].values()) and
            v['original_gates_passed'] and v['runtime_passed'] and
            len(v['performance'])==2 and all(p['acceptance_passed'] for p in v['performance']))
    accepted=bool(complete and restored and phases_complete and
        recovery and recovery['initial_controller_exit_code']==0 and all(p['code']==0 for p in phases) and
        all(v['qualified_within_scope'] for v in variants.values()))
    return dict(variants=variants,missing=missing,complete=complete,restored=restored,
        final_board=final,flash_restoration=flash,flash_status_restoration=flash_status,
        restoration_recovery=recovery,
        phases=phases,phases_complete=phases_complete,all_gates_passed=accepted,
        acoustic_continuity_qualified=False,
        scope='Matched sequential DIO then QIO; awake ESP-IDF 6.1 laboratory profile. '
              'CPU utilization informational; all original failures retained. '
              'Two probed boots and five software readiness boots per mode. '
              'No cold power cycle, deep sleep or acoustic capture. OTA while playing not repeated.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--output',type=Path);a=p.parse_args()
    result=summarize(a.root)
    (a.output or a.root/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    for mode,v in result['variants'].items():
        print(mode,v['matrix_counts'],'failures',[(c['suite'],c['name'],c.get('reason')) for c in v['failures']])
    print('complete',result['complete'],'restored',result['restored'],'accepted',result['all_gates_passed'])
