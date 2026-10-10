import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-growth-tls')
review=json.loads((ROOT/'review.json').read_text())
assert review['exact_listened_image_restored'] and review['counts']==dict(passed=15,total=16)
manifest=json.loads((ART/'manifest.json').read_text())
assert hashlib.sha256((ART/'app.bin').read_bytes()).hexdigest()==manifest['image']['sha256']
for name,digest in json.loads((ROOT/'source-hashes.json').read_text()).items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
manifest.update(hardware_tested=True,production_qualified=False,quiet_runtime=True,
    qualification='Laboratory HTTPS AAC growth: 15/16 checks; all six files complete; HE growth contiguous headroom FAIL; no output/OOM/watchdog events in measured scope',
    physical_report='tests/results/esp32c3-aac-growth-tls-20261010/physical/files/report.json',
    reference_archive='tests/results/esp32c3-aac-growth-20261010/',
    static_ram_unchanged_from='esp32c3-idf-6.1-r9a97-quiet-output-health')
(ART/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(ART/'.gitattributes').write_text('* -text -filter -whitespace\n')
(ROOT/'firmware-manifest.json').write_bytes((ART/'manifest.json').read_bytes())
print('Finalized laboratory-only artifact and retained 15/16 result')
