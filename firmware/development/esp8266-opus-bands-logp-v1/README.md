# Diagnostic Opus ASM bit_logp shrink-wrap — rejected

Not ordinary radio firmware. Default remains unchanged. Implementation:
`15b708a0`, build-time `bands-logp-asm`, best tell-inline parent.
App903232 B SHA256
`4d702c39ecb911d6d941059cb66323f72058bee0d03823cfbf62c7a9940b2b5d`.
CPU160/QIO40, preloaded RAM fixtures, no audio output or stage/function profiling.

100000 instruction cases,58 Node PASS, exact host PCM12..510 kbit/s,
mixed/PLC/reset/OOM. No static RAM growth, fast path stack0/cold16 bytes.

All30 physical A/B/A reports: `controls/before`, `runs`, `controls/after`.
CPU192 medians88.100 /92.442 /88.121%,4.93% slowdown. All PCM hashes exact.
Run9 pressure/outlier retained (CPU106.260%, sampled DRAM1356 B).
`comparison.json` includes all sources/hashes, memory, maxima and both gates.

`ota-restore.json`, `restored-snapshot.json`, `root-http.json` confirm return
to ordinary `esp8266-opus-live512-idle3s-20260913` via OTA, stopped as before,
HTTP/WS/playlist responsive. No UART or SPIFFS writes. Candidate live playback
not qualified because raw speed gate failed. Goal70% remains unachieved.

See [full report](../../../docs/ESP8266_OPUS_ASM_LOGP.md).
