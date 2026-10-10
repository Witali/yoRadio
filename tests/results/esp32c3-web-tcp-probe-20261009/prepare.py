"""Prepare a source-frozen repetition of the previously failing physical trial."""
from pathlib import Path
import json
import hashlib

root = Path(__file__).resolve().parent
prior = Path('.build/c3-switch-owner-20261009')
trial = (prior/'trial-final.py').read_text()
trial = trial.replace('TransportTrace(urlsplit(a.board).hostname,log)',
                      'TransportTrace(urlsplit(a.board).hostname,log,capture_socket_ports=True)')
(root/'trial.py').write_text(trial)
source = (prior/'physical-confirmed.py').read_text()
source = source.replace("ROOT = Path('.build/c3-switch-owner-20261009')", "ROOT = Path('.build/c3-web-timeout-20261009')")
source = source.replace("OUT = ROOT/'physical-confirmed'", "OUT = ROOT/'physical'")
source = source.replace("TRUST = ROOT/'trust'", "TRUST = Path('.build/c3-switch-owner-20261009/trust')")
start = source.index("paths={'before':")
end = source.index("quiet=image_info", start)
source = source[:start]+'''paths={'probe':Path('firmware/development/esp32c3-idf-6.1-r9a97-web-tcp-probe/app.bin')}
images={name:image_info(path.read_bytes()) for name,path in paths.items()}
manifests={name:json.loads(path.with_name('manifest.json').read_text()) for name,path in paths.items()}
for name in paths:
    require(images[name]==manifests[name]['image'],'Image differs from manifest')
require(json.loads((ROOT/'build-audit.json').read_text())['result']=='PASS','Build unaudited')
''' + source[end:]
source = source.replace('trial-final.py','trial.py').replace("(('retained-confirmed','after'),)","(('web-tcp-probe','probe'),)")
(root/'physical.py').write_text(source)
files = [p for folder in ('tools/esp32c3_tests','tools/audio_test_server') for p in Path(folder).glob('*.py')]
files += list(Path('idf/esp32c3-oled-native/main').glob('*'))
files = [p for p in files if p.is_file()]
for path in files:
    dest = root/'sources'/path
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(path.read_bytes())
(root/'sources.json').write_text(json.dumps({p.as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2)+'\n')
for name in ('ca.pem','server.pem'):
    (root/name).write_bytes((prior/'trust'/name).read_bytes())
print('Prepared independent trial and frozen sources; no private key copied')
