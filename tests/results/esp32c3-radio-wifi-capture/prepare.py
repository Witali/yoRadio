from pathlib import Path
root=Path('.build/c3-radio-wifi-capture')
source=Path('.build/c3-production-radio-opus/physical.py').read_text(encoding='utf-8')
prefix=source.split("with (OUT/'request-phases.jsonl').open('x') as trace_log:")[0]
prefix=prefix.replace('esp32c3-idf-6.1-r9a97-production-radio','esp32c3-idf-6.1-r9a97-radio-wifi-probe')
prefix=prefix.replace('.build/c3-production-radio/production-radio/build-audit.json','.build/c3-radio-wifi-probe/build-audit.json')
prefix=prefix.replace("specs=fixtures(ROOT/'fixtures/manifest.json')", "specs=fixtures(Path('.build/c3-production-radio-opus/fixtures/manifest.json'))")
imports='''import re
import threading
import serial
from serial_lines import serial_lines
from common import check_recovery_heap
'''
start='''
class PassiveCapture:
    def __init__(self):
        self.rows=[];self.transport=[]
        self.closed=threading.Event();self.ready=threading.Event()
        self.thread=threading.Thread(target=self.read,daemon=True);self.thread.start()
        if not self.ready.wait(5):
            self.close();require(False,'Passive USB capture unavailable')
    def read(self):
        first=True
        while not self.closed.is_set():
            port=serial.Serial(port=None,baudrate=115200,timeout=.2)
            port.dtr=port.rts=False;port.port='COM9'
            try:
                port.open()
                if first:port.reset_input_buffer();first=False
                self.ready.set()
                for line in serial_lines(port,self.closed):
                    if 'PERF ' in line:
                        self.rows.append(dict(at=time.perf_counter(),line=line))
                    elif 'serial capture interrupted' in line:
                        self.transport.append(dict(at=time.perf_counter(),event=line))
            except (OSError,serial.SerialException):
                self.transport.append(dict(at=time.perf_counter(),event='USB reopen pending'))
            finally:port.close()
            self.closed.wait(.2)
    def close(self):
        self.closed.set();self.thread.join(3)
        require(not self.thread.is_alive(),'Capture reader did not stop')

capture=None
with (OUT/'request-phases.jsonl').open('x') as trace_log:
    with TransportTrace('192.168.100.4',trace_log,capture_socket_ports=True):
        try:
            capture=PassiveCapture()
            print('INSTALL TCP/Wi-Fi diagnostic application',flush=True)
            save('installed.json',dict(identity=install(ART/'app.bin'),persistence=verify_snapshot(board,before)))
            b=HealthBoard(board.origin)
            suite=Suite(b,'http://192.168.100.253:8772',specs,Capture(None),OUT,checkpoint=progress)
            with Server('192.168.100.253',8772,specs,pacing_ratio=1.0,delivery_stats=True) as server:
                stop_control(b);suite.observe(12,'idle:initial',interval=.4)
                initial=b.health_samples[-3:]
                for cycle in range(5):
                    name='opus:'+str(cycle+1)
                    b.play('http://192.168.100.253:8772/file/'+fixture)
                    begin=len(b.health_samples);states=suite.observe(60,name,interval=.4)
                    rows=b.health_samples[begin:];steady=[h for s,h in zip(states,rows) if s['seconds']>=15]
                    collected=evaluate(lambda:sustained_window(states,rows,60))
                    results[name]=dict(collection=dict(result=collected['result'],reason=collected.get('reason')),
                        transport=dict(result='FAIL' if suite.observations[-1]['errors'] else 'PASS',errors=suite.observations[-1]['errors']),
                        format=evaluate(lambda:check_playback(states,specs[fixture],minimum=27,warmup=15)),
                        output=evaluate(lambda:check_output(steady)),memory=evaluate(lambda:check_memory(steady)))
                    stop_control(b)
                    name='hev2-eof:'+str(cycle+1);b.play('http://192.168.100.253:8772/file/hev2-44100-stereo','aac')
                    begin=len(b.health_samples);states=suite.observe(24,name,interval=.4)
                    rows=b.health_samples[begin:]
                    def terminal():
                        require(len(states)>=15,'Sparse EOF observation')
                        require(all(not s['audio'] and s['format']=='stream ended' and not s['pcm_sample_rate'] and not s['pcm_channels'] for s in states[-5:]),'Wrong terminal state')
                        return dict(last_samples=5)
                    active=[h for s,h in zip(states,rows) if 3<=s['seconds']<=8 and s['audio']]
                    results[name]=dict(transport=dict(result='FAIL' if suite.observations[-1]['errors'] else 'PASS',errors=suite.observations[-1]['errors']),
                        format=evaluate(lambda:check_playback([s for s in states if s['seconds']<=8],specs['hev2-44100-stereo'])),
                        output=evaluate(lambda:check_output(active)),terminal=evaluate(terminal),health=check_health(rows))
                    stop_control(b);suite.observe(10,'idle:cycle:'+str(cycle+1),interval=.4)
                    results[name]['recovery']=evaluate(lambda:check_recovery_heap(initial,b.health_samples[-3:]))
                    save('results.json',results);save('health.json',b.health_samples);save('server.json',server.events)
                    save('performance.json',list(capture.rows));save('serial-transport.json',list(capture.transport))
                    print('CYCLE',cycle+1,{k:v['result'] for k,v in results[name].items() if isinstance(v,dict) and 'result' in v},flush=True)
                save('recovery.json',dict(initial=initial,final=b.health_samples[-3:],check=evaluate(lambda:check_recovery_heap(initial,b.health_samples[-3:]))))
        except Exception as error:
            save('controller-failure.json',dict(exception_chain=exception_details(error)))
            raise
'''
restore=source[source.index('        finally:\n            print(\'RESTORE original production application\''):]
restore=restore.replace("            print('RESTORE original production application',flush=True)","""            if capture:
                capture.close()
                save('performance.json',capture.rows);save('serial-transport.json',capture.transport)
            if 'b' in globals():save('health.json',b.health_samples)
            if 'server' in globals():save('server.json',server.events)
            print('RESTORE original production application',flush=True)""")
(root/'physical.py').write_text(prefix+imports+start+restore,encoding='utf-8')
print('Prepared five bounded Opus/HEv2 EOF cycles with passive USB and host TCP tracing')
