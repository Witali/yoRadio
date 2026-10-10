# Public HTTPS file qualification, 2026-10-10

The exact `idf61-quiet-mpi-health` application was tested on the physical
ESP32-C3 with normal public trust roots. Original results are **13/15 PASS**.
Two format failures are retained in `physical/files/report.json`; both sampled
the container-detection state before the first decoded frame. A corrected
verifier passes all six file cases when replaying the same recorded data.
This is an offline correction, not a second physical campaign or an original
15/15 result. Firmware and acceptance thresholds were unchanged.

## Independent references and physical results

The host downloaded each public fixture over verified TLS and completely
decoded it with FFmpeg. `reference/` retains URLs, encoded and S16 PCM hashes,
frame counts, FFprobe output and tool versions. No media is committed.

| Case | Reference duration, s | Observed duration, s | Minimum steady free / largest, B | Maximum paired request, ms | Original / corrected offline |
| --- | ---: | ---: | ---: | ---: | --- |
| FLAC auto | 60.480 | 60.831 | 57,332 / 43,008 | 400 | PASS / PASS |
| FLAC explicit | 60.480 | 60.624 | 56,996 / 40,960 | 382 | PASS / PASS |
| Opus auto | 29.480 | 29.483 | 67,392 / 47,104 | 429 | FAIL / PASS |
| Opus explicit | 29.480 | 29.666 | 67,420 / 45,056 | 412 | PASS / PASS |
| Vorbis auto | 76.488 | 76.502 | 53,540 / 36,864 | 345 | PASS / PASS |
| Vorbis explicit | 76.488 | 76.552 | 54,076 / 38,912 | 405 | FAIL / PASS |

FLAC is 44.1 kHz stereo; Opus and Vorbis are 48 kHz stereo. The reference
output is signed 16-bit PCM. Board durations are status observations, with
polling and HTTP timing uncertainty; they are not exact output frame counts.

All **859 health observations** retain one boot identity, zero allocation
failures and zero task-watchdog events. Settled free heap is 140,116 B initially
and 139,708 B after each codec. The largest block remains 114,688 B, with
16 tasks. All recorded recovery checks pass.

## Why the original verifier failed

`audio_service.c` marks an opened connection as `audio=true`, then publishes
the container label when it sends the first compressed chunk. Rate/channels
are still zero until the decoder supplies stream information. Opus auto at
3.978 s and Vorbis explicit at 4.034 s each capture exactly one such `OGG`
sample. Subsequent decoded samples have the expected format until EOF.

The repair skips only the initial `connected`/expected-container prefix with
all five rate/channel/depth fields zero and both format flags false. It still
rejects incorrect nonzero metadata, the wrong container, lost metadata after
decoding starts, late decoding, stopped/resumed playback, early/missing EOF
and slow requests. Six host tests, including these fault cases, pass.
Original and corrected test sources are saved separately. See
`correction-commit.txt`, `host-tests.log` and `corrected-host-tests.log`.

## Image and restoration

- Candidate app SHA-256: `5505393d2b7d4fcad1303b3b96d9c41709c86a84e687bcbeb059a4241d243da6`.
- Candidate ELF SHA-256: `6524f1457d6009ee1c229e86bc64a2ff3361fd7df3810b1d2b652b9f0c2ce751`.
- Restored app: `idf61-listen48-8c1f2d`, partition `app0`.
- Restored ELF SHA-256: `76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`.
- Wi-Fi, playlist and settings comparisons all pass; three final observations
  confirm stopped playback. No serial recovery was used.

The controller exits 1 because the original suite failed. Its `finally` block
successfully restores the listened image; the failure record must not be
mistaken for failed restoration.

## Scope and remaining work

These observations qualify recorded format, duration, EOF, heap recovery,
fault counters and WebUI timing. They do not measure PCM accuracy, DMA
underruns or analog continuity. Finite HTTPS fixtures extend codec coverage;
they do not substitute for a ten-minute sustained playback test.

The earlier HE-AAC response-time and contiguous-headroom failures remain
open. `headroom-review.json` records seven consecutive 7,936-byte-largest
samples over 3.29 seconds, with no OOM. `reserve_frame()` may request up to
8,191 bytes; in-place realloc may succeed, so the shortfall is a risk rather
than proof of failure. A valid frame-growth fixture must be independently
decoded and tested after HE-AAC reaches steady memory use. Existing framing
tests use a mocked decoder and do not cover this real-audio combination.

`input-capacity-audit.json` records that five 1,600-byte configuration units
already round up to four 2,060-byte packet slots. Reducing a supposed
five-slot floor to four would be based on incorrect units.

## Offline replay

From the repository root, with the saved firmware artifacts available:

```powershell
python tests/results/esp32c3-public-files-20261010/review.py --output .build/public-files-replay/review.json
```

Use a fresh output path. The replay checks archive hashes, frozen controller
and tool sources, reference/image identities, both original failures, the
corrected file/health checks and exact restoration. It makes no network
requests and does not access the board. `index.json` hashes every archived
file except itself; `.gitattributes` preserves the original bytes.
