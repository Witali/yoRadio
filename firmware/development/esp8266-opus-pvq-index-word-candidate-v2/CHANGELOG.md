# Signed PVQ index word-load candidate v2

Experimental raw Opus ASM benchmark, not ordinary radio or a default profile.
CPU160MHz/runtime QIO40, packets in RAM, physical audio output OFF.
Native application-only OTA; no UART commands or reset on GPIO3.

Three patches,total35 bytes. Early original return store,29-byte fixed-J
helper, exact signed16 extraction by SLLI16/SRAI16. No added RAM/frame/table.
Image903216 B. Host24 cases and137792 linked prefix cases exact.
Physical30 A/B/A complete:CPU19280.97738 /80.08060 /80.99402%.
CPU12872.59440 /72.02094 /72.60467%; both high-bitrate gates PASS.
Max19221047 /21318 /20826us; minimum DRAM8528 /8168 /8176 B,
free stack1660 B. No observation/decoder errors; A2/run10 mono12
task>wall784us retained. Raw target80% and live20second gate not reached.
Ordinary C radio restored OTA with stopped167/playlist/HTTP/WS unchanged.

v1 was rejected by the assembler (SEXT unavailable); never flashed.
v2 uses the supported exact shift pair. Failure log is retained.
See docs/ESP8266_OPUS_ASM_PVQ_INDEX_WORD.md and preflight.json.
Full154 related preflight PASS/0skip in229.79seconds. Initial153/154 log
retained: negative test used a code-only locator for rodata; fixed test only.
No firmware/proof/image change for that test-harness correction.
Final156 related regressions PASS/0skip,244.84seconds; full log retained.
Restored ordinary HTTP200/27249 gzip bytes/110.54ms,heap27628 B/min24748 B.
