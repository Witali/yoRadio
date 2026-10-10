"""Save the measured one-second prefill experiment without promoting defaults."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill1000-reneg')
DOC = 'ESP32C3_PREFILL1000_RENEGOTIATION_20261010.md'
ARCHIVE = 'esp32c3-prefill1000-reneg-20261010'
review = json.loads((ROOT / 'review.json').read_text())
assert review['replay'] == 'PASS' and review['exact_listened_image_restored']
report = json.loads((ROOT / 'physical/records/report.json').read_text())
health = json.loads((ROOT / 'physical/records/health.json').read_text())
audit = json.loads((ROOT / 'quiet-prefill1000-reneg/build-audit.json').read_text())
assert audit['result'] == 'PASS'
assert audit['config_changes'] == {'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS': ['250', '1000'],
                                   'CONFIG_YORADIO_INPUT_PREFILL_MS': ['500', '1000']}
objects = json.loads((ROOT / 'application-object-comparison.json').read_text())
assert objects['result'] == 'PASS' and objects['unchanged'] == 48
assert json.loads((ROOT / 'output-and-ram-audit.json').read_text())['result'] == 'PASS'
host = json.loads((ROOT / 'host-prefill/report.json').read_text())
assert len(host['variants']) == 18
assert all(v['result'] == 'PASS' for v in host['variants'].values())
assert sum(v['cases'] for v in host['variants'].values()) == 198
counts = review['counts']
assert counts['total'] == 34
manifest_path = ART / 'manifest.json'
manifest = json.loads(manifest_path.read_text())
assert hashlib.sha256((ART / 'app.bin').read_bytes()).hexdigest() == manifest['image']['sha256']
manifest.update(hardware_tested=True, production_qualified=False,
                qualification='Four-case laboratory TLS renegotiation experiment; broader qualification pending',
                physical_acceptance=counts, physical_failures=review['failed_cases'],
                physical_report='docs/' + DOC)
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
(ROOT / 'firmware-manifest.json').write_bytes(manifest_path.read_bytes())

prior = json.loads(Path('tests/results/esp32c3-prefill500-reneg-20261010/review.json').read_text())
comparison, correlations = {}, []
table = ['| Stream / TLS record | Handshake, ms | Queue drops: 500 / 1000 ms prefill | Write errors | Min free / largest, B | First observed PCM format, s | Max status + health, ms |',
         '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
for name, window in review['windows'].items():
    request = report['record_observations'][name]['events'][0]['renegotiation_requests'][0]['at']
    changes = []
    for before, after in zip(health, health[1:]):
        delta = (after['output']['completion_queue_drops'] - before['output']['completion_queue_drops']) & 0xffffffff
        if delta and request - 5 < after['at'] < request + 10:
            changes.append(dict(from_request_seconds=[before['at'] - request, after['at'] - request], drops=delta))
    correlations.append(dict(name=name, output_event_intervals=changes))
    old = prior['windows'][name]
    comparison[name] = dict(prefill500=old, prefill1000=window)
    h, o = window['health'], window['output']
    table.append(f"| {name} | {window['renegotiation']['duration_ms']:.1f} | {old['output']['completion_queue_drops']} / {o['completion_queue_drops']} | {o['write_errors']} | {h['minimum_heap']:,} / {h['minimum_largest']:,} | {window['format']['first_full_pcm_seconds']:.2f} | {window['maximum_status_health_ms']:.1f} |")
(ROOT / 'correlation.json').write_text(json.dumps(correlations, indent=2) + '\n')
(ROOT / 'comparison.json').write_text(json.dumps(comparison, indent=2) + '\n')
failed = ', '.join('`' + name + '`' for name in review['failed_cases']) or 'None'
conclusion = ('All four measured playback windows have zero completion-queue drops and write errors. '
              'This supports testing one-second startup prefill in the normal-trust production candidate.'
              if not review['failed_cases'] else
              'The one-second prefill does not pass every acceptance gate. Keep the failed cases and investigate before changing production defaults.')
doc = f'''# One-second input prefill: physical TLS renegotiation experiment

## Result

Physical acceptance: **{counts['passed']}/{counts['total']}**. Failed checks: {failed}.
{conclusion}
The option is **not adopted as a production default by this experiment**.

{chr(10).join(table)}

The campaign contains {len(health)} health observations. SDK lifetime minimum
free heap is {min(h['minimum_heap'] for h in health):,} bytes.
Lifetime health and individual output checks are preserved in the replay;
startup/idle counter increments are excluded from steady playback deltas.
First observed PCM format is sampled WebUI telemetry, not the exact time of
the first DMA sample. The comparisons are separate bounded campaigns, not
paired measurements under identical Wi-Fi timing or a failure-rate estimate.

## Controlled change

The minimum and maximum input-prefill times change from 250/500 to 1000/1000 ms.
Four input packet slots, the 17,058-byte TLS RX reserve, PCM capacity,
output/decoder priorities 8/7, full-rate compact AAC, read timeout and
fractional nominal 48 kHz output remain unchanged. The optional pipeline
probe is disabled. No new buffer is allocated for the added wait.

All 119 nonempty AAC/FLAC code and constant sections in 18 objects match the
control. Of 50 application objects, 48 match; audio_service changes for
prefill, and native_audio_output differs only in an ESP_ERROR_CHECK source
line number (599 to 606). Every linked static IRAM/DRAM/RTC section has the
same size. App size is {manifest['image']['bytes']:,} bytes.

The actual prefill C function passes 198 ASan/UBSan cases in 18 variants,
including prompt Stop/generation cancellation, full/slow input, deadlines,
timer wrap and reduced adaptive capacity. These are deterministic host tests,
not a substitute for physical decoder integration or a measured Stop latency.

## Physical scope and limitations

Four cases run for 75 seconds each: HE-AAC and HE-AACv2 at 44.1 kHz stereo,
with 1 KiB and 16 KiB TLS records. Audio is supplied at 1.0 times real-time
rate. At 30 seconds the server requests a full TLS 1.2 renegotiation, with
session cache and tickets disabled. Certificate verification remains enabled;
the laboratory firmware adds one test CA to the normal public roots.

Output counters record lost I2S completion notifications and write errors,
not an analog recording or a count of audible gaps. The earlier diagnostic
[attributes the observed stall to upstream input starvation](ESP32C3_PIPELINE_PROBE_20261010.md).
Longer prefill is a candidate mitigation for this measured pause, not a
guarantee against arbitrary network outages. The earlier
[HE-AAC contiguous-memory headroom failure](ESP32C3_AAC_TLS_HEADROOM_20261010.md)
is not closed by these different fixtures.

Next: qualify the same prefill with normal public trust, all supported codecs,
EOF/Stop/switching/network recovery, real HTTPS playback and AAC frame growth.
Keep the existing memory and output gates; do not qualify the firmware from
these four cases alone.

## Reproducibility and restoration

App SHA-256: `{manifest['image']['sha256']}`.
ELF SHA-256: `{manifest['image']['app_elf_sha256']}`.
Verdicts are replayed from frozen raw measurements and test sources.
The controller restores the exact previously listened app by OTA, verifies
Wi-Fi/playlist/settings and confirms stopped playback in three observations.
Restored ELF: `76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`.

[Frozen evidence and replay](../tests/results/{ARCHIVE}/README.md).
'''
Path('docs', DOC).write_text(doc)
(ROOT / 'README.md').write_text(f'''# One-second input prefill: physical TLS renegotiation

Physical acceptance: {counts['passed']}/{counts['total']}. Production qualification is pending.
Exact listened firmware and settings were restored after the campaign.

```text
python -B tests/results/{ARCHIVE}/review.py
```

Replay PASS means all saved verdicts reproduce, including any failed checks.
The archive contains source/build identities, host tests, measurements,
public certificates and restoration evidence. Private keys and dependencies
are excluded. Firmware: `firmware/development/{ART.name}/`.

[Report](../../../docs/{DOC}).
''')
(ART / 'README.md').write_text(f'''# Laboratory one-second prefill candidate

Not production-qualified. Includes a laboratory CA and 1000 ms minimum/maximum
startup prefill. [Physical report](../../../docs/{DOC}).
The controller restored the previously listened firmware after testing.
''')
build = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-prefill1000-reneg/log')
for source in sorted(build.iterdir()):
    if source.is_file():
        dest = ROOT / 'build-logs' / (source.name + '.log')
        dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(source.read_bytes())
print(json.dumps(dict(counts=counts, failed=review['failed_cases'], restored=True)))
