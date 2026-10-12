"""Record completed public MP3 campaign without masking failed host controls."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
review=json.loads((root/'review.json').read_text())
assert review['review']=='PASS' and review['restoration']
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-http-txrelease/manifest.json')
manifest=json.loads(art.read_text())
manifest.update(public_mp3_long_report='tests/results/esp32c3-public-mp3-long/review.json',public_mp3_long=review['cases'],production_qualified=False)
art.write_text(json.dumps(manifest,indent=2)+'\n')
lines=['','## Ten-minute public MP3 controls, 2026-10-12','',
'The same `quiet-http-txrelease` binary was observed for 600 seconds each on',
'`ice5.somafm.com/groovesalad-256-mp3`, first HTTP and then HTTPS. Steady gates',
'exclude the first 15 seconds; firmware fault counters cover the whole run.',
'The source reference was probed through HTTPS for both cases. That reference',
'does not independently establish HTTP route equivalence.','',
'| Transport | Observation / format / output / memory / WebUI | Min sampled free / largest, B | Concurrent FFmpeg |',
'|---|---|---:|---|']
for transport,case in review['cases'].items():
    checks=case['checks'];order=('collection','format','output','memory','transport')
    outcomes=' / '.join(checks[k]['result'] for k in order)
    metrics=case['metrics'];host=case['host']
    host_label=f"{host['result']}, {host['decoded_seconds']:.3f} decoded s"
    lines.append(f"| {transport.upper()} | {outcomes} | {metrics['heap']['minimum']:,} / {metrics['largest']['minimum']:,} | {host_label} |")
lines += ['',
'The HTTP host control failed before decoding: FFmpeg rejected `tls_verify`',
'on a plain HTTP input. This is a test-command failure, not a board decoding',
'failure or a completed independent comparison. The corrected controller adds',
'that option only for HTTPS; a separate three-second HTTP command check passed.',
'The original controller and failure remain retained. A complete simultaneous',
'HTTP host/board comparison is still required.','',
'HTTPS FFmpeg uses certificate verification. Separate live clients can receive',
'different content/start points; their results do not prove bit-identical input.',
'Queue-drop totals include deliberate idle periods; only steady-window deltas',
'are used for output acceptance. These are digital counters, not an analog',
'listening measurement. Passing runs do not establish a fix for historical',
'intermittent MP3 stops or WebUI TCP-connect failures.','',
'Original application, settings, selected station and decoded playback were',
'restored and verified. [Raw evidence and replay](../tests/results/esp32c3-public-mp3-long/)',
'retain each case outcome, host failure, corrected command check and restoration.',
'Public audio and private FFmpeg stderr are not archived.','']
p=Path('docs/ESP32C3_HTTP_REQUEST_BUFFER.md');s=p.read_text();assert lines[1] not in s;p.write_text(s+'\n'.join(lines))
print('Recorded all MP3 outcomes, including the failed HTTP host control')
