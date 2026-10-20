# CYD output telemetry host integration

The runner compiles frozen, byte-exact `native_audio_output.c` and the complete
`native_output_metrics.c` as separate translation units for PDM, continuous DAC
and legacy DAC, in both quiet and diagnostic configurations. SDK driver calls,
GPIO, task delays, clock and critical sections are explicit host seams; the two
production translation units share the same ESP-IDF error constants.

Only public output functions and public metric snapshots drive the cases. The
fixture never seeds private counters, output state, owner phases or ACKs.
An independent driver ledger records actual requested/reported bytes and return
values. Each outcome checks public return propagation and every metric field.

Cases cover prime writes, successful/failed/timed-out/short/over-reported writes,
full chunks and tails, PDM padded flush, DAC/legacy idle, and paused requests
that never reach the driver. PDM additionally checks callback registration
failure cleanup before preload/enable, queue availability, the registered ISR
hook, and coherent snapshots while real output writes and callbacks overlap.
Assertions fix the existing GPIO26, clock, slot/channel, DMA and timeout
configuration at the driver boundary. Preloads are deliberately not synchronous
driver-write observations. Exact source mutants must fail named semantic checks.

The pre-existing PCM/normalizer/pause/maintenance suites use an explicitly empty
metrics seam to preserve their original scope; this separate suite has no
metrics seam. ASan/UBSan run with fail-fast settings. Mutex seams cannot prove
ESP32 SMP/ISR timing, target placement, DMA transmission, audible underruns,
physical pins, driver resource margins or performance. Final firmware linkage
and device qualification remain separate gates.
