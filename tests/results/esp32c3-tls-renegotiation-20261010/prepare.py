from pathlib import Path
root=Path(__file__).resolve().parent
source=Path('.build/c3-quiet-tls-records-20261010/physical.py').read_text()
source=source.replace('TLS record-size campaign','TLS renegotiation campaign')
source=source.replace('import json, subprocess, sys, time','import json, os, subprocess, sys, time')
source=source.replace("'--seconds', '75', ","'--seconds', '75', '--mode', 'small', '--renegotiate-seconds', '30', ")
source=source.replace("child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)",
    "child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=dict(os.environ, PYTHONPATH=str(ROOT/'packages'), PYTHONDONTWRITEBYTECODE='1'))")
source=source.replace('measured quiet TLS records','full TLS renegotiation')
(root/'physical.py').write_text(source)
comparison=source.replace("OUT = ROOT / 'physical'", "OUT = ROOT / 'physical-comparison'")
comparison=comparison.replace("'--mode', 'small',", "'--case', 'he-44100-stereo', '--mode', 'small', '--mode', 'large',")
(root/'physical_comparison.py').write_text(comparison)
for name in ('ca.pem','server.pem','fixture-inputs.json'):
    (root/name).write_bytes((Path('.build/c3-quiet-tls-records-20261010')/name).read_bytes())
print('Prepared controller; app-only OTA and exact restoration remain unchanged')
