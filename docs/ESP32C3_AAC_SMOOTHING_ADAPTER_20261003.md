# Four-row smoothing: production-adapter integration

The optional `CONFIG_YORADIO_AAC_SMOOTHING_HISTORY` uses the already measured
[four-row implementation](ESP32C3_AAC_SMOOTHING_HISTORY_20261003.md) in the
real TLS-scoped AAC adapter. It depends on PC18 high-history storage and remains
disabled by default. Use `sdkconfig.aac-smoothing-history.defaults` to select it.

## QEMU results

[Retained results](../tests/results/esp32c3-aac-smoothing-adapter-20261003/adapter/result.json):

| Check | Result |
| --- | --- |
| Streaming format/restart cases | 10 passed, including LC, HE-AAC and HE-AACv2 |
| PCM versus previous PC18 adapter | All 657,540 signed-16 samples identical |
| PCM versus original decoder | Maximum 1 LSB; 10 differing samples |
| Two concurrent HE-AACv2 decoders | Identical full-output hashes |
| Live temporary rows in different tasks | Forced overlap, peak 2 |
| Remaining concurrent-task stack | At least 4,956 of 8,192 bytes |
| Allocation failures / reset | 2 failures and 2 resets handled; heap valid |
| SBR owner request | 45,932 bytes |
| SBR allocator block | 47,104 bytes; poisoned-heap API reports 47,092 usable |

This saves another 2,048 allocator bytes per active SBR owner relative to
PC18-only, or 8,192 relative to the original owner. The new row payload uses
1,024 bytes of the existing decoder stack. These results do not establish
physical CPU timing or whole-radio free memory.

The first integration run exposed an undersized 4 KiB QEMU task stack.
[A hardware watchpoint confirmed the first corrupting stack write](../tests/results/esp32c3-aac-smoothing-adapter-20261003/rejected-stack4096/README.md).
All AAC emulator tests now receive the production decoder's stack plus harness
space; the separate concurrency tasks still use 8 KiB and passed unchanged.

## Physical status

The awake test image is retained in
[`firmware/development/esp32c3-aac-smoothing-history`](../firmware/development/esp32c3-aac-smoothing-history/manifest.json).
It has not been installed on the board. Physical stack/memory, OTA, and public
station tests remain pending. The earlier PC18 image's public HE-AAC memory
failures are not resolved by these emulator results.

Host evidence checks: `python tests/test-aac-smoothing-adapter.py`.
The result JSON retains the QEMU command and source/fixture hashes. This
integration is experimental until physical qualification passes.
