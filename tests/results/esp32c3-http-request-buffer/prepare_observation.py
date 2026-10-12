from pathlib import Path
root=Path(__file__).resolve().parent
source=(root/'physical_repeat.py').read_text()
source=source.replace("OUT=ROOT/'physical-repeat'", "OUT=ROOT/'physical-observed'")
source=source.replace('from common import Board,Failure,check_playback,fixtures,require,sha','from common import Board,Failure,check_playback,fixtures,require,sha,exception_details')
source=source.replace('from run import Suite,Capture','from run import Suite as OriginalSuite,Capture\nfrom trace_transport import TransportTrace')
insertion='''
class Suite(OriginalSuite):
    def observe(self, seconds, name, interval=.4):
        start=time.perf_counter();samples=[];errors=[]
        batch=dict(case=name,started_at=start,samples=samples,errors=errors)
        try:
            while time.perf_counter()-start<seconds:
                requested=time.perf_counter()
                try:
                    state=self.board.status()
                    samples.append(dict(seconds=requested-start,request_ms=(time.perf_counter()-requested)*1000,**state))
                    progress(None,batch)
                except (OSError,TimeoutError) as error:
                    errors.append(dict(seconds=requested-start,exception_chain=exception_details(error)))
                time.sleep(interval)
        finally:
            batch['ended_at']=time.perf_counter();self.observations.append(batch)
            (self.output/'status.json').write_text(json.dumps(self.observations,indent=2)+'\\n')
        return samples

def stop_control(b):
    for attempt in range(3):
        try:return b.stop()
        except (OSError,TimeoutError) as error:
            control_errors.append(dict(operation='stop',attempt=attempt,exception_chain=exception_details(error)))
            save('control-errors.json',control_errors)
            if attempt==2:raise
            time.sleep(1)
control_errors=[]
'''
source=source.replace('results={};last=0',insertion+'\nresults={};last=0')
source=source.replace('b.stop();','stop_control(b);')
source=source.replace("format=evaluate(lambda:check_playback", "transport=dict(result='FAIL' if suite.observations[-1]['errors'] else 'PASS',errors=suite.observations[-1]['errors']),\n                    format=evaluate(lambda:check_playback")
source=source.replace("('format','output','memory')", "('transport','format','output','memory')")
# Keep transport logs around the whole campaign, including its restoration.
start=source.index('try:\n    for variant')
source=source[:start]+"with (OUT/'request-phases.jsonl').open('x') as trace_log:\n    with TransportTrace('192.168.100.4',trace_log,capture_socket_ports=True):\n"+''.join('        '+line if line.strip() else line for line in source[start:].splitlines(keepends=True))
path=root/'physical_observed.py';assert not path.exists();path.write_text(source)
