from pathlib import Path
root=Path('.build/c3-production-radio-opus')
source=Path('.build/c3-production-radio-mp3-http/physical.py').read_text(encoding='utf-8')
prefix=source.split("with (OUT/'request-phases.jsonl').open('x') as trace_log:")[0]
prefix=prefix[:prefix.index('def reference_start(')]
prefix=prefix.replace('specs=fixtures()',"specs=fixtures(ROOT/'fixtures/manifest.json')")
prefix=prefix.replace("source='https://ice5.somafm.com/groovesalad-256-mp3'", "fixture='stress-opus-48000-2ch-16bit-90s'")
restore=source[source.index('        finally:\n            print(\'RESTORE original production application\''):]
body='''with (OUT/'request-phases.jsonl').open('x') as trace_log:
    with TransportTrace('192.168.100.4',trace_log,capture_socket_ports=True):
        try:
            save('installed.json',dict(identity=install(ART/'app.bin'),persistence=verify_snapshot(board,before)))
            b=HealthBoard(board.origin)
            suite=Suite(b,'http://192.168.100.253:8772',specs,Capture(None),OUT,checkpoint=progress)
            from common import check_recovery_heap
            with Server('192.168.100.253',8772,specs,pacing_ratio=1.0,delivery_stats=True) as server:
                stop_control(b);suite.observe(10,'idle:initial',interval=1)
                initial=b.health_samples[-3:]
                for cycle in range(3):
                    name='opus:auto:'+str(cycle+1)
                    stop_control(b);time.sleep(2)
                    b.play('http://192.168.100.253:8772/file/'+fixture)
                    begin=len(b.health_samples)
                    states=suite.observe(60,name,interval=1)
                    rows=b.health_samples[begin:];steady=[h for s,h in zip(states,rows) if s['seconds']>=15]
                    collection=evaluate(lambda:sustained_window(states,rows,60))
                    results[name]=dict(collection=dict(result=collection['result'],reason=collection.get('reason')),
                        transport=dict(result='FAIL' if suite.observations[-1]['errors'] else 'PASS',errors=suite.observations[-1]['errors']),
                        format=evaluate(lambda:check_playback(states,specs[fixture],minimum=27,warmup=15)),
                        output=evaluate(lambda:check_output(steady)),memory=evaluate(lambda:check_memory(steady)),health=check_health(rows))
                    save('health.json',b.health_samples);save('results.json',results);save('server.json',server.events)
                    if cycle==2:
                        tail=suite.observe(36,name+':terminal',interval=1)
                        def terminal():
                            stopped=next((i for i,s in enumerate(tail) if not s['audio']),None)
                            require(stopped is not None and len(tail)-stopped>=2,'No stable EOF')
                            require(all(not s['audio'] and s['format']=='stream ended' and not s['pcm_sample_rate'] and not s['pcm_channels'] for s in tail[stopped:]),'Incorrect terminal state')
                            return dict(samples=len(tail)-stopped)
                        results[name]['terminal']=evaluate(terminal)
                    stop_control(b);suite.observe(10,name+':idle',interval=1)
                    results[name]['recovery']=evaluate(lambda:check_recovery_heap(initial,b.health_samples[-3:]))
                    results[name]['idle_health']=b.health_samples[-3:]
                    save('health.json',b.health_samples);save('results.json',results);save('server.json',server.events)
                    print('RESULT',name,{k:v['result'] for k,v in results[name].items() if isinstance(v,dict) and 'result' in v},flush=True)
                save('recovery.json',dict(initial=initial,final=b.health_samples[-3:],check=evaluate(lambda:check_recovery_heap(initial,b.health_samples[-3:]))))
'''
(root/'physical.py').write_text(prefix+body+restore,encoding='utf-8')
print('Prepared three sustained AUTO Opus cycles with independent memory/output/recovery gates and final EOF')
