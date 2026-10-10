"""Summarize the measured campaign; retain all verdicts and earlier limitations."""
import json,math,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
r=json.loads((root/'review.json').read_text())
report=json.loads((root/'physical/records/report.json').read_text())
health=json.loads((root/'physical/records/health.json').read_text())
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-growth-tls')
assert hashlib.sha256((art/'app.bin').read_bytes()).hexdigest()==report['image']['sha256']
assert hashlib.sha256((art/'sdkconfig').read_bytes()).hexdigest()==report['sdkconfig_sha256']
(root/'firmware-manifest.json').write_bytes((art/'manifest.json').read_bytes())
for name in ('audit.log','bundle-audit.json','application-object-comparison.json'):
    (root/('reused-build-'+name)).write_bytes((Path('.build/c3-aac-growth-tls-20261010')/name).read_bytes())
table=['| Profile / TLS record mode | Min free / largest, B | Output drops / errors | Max status + health, ms | Gates |',
       '| --- | ---: | ---: | ---: | ---: |']
for name,w in r['windows'].items():
    h,o=w['health'],w['output']
    cases=[c for c in report['cases'] if c['name'].startswith(name+':')]
    table.append(f"| {name} | {h['minimum_heap']:,} / {h['minimum_largest']:,} | {o['completion_queue_drops']} / {o['write_errors']} | {math.ceil(w['maximum_status_health_ms'])} | {sum(c['result']=='PASS' for c in cases)}/{len(cases)} |")
failures='None.' if not r['failed_cases'] else ', '.join(r['failed_cases'])+'.'
doc=f'''# Quiet HE-AAC playback with measured TLS record sizes

## Scope and result

The physical ESP32-C3 campaign completes **{r['counts']['passed']}/{r['counts']['total']} checks**.
Failed checks: {failures}
It runs eight 75-second playback observations: HE-AAC and HE-AACv2, each with
constant 1 KiB records, constant 16 KiB records, growth from 1 to 16 KiB after
30 seconds, and alternating sizes. Delivery is paced at exactly 1.0 audio
seconds per wall second. Both profiles produce 44.1 kHz stereo PCM.

{chr(10).join(table)}

The output deltas cover each measured steady window after a 15-second
startup exclusion; the raw lifetime counters keep startup/idle/Stop events.
The table rounds response times up. Free/largest values are sampled minima,
not a guarantee about allocations between observations.

Across {r['lifetime_health']['samples']} health observations, the allocation-failure
and watchdog counters are {r['lifetime_health']['allocation_failures']} and
{r['lifetime_health']['task_watchdog_events']}; boot identity remains unchanged.
The SDK lifetime minimum free heap is {min(h['minimum_heap'] for h in health):,} bytes,
including startup and transients outside the steady windows.
`review.json` records exact durations, record counts, first full-rate PCM,
RSSI ranges and memory recovery after each Stop.

## Image and protocol evidence

The reused laboratory application is `idf61-quiet-growth-tls`, app SHA-256
`{report['image']['sha256']}`. Its earlier build audit shows identical
application code/constants and static RAM to the quiet output-health image;
the test image only adds one local CA to all 145 public trust entries.
QIO/80 MHz, nominal fractional 48 kHz output, full compact AAC, 17,058-byte
TLS RX reserve and the four-slot input floor remain unchanged. There is no
UART capture or optional runtime CPU profiling in this campaign.

The server negotiates TLS 1.2 / `ECDHE-RSA-AES128-GCM-SHA256`. Its MemoryBIO
parser observes actual ciphertext records, and the verifier compares them
with completed socket writes. A 16 KiB plaintext record is the maximum allowed
by [RFC 5246 section 6.2.1](https://www.rfc-editor.org/rfc/rfc5246.html#section-6.2.1).
With this AES-GCM suite, recorded payload lengths are 1,048 and 16,408 bytes:
the plaintext plus an 8-byte explicit nonce and a 16-byte authentication tag;
the 5-byte outer record header is separate. See
[RFC 5288 section 3](https://www.rfc-editor.org/rfc/rfc5288.html#section-3).

For growth cases, the first 16 KiB record must occur after the board first
reports full-rate PCM. Gates reject retried/ended TLS connections, incorrect
fixture hashes, changed pacing, incomplete write evidence, missing samples,
late PCM startup, stopped/mismatched playback and output errors independently.
The server may record a socket error after intentional Stop; the immutable
pre-Stop snapshot is the acceptance evidence, and later events are also saved.

## Interpretation and remaining work

These observations test maximum-size application records and size changes
with a live HE-AAC decoder. They do not reduce the existing 8,192-byte
largest-block budget or overwrite the earlier 7,424-byte headroom failures
in [the AAC frame-growth campaign](ESP32C3_AAC_TLS_HEADROOM_20261010.md).
The AAC fixtures are repeated without changing their frame payloads or lengths;
this is TLS-record growth, a separate scenario from ADTS frame growth.

This is not a renegotiation test. The pinned ESP-IDF `set_client_config()`
explicitly enables TLS renegotiation when `CONFIG_MBEDTLS_SSL_RENEGOTIATION=y`,
which the saved image uses. Its dynamic adapter can allocate handshake,
session and transform state again. The RX reserve alone does not reserve
those allocations. Late handshake allocation requirements remain to be checked.
Likewise, a run without the earlier seven-second WebUI delay does not establish
that delay's cause or resolution. Output service counters do not measure the
analog waveform. Production qualification remains open.

The controller restores the exact listened `idf61-listen48-8c1f2d` application
and verifies Wi-Fi/playlist/settings persistence plus three stopped states.
No serial recovery or settings erase is used.

[Frozen measurements and offline replay](../tests/results/esp32c3-quiet-tls-records-20261010/README.md).
'''
Path('docs/ESP32C3_QUIET_TLS_RECORDS_20261010.md').write_text(doc)
(root/'README.md').write_text(f'''# Quiet HE-AAC TLS record-size campaign

Physical verdict: **{r['counts']['passed']}/{r['counts']['total']}**; failed checks: {failures}
The exact listened application and settings were restored.

Run the offline review from the repository root:

```text
python -B tests/results/esp32c3-quiet-tls-records-20261010/review.py
```

Replay PASS means saved verdicts reproduce; it does not turn a failed physical
gate into PASS. Frozen test modules, numeric status/health, request-phase timing,
actual TLS record lengths, completed write counts, public certificates, image
identity and restoration evidence are retained. Private keys, Wi-Fi credentials,
playlist contents and TLS plaintext/ciphertext are excluded. The running
controller's arguments contain only a local key path, never key contents.

The build is reused byte-for-byte from the preceding AAC growth campaign.
`reused-build-*` files and `firmware-manifest.json` identify that saved audit;
the original full build evidence is in `../esp32c3-aac-growth-tls-20261010/`.
Host checks: three quiet-record gate tests, six real local TLS server tests,
three sustained-output gate tests. Initial sandbox access failure did not run
the server tests; the saved six-test log is from the successful permitted run.

`index.json` covers all archived files except itself with size and SHA-256.
`verify_commit.py` also checks byte-for-byte equality with committed Git blobs.
[Report](../../../docs/ESP32C3_QUIET_TLS_RECORDS_20261010.md).
''')
print('Wrote report and archive README')
