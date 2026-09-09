# 2026-09-09 — experimental Ogg Opus

Source `6a9f8eaffd8075fd9da7280346804e8ccd41c0d7`, app 881536 bytes.
SHA-256 `2172c0bbb8f11cc9c9b93229f738b956f7eb059247f24a106936c2aed8dbc257`.
101504 bytes remain in the 960-KiB OTA slot. No flash layout change.

- Optional fixed-point Ogg Opus, mono output, maximum 20 ms / 1536-byte packets.
- Bounded 7168-byte DRAM scratch, shared 16-KiB IRAM, 1536-byte input,
  1920-byte PCM and 6144-byte audio task stack. MP3/AAC input remains 4096.
- I2S PDM32/GPIO3, CPU 160/QIO40, short WebUI audio pause, LED 10 Hz/max 32.
- This is an **experimental, not device-qualified** application image.
  No OTA, USB/serial, Wi-Fi changes or physical audio test were performed.
- Apply through the native WebUI OTA endpoint only after qualification;
  no automatic serial fallback. Do not upload as bootloader/merged/SPIFFS image.
- Included `script.js.gz` matches current source, SHA-256
  `f755b140f2aeb4dde1e9ea907c043252ac7da3a65cf56758281549338c84c9ac`.
  Boards predating volume0..100 need this `/www/script.js.gz` update before
  application OTA and a page reload. Other WebUI files are unchanged here.

## Verification

- Full ESP8266/shared WebUI host suite: 334/334 PASS, no skips.
- After final SILK IRAM-width correction: 12/12 focused tests PASS; all 5
  pristine/baseline/bounded fixtures again exact (292800 samples, max error 0).
- 100 mixed MP3/AAC/Opus lifecycle cycles, 67 allocation-failure sites:
  no leaks/double free; same-Opus reset allocates nothing.
- Ogg parser ASan/UBSan; native adapter no packet-time malloc/calloc/realloc.
- Xtensa GCC 8.4: state 9134 B; corrected SILK gain-load uses l32i rather than
  l16si. Selected CELT/FFT/history paths audited; not proof of every path or
  compiler configuration. Runtime IRAM/stack/heap tests are still required.
- No physical CPU/realtime/20-second-continuity claim. Free heap and stack
  reserve on the complete running radio remain unmeasured for Opus.

Full host TAP and final focused TAP are saved alongside this file. Detailed
memory/PCM report: [Opus documentation](../../../docs/ESP8266_OPUS_NATIVE.md).
