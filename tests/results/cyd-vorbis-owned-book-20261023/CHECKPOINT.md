# Owned codebook publication unit — 2026-10-23

The actual ESP32/Xtensa unit passes all16 codebooks,59 active codewords,
61 vector probes, two wide sparse/dense pairs and97 native protocol events.
It compiles the exact production `setup.c`
`6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c`
and ABI declaration `e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60`.
The test calls the real static book parser through a controlled bounded
bit-reader and checks its actual published fields, decode table, compact
quantization rows, consumed bits, allocation guards and normal ownership clear.
Every case ends with zero live tracked allocations.

The separate bounded public vector consumer uses point0 with minimum−1 and
delta1. It checks every active codeword and both singleton bit values against
independent fixture expectations. Both D16 lookup2 sparse/dense pairs have
equal actual tables, compact rows and vectors. The test adds no vendor decoder,
private handle inspection, artificial vendor function or codec archive.

The actual SDK6.0.2 revision is
`7101770dc6db2667b3c477cc31365dd1acd6db4e`. Compile macros prove ILP32,
little-endian ESP32/Xtensa,240MHz, two cores and main task core0/16384-byte stack.
Actual GCC dependencies contain all109 rows,104 distinct paths and five legal
repeated SDK headers. Every input is frozen and hashed; raw macros and dependency
output match before and after build. Actual ELF machine94, nm, map, generated
link commands and verbose build logs bind the real unit/parser and show absent
vendor codec/decode/register/wrapper linkage. Production task affinities and
firmware sources are unchanged by this unit.

All14 owned commands completed normally with exit0. The actual capture report is
`aa64efbca21196b0384ce784b31cae48139baee7d3673f3d6457dab82e90a3eb`;
the direct tool session66930 ended0, chunk `b24da6`. Raw QMP records contain the
real greeting, capabilities acknowledgement, host-qmp-quit SHUTDOWN and quit
acknowledgement, plus the two actual requests and process terminal facts.
COMPLETE alone never qualifies the unit. The executed hash-pinned helper
required pipe EOF and reader completion; no separate EOF boolean receipt was
recorded or fabricated afterward.

The first actual campaign remains NONPASS before build/QEMU: its observer
incorrectly required unique GCC dependency spellings. The successor removes
only that requirement, retains all109 rows, and preserves the earlier failed
campaign. A separate source-only predecessor fixes the outer/SDK-child log-name
collision before any runtime was launched. All preparation history is retained.

This is a finite test of our parser publication and this public consumer.
It does not qualify the opaque vendor consumer, floor0 field/curve behavior,
backend PCM, full G6, radio integration, resource benefit or physical hardware.
The existing wide/floor0 numerical failures remain open. No fault/OOM, transport,
device, COM, flash or network-device operation was performed. The local QEMU
images are fixture applications, not production firmware or handoff binaries.

The archive retains sources, fixtures, actual logs, SDK-child/process receipts,
compile dependencies, config and link evidence. Large data uses lossless gzip.
Target/tool binary identities are explicit omissions; the actual ELF header64
slice is retained. `README.md` describes the packer and separate offline verifier.
Successful archive verification confirms these records and the full97-event
result, while preserving the failed first campaign and all scope limits.
