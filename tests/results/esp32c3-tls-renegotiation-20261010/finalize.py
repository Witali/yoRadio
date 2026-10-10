import json,math,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
rows=[]
for phase,review_name in [('physical','review.json'),('physical-comparison','comparison-review.json')]:
    review=json.loads((root/review_name).read_text())
    report=json.loads((root/phase/'records/report.json').read_text())
    health=json.loads((root/phase/'records/health.json').read_text())
    for name,w in review['windows'].items():
        request=report['record_observations'][name]['events'][0]['renegotiation_requests'][0]['at']
        changes=[]
        for before,after in zip(health,health[1:]):
            delta=(after['output']['completion_queue_drops']-before['output']['completion_queue_drops'])&0xffffffff
            if delta and request-5<after['at']<request+10:
                changes.append(dict(from_request_seconds=[before['at']-request,after['at']-request],drops=delta))
        rows.append(dict(campaign=phase,name=name,metrics=w,output_event_intervals=changes,
                         lifetime_minimum_free=min(h['minimum_heap'] for h in health)))
(root/'correlation.json').write_text(json.dumps(rows,indent=2)+'\n')
table=['| Campaign / stream | Handshake, ms | Output drops / errors | Min free / largest, B | Max status + health, ms |',
       '| --- | ---: | ---: | ---: | ---: |']
for row in rows:
    w=row['metrics'];h,o=w['health'],w['output']
    table.append(f"| {row['campaign']} / {row['name']} | {w['renegotiation']['duration_ms']:.1f} | {o['completion_queue_drops']} / {o['write_errors']} | {h['minimum_heap']:,} / {h['minimum_largest']:,} | {math.ceil(w['maximum_status_health_ms'])} |")
doc=f'''# TLS renegotiation during HE-AAC playback

## Physical result: output service failure reproduced

The first quiet-image campaign passes **17/18** checks. HE-AAC with 1 KiB
records has four I2S completion-queue drops; HE-AACv2 has none. A second
campaign on the same application repeats HE-AAC with 1 KiB and 16 KiB records:
**16/18**, with 13 and 23 drops respectively. No I2S write errors, allocation
failures, watchdog events or reboots are recorded. Each campaign contains
161 health observations. All four full TLS handshakes finish and playback
status continues at the expected 44.1 kHz stereo format.

{chr(10).join(table)}

The deltas cover the steady interval after the first 15 seconds and before
Stop. Every observed in-playback queue-drop increase is in the sample
interval surrounding/following the renegotiation request. `correlation.json`
retains exact before/after sample times relative to that request; these
sampled counters cannot establish the exact interrupt time or analog waveform.
Sampled free/largest blocks remain above the existing 16/8 KiB budgets.
SDK lifetime minimum free heap, including unobserved transients, is
{rows[0]['lifetime_minimum_free']:,} B for the initial campaign and
{rows[-1]['lifetime_minimum_free']:,} B for the comparison.

The four failures counted here are not four failed handshakes: there are
three failed output gates across four playback cases. Both reports preserve
their failures, and offline replay reproduces them without converting them
to PASS. Each controller restores the exact listened image and verifies
Wi-Fi, playlist, settings and stopped state before returning.

## Server and acceptance evidence

The saved application is the unchanged laboratory `idf61-quiet-growth-tls`,
SHA-256 `7871681aef75c9bb89caffab97f073eabe62b272ff8dc20f710cb4473c56b6fd`.
It has the same full compact AAC and 17,058-byte RX reservation as the prior
quiet tests, four input slots, and a 250..500 ms initial prefill. The test CA
extends normal roots, verification remains enabled, and no UART or optional
runtime profiler is used. No new firmware is compiled for these baseline runs.

The host server uses pyOpenSSL 26.4.0 / OpenSSL 4.0.3. TLS 1.2 and
`ECDHE-RSA-AES128-GCM-SHA256` are fixed, and session tickets and the session
cache are disabled. The same verified connection carries audio before and
after the request at 30 seconds. Delivery remains paced at 1.0 audio seconds
per wall second. No cipher, certificate check or AAC feature is removed.

Host tests check the real encrypted transfer against the original bytes and
a negative case where the client refuses renegotiation. OpenSSL emits a
HANDSHAKE_DONE callback for HelloRequest while renegotiation is pending;
the verifier requires a later callback with pending=false, the completed
renegotiation counter, and subsequent audio writes. That intermediate callback
alone is not proof of a handshake. The initial host-test failure identified
this distinction and is retained alongside the corrected passing tests.
See the [pyOpenSSL connection API](https://www.pyopenssl.org/en/stable/api/ssl.html#OpenSSL.SSL.Connection.renegotiate)
and [TLS 1.2 HelloRequest](https://www.rfc-editor.org/rfc/rfc5246.html#section-7.4.1.1).

## Interpretation and next experiment

This narrows the memory concern: the tested late handshakes fit with the full
HE-AAC/HE-AACv2 decoders alive. It does not establish a universal bound for
different certificates, groups, simultaneous clients or larger AAC frames.
The earlier 7,424-byte largest-block case remains separate evidence.

An output service interruption is now reproducible, rather than merely a
small-memory warning. Input starvation is a hypothesis: HE-AACv2 survives a
longer handshake at lower encoded bitrate, but both small and large HE-AAC
record modes fail. Those results do not prove that short records alone cause
the problem, or rule out scheduling/crypto effects.

`prefill_encoded_input()` retains the first decoder lease and waits at most
500 ms. It can exit once all input slots are occupied after only 250 ms;
occupation does not establish that every packet contains 2,048 audio bytes.
The SDK HTTP reader may return partial data (including data before a timeout).
The next isolated experiment sets only the minimum prefill to 500 ms, retaining
the current maximum, queue sizes, TLS record support, decoder precision and
stream-read timeouts. It is not a production-default change. Require new
measurements before attributing the failure to this mechanism or adopting it.

[Frozen baseline measurements and replay](../tests/results/esp32c3-tls-renegotiation-20261010/README.md).
'''
# Avoid suggesting the number of callback drops equals failed test cases.
doc=doc.replace('The four failures counted here are not four failed handshakes: there are\nthree failed output gates across four playback cases.',
                'There are three failed output gates across four playback cases; all four\nhandshakes themselves complete.')
Path('docs/ESP32C3_TLS_RENEGOTIATION_20261010.md').write_text(doc)
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-growth-tls')
(root/'firmware-manifest.json').write_bytes((art/'manifest.json').read_bytes())
(root/'requirements-tls-renegotiation.txt').write_bytes(Path('tools/audio_test_server/requirements-tls-renegotiation.txt').read_bytes())
(root/'README.md').write_text('''# Full TLS renegotiation: preserved output failures

Initial campaign: 17/18. HE-AAC record-size comparison: 16/18.
Both controllers restore the listened application and verify saved settings.

```text
python -B tests/results/esp32c3-tls-renegotiation-20261010/review.py
python -B tests/results/esp32c3-tls-renegotiation-20261010/review.py physical-comparison
```

Replay PASS reproduces the saved failures; it does not certify the firmware.
Numeric health/status, TLS handshake callbacks, completed writes, request
timing, dependency versions/hashes, test sources and restoration are retained.
Private keys and dependency installation contents are excluded. Only public
certificates and a local path to the existing test key are saved.

Host verification: two real renegotiation/refusal cases, four quiet gate
tests, and six existing record-server regressions. `host-renegotiation.log`
retains the initial callback-count assertion failure; `host-renegotiation-final.log`
is the corrected positive/negative result. Frozen module names identify the
final implementation; the initial failure is not represented as a passing run.

The firmware is reused from the AAC growth campaign; its full build audit is
in `../esp32c3-aac-growth-tls-20261010/`. Index hashes protect raw file bytes.
[Report](../../../docs/ESP32C3_TLS_RENEGOTIATION_20261010.md).
''')
print('Saved baseline report, correlations and replay instructions')
