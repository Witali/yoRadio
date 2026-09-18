# Decoder-only quant_all_bands ASM — rejected, 2026-09-18

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
prototype, with identical binary bytes. Fresh30 physical A/B/A attempts:
CPU19277.860125/81.874792/77.869875%, CPU12870.394375/74.089958/70.363958%.
Both speed gates FAIL; all PCM hashes/counts exact. Keep eBands-final.
All raw files, maxima and errors retained, including10 earlier A-only runs
interrupted before B by the user's memory audit. MinDRAM1052/1928/4648B,
free stack1660B. A/run6 timeout/90.111542% and timing-window excesses kept.
Local ASM/memory/reconnect/HTTP suite27/27 passes; result tests authenticate
all40 files and recompute the gates. Ordinary heapreserve ASM radio restored
OTA, HTTP/WS/playlist checked, stopped. Not live I2S/WebUI qualification;
75% raw target remains unmet and this candidate must not be promoted.

[Contract and remaining gates](../../../../docs/ESP8266_OPUS_QUANT_DECODE.md).
