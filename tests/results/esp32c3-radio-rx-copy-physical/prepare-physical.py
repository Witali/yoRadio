from pathlib import Path

root=Path(__file__).resolve().parent
text=Path('.build/c3-radio-wifi-capture/physical.py').read_text()
text=text.replace('r9a97-radio-wifi-probe','r9a97-radio-rx-copy')
text=text.replace('.build/c3-radio-wifi-probe/build-audit.json','.build/c3-radio-rx-copy/build-audit.json')
text=text.replace('INSTALL TCP/Wi-Fi diagnostic application','INSTALL copied RX diagnostic application')
text=text.replace('"""Bounded public MP3 HTTP/HTTPS observations and independent host decoding."""',
                  '"""Observe copied RX ownership during Opus HTTP and HE-AAC HTTPS; restore original board state."""')
start=text.index("            with Server(")
end=text.index("        except Exception as error:",start)
text=text[:start]+'''            stop_control(b);suite.observe(12,'idle:initial',interval=.4)
            initial=b.health_samples[-3:]
            with Server('192.168.100.253',8772,specs,pacing_ratio=1.0,delivery_stats=True) as server:
                for cycle in range(3):
                    name='opus:'+str(cycle+1)
                    b.play('http://192.168.100.253:8772/file/'+fixture)
                    begin=len(b.health_samples);states=suite.observe(60,name,interval=.4)
                    rows=b.health_samples[begin:];steady=[h for s,h in zip(states,rows) if s['seconds']>=15]
                    collected=evaluate(lambda:sustained_window(states,rows,60))
                    results[name]=dict(collection=dict(result=collected['result'],reason=collected.get('reason')),
                        transport=dict(result='FAIL' if suite.observations[-1]['errors'] else 'PASS',errors=suite.observations[-1]['errors']),
                        format=evaluate(lambda:check_playback(states,specs[fixture],minimum=27,warmup=15)),
                        output=evaluate(lambda:check_output(steady)),memory=evaluate(lambda:check_memory(steady)))
                    stop_control(b);suite.observe(10,'idle:cycle:'+str(cycle+1),interval=.4)
                    results[name]['recovery']=evaluate(lambda:check_recovery_heap(initial,b.health_samples[-3:]))
                    save('results.json',results);save('health.json',b.health_samples);save('server.json',server.events)
                    save('performance.json',list(capture.rows));save('serial-transport.json',list(capture.transport))
                    print('CYCLE',cycle+1,{k:v['result'] for k,v in results[name].items() if isinstance(v,dict) and 'result' in v},flush=True)
            source='https://ice5.somafm.com/groovesalad-64-aac'
            reference_command=json.loads(Path('.build/c3-prefill1000-public-20261010/faad-reference-command.json').read_text())
            reference=probe(source,'ffprobe',reference_command)
            save('reference.json',reference)
            b.play(source);begin=len(b.health_samples)
            states=suite.observe(600,'public-he-https-600s',interval=1)
            rows=b.health_samples[begin:]
            collected=evaluate(lambda:sustained_window(states,rows,600))
            steady=[h for s,h in zip(states,rows) if s['seconds']>=15]
            results['he-https']=dict(collection=dict(result=collected['result'],reason=collected.get('reason')),
                transport=dict(result='FAIL' if suite.observations[-1]['errors'] else 'PASS',errors=suite.observations[-1]['errors']),
                format=evaluate(lambda:check_playback(states,reference['spec'],minimum=351,warmup=15)),
                output=evaluate(lambda:check_output(steady)),memory=evaluate(lambda:check_memory(steady)),
                health=check_health(rows))
            save('results.json',results);save('health.json',b.health_samples)
            stop_control(b);suite.observe(12,'idle:final',interval=.4)
            save('recovery.json',dict(initial=initial,final=b.health_samples[-3:],check=evaluate(lambda:check_recovery_heap(initial,b.health_samples[-3:]))))
''' + text[end:]
(root/'physical.py').write_text(text)
compile(text,str(root/'physical.py'),'exec')
print('Prepared 3x60s Opus and 600s public HE-AAC RX capture with finally restoration')
