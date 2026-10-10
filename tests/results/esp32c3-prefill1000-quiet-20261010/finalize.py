"""Persist the completed normal-trust qualification without changing defaults."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill1000')
DOC = 'ESP32C3_PREFILL1000_QUIET_20261010.md'
ARCHIVE = 'esp32c3-prefill1000-quiet-20261010'
review = json.loads((ROOT / 'review.json').read_text())
windows = json.loads((ROOT / 'file-output-windows.json').read_text())
specs = json.loads((ROOT / 'fixture-specs.json').read_text())
assert review['replay'] == 'PASS' and review['exact_listened_image_restored']
assert windows['counts']['total'] == 22
manifest_path = ART / 'manifest.json'
manifest = json.loads(manifest_path.read_text())
assert hashlib.sha256((ART / 'app.bin').read_bytes()).hexdigest() == manifest['image']['sha256']
assert manifest['production_profile'] and not manifest['lab_ca']
assert json.loads((ROOT / 'laboratory-comparison.json').read_text())['identical_objects'] == 50
manifest.update(hardware_tested=True, production_qualified=False,
                qualification='Normal-trust local multi-codec and OTA qualification; public HTTPS/headroom still pending',
                physical_acceptance=review['phases'], finite_output_windows=windows['counts'],
                physical_report='docs/' + DOC)
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
(ROOT / 'firmware-manifest.json').write_bytes(manifest_path.read_bytes())

table = ['| Fixture | Format | File gates (auto / explicit) | Short output windows | Min free / largest, B | First observed PCM format, s |',
         '| --- | --- | --- | --- | ---: | ---: |']
grouped = {}
for name, row in windows['windows'].items():
    grouped.setdefault(row['fixture'], []).append(row)
for name, rows in grouped.items():
    spec = specs[name]
    verdicts = ' / '.join(r['original_gate'] for r in rows)
    output = ' / '.join(r['result'] for r in rows)
    measured = [r['health'] for r in rows if 'health' in r]
    memory = (f"{min(r['minimum_heap'] for r in measured):,} / {min(r['minimum_largest'] for r in measured):,}"
              if measured else 'unavailable')
    fmt = f"{spec.get('profile', spec['codec'])}, {spec['rate']} Hz, {spec['channels']} ch"
    starts = [r['first_full_pcm_seconds'] for r in rows if 'first_full_pcm_seconds' in r]
    latency = f'{min(starts):.2f}..{max(starts):.2f}' if starts else 'unavailable'
    table.append(f'| {name} | {fmt} | {verdicts} | {output} | {memory} | {latency} |')
phase_lines = '\n'.join(f"- {name}: **{p['passed']}/{p['total']}**; failed: " +
                        (', '.join(p['failures']) or 'none') + '.'
                        for name, p in review['phases'].items())
health = review['health']
idle = review['idle_medians']
doc = f'''# One-second prefill: normal-trust multi-codec and OTA qualification

## Results

{phase_lines}
- Additional short finite-file output windows: **{windows['counts']['passed']}/{windows['counts']['total']}**;
  failed: {', '.join(windows['failed']) or 'none'}.

{chr(10).join(table)}

The local campaign records {health['samples']} health observations with one
boot identity, {health['allocation_failures']} allocation failures and
{health['task_watchdog_events']} task-watchdog events. SDK lifetime minimum
free heap reaches {review['sdk_lifetime_minimum_heap']:,} bytes, including
transient setup. Sampled and lifetime minima are different measurements.
Settled free heap is {idle['initial']['heap']:,} B initially and
{idle['websocket']['heap']:,} B after the last suite; largest free capacity is
{idle['initial']['largest']:,} / {idle['websocket']['largest']:,} B, with
{idle['initial']['tasks']} / {idle['websocket']['tasks']} tasks.

## Scope

Local tests play eleven fixtures with automatic and explicit codec selection:
MP3, FLAC, Vorbis, Opus, AAC-LC, HE-AAC and HE-AACv2, including 22.05/44.1/48 kHz
and mono/stereo where fixtures cover them. They check finite EOF, AAC profile
and frequency transitions, immediate Stop/Play, recovery from truncated and
stalled delivery, HTTP errors, redirects, jitter, and WebSocket reconnection.

The extra output review pairs recorded status/health after a two-second warmup
in each finite playback batch, before its separate EOF observation. These are
short windows, not long stream or analog quality tests. Startup, Stop, EOF and
deliberate network-fault gaps are excluded. Raw counters and excluded periods
remain in the archive; they are not discarded or presented as zero.
The first full PCM format is a sampled WebUI observation, not a measurement
of the exact first DMA sample.

The OTA suite includes rejected malformed/wrong-target images, interrupted
uploads, two valid round trips, update during HE-AAC playback and a valid slow
upload (80 ms between 4096-byte chunks). The playing case requires three
consecutive correct HE-AAC PCM-format observations before uploading. It tests
safe update/boot/persistence, not uninterrupted sound while flash is written.
OTA deliberately restarts the board, so its checks are separate from the
single-boot local health campaign.

## Build identity and controls

The production-profile candidate has the normal public CA bundle with no
laboratory CA, quiet logging, awake operation, QIO 80 MHz and nominal fractional
48 kHz output. It retains four input packet slots, the 17,058-byte TLS RX reserve,
FLAC's conditional extra slots, output/decoder priorities 8/7 and full compact
AAC/SBR/PS. Minimum/maximum startup prefill are both 1000 ms.

All 50 application objects and linked static RAM/IRAM sizes match the
[successful laboratory candidate](ESP32C3_PREFILL1000_RENEGOTIATION_20261010.md).
The normal trust bundle matches the previous ordinary firmware; all 119
AAC/FLAC code/constant sections in 18 codec objects match its baseline.
App size: {manifest['image']['bytes']:,} bytes.
App SHA-256: `{manifest['image']['sha256']}`.
ELF SHA-256: `{manifest['image']['app_elf_sha256']}`.

## Remaining qualification

Production defaults are unchanged. These local HTTP and OTA checks do not
close the earlier real-HTTPS contiguous-memory headroom or response-time
failures. Next run public HTTPS stations on this exact image, then exercise
AAC frame growth and late TLS allocation pressure as needed. The separate
four-case laboratory renegotiation pass remains evidence for that specific
scenario, not for every network stall or AAC configuration.

The offline review reproduces {len(review['replayed_local_gates'])} local gates
from saved observations. WebSocket payload comparison, private settings
equality and OTA HTTP exchanges remain recorded live assertions; their
contents are not falsely described as replayed raw exchanges.

The controller restored the exact listened application by app-only OTA and
verified Wi-Fi, playlist and settings. Three final observations confirm
stopped playback. Restored ELF:
`76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`.

[Frozen evidence and replay](../tests/results/{ARCHIVE}/README.md).
'''
Path('docs', DOC).write_text(doc)
(ROOT / 'README.md').write_text(f'''# Normal-trust one-second prefill qualification

See [results and limitations](../../../docs/{DOC}). Production qualification
is still open. The exact previously listened app was restored after tests.

```text
python -B tests/results/{ARCHIVE}/review.py
python -B tests/results/{ARCHIVE}/inspect_file_windows.py
```

Review PASS means the recorded verdicts reproduce within the documented scope.
Raw evidence, source snapshots, build audit and restoration are preserved;
private settings and private keys are not saved. The build is available under
`firmware/development/{ART.name}/`.
''')
(ART / 'README.md').write_text(f'''# Normal-trust one-second prefill candidate

Ordinary public trust roots; no laboratory CA. Hardware-tested, but broader
production qualification is pending. [Results](../../../docs/{DOC}).
The previously listened firmware was restored after testing.
''')
logs = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-prefill1000/log')
for source in sorted(logs.iterdir()):
    if source.is_file():
        dest = ROOT / 'build-logs' / (source.name + '.log')
        dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(source.read_bytes())
print(json.dumps(dict(phases=review['phases'], output_windows=windows['counts'], restored=True)))
