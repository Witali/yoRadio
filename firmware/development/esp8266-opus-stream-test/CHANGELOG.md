# ESP8266 Opus: reduced scratch and live-stream diagnosis

## 2026-09-09

Application 910944 bytes, source f7b099a; SHA-256 and actual configuration in
manifest.json. OTA to app1 verified; no serial access or SPIFFS replacement.
CPU160, QIO40, I2S PDM32 GPIO3, two 512-word buffers. Opus remains experimental.

Changes: incremental HTTP response headers (real IntenseRadio 1049-byte header
now accepted), idle-PCM folding-buffer reuse, shorter PLC scratch lifetime,
6144-byte scratch / 1024-byte read-ahead, diagnostic-only init-failure snapshot.
Audio task stack remains 5120 bytes; observed minimum free 1780 bytes.

The actual Xtensa preprocessor selects FIXED_POINT=1, DISABLE_FLOAT_API=1,
OPUS_FAST_INT64=0. The target Opus archive has no unresolved software float/
double arithmetic, conversion, or floating libm calls. FLOAT_APPROX is present
in the inherited config but its floating arithmetic branch is inactive.

All five raw-RAM fixture fingerprints pass (ten measured rounds per case).
No audio HTTP/Ogg/normalization/PDM output runs inside the decode measurement;
task CPU still includes attributed interrupts and instrumentation.

| Input fixture | Task CPU budget | Maximum wall call | Scratch peak |
| --- | ---: | ---: | ---: |
| SILK mono12 | 58.61% | 13.400 ms | 1808 B |
| Hybrid mono24 | 93.17% | 23.112 ms | 2904 B |
| CELT stereo64 | 77.44% | 17.667 ms | 5488 B |
| CELT stereo128 | 96.02% | 22.242 ms | 5488 B |
| CELT stereo510 | 172.69% | 38.560 ms | 5488 B |

The 22 host phase/PLC tests were rerun: all PCM matches pristine generic32,
with a real 6144-byte capacity and immediate canaries. Maximum corpus scratch
5968 B; this is not a proof for every valid stream. Target pitch, zero-fill and
MDCT/FFT word-access guards also pass.

Normal radio playback is NOT qualified:

- Local HTTP stereo64 fixture: init failure stage 8, scratch allocation 6144 B
  failed with 6304 B total free DRAM before cleanup. A 25-second continuity
  observation correctly fails: no PCM. No failed interval is discarded.
- Real http://secure.live-streams.nl/opus.opus: headers now pass and decoder
  allocations/init succeed, but stage 10 rejects the remaining 1440 B DRAM
  against the unchanged 4096 B reserve. No audio is emitted.
- Web/API and OTA remain responsive. Wi-Fi RSSI about -56 dBm during diagnosis.

Ordinary playback includes the Ogg/native workspace and the active socket's
receive buffers, absent from the raw decoder measurement. Both whole-pipeline
RAM and remaining decoder/output CPU cost still need improvement. Reports in
this directory retain the successful benchmark and both failed stream tests.
