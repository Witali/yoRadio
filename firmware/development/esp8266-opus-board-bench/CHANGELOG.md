# Experimental Opus board benchmark

## 2026-09-09 — word-only MDCT/FFT flash reads

OTA to app0 verified. Current artifact: 908768 bytes; see manifest for SHA.
All five PCM fingerprints still match. No scratch borrowing in this build.

| Input fixture | Before CPU | After CPU | Maximum call after |
| --- | ---: | ---: | ---: |
| SILK mono12 | 58.88% | 58.62% | 14.046 ms |
| Hybrid mono24 | 115.62% | 92.98% | 20.319 ms |
| CELT stereo64 | 99.11% | 75.85% | 17.011 ms |
| CELT stereo128 | 120.55% | 94.73% | 21.620 ms |
| CELT stereo510 | 198.72% | 175.44% | 38.037 ms |

Audio stack now 5120 B, minimum free 1772 B. Read-ahead in THIS binary is
still 1536 B: the existing SDK configuration retained its previous value.
Manifest corrected to the actual sdkconfig; the builder now rejects this
stale configuration instead of silently claiming 1024 B. The next variant
must be configured freshly. This does not affect raw benchmark input (1536 B).
Scratch reservation 7680 B; normal streaming still fails decoder initialization.
Wi-Fi RSSI around -48 dBm, stopped free IRAM 28 B.

Actual Intense Radio response has 1049 header bytes, exceeding the old whole-
header limit 1023: it fails before decoder initialization. A local fixture with
short headers reaches decoder initialization but does not yet start playback.
Neither error is discarded from the acceptance results.

`board-results.json` / `ota-results.json` describe this artifact;
`baseline-results.json` retains the previous CPU run. No production qualification.

## 2026-09-09 — generic32 reference, first complete physical run

OTA-only application update verified on Wemos D1 mini at 192.168.100.6.
Current binary: see `manifest.json` for SHA-256, configuration and source hashes.
CPU 160 MHz, QIO40, I2S PDM32 GPIO3; application-only OTA preserves SPIFFS.
The raw benchmark deliberately does not send PCM to the output.

Corrected the host golden arithmetic to `OPUS_FAST_INT64=0`, matching Xtensa.
All five on-board PCM fingerprints pass. This does NOT yet qualify Opus
radio playback: several decoder modes exceed the realtime CPU budget.

| Input fixture | Decoder task CPU budget | Maximum call | Scratch DRAM peak | IRAM peak |
| --- | ---: | ---: | ---: | ---: |
| SILK mono 12 kbit/s | 58.88% | 13.525 ms | 1808 B | 14112 B |
| Hybrid mono 24 kbit/s | 115.62% | 25.073 ms | 2904 B | 15600 B |
| CELT stereo 64 kbit/s | 99.11% | 23.395 ms | 6736 B | 15600 B |
| CELT stereo 128 kbit/s | 120.55% | 27.810 ms | 6736 B | 15600 B |
| CELT stereo 510 kbit/s | 198.72% | 42.761 ms | 6736 B | 15600 B |

Each row measures 120 packets / 2.4 seconds of mono 48-kHz PCM after warmup.
Task time excludes other tasks but includes attributed interrupt time and
instrumentation (empty interval 12 us). Wi-Fi stays connected; no network audio,
Ogg demux, normalization or PDM generation is inside the measured interval.
Task stack: 6144 B, minimum free watermark across all cases 2788 B.
DRAM: 20264 B before, 21168 B after (other system activity can release memory),
minimum observed in a measured case 2376 B. Decoder state 6582 B; scratch
reservation remains 7680 B, not just the observed per-case peak.

`board-results.json`, `ota-results.json` and `fixtures-manifest.json` retain
the physical evidence. `first-host64-reference.json` preserves the earlier
failed fingerprint run: the target PCM matched the generic32 reference exactly;
host64 used a different stock fixed-point multiply in the CELT VQ path.

Remaining: reduce decoder CPU cost and normal streaming memory, then verify
at least 20 seconds of real Opus radio with no DMA underruns and working WebUI.
