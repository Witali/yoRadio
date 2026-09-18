# Decoder-only quant_all_bands ASM preflight — 2026-09-18

Experimental raw RAM-packet benchmark at CPU160/runtime QIO40; no audio
output or function/stage profiler. Parent is accepted eBands-final.

557 unreachable instructions omitted, 27 constant checks removed and five
converted to jumps. 2786 retained instructions have exact linked operand,
branch and reference checks. Live body7687 B inside the original9416-B slot.
The384-B frame, static RAM and903216-B application size are unchanged.

SHA256 `714e7ca0b882a4289c50c0d511c911cf6eeca349bdea0a06ceb627e996000905`.
Host semantic model:24 exact PCM/state/ASan/UBSan cases through510 kb/s.
Final preflight6/6 and combined memory/lifecycle/reconnect25/25 pass.
Original C fallback and saved GCC ASM unchanged; no mode/bitrate limit.

v2 fixes the copied purpose label and removal counter of a never-flashed
prototype, with identical binary bytes. Physical A/B/A speed gate pending:
not accepted, not a production default, not live I2S/WebUI qualification.

[Contract and remaining gates](../../../../docs/ESP8266_OPUS_QUANT_DECODE.md).
