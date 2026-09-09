# ESP8266 Opus: private-memory word-instruction A/B

## 2026-09-09

Application 910144 bytes, OTA to app0 verified. Configuration and binary SHA
are in manifest.json. This build includes the then-uncommitted word-access
experiment; comparison-results.json pins its actual memory helper/CMake source
hashes. No SPIFFS, playlist, credentials or UART access were changed by OTA.
The tested helper changes were subsequently committed as b89b4b1.

`YORADIO_OPUS_WORD_ASM=ON` uses explicit LX106 L32I/S32I for aligned private
decoder RAM and audited read-only mapped flash. Compiler memory clobbers retain
alias/order semantics; only hardware MEMW fences for these private accesses are
removed. MMIO, DMA publication and SDK volatile semantics are untouched. The
option defaults OFF and has a C fallback. Build with `-EnableOpus -OpusWordAsm`.

Two complete runs per variant, ten measured rounds per fixture per run:

| Fixed-point input | C mean CPU budget | Asm mean CPU budget | Speed change |
| --- | ---: | ---: | ---: |
| SILK mono12 | 58.60% | 59.56% | -1.63% |
| Hybrid mono24 | 93.15% | 92.56% | +0.63% |
| CELT stereo64 | 77.43% | 73.75% | +4.99% |
| CELT stereo128 | 96.05% | 91.37% | +5.12% |
| CELT stereo510 | 172.66% | 166.05% | +3.98% |

Every on-board PCM fingerprint matches the same pristine generic32 reference.
Scratch peaks (normal CELT5488), IRAM peak15600 and audio stack minimum free1780
remain unchanged. All22 host phase/PLC cases remain exact. Isolated target
tests verify full-width access, ordinary/asm alias ordering and no static RAM
or local stack growth; full firmware pitch/zero-fill/MDCT/FFT guards pass.

Task CPU includes attributed interrupts and measurement overhead; no network
audio, Ogg, normalization or PDM output is measured. This is a useful CELT
optimization, not a universal speedup: SILK is slightly slower. 128-kbit CELT
still has little margin for output, and 510-kbit CELT is not realtime.

Normal Opus radio remains unqualified because its active network/codec memory
leaves less than the protected4096-byte reserve. The previous stream-test
artifact records that failure. This CPU A/B does not lower the reserve or
claim continuous audio.
