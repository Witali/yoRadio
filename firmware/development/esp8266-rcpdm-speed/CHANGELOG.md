# 2026-09-06 — Bit-exact RCPDM speed experiments

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
