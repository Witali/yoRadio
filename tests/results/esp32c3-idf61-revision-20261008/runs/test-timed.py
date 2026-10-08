import ast, http.client, io, json, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import build_opener, ProxyHandler, HTTPHandler

source = Path('.build/c3-idf-head-20261008/public-timed.py')
tree = ast.parse(source.read_text())
definition = next(n for n in tree.body if isinstance(n,ast.ClassDef))
log = io.StringIO()
env = dict(http=http,json=json,time=time,original=http.client.HTTPConnection,
           request_number=0,trace=log,board_host='127.0.0.1')
exec(compile(ast.Module(body=[definition],type_ignores=[]),str(source),'exec'),env)
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=='/slow': time.sleep(.25)
        self.send_response(200)
        self.send_header('Content-Length','5')
        self.end_headers()
        try: self.wfile.write(b'hello')
        except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError): pass
    def log_message(self,*args): pass
class TimedHandler(HTTPHandler):
    def http_open(self,req):return self.do_open(env['TimedConnection'],req)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
opener=build_opener(ProxyHandler({}),TimedHandler())
try:
    with opener.open(f'http://127.0.0.1:{server.server_port}/',timeout=1) as r:
        assert r.read()==b'hello'
    try:
        opener.open(f'http://127.0.0.1:{server.server_port}/slow',timeout=.1)
        raise AssertionError('Missing timeout')
    except TimeoutError: pass
finally:
    server.shutdown();server.server_close();thread.join()
rows=[json.loads(line) for line in log.getvalue().splitlines()]
assert [(r['phase'],r['result']) for r in rows] == [
    ('connect','PASS'),('request_including_connect','PASS'),('response_headers','PASS'),('response_body','PASS'),
    ('connect','PASS'),('request_including_connect','PASS'),('response_headers','FAIL')]
assert all(not any(key in r for key in ('url','headers','body')) for r in rows)
print(json.dumps(dict(result='PASS',cases=2,phases=rows),indent=2))
