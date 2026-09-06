# 2026-09-06 — Bit-exact RCPDM speed experiments

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
