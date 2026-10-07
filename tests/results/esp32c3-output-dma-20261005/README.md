# PCM direct DMA experiment, 2026-10-05

Read docs/ESP32C3_OUTPUT_DMA_20261005.md for the implementation and qualification
limits. Four DMA descriptors are retained. All measured FAIL results remain.

- control-load: staged output, Vorbis retry/EOF repair present.
- candidate-load: rejected partial DMA implementation (44.1 kHz timing failure).
- prefill-load: whole-block leases and three-block startup target. Correct
  audio/wall timing; progressive-heap-loss gates still fail on three codecs.
- prefill-eof: Vorbis and HE-AACv2, auto/explicit codec, all four PASS. Board
  rebooted afterwards, exact firmware identity verified by restore-board.
- ota-*: three successful application transitions while playing, settings checked.
- comparison*.json: derived from the complete raw load/status/performance logs.
- verify-*: linked sections/calls and source snapshots; these pre-test build
  records deliberately retain hardware_tested=false. Updated artifact manifests
  separately record physical results. Native DMA sources are in verify-prefill
  and host-final; initial host generated translation units retain prior code.
- host-final: reproducible source snapshot, guarded DMA/RTOS test, ASan/UBSan,
  432 exact-PCM cases plus 648 actual-normalizer chunk-size cases.
- host-first and host-leased: intermediate reports, PCM and generated C. Their
  platform stub/test include snapshots were not taken before those runs. Use
  host-final for complete host reproduction, not these partial historical copies.

Raw serial/private logs are excluded. Physical logs contain filtered technical
telemetry. Fixture identities, config identities and ELF hashes are in reports.
Firmware bytes are retained under firmware/development/esp32c3-output-*.
This is not acoustic/IRQ continuity proof or production qualification.
