"""Preserve normal urllib requests while timing their board transport phases.

No retries, longer timeouts, URLs, headers or response contents are recorded.
Only connections to the explicitly named test board are instrumented.
"""
import hashlib, http.client, json, sys, time
from pathlib import Path
from urllib.parse import urlsplit

output = Path(sys.argv[sys.argv.index('--output')+1])
output.parent.mkdir(parents=True,exist_ok=True)
trace = output.with_name(output.name+'-request-phases.jsonl').open('x',encoding='utf-8')
board_host = urlsplit(sys.argv[sys.argv.index('--board')+1]).hostname
original = http.client.HTTPConnection
request_number = 0

class TimedConnection(original):
    def __init__(self,*args,**kwargs):
        global request_number
        super().__init__(*args,**kwargs)
        request_number += 1
        self.observed_number = request_number

    def measured(self,phase,action):
        if self.host != board_host: return action()
        started=time.monotonic()
        row=dict(request=self.observed_number,phase=phase,at=started)
        try:
            result=action()
            row['result']='PASS'
            return result
        except BaseException as e:
            row['result']='FAIL'
            row['error_type']=type(e).__name__
            for key in ('errno','winerror'):
                value=getattr(e,key,None)
                if type(value) is int: row[key]=value
            raise
        finally:
            row['ms']=(time.monotonic()-started)*1000
            trace.write(json.dumps(row)+'\n');trace.flush()

    def connect(self):
        return self.measured('connect',lambda:super(TimedConnection,self).connect())

    def request(self,*args,**kwargs):
        return self.measured('request_including_connect',lambda:super(TimedConnection,self).request(*args,**kwargs))

    def getresponse(self):
        response=self.measured('response_headers',lambda:super(TimedConnection,self).getresponse())
        read=response.read
        response.read=lambda *args,**kwargs:self.measured('response_body',lambda:read(*args,**kwargs))
        return response

http.client.HTTPConnection=TimedConnection
sys.path.insert(0,'tools/esp32c3_tests')
import tls_records
try:
    code=tls_records.main()
finally:
    http.client.HTTPConnection=original
    trace.close()
    output.with_name(output.name+'-transport-timing.json').write_text(json.dumps(dict(
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        python=sys.version, connection_instances=request_number,
        note='Original urllib transport and five-second timeout; no retries. Connect is included in request duration. Timestamps use the same monotonic clock as playback observations.'),indent=2)+'\n')
raise SystemExit(code)
