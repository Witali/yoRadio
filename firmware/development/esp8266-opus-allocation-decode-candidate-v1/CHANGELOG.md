# Decoder-only allocation ASM experiment — 2026-09-18

CPU160/runtime QIO40, raw RAM-packet benchmark, no physical audio output.
Based on accepted eBands-final; not a production/default change.

Remove67 proven encoder-only instructions and3 constant branches from
clt_compute_allocation.930 retained instructions have identical operands,
references and CFG successors. Live2345B in original2564B slot; original
192B stack frame, static RAM and903216B application size unchanged.

SHA256 `3afa449c417903c91126c35940955a4fba0fe5ba30d294db6af6159cccca57fe`.
Seven preflight regressions and24 exact host PCM/state/sanitizer cases pass.
All30 physical A/B/A attempts now saved. CPU192 medians77.861000 /
77.851250 /77.869417%, CPU12870.376938 /70.352396 /70.381438%.
Both relative high-bitrate versus low-bitrate selection gates FAIL.
Rejected; keep accepted eBands-final.75% CPU not reached.

Exact target PCM, unchanged static RAM/stack. Minimum DRAM900/896/1048B;
task stack-free1660B. A2/run9 polling timeout and90.011750% outlier retained.
Combined30 preflight/lifecycle/reconnect tests pass; result tests recompute
all30 authenticated attempts. Full reports/maxima archived here.

Ordinary heapreserve ASM radio restored by OTA to0x10000, HTTP200/OK;
status/audio/WebSocket/playlist checked, stopped. No live20s qualification.

[Contract, verification and remaining gates](../../../../docs/ESP8266_OPUS_ALLOCATION_DECODE.md).
