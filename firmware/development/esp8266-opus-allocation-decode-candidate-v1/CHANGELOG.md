# Decoder-only allocation ASM experiment — 2026-09-18

CPU160/runtime QIO40, raw RAM-packet benchmark, no physical audio output.
Based on accepted eBands-final; not a production/default change.

Remove67 proven encoder-only instructions and3 constant branches from
clt_compute_allocation.930 retained instructions have identical operands,
references and CFG successors. Live2345B in original2564B slot; original
192B stack frame, static RAM and903216B application size unchanged.

SHA256 `3afa449c417903c91126c35940955a4fba0fe5ba30d294db6af6159cccca57fe`.
Seven preflight regressions and24 exact host PCM/state/sanitizer cases pass.
Physical A/B/A is pending; no speed benefit claimed or promotion permitted.

[Contract, verification and remaining gates](../../../../docs/ESP8266_OPUS_ALLOCATION_DECODE.md).
