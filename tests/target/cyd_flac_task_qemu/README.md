# Actual CYD audio-task FLAC checkpoint

Run from the repository root on Windows with installed ESP-IDF 6.0.2, its
Xtensa tools, the existing `esp_audio_codec` component, PowerShell 7, FFmpeg and
Espressif ESP32 QEMU. This runner does not install dependencies or use a board.

```powershell
& C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -X utf8 `
    tests/run-cyd-flac-task-qemu.py `
    --qemu C:/Work/QEMU-ESP32/bin/qemu-system-xtensa.exe `
    --output .build/cyd-flac-task-new-run
```

Use `--help` for explicit SDK, Python, vendor-component, FFmpeg, PowerShell and
ROM paths. `--preflight-only` validates inputs without creating output or
starting tools. Every campaign requires a fresh directory. Source/install
trees and existing evidence directories are protected from output overlap.

The harness compiles the complete unchanged `audio_service.c`, state, health
and decoder registration with actual SDK tasks, queues, ring buffers, adaptive
input and custom FLAC. It verifies the original core, priority and stack
profiles. Real HTTP client allocation and cleanup remain enabled; transport,
output hardware and LED functions are explicit test seams.

Three public-API cases check ordered EOF with exact PCM, Stop followed by Play,
and three-owner OTA maintenance followed by automatic resume. Independent
FFmpeg PCM oracles check every output byte. The fixture generator produces 130
oracles; this checkpoint executes three lifecycle cases. It does not claim
130 full-pipeline cases or replace the separate 520-case adapter/core suite.

`CONFIG_YORADIO_HTTP_REQUEST_BUFFER_RELEASE=n` is explicit because synthetic
HTTP transport never enters the real SDK response state. Its release/redirect
guards are tested by the separate HTTP suites. No private phase or ACK is
assigned to simulate owner cleanup.

The runner preserves build commands/logs, actual compiler dependency closure,
source/configuration/tool hashes, test images and QEMU stdout. It checks bound
inputs before and after execution and requires terminal emulator exit 0.
Images use a dedicated test partition table and must not be flashed as radio
firmware. OOM injection, output backpressure, target semantic controls, physical
HTTP/TLS/DMA, audio quality and production resource margins remain separate
qualification gates.
