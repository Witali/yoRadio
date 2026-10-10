"""Save public qualification, retaining failed gates and previous results."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill1000')
ARCHIVE = 'esp32c3-prefill1000-public-20261010'
DOC = 'ESP32C3_PREFILL1000_PUBLIC_20261010.md'
review = json.loads((ROOT / 'review.json').read_text())
assert review['review'] == 'PASS' and review['exact_listened_image_restored']
assert len(review['windows']) == 5
manifest_path = ART / 'manifest.json'
manifest = json.loads(manifest_path.read_text())
before = json.loads((ROOT / 'firmware-manifest-before.json').read_text())
assert hashlib.sha256((ART / 'app.bin').read_bytes()).hexdigest() == before['image']['sha256']
assert manifest['image'] == before['image']
assert manifest['physical_acceptance'] == before['physical_acceptance']
assert manifest['finite_output_windows'] == before['finite_output_windows']
manifest.update(production_qualified=False,
    qualification='Local and OTA gates pass; public HTTPS retains memory and playback/output failures',
    public_acceptance=dict(**review['original_acceptance'], failures=review['original_failures']),
    public_report='docs/' + DOC)
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
(ROOT / 'firmware-manifest.json').write_bytes(manifest_path.read_bytes())

table = ['| Public variant | Reference PCM | Original gate | Min free / largest, B | Lost I2S notifications / write errors | Max status + health, ms |',
         '| --- | --- | --- | ---: | ---: | ---: |']
for name, window in review['windows'].items():
    assert window.get('result') != 'INCOMPLETE'
    s, h, o = window['spec'], window['health'], window['output']
    table.append(f"| {name} | {s.get('profile') or s['codec']}, {s['rate']} Hz, {s['channels']} ch | "
                 f"{window['original']['result']} | {h['minimum_heap']:,} / {h['minimum_largest']:,} | "
                 f"{o['completion_queue_drops']} / {o['write_errors']} | {window['maximum_status_health_ms']:.2f} |")
failures = '\n'.join(f"- `{f['name']}`: {f['reason']}." for f in review['original_failures'])
health, idle = review['lifetime_health'], review['idle_medians']
details = {}
for batch in json.loads((ROOT / 'physical/public/status.json').read_text()):
    if not batch['case'].startswith('https:'):
        continue
    states = batch['samples']
    first = next((s['seconds'] for s in states if s['audio']), None)
    after = [s for s in states if first is not None and s['seconds'] > first and not s['audio']]
    details[batch['case']] = dict(total_samples=len(states), playing_samples=sum(s['audio'] for s in states),
        first_playing_seconds=first, first_not_playing_after_start=after[0] if after else None,
        final_state=states[-1])
(ROOT / 'playback-detail.json').write_text(json.dumps(details, indent=2) + '\n')
mp3 = details['https:groovesalad-256-mp3']
document = f'''# One-second prefill: public HTTPS qualification

## Decision

The overall playback/memory-stability goal remains open. The exact normal-trust
candidate passed **{review['original_acceptance']['passed']}/{review['original_acceptance']['total']}**
original gates in this campaign. Retain the failed checks; do not promote the
candidate to production defaults on the strength of local playback and OTA alone.

{failures}

## Physical observations

Five live HTTPS variants of SomaFM Groove Salad were observed for 60 seconds
each. These are five bitrate/codec variants, not five independent stations.
FFprobe and the unquantized FAAD reference independently identify the source
format; they do not establish sample-for-sample identity or analog audio quality.
TLS certificate verification is enabled. Public audio is not archived.

{chr(10).join(table)}

The table's memory/output observations use the supplementary paired window
after a 15-second warmup. Original live verdicts remain unchanged. Their memory
cutoff starts just before Play, whereas the supplementary cutoff starts with
the observation batch just after Play. A borderline early sample can therefore
produce different trend verdicts. The exact pre-Play timestamp was not retained;
the supplementary calculation is not an exact replay of the original gate.

There are {health['samples']} health observations, {health['allocation_failures']}
registered allocation failures and {health['task_watchdog_events']} watchdog
events. The SDK lifetime minimum free heap is {review['sdk_lifetime_minimum_heap']:,} B,
including transient setup. This differs from sampled steady-state minima.
Idle recovery gate: **{review['recovery']['result']}**. Settled free heap changes
from {idle['initial']['heap']:,} to {idle['public']['heap']:,} B; largest free block
from {idle['initial']['largest']:,} to {idle['public']['largest']:,} B;
task counts are {idle['initial']['tasks']} and {idle['public']['tasks']}.

An in-playback heap decline alone does not prove a leak: queued network data and
deferred allocations can also consume RAM. Recovery after Stop and bounded
steady-state behaviour must be distinguished from progressive unrecovered loss.
The existing gates remain 16,384 B free / 8,192 B contiguous, with median start/end
loss tolerances of 2,048 B free / 4,096 B contiguous. No threshold was relaxed.

## Previous evidence and next work

The same image already passed [42/42 local gates, 22/22 short output windows and
15/15 OTA gates](ESP32C3_PREFILL1000_QUIET_20261010.md). The corresponding
[laboratory image passed 34/34 TLS-renegotiation gates](ESP32C3_PREFILL1000_RENEGOTIATION_20261010.md).
Those results remain valid for their recorded scenarios; they do not erase
the public memory failures above.

The supplementary output check also fails for HE-AAC 64 kbit/s: 56 I2S completion
notifications were lost during the measured window. These counters are not a
count of missing PCM samples or audible clicks. MP3 reports playing in
{mp3['playing_samples']}/{mp3['total_samples']} observations and ends with
`{mp3['final_state']['format']}`. Its output-window counter includes the subsequent
non-playing interval, so it must not be presented as thousands of audible gaps
during successful playback. The source/network/firmware cause is not established.

Next diagnose the HE-AAC output notifications and MP3 read failure, and isolate
the live HE-AAC memory trajectory and contiguous headroom, separating
bounded TCP/TLS occupancy from retained allocations. Repeat the failing cases on
any proposed fix and preserve local/OTA/format coverage. The goal should close
only after the remaining concrete qualification failures are resolved.

## Identity and restoration

App SHA-256: `{manifest['image']['sha256']}`.
ELF SHA-256: `{manifest['image']['app_elf_sha256']}`.
No application source, codec arithmetic or build default changed in this campaign.
The [previous archive](../tests/results/esp32c3-prefill1000-quiet-20261010/README.md)
contains the build source/configuration audit; its index hash is referenced here.

The controller restored the exact listened application by app-only OTA,
verified settings/Wi-Fi/playlist equality and recorded three stopped states.
Private settings and credentials are not serialized in the evidence.

[Frozen evidence and review](../tests/results/{ARCHIVE}/README.md).
'''
Path('docs', DOC).write_text(document, encoding='utf-8')
(ROOT / 'README.md').write_text(f'''# Public HTTPS evidence for one-second prefill

See [the report](../../../docs/{DOC}). Original acceptance failures are retained.
`review.json` saying `review: PASS` means that evidence/identity/restoration checks
succeeded, not that the firmware passed all acceptance gates.

`physical/` contains original observations and controller restoration evidence.
`test-sources/` freezes the exact runner sources. `prior-build/` references the
previous committed build audit instead of duplicating the build.
`firmware-manifest-before.json` and `firmware-manifest.json` retain earlier gates.

From the repository root, replay without board access:

```text
python -B tests/results/{ARCHIVE}/review.py
python -B tests/results/{ARCHIVE}/verify_commit.py
```

`index.json` records byte sizes and SHA-256; `.gitattributes` prevents conversion.
Network/OTA/private-settings equality checks remain recorded live assertions.
The controller script requires a reachable board and changes firmware; do not
run it as part of offline review. Public audio and private keys are not included.
''', encoding='utf-8')
print('Saved public qualification and preserved earlier local/OTA results')
