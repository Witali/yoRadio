# Actual CYD task pipeline with Espressif Vorbis

This diagnostic compiles the unchanged complete production `audio_service.c`,
state, health and decoder registration. The SDK tasks, adaptive input, PCM ring
and unchanged target-specific Espressif Ogg/Vorbis library are real. HTTP
transport, audio hardware and LED callbacks are explicit test seams. HTTP
client initialization and cleanup remain actual SDK operations.

Run in the task worktree with the installed SDK 6.0.2, tools and ESP32 QEMU:

```text
python -B tests/run-cyd-espressif-vorbis-task-qemu.py --output .build/cyd-vorbis-task-new-run
```

`--preflight-only` checks dependencies without creating output. Every campaign
needs a fresh output below `.build`. Inputs, actual compiler dependencies,
configuration, tools, images, command results and emulator transcripts are
retained. No physical board or real network connection is used.

The embedded 703,584-byte q10 fixture is supplied through uneven HTTP reads.
Output-side SHA-256 checks all 2,112,000 PCM bytes against the frozen direct
vendor checkpoint. This is an integration regression reference, not an
independent numeric oracle. Three cases exercise complete ordered EOF,
Stop/reopen and three-owner maintenance/resume with valid/stale token checks.

Partial-stream holds are activated by real first PCM, rather than a guessed
encoded offset. Stop waits for public client/container cleanup and for the
actual output owner to discard at the new public generation before resetting
the checksum. Successful maintenance begin is the three-owner barrier before
resuming. No private state, phase or acknowledgment is assigned by the test.

Production task profiles are checked at creation and callback execution:
stream core 0 / priority 3 / stack 6144, decode core 1 / priority 5 / stack
16384, output core 1 / priority 6 / stack 4096. Assertions, idle watchdogs,
stack canaries and heap poisoning stay enabled. Output-side checksum work must
fit the unchanged stack; observed stack/heap figures describe this diagnostic.

Request-buffer release is explicitly off because synthetic HTTP open/read
does not enter the SDK's connected transport state. No custom decoder or
private repair is selected. These images are diagnostics and must not be
flashed as production radio firmware. Real HTTP/TLS, DMA/TFT, backpressure,
decoder allocation-failure internals, timing, production resource margins,
physical audio and universal Vorbis conformance remain separate gates.
