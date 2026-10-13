import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
review=json.loads((root/'review.json').read_text())
assert review['review']=='PASS' and review['rebooted_baseline_control']['restoration']
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-http-txrelease')
manifest=json.loads((art/'manifest.json').read_text())
assert hashlib.sha256((art/'app.bin').read_bytes()).hexdigest()==manifest['image']['sha256']
manifest.update(hardware_tested=True,production_qualified=False,
    qualification='Experimental: two 60-second HE-AAC physical cases passed format, output counters, transport and memory gates; original production restored. All-codec, HTTP lifecycle and longer playback regression pending.',
    implementation_commit='17d584dd',
    physical_report='tests/results/esp32c3-http-request-buffer/review.json',
    physical_cases=review['cases'],rebooted_baseline_control=review['rebooted_baseline_control'])
(art/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Saved limited physical qualification; production_qualified remains false')
