# One-second input prefill: physical TLS renegotiation experiment

## Result

Physical acceptance: **34/34**. Failed checks: None.
All four measured playback windows have zero completion-queue drops and write errors. This supports testing one-second startup prefill in the normal-trust production candidate.
The option is **not adopted as a production default by this experiment**.

| Stream / TLS record | Handshake, ms | Queue drops: 500 / 1000 ms prefill | Write errors | Min free / largest, B | First observed PCM format, s | Max status + health, ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| he-44100-stereo:small | 680.8 | 6 / 0 | 0 | 30,424 / 19,456 | 2.42 | 223.8 |
| he-44100-stereo:large | 561.5 | 5 / 0 | 0 | 24,156 / 11,264 | 2.42 | 275.1 |
| hev2-44100-stereo:small | 628.5 | 8 / 0 | 0 | 24,096 / 18,432 | 2.39 | 213.5 |
| hev2-44100-stereo:large | 626.4 | 9 / 0 | 0 | 24,556 / 18,432 | 2.38 | 202.7 |

The campaign contains 316 health observations. SDK lifetime minimum
free heap is 17,480 bytes.
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
same size. App size is 1,456,304 bytes.

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

### Follow-up with normal public trust

The [normal-trust candidate](ESP32C3_PREFILL1000_QUIET_20261010.md) subsequently
passes 42/42 local multi-codec/lifecycle checks, 22/22 additional short output
windows and 15/15 OTA checks, including update during HE-AAC playback and
slow upload. Its 50 application objects and static RAM/IRAM sizes match this
laboratory image. Public HTTPS and the earlier memory-headroom scenario
remain separate pending qualification; production defaults are unchanged.

## Reproducibility and restoration

App SHA-256: `da17257c0d8a523ed4f6a758bc3f081ccda7c03d648463b39da7db6a0abae8d2`.
ELF SHA-256: `dfe8a8449af5e6d58c9b6234bcb1a12761b6407dd57c9c8b399ee03bece98bba`.
Verdicts are replayed from frozen raw measurements and test sources.
The controller restores the exact previously listened app by OTA, verifies
Wi-Fi/playlist/settings and confirms stopped playback in three observations.
Restored ELF: `76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`.

[Frozen evidence and replay](../tests/results/esp32c3-prefill1000-reneg-20261010/README.md).
