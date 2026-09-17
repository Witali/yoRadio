# 2026-09-17: frozen eBands pair ASM experiment

Two signed16 flash reads in clt_compute_allocation replaced by a call0 leaf
using one/two aligned word reads. Caller-dead a0 proved across176 instructions;
all other live GPRs/SAR and full signed results exact. No stack or DRAM growth.
Same903216-B application, outside addresses and original44-B table.
132416 linked numeric cases and symbolic independent word bits pass.
24 host exact PCM/state/PLC/reset/OOM cases through510kbps/120ms pass.
Physical10 A/10 B/10 A2 complete at15s polling. CPU192:
79.648167 /78.926917 /79.683646%; relative gain0.905545/0.949667%.
CPU128:71.855896 /71.338729 /71.856417%; both acceptance gates pass.
Accepted as experimental raw ASM baseline; no production default change.
Min sampled DRAM7492/8172/8344B; audio stack free1660B. Static RAM unchanged.
Max192 wall call20.409/20.025/21.427ms; all30 attempts retained, zero errors.
Two mono12 task>wall accounting cases retained:934/34us; no filtering.
17 local regression tests PASS/0skip,24 host PCM cases exact.
No claim of75% CPU or continuous I2S/WebUI qualification.
7 result/attribute tests PASS; all30 raw reports independently recomputed.
Prior ordinary C diagnostic radio restored via OTA to0x110000; benchmark OFF.
Saved station167 stopped, volume100/balance0, playlist and WS preserved.
RSSI-58dBm, free heap27452B. API check only, not visual/live qualification.
