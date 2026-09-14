# Same-image division diagnostic, 2026-09-14

Both real ROM __udivsi3 and exact small-div ASM execute the same indirect-call
batch loop, with all 6163 ordered operand pairs from the five raw Opus fixtures.
Twenty paired physical runs: ten after yielding and ten with immediate batch
warmup. After-yield is NOT a guaranteed cold cache. No decoder CPU claim.

CPU160/QIO40; application 938928 bytes; static DRAM/IRAM unchanged.
Measurement results retain the raw benchmark's 220-byte static budget.
Only a 1536-byte operand chunk is allocated, not the full 49304-byte trace.
Use SDK accumulated microseconds, atomically sampled; do not mask interrupts
over the measured batch. Retain maxima, interrupts and all attempts.

Exact per-operand quotients and batch hashes checked on the board.
See comparison.json, census/, runs/ and preflight.json. Original radio is
restored via OTA after testing; this diagnostic is not a production default
or a raw decoder <=70% CPU qualification.
