# Current C3 format-suite qualification

The existing `run-esp32c3-stream-format.py` first failed to compile because its
FreeRTOS seam omitted `BaseType_t` and its test no longer included the quiet
`audio_pipeline_probe.h` macros used by production PCM publication. The harness
now uses the actual quiet probe header, restores the platform type, and links
sanitized host executables without PIE for reproducible ASan mapping.

The [complete output](test.log) passes all seven groups: real callbacks/PCM /
state/WebUI snapshots; PCM workspace resize/OOM; actual Helix AAC format changes;
ADTS framing/CRC/resync; adaptive AAC input/OOM; SBR ownership; scratch transfer /
reopen/cleanup. `C3_MEMORY_SANITIZE=1` enables ASan/UBSan for the C host executables.
The suite's real Helix C++ adapter command remains an ordinary host codec test;
it must not be represented as sanitized codec arithmetic. OLED snapshot logic is
donor regression coverage only and is excluded from the CYD transfer.

This is a harness repair and host evidence, not a firmware behavior change or
physical board acceptance.
