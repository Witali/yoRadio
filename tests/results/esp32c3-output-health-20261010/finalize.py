import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-output-health')
review=json.loads((ROOT/'review.json').read_text())
assert review['exact_listened_image_restored'] and review['counts']==dict(passed=7,total=8)
manifest=json.loads((ART/'manifest.json').read_text())
assert hashlib.sha256((ART/'app.bin').read_bytes()).hexdigest()==manifest['image']['sha256']
for name,digest in json.loads((ROOT/'source-hashes.json').read_text()).items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
manifest.update(hardware_tested=True,production_qualified=False,
    qualification='600-second public HE-AAC HTTPS observation: 7/8 checks; contiguous headroom FAIL; no output/OOM/watchdog events in measured scope',
    physical_report='tests/results/esp32c3-output-health-20261010/physical/files/report.json',
    output_health=True,output_health_counter_bytes=8,output_health_isr_bytes=18)
(ART/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(ART/'.gitattributes').write_text('* -text -filter whitespace=cr-at-eol\n')
(ROOT/'firmware-manifest.json').write_bytes((ART/'manifest.json').read_bytes())
print('Finalized saved image identity and retained 7/8 verdict')
