import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
review=json.loads((root/'review.json').read_text())
assert review['review']=='PASS' and review['restoration']
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-production-radio')
manifest=json.loads((art/'manifest.json').read_text())
assert hashlib.sha256((art/'app.bin').read_bytes()).hexdigest()==manifest['image']['sha256']
manifest.update(hardware_tested=True,production_qualified=False,
    regression_report='tests/results/esp32c3-production-radio-regression/review.json',
    http_regression=dict(cases=review['controller_cases'],passed=review['passed'],failures=review['failures']),
    qualification='Exact production rebuild physically exercised for HTTP codec/EOF/network/lifecycle checks. Failures retained in report; exact-image HTTPS, OTA and sustained qualification remain pending. Original application/settings/station restored.')
(art/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
p=Path('docs/ESP32C3_HTTP_REQUEST_BUFFER.md')
s=p.read_text(encoding='utf-8');heading='## Production rebuild HTTP regression, 2026-10-12';assert heading not in s
text='\n'+heading+'\n\n'
text+='The exact `production-radio` application above was installed by OTA and\nverified by embedded ELF hash before running the same 33-case HTTP matrix.\n'
text+=f"Result: **{review['passed']}/{review['controller_cases']} PASS**. Failed cases remain:\n\n"
for case in review['failures']:text+=f"- `{case['name']}`: {case.get('reason') or case.get('exception_chain')}.\n"
if not review['failures']:text+='- None in this campaign.\n'
text+='''
The matrix covers eleven finite fixtures in automatic/explicit codec modes,
two AAC transitions, Stop/Play, dropped/stalled/error sources, redirect/jitter,
WebSocket reconnect, settled memory recovery and lifetime health. A failure
inside a finite-file case can prevent its later EOF checks; it must not be
counted as full EOF coverage for that case.

Original production, settings and station were restored and verified.
[Raw observations and replay](../tests/results/esp32c3-production-radio-regression/)
retain outcomes and the controller. Hardware testing is now recorded for this
exact binary; complete production qualification remains false. This HTTP
matrix does not replace exact-image HTTPS/OTA or sustained-playback checks.
'''
p.write_text(s+text,encoding='utf-8')
p=Path('docs/ESP32C3_MEMORY_STABILITY_TODO.md');s=p.read_text(encoding='utf-8')
s=s.replace('Its manifest remains `hardware_tested=false`, `production_qualified=false`.',f"Its [HTTP matrix](ESP32C3_HTTP_REQUEST_BUFFER.md#production-rebuild-http-regression-2026-10-12)\nnow records {review['passed']}/{review['controller_cases']} passes; hardware testing is recorded, while\n`production_qualified=false` remains. Failed cases require follow-up.")
p.write_text(s,encoding='utf-8')
print('Recorded exact-image matrix with original failed outcomes')
