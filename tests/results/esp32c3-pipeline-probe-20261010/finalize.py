"""Record the measured pipeline stall and restore evidence without qualifying it."""
import json,shutil
from pathlib import Path
root=Path(__file__).resolve().parent
artifact=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-pipeline-probe')
review=json.loads((root/'review.json').read_text())
analysis=json.loads((root/'pipeline-analysis.json').read_text())
assert review['exact_listened_image_restored'] and review['replay']=='PASS'
assert review['counts']==dict(passed=17,total=18)
large=analysis['he-44100-stereo:large']
assert large['phase_drops']==[0,2,0,0,0,0,0,15]
assert large['retained_events']==16 and large['overwritten_events']==1
assert max(e['ages_ms']['output_checkpoint'] for e in large['events'])==4.735
health=json.loads((root/'physical-walltime/records/health.json').read_text())
table=['| TLS record size | Full renegotiation, ms | Steady queue drops / write errors | Min free / largest, B |',
       '| --- | ---: | ---: | ---: |']
for name,w in review['windows'].items():
    table.append(f"| {name.split(':')[1]} | {w['renegotiation']['duration_ms']:.1f} | {w['output']['completion_queue_drops']} / {w['output']['write_errors']} | {w['health']['minimum_heap']:,} / {w['health']['minimum_largest']:,} |")
doc=f'''# DMA overrun diagnosis during HE-AAC TLS renegotiation

## Finding: the observed output task remains responsive while PCM runs out

The diagnostic firmware completes **17/18** checks on physical ESP32-C3.
Both 75-second cases play HE-AAC 44.1 kHz stereo and request a full TLS 1.2
renegotiation at 30 seconds. The 1 KiB case has no steady output events;
the 16 KiB case has 17 I2S completion-queue drops. All handshakes finish.

{chr(10).join(table)}

The phase histogram captures all 17 events. At 15 of them, output is inside
PCM receive, the decoder is inside encoded-input receive, and the network
task is inside HTTP body read (phase 7). At the remaining two, output still
waits for PCM but the decoder/network have left those receive/read calls
(phase 1). Call phases alone do not establish scheduler state.

The last 16 events retain full timestamps; **one older event was overwritten**.
For those 16, output's latest queue checkpoint is only **0.058..4.735 ms** old.
It is being scheduled at the normal approximately 5 ms empty-queue polling
interval. Its latest accepted PCM packet is **53.166..213.172 ms** old.
During the retained phase-7 events, the latest encoded packet is
350.989..489.661 ms old and the latest successful HTTP read is
1,359.252..1,497.924 ms old. In the final two events, fresh input and a positive
HTTP read have returned 5..16 ms earlier, while output still awaits PCM.

For this captured stall, the evidence supports exhaustion of buffered audio
during the TLS read pause, followed by decoder refill. It does not support
raising output priority as the remedy: the output task already gets CPU time.
The counters are not an analog waveform capture or an exact audible-gap count.

## Qualification and next change

There are {len(health)} health observations with one boot identity, zero
allocation failures, zero watchdog events and zero I2S write errors.
The SDK lifetime minimum free heap is {min(h['minimum_heap'] for h in health):,} B.
The two runs do not make the firmware production-qualified, and do not erase
earlier quiet-image output failures or contiguous-memory headroom failures.

The baseline uses a 250..500 ms startup prefill. In
`prefill_encoded_input()`, a full input queue permits departure after only
250 ms; slower arrival can extend it to 500 ms. Large TLS records can fill
the queue in a burst. That code path is consistent with the large-record
failure despite its shorter handshake, but these probes do not directly
measure prefill duration or queued audio duration.

Next controlled experiment: require 1,000 ms minimum and maximum startup
prefill, retaining queue capacities, TLS support, decoder arithmetic and task
priorities. Measure actual startup latency and rerun both record sizes and
HE-AACv2. Do not adopt it by default solely because these cases improve:
higher bitrates, other codecs, memory headroom and recovery still need checks.
This is a buffering hypothesis to test, not a completed repair.

## Diagnostic implementation and audit

The optional probe uses 516 static bytes; alignment makes the linked DRAM
data-section increase 512 bytes. IRAM text grows by 132 bytes and stays within
the previous reserved aligned region. The full image is 1,457,952 bytes.
All 119 AAC/FLAC code/constant sections in 18 objects match the prior baseline.
Of 50 application objects, only audio_service, native_audio_output and
web_service change. TLS roots and the 17,058-byte RX reservation are unchanged.

With the option disabled, recompiled text/data sizes do not grow. Sections
match the quiet baseline except the verified source line and Windows path
spelling in the suspend error diagnostic. No playback code difference is
waived by that check. Host ASan/UBSan tests cover phase/history/counter wrap,
bounded JSON, and unchanged Stop/EOF ownership behavior.

An initial implementation used the CPU cycle counter. It was replaced before
the measured playback campaign because C3 stops that counter during WFI;
see [TRM mpcER/CYCLE](https://espressif.com/sites/default/files/documentation/esp32-c3_technical_reference_manual_en.pdf#page=39).
The final implementation uses the hardware system timer through
[`esp_timer_get_time()`](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/api-reference/system/esp_timer.html#obtaining-current-time).
Linked overrun, timer read, HAL counter read and conversion functions are all
in IRAM. The first controller invocation used an invalid `--name` argument,
exited before audio collection, and restored the board. Its failure and
restoration are preserved separately; they are not counted as playback tests.

The final controller restores the exact listened application ELF
`76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`.
Wi-Fi, playlist and settings remain unchanged. Three final observations
confirm stopped playback. Diagnostic firmware is laboratory-only and contains
a test CA; it is not left on the board.

[Probe interpretation](ESP32C3_PIPELINE_DIAGNOSTICS.md).
[Frozen evidence and replay](../tests/results/esp32c3-pipeline-probe-20261010/README.md).
'''
Path('docs/ESP32C3_PIPELINE_PROBE_20261010.md').write_text(doc)
manifest_path=artifact/'manifest.json'
manifest=json.loads(manifest_path.read_text())
manifest.update(hardware_tested=True,production_qualified=False,
    qualification='17/18 diagnostic TLS renegotiation checks; large-record output queue starvation observed',
    physical_report='docs/ESP32C3_PIPELINE_PROBE_20261010.md',
    diagnostic_timebase='esp_timer microseconds, modulo 2^32',
    physical_acceptance=review['counts'],physical_failures=review['failed_cases'])
manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
(root/'firmware-manifest.json').write_bytes(manifest_path.read_bytes())
(artifact/'README.md').write_text('''# Laboratory pipeline diagnostic firmware

Not production-qualified. Includes a laboratory TLS CA and optional 516-byte
DMA checkpoint probe. The listened image was restored after testing.
[Results](../../../docs/ESP32C3_PIPELINE_PROBE_20261010.md).
''')
(root/'README.md').write_text('''# HE-AAC TLS pause: PCM starvation with responsive output task

Physical result: 17/18; the 16 KiB record case has 17 output queue drops.
Sixteen detailed events remain; one was overwritten, and the phase histogram
retains all 17. Replay PASS reproduces the saved failure, not production acceptance.

```text
python -B tests/results/esp32c3-pipeline-probe-20261010/review.py
python -B tests/results/esp32c3-pipeline-probe-20261010/analyze.py
```

`physical-walltime/` is the measured final campaign and exact restoration.
`physical/` and `initial-cycles/` retain the earlier CLI-argument failure,
initial cycle-counter build and restoration. No playback result is inferred
from that aborted invocation. The final system-timer source and build audit
are separate from the initial cycle-counter files.

The archive includes frozen source, raw numeric health/status, encrypted
record metadata, source/build audits, host sanitizer evidence and public
certificates. Private keys, package installations and temporary binaries are
excluded. Local key paths are references only. The saved development app is
in `firmware/development/esp32c3-idf-6.1-r9a97-quiet-pipeline-probe/`.

[Report](../../../docs/ESP32C3_PIPELINE_PROBE_20261010.md).
''')
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-pipeline-probe/log')
for source in build.iterdir():
    if source.is_file():
        dest=root/'build-logs'/(source.name+'.log');dest.parent.mkdir(exist_ok=True)
        shutil.copyfile(source,dest)
for name in ('production-health-native','c3-pipeline-walltime-boundaries-20261010'):
    source_root=Path('.build')/name
    for source in source_root.rglob('*'):
        if not source.is_file() or source.suffix not in ('.json','.log','.c','.h','.py'):continue
        if name=='production-health-native' and '-probe' not in source.name and source.name!='report.json':continue
        dest=root/'host-tests'/name/source.relative_to(source_root);dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
for name in ('test-pipeline-health.py','test-production-health.py','test-production-health-native.py','run-output-task-boundaries.py'):
    dest=root/'host-test-sources'/name;dest.parent.mkdir(exist_ok=True)
    shutil.copyfile(Path('tests')/name,dest)
print('Saved diagnostic findings, build/host evidence and verified restoration')
