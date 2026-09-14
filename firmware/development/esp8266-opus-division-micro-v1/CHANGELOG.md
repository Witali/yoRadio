# Invalid-clock diagnostic, 2026-09-14 — do not use for speed comparison

Same-image ROM versus exact ASM division microbenchmark, CPU160/QIO40.
Application 938896 bytes. All operands are in flash and copied to a 1536-byte
RAM chunk; static RAM unchanged. No UART or SPIFFS writes.

First physical attempt stopped with error -9104: subtracting raw CCOUNT gave
a huge duration. The SDK resets CCOUNT in FreeRTOS port.c/os_cpu_a.S, so this
clock is invalid across interrupts. Quotients matched, but timing is invalid.
The failed run, binary, manifest, preflight and OTA evidence are preserved.
Superseded by v2 with an atomic SDK accumulated-microseconds snapshot.
