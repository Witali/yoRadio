"""Save the completed prefill experiment without promoting its firmware."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill500-reneg')
review = json.loads((ROOT / 'review.json').read_text())
assert review['replay'] == 'PASS' and review['exact_listened_image_restored']
report = json.loads((ROOT / 'physical/records/report.json').read_text())
health = json.loads((ROOT / 'physical/records/health.json').read_text())
audit = json.loads((ROOT / 'quiet-prefill500-reneg/build-audit.json').read_text())
assert audit['config_changes'] == {'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS': ['250', '500']}
assert audit['result'] == 'PASS'
objects = json.loads((ROOT / 'application-object-comparison.json').read_text())
assert objects['result'] == 'PASS' and objects['unchanged'] == 49

manifest_path = ART / 'manifest.json'
manifest = json.loads(manifest_path.read_text())
assert hashlib.sha256((ART / 'app.bin').read_bytes()).hexdigest() == manifest['image']['sha256']
manifest.update(hardware_tested=True, production_qualified=False,
                qualification='Completed four-case TLS renegotiation experiment; see physical_acceptance',
                physical_acceptance=review['counts'], physical_failures=review['failed_cases'],
                physical_report='docs/ESP32C3_PREFILL500_RENEGOTIATION_20261010.md')
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
(ROOT / 'firmware-manifest.json').write_bytes(manifest_path.read_bytes())

correlations = []
table = ['| Stream / record size | Handshake, ms | Queue drops / write errors | Min free / largest, B | Max status + health, ms |',
         '| --- | ---: | ---: | ---: | ---: |']
for name, window in review['windows'].items():
    request = report['record_observations'][name]['events'][0]['renegotiation_requests'][0]['at']
    changes = []
    for before, after in zip(health, health[1:]):
        delta = (after['output']['completion_queue_drops'] - before['output']['completion_queue_drops']) & 0xffffffff
        if delta and request - 5 < after['at'] < request + 10:
            changes.append(dict(from_request_seconds=[before['at'] - request, after['at'] - request], drops=delta))
    correlations.append(dict(name=name, output_event_intervals=changes))
    h, o = window['health'], window['output']
    table.append(f"| {name} | {window['renegotiation']['duration_ms']:.1f} | {o['completion_queue_drops']} / {o['write_errors']} | {h['minimum_heap']:,} / {h['minimum_largest']:,} | {window['maximum_status_health_ms']:.1f} |")
(ROOT / 'correlation.json').write_text(json.dumps(correlations, indent=2) + '\n')
counts = review['counts']
failed = ', '.join('`' + name + '`' for name in review['failed_cases']) or 'None'
doc = f'''# Minimum input prefill of 500 ms: TLS renegotiation experiment

## Result

Physical acceptance: **{counts['passed']}/{counts['total']}**.
Failed checks: {failed}.
The larger minimum startup prefill does not establish uninterrupted output
under TLS renegotiation and is **not adopted as a production default**.

{chr(10).join(table)}

The campaign contains {len(health)} health observations. SDK lifetime minimum
free heap is {min(h['minimum_heap'] for h in health):,} bytes.
All observations retain the same boot ID, with zero allocation failures,
watchdog events and I2S write errors. All four full renegotiations complete.
All verdicts are reproduced offline from the frozen measurements and test
sources. Replay PASS means the saved results, including failures, reproduce;
it does not mean physical acceptance passed.

## Controlled change and scope

Only `CONFIG_YORADIO_INPUT_PREFILL_MIN_MS` changes from 250 to 500 ms.
The maximum remains 500 ms. The four input slots, TLS reservation, decoder
precision, read timeout, scheduling priorities and nominal 48 kHz output
remain unchanged. All 119 AAC/FLAC code and constant sections in 18 objects
are identical to the baseline. Of 50 application objects, only
`audio_service.c.obj` changes; static IRAM, DRAM and RTC section sizes are
unchanged. Image size is 1,456,288 bytes, 64 bytes below the laboratory baseline.

Each case runs 75 seconds with a full, server-requested TLS 1.2 renegotiation
at 30 seconds, using either 1 KiB or 16 KiB records. Session cache and tickets
are disabled. Certificate verification stays enabled. HE-AAC and HE-AACv2
both use 44.1 kHz stereo fixtures. The test firmware includes a laboratory CA
and is not a release image.

Output deltas cover the steady interval after startup and before Stop.
They count lost I2S completion notifications, not measured missing analog
samples. `correlation.json` retains counter-change intervals near each
handshake; it cannot locate the exact ISR event or establish an audible gap.

## Comparison and conclusion

The [250..500 ms baseline](ESP32C3_TLS_RENEGOTIATION_20261010.md)
recorded HE-AAC queue-drop counts of 4 and 13 with 1 KiB records, and 23 with
16 KiB records. Its HE-AACv2 1 KiB case had zero. The present run is a bounded
comparison, not a statistical distribution of failures. Increasing startup
prefill alone is insufficient to qualify this path. Input starvation versus
CPU/scheduling delays during cryptography still requires causal measurement.

The exact previously listened application was restored by app-only OTA.
Wi-Fi, playlist and settings match their pre-test snapshot, and three
post-restoration observations confirm stopped playback. The restored ELF is
`76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`.

[Frozen evidence and replay](../tests/results/esp32c3-prefill500-reneg-20261010/README.md).
'''
Path('docs/ESP32C3_PREFILL500_RENEGOTIATION_20261010.md').write_text(doc)
(ROOT / 'README.md').write_text(f'''# 500 ms minimum prefill: physical TLS renegotiation comparison

Physical acceptance: {counts['passed']}/{counts['total']}. The candidate is not
production-qualified. Exact listened firmware and settings were restored.

```text
python -B tests/results/esp32c3-prefill500-reneg-20261010/review.py
```

Replay PASS reproduces the saved failures. The archive preserves build/source
identities, object comparison, public certificates, physical observations,
test sources and restoration. Private keys and installed packages are excluded.
The existing test key path appears only as a local reference.
Build artifacts are in `firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill500-reneg/`.

[Report](../../../docs/ESP32C3_PREFILL500_RENEGOTIATION_20261010.md).
''')
(ART / 'README.md').write_text('''# Laboratory prefill experiment

Not production-qualified. Contains a laboratory CA and a 500 ms minimum
startup input prefill. See the [physical report](../../../docs/ESP32C3_PREFILL500_RENEGOTIATION_20261010.md).
The controller restored the previously listened application after testing.
''')
build = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-prefill500-reneg/log')
for source in sorted(build.iterdir()):
    if source.is_file():
        dest = ROOT / 'build-logs' / (source.name + '.log')
        dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(source.read_bytes())
(ROOT / 'prepare_prefill.py').write_bytes(Path('.build/c3-tls-renegotiation-20261010/prepare_prefill.py').read_bytes())
print(json.dumps(dict(counts=counts, failed=review['failed_cases'], restored=True)))
