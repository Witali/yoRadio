# 2026-09-06 — Bit-exact RCPDM speed experiments

## Simple32 Xtensa LX106 assembly with portable C fallback

`production-simple-lx106-asm` and `simple-simple-lx106-asm`: CPU160/QIO40,
alpha=1/16, 48-kHz PCM, GPIO3, 32 bits/sample, 2x512 DMA words, batch output.
Diagnostic images without Wi-Fi, WebUI or codecs; not ordinary radio.

- Predictive: 128592 bytes, SHA256
  `58F6F8D7519CA9A53DFE4A8B7E174771D339A6FFB5EEECF523620CCC938FFB7C`.
- Simple asm: 129424 bytes, SHA256
  `EEE154709076F5A17AE69CE4D178EAAF4875BFC75171D19126EDD4420E28239C`.
- Pack 48000 words: 112275 vs 107177 us; previous literal Simple C 139047 us.
- Producer excluding DMA wait: 122843 vs 120053 us/audio-second; previous
  literal Simple C 155637 us. These are not total CPU utilization figures.
- ASM backend confirmed in UART; scalar 493216, batch 2144 and dispatch
  240 comparisons passed per Simple boot. No DMA errors or additional RAM.
- Portable C retained; only ESP8266/Xtensa alpha=1/16 selects ASM. Other
  targets/coefficients and `RCPDM_SIMPLE_FORCE_C=1` select C.

Implementation `7f62157`, built as a working change over `c62decd`.
The diagnostic image includes new dispatch checks/logs; scalar/batch packers
shrank to 45/175 bytes. All 21 host tests passed. Exact original native PDM32
app0 restored from a fresh private backup; boot, DHCP and HTTP 200 verified.
[Report](../../../docs/benchmarks/esp8266-rcpdm-simple-lx106-asm-2026-09-06/README.md).

## Literal Simple32 charge/discharge loop

`production-simple-literal` and `simple-simple-literal` are isolated images
built from the Simple change `7dfc1af`. The readable `UINT32_MAX - state`
expression is retained; GCC already compiles it as bitwise inversion.
Same CPU160/QIO40, 48-kHz PCM, alpha=1/16, 32 bits/sample, GPIO3 and 2x512
DMA words. No Wi-Fi, WebUI or codecs in these diagnostic binaries.

- Predictive: 128592 bytes, SHA256
  `3F6FC789721E1EE7EA8E1A83ADCCD59198F514C248410FF9EA450C7997B550C3`.
- Literal Simple: 128816 bytes, SHA256
  `E8BBBE57E4C92894BC7C9BE3099452EDFF70769B477EC5C4CF7246412950791C`.
- Physical ABBA: pack 48000 words 112275 vs 139047 us (+23.85% for Simple).
- Producer excluding DMA wait: 122843 vs 155637 us/audio-second (+26.70%).
  This is not total CPU utilization. Previous one-branch Simple: 126617 /
  130634 us respectively; the literal source loop does not improve speed.
- Scalar/batch exactness, stalled-producer and DMA checks passed at each
  boot. All 72 archived bitstreams unchanged and 20 host tests passed.
- Free/min heap identical at 108532/105752 B in these isolated images.

The exact original native I2S-PDM32 app0 was restored from a fresh private
backup. Boot, DHCP and HTTP 200 verified. No default-profile or algorithm
change during testing. [Report](../../../docs/benchmarks/esp8266-rcpdm-simple-literal-2026-09-06/README.md).

## Simple32 rewritten with one bit-selection branch

`production-simple-one-branch` and `simple-simple-one-branch` repeat the ABBA
diagnostic comparison after removing Simple's intermediate `high` and its
extra GCC branch. No predictive threshold is added back. Same CPU160/QIO40,
32 bits/sample, alpha=1/16, GPIO3, 2x512 DMA words and batch path.

- Predictive: 128592 bytes, SHA256
  `D5E4B9180F4763C31D9A81EAE2C819E095B389C2CB73F666822536DF1709C0E9`.
- Simple: 128832 bytes, SHA256
  `D695322CC81AC1277F9EB1766461F70FF5A7A6DB00A9DD3899B771724F9322A8`.
- Pack 48000 words: Simple 170046 -> 126617 us (-25.54%); predictive 112275 us.
- Producer excluding DMA wait: Simple 182385 -> 130634 us/audio-second;
  predictive 122843 us/audio-second. These are not total CPU utilization.
- All 72 archived bitstreams unchanged; 20 host tests and physical scalar,
  batch, stall and DMA checks passed. No extra RAM.

Source change `67f3ec2`, built as a working change over `c950d19`.
These images are diagnostics without Wi-Fi/WebUI/codecs. The exact original
native PDM32 radio was restored; boot, DHCP and HTTP 200 verified. No default
profile change. [Report](../../../docs/benchmarks/esp8266-rcpdm-simple-one-branch-2026-09-06/README.md).

## Additional Simple32 board experiment

`production-simple-board` and `simple-simple-board` are isolated diagnostic
images (no Wi-Fi, WebUI or codecs), not ordinary radio. CPU160/QIO40,
alpha=1/16, 32 bits/sample, GPIO3, 2x512 DMA words, batch output enabled.
Both were flashed twice in ABBA order. Each boot passed 493216 scalar
word/state checks and 2144 mono/stereo batch words, with no DMA underruns.

- Predictive: 128592 bytes; SHA256
  `56E5400944BF13BDBEB706C8CAAFB55344115B1194314B2AEC3D101F0562BDDC`.
- Simple: 128864 bytes; SHA256
  `D119E53B96017DE969DBE587B4E0B27DF3C7526C52A7EF418ECF6349EA3BE34C`.
- Pack 48000 words: 112275 vs 170046 us (Simple +51.45%).
- Output excluding DMA wait: 122843 vs 182385 us/audio-second (+48.47%).
- Identical free/min heap 108532/105752 B in the isolated images.

Simple changes the algorithm: its independent direct-comparator reference
is used instead of the predictive reference. No quality/SNR claim is made
from digital timing. Default firmware unchanged; exact previous app0 was
restored from a private backup and its native-radio boot/DHCP verified.
See [physical results](../../../docs/benchmarks/esp8266-rcpdm-simple-board-2026-09-06/README.md).

## Previous predictive optimizations

CPU160/QIO40, GPIO3, alpha=1/16, nominal 1.536 MHz, 32 bits/sample,
two 512-word DMA buffers. Board default remains ordinary I2S PDM32.

Only **production-final-radio/app.bin** is an ordinary radio image:
698304 bytes, SHA256
`CC3B8BB1F9363BFE8FBFA26BF2C16A200FB450D161B4C5CC0C48B0EB2C0080AC`.
It contains the accepted threshold and specialized 48-kHz batch changes
(implementation committed as `a788c95`; built from that working snapshot
before the commit). MP3/AAC, Wi-Fi and WebUI are enabled as in ordinary radio.
Its build was verified; physical timing/exactness was tested in isolated images.

All other subdirectories contain **diagnostic firmware without Wi-Fi/codecs**:

| Directory | Meaning |
| --- | --- |
| original | frozen original scalar implementation |
| limit | accepted once-per-sample threshold |
| unroll4 / unroll8 / unroll32 | rejected unrolled candidates |
| mask8 / branchless8 | rejected mask/branchless candidates |
| production-no-batch | accepted threshold, scalar output control |
| production | **rejected first generic batch experiment**, not ordinary radio |
| production-specialized | accepted final diagnostic mono/stereo batch variant |

Final output producer time excluding DMA sleep: **158586 → 124764 us per
second of 48-kHz audio (-21.33%)**. Every selected scalar word and state
matches the frozen original (493216 cases per physical run); the actual
batch routine additionally passes 2144 words. Host direct-DMA tests cover
six sample rates, mono/stereo, normalization, chunk boundaries, EOF and timeout.
No new audio buffers/heap/IRAM. Batch helper uses a 16-byte stack frame.

Each image has its SHA256/size in manifest.json. Older manifests identify
the HEAD before uncommitted experimental changes; hashes identify the exact
tested binaries. Do not treat diagnostic names as a board-default change.

Flash **app0 only at 0x10000**, preserving NVS/SPIFFS/partitions/bootloader.
GPIO3 carries audio; never send application UART commands. The ordinary
PDM32 image was restored after the physical tests.

See [plan and results](../../../docs/ESP8266_RCPDM_SPEED_OPTIMIZATION.md)
and [raw measurements](../../../docs/benchmarks/esp8266-rcpdm-speed-2026-09-06/README.md).
