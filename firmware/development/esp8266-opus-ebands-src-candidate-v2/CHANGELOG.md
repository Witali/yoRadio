# Branchless eBands SRC — rejected, 2026-09-18

CPU160/runtime QIO40 raw benchmark over accepted eBands-final. One existing
36-byte leaf replaced; original callers/layout, RAM, stack and image size
903216 B unchanged. Candidate SHA256:
`95584ccfcf27e3d20807dce204b02a925497273900a01a1f32de4065169fc697`.

132416 numeric cases, independent signed16/SAR/bounds proof, 24 exact host
PCM/state/OOM/PLC cases and six rerun regressions pass. All30 physical
A/B/A attempts match PCM hashes and sample counts; no attempt omitted.

CPU192 A/B/A2:77.878917/77.872167/77.863833%.
CPU128:70.353646/70.378500/70.363833%. Both speed gates fail; do not promote.
Max192 wall calls19.930/19.813/20.314ms; minDRAM5324/1580/900B and B/run10
task>wall1216us retained. Free task stack1660B; no static RAM growth.

Normal heapreserve accepted-ASM radio restored by OTA to0x10000; HTTP,
WebSocket and playlist checked, board stopped. No new live-audio or visual
browser qualification. Goal75% and continuous20s are still not achieved.

[Full report](../../../../docs/ESP8266_OPUS_ASM_EBANDS_SRC.md).
