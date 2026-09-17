# Before-I/O allocation experiment, 2026-09-17 — rejected

Reserve state/scratch before input/PCM as well as demux. Same RAM allocations,
buffers and4096B guard; cold create frame grows16B, task stack unchanged.
All115 Opus runtime objects unchanged. Host lifecycle tests pass, but9/10
final board diagnostics fail the reserve check;0/10 continuous windows.
Runtime source restored to the pre-experiment ordering. No ASM speed claim.

`comparison.json` and `board-20260917/` preserve all30 physical attempts,
source snapshots, manifests, layout and OTA recovery evidence. See
`docs/ESP8266_OPUS_LARGE_FIRST_ALLOCATION.md` for the interpretation.
