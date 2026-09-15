# 2026-09-15 — Opus PVQ flash-byte ASM experiment

- Five byte probes use a verified aligned-word leaf in existing unused
  decoder code storage. Exact PCM, no new tables/allocations/stack slots;
  unchanged outside code addresses, flash tables and903216-byte image.
- CPU160/QIO40, raw packets preloaded in RAM, no audio output or profiler.
  All30 physical A/B/A attempts archived, plus24 host correctness scenarios.
- Median CPU192:85.91985 ->84.01121 ->85.91904%; CPU128:
  75.70981 ->74.43904 ->75.69485%. Both comparison gates pass.
  Mono12 slowdown0.065–0.080% accepted under the high-bitrate priority rule.
- Static RAM/IRAM/frame unchanged; minimum free stack1660 B. Observed free
  DRAM minima A/B/A2:8860/1252/7492 B. Low memory and every outlier retained.
  Maximum B19221.428ms, B12821.842ms: not an underrun-free audio guarantee.
- Ordinary live512-idle3s radio restored OTA; station/playlist/HTTP/WS verified.
  The candidate is an experimental raw benchmark, not the ordinary app left
  running on the board.80% and continuous20s I2S PDM/WebUI remain outstanding.
- Final118 related regressions PASS,0 failures/skips,116.90seconds;
  final-tests.log includes independent physical-report/restore checks.
- Source/proofs commit:4e25614d. See comparison.json, preflight.json,
  host.json, restore reports and the full explanation in
  docs/ESP8266_OPUS_ASM_PVQ_BYTE_WORD.md.
