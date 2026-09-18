# Branchless eBands pair: preflight only — 2026-09-18

Candidate `esp8266-opus-ebands-src-candidate-v2` is based on the accepted
`eBands-final-candidate-v2`, not the rejected quant/u16 experiments.
It replaces only the existing36-byte leaf at0x4024dd48; its caller at
0x40248418 and all other instructions/addresses remain unchanged.

The leaf loads `align(p)` and `align(p+2)`, sets SAR with `SSA8L`, then
uses `SRC` to extract the exact signed16 pair. Both accesses remain inside
the44-byte table, including the last pair. Other GPRs are unchanged;
the only caller overwrites SAR with `SSL a4` before using it.
The ISA semantics were checked against the
[Cadence Xtensa ISA summary, SRC/SSA8L](https://www.cadence.com/content/dam/cadence-www/global/en_US/documents/tools/silicon-solutions/compute-ip/isa-summary.pdf).

Preflight passed132416 numeric cases plus independent symbolic bit proofs,
all21 table pairs/all64 initial SAR values and negative ABI/bounds tests.
Six regression tests passed. The host semantic mirror passed24 exact PCM,
state/reset/OOM/PLC cases, including510kbps and120ms packets.
No new RAM, stack or image bytes:903216B, candidate SHA256
`95584ccfcf27e3d20807dce204b02a925497273900a01a1f32de4065169fc697`.

This is **not an accepted speed improvement**. It executes12 instructions
and two loads per pair, versus6/9 instructions and1/2 loads in the accepted
leaf. Fewer branches do not prove fewer cycles. Physical10A/10B/10A2 tests
are still pending; the user redirected priority to full-radio fragmentation.
Neither candidate nor control was flashed. The board was only read via
HTTP/WebSocket; it remained on the ordinary accepted ASM radio, stopped.

Two preflight issues were corrected before any OTA: the test normalizer
initially expected `RET` instead of `RET.N`; the first host model modified
the adjacent allocation-vector search instead of the init loop. A regression
reproduced the latter and now pins exactly the three source uses sharing
the changed pair. v2 fixes model metadata, with unchanged candidate bytes.
Failure and final test logs are retained with the v2 artifact.

Reproduce:

```text
node tools/esp8266_opus_asm/ebands_src.cjs
node tools/esp8266_opus_asm/check_bands.cjs ebands-src
node --test tests/esp8266-opus-ebands-src.test.js
```

The ordinary C fallback and production defaults are unchanged. The accepted
CPU192 reference remains77.880896%;75% and20s live qualification are pending.
