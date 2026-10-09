import json
from pathlib import Path
import ssl
import sys
import time
sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board
from serial.tools.list_ports import comports

root = Path(__file__).resolve().parent
trust = Path('.build/c3-tls-records-20261007/trust')
untrusted = Path('.build/c3-tls-final-gates-20261009/untrusted')
certs = {}
for name, path in [('trusted', trust/'server.pem'), ('untrusted', untrusted/'cert.pem')]:
    cert = ssl._ssl._test_decode_cert(str(path))
    certs[name] = dict(not_before=cert['notBefore'], not_after=cert['notAfter'],
        seconds_remaining=ssl.cert_time_to_seconds(cert['notAfter'])-time.time(), san=cert['subjectAltName'])
board = Board('http://192.168.100.4')
state = dict(identity=board.info(), status=board.status(), certificates=certs,
    ports=[dict(port=p.device, vid=p.vid, pid=p.pid) for p in comports()])
(root/'preflight.json').write_text(json.dumps(state, indent=2)+'\n')
print(json.dumps(state, indent=2))
