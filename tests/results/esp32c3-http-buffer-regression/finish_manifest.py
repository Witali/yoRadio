import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
matrix=json.loads((ROOT/'review.json').read_text())
vorbis=json.loads((ROOT/'vorbis-review.json').read_text())
assert matrix['restoration'] and vorbis['restoration']
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-http-txrelease')
manifest=json.loads((art/'manifest.json').read_text())
assert hashlib.sha256((art/'app.bin').read_bytes()).hexdigest()==manifest['image']['sha256']
manifest['regression_report']='tests/results/esp32c3-http-buffer-regression/review.json'
manifest['http_regression']=dict(cases=matrix['controller_cases'],passed=matrix['passed'],failures=matrix['failures'])
manifest['vorbis_followup_report']='tests/results/esp32c3-http-buffer-regression/vorbis-review.json'
manifest['production_qualified']=False
manifest['qualification']='Experimental: physical HE-AAC memory comparison and 33-case HTTP codec regression retained, including two original failures and targeted follow-ups. Longer heavy HTTPS playback and candidate OTA regression remain pending. Original production restored.'
(art/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Recorded regression and preserved production_qualified=false')
