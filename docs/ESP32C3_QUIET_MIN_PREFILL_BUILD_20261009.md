# ESP32-C3 quiet minimum-prefill candidate — 2026-10-09

## Purpose and status

The [saved development image](../firmware/development/esp32c3-idf-6.1-r9a97-quiet-min250/)
combines the tested memory configuration and minimum input prefill with a
quiet production build. Console logging, CPU and queue profilers, clock
diagnostics and the laboratory CA are disabled. This report covers compilation
and linked-code checks only; this image has not yet been installed on the board.

The fractional clock is still experimental. It targets nominal 48,000 Hz,
but analog noise has not been measured or listened to. The user cannot listen
at present. No production default is changed, and this candidate is not marked
production-qualified.

## Configuration

The image uses ESP-IDF 6.1 revision `9a97f6c54ec638111ce55cd36581b3c192f15207`,
QIO 80 MHz, no deep sleep, full compact AAC/SBR/PS including late SBR, and the
existing PCM tail flush/discard fix. The functional changes from the previous
quiet image are:

- A 17,058-byte TLS receive reserve, dynamic TLS allocation and adaptive audio
  input with a minimum of five nominal input blocks.
- TCP receive window 8,640 bytes, receive mailbox eight, copied network receive
  buffers and the bounded TCP control-block pool.
- Heap functions in flash and the previously tested SPI interrupt placement.
- Minimum input prefill 250 ms, maximum 500 ms, and fractional nominal 48 kHz.

The archived configuration audit checks all 18 effective SDK configuration
changes, including legacy aliases. Decoder arithmetic, compact AAC precision
settings and output task priority are unchanged from the diagnostic candidate.

The generated certificate bundle is byte-identical to the previous quiet
image's full normal CA bundle. The test CA is absent. No configured Wi-Fi SSID
or password is included in the saved SDK configuration.

## Build evidence

| Measurement | Diagnostic minimum-prefill image | Quiet candidate |
| --- | ---: | ---: |
| Application binary | 1,622,096 B | 1,453,344 B |
| IRAM text | 47,690 B | 46,184 B |
| DRAM initialized data | 12,856 B | 11,524 B |
| DRAM BSS | 45,664 B | 44,840 B |

These are linked section sizes. Their differences are not a measurement of
runtime free heap, fragmentation or a speed improvement.

The AAC build audit verifies full AAC/SBR/PS and the compact/late-SBR call
paths. The HTTP and allocator audits verify the linked TLS reader, allocator
function pointer, 17,058-byte reserve and RX-only hooks, including relocations
in the generated SDK object. The output task calls the PCM tail flush and
discard functions. Profiler symbols, diagnostic strings, the direct-DMA output
experiment and the unrelated CLZ experiment are absent.

- Embedded version: `idf61-quiet-min250`.
- Application SHA-256: `4fc2a9e630b0ff44dfa7f106755b58306062463c70c0f9eaaa47d6164c8206fc`.
- ELF identity: `8b364fe969bab5b42c73c7d1cc5fc987f26f2a1ecfb1e6487a48ffae04807c17`.
- Source capture: `13d9f70e`, with exact source hashes in the artifact manifest.

QIO is selected in the SDK configuration. The SDK's bootstrap image/header
may still say DIO; actual flash bus operation needs startup register evidence.
This quiet image has no such physical observation yet.

## Rechecking the saved evidence

The [build archive](../tests/results/esp32c3-quiet-min250-build-20261009/)
contains compiler output, exact source snapshots, configuration differences,
linked-code audit results and selected disassembly. It excludes private
settings and keys. The application and bootloader remain in `firmware/`.

```powershell
python tests/results/esp32c3-quiet-min250-build-20261009/verify_evidence.py
```

This checks archive hashes and agreement with the saved firmware. It does not
rerun the compiler or qualify playback. Quiet-image playback across formats,
public HTTPS radio, OTA, memory recovery and analog clock quality remain open.
Diagnostic results are recorded separately in the
[minimum-prefill report](ESP32C3_MIN_PREFILL_20261009.md).
