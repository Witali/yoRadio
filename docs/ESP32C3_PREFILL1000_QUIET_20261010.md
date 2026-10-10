# One-second prefill: normal-trust multi-codec and OTA qualification

## Results

- local: **42/42**; failed: none.
- ota: **15/15**; failed: none.
- Additional short finite-file output windows: **22/22**;
  failed: none.

| Fixture | Format | File gates (auto / explicit) | Short output windows | Min free / largest, B | First observed PCM format, s |
| --- | --- | --- | --- | ---: | ---: |
| mp3-320 | mp3, 48000 Hz, 2 ch | PASS / PASS | PASS / PASS | 79,592 / 65,536 | 1.23..1.24 |
| flac-level8 | flac, 48000 Hz, 2 ch | PASS / PASS | PASS / PASS | 59,472 / 45,056 | 1.23..1.52 |
| vorbis-q10 | vorbis, 48000 Hz, 2 ch | PASS / PASS | PASS / PASS | 66,192 / 51,200 | 1.22..1.23 |
| opus-510 | opus, 48000 Hz, 2 ch | PASS / PASS | PASS / PASS | 77,148 / 63,488 | 1.20..1.22 |
| aac-lc-320 | AAC-LC, 48000 Hz, 2 ch | PASS / PASS | PASS / PASS | 59,384 / 45,056 | 1.22..1.30 |
| lc-44100-stereo | AAC-LC, 44100 Hz, 2 ch | PASS / PASS | PASS / PASS | 59,716 / 43,008 | 1.23..1.23 |
| lc-22050-mono | AAC-LC, 22050 Hz, 1 ch | PASS / PASS | PASS / PASS | 59,616 / 45,056 | 1.21..1.22 |
| lc-48000-stereo | AAC-LC, 48000 Hz, 2 ch | PASS / PASS | PASS / PASS | 59,708 / 45,056 | 1.19..1.23 |
| he-44100-stereo | HE-AAC, 44100 Hz, 2 ch | PASS / PASS | PASS / PASS | 25,592 / 13,312 | 1.21..1.23 |
| he-48000-stereo | HE-AAC, 48000 Hz, 2 ch | PASS / PASS | PASS / PASS | 25,840 / 9,216 | 1.19..1.25 |
| hev2-44100-stereo | HE-AACv2, 44100 Hz, 2 ch | PASS / PASS | PASS / PASS | 25,892 / 14,336 | 1.20..1.25 |

The local campaign records 1070 health observations with one
boot identity, 0 allocation failures and
0 task-watchdog events. SDK lifetime minimum
free heap reaches 17,028 bytes, including
transient setup. Sampled and lifetime minima are different measurements.
Settled free heap is 139,984 B initially and
139,716 B after the last suite; largest free capacity is
114,688 / 114,688 B, with
16 / 16 tasks.

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
App size: 1,455,936 bytes.
App SHA-256: `e15c8a37a9c06a069e8146b00e305cb5aa176a52cfa4a1d7381fd8d9dca6754a`.
ELF SHA-256: `c313596b699973d3000b768edec9781848bd1741b033da765b6e0a40382c2cd5`.

## Remaining qualification

Follow-up: [public HTTPS qualification](ESP32C3_PREFILL1000_PUBLIC_20261010.md)
of this exact image passed 6/10 original gates. HE-AAC memory/output checks and
a public MP3 read failure remain unresolved; the local and OTA passes below
are not evidence that the overall goal is complete.

Production defaults are unchanged. These local HTTP and OTA checks do not
close the earlier real-HTTPS contiguous-memory headroom or response-time
failures. Next run public HTTPS stations on this exact image, then exercise
AAC frame growth and late TLS allocation pressure as needed. The separate
four-case laboratory renegotiation pass remains evidence for that specific
scenario, not for every network stall or AAC configuration.

The offline review reproduces 40 local gates
from saved observations. WebSocket payload comparison, private settings
equality and OTA HTTP exchanges remain recorded live assertions; their
contents are not falsely described as replayed raw exchanges.

The controller restored the exact listened application by app-only OTA and
verified Wi-Fi, playlist and settings. Three final observations confirm
stopped playback. Restored ELF:
`76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`.

[Frozen evidence and replay](../tests/results/esp32c3-prefill1000-quiet-20261010/README.md).
