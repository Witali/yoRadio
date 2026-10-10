import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
assert json.loads((ROOT/'output-audit.json').read_text())['result']=='PASS'
assert json.loads((ROOT/'quiet-output-health/build-audit.json').read_text())['result']=='PASS'
source=Path('.build/c3-aac-growth-20261010/physical.py').read_text()
source=source.replace('HTTP AAC-growth','HTTPS output-health').replace('from aac_growth import load_pairs\n','')
source=source.replace('quiet-mpi-health','quiet-output-health')
source=source.replace("reference = ROOT / 'references.json'\nload_pairs(ROOT)","reference = ROOT / 'faad-reference-command.json'")
source=source.replace('5505393d2b7d4fcad1303b3b96d9c41709c86a84e687bcbeb059a4241d243da6','ada20228227e7fc6af79de6ba01d26b4da2b98b140a1faca4ab9c398f53df99d')
source=source.replace("'tools/esp32c3_tests/aac_growth.py'","'tools/esp32c3_tests/sustained_output.py'")
source=source.replace("'--fixtures', str(ROOT), '--host', '192.168.100.253', '--output', str(OUT / 'files')", "'--aac-reference-command', str(reference), '--seconds', '600', '--stream', 'groovesalad-64-aac', '--output', str(OUT / 'files')")
source=source.replace('AAC growth files','HE-AAC HTTPS 600 seconds')
(ROOT/'physical.py').write_text(source)
shutil.copyfile('.build/c3-quiet-health-20261010/faad-reference-command.json',ROOT/'faad-reference-command.json')
shutil.copytree('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-output-health/log',ROOT/'build-logs')
print('Prepared bounded controller with exact listened-image restoration')
