# CYD full TLS records and PDM startup recovery

The [isolated traffic target](../../target/cyd_tls_traffic_qemu/README.md)
ran twice on dual-core ESP32 QEMU with ESP-IDF 6.0.2. The profiles use the same
RX 16384/TX 4096 limits, hardware cryptography, early MPI, adaptive-input
reclaim, local CA and fixture. The comparison switches between the SDK's
dynamic buffers and the CYD static RX reservation.

Each profile accepted seven exact 65,536-byte responses and verified all 28
16,384-byte plaintext records against the known payload digest and sender
record headers. Two connections were live concurrently for four rounds on
the two cores. Wrong-name, early close and truncated-record cases were
refused, and subsequent complete requests succeeded. One real 4096-byte
allocation failure recovered in each profile after releasing one idle slot.
The static profile balanced ten allocation, release and bundle attach calls.
The dynamic profile made ten bundle attaches and linked the SDK's RX
allocation and release calls. QEMU exited cleanly in both runs.

[PDM startup recovery](../cyd-openeth-full-records-20261111/README.md) closes
the partially initialized channel after a failed bias write or clock query,
while keeping ownership if cleanup itself fails. The host ASan/UBSan suite
passed 17 PDM, 17 continuous DAC and 10 legacy DAC cases. The original
readiness condition failed its negative control. A focused Espressif
clang-tidy run completed with seven warnings and zero errors.

The full dynamic-buffer application rebuilt with the recovery change and a
fresh disposable CA. It completed all 43 full TLS records and the 1807-byte
tail, served the exact WebUI asset during playback, reported `stream ended`,
and wrote exactly 1,058,176 bytes in 1034 PDM calls. Decoder, stream and output
failure counters were zero. The strict test returned **NONPASS** after 366
allocation failures and two recovered OpenETH RX waits. Heap fell to 1544
bytes, and the driver reported 39 completion queue drops. The gate stopped
before reading the post-EOF WebUI asset.

The isolated traffic result applies to the diagnostic TLS receiver. The full
application result includes TFT and the real firmware PDM path in QEMU.
Physical Wi-Fi, DAC variants and the full static-reserve playback failure
remain open. [Artifact identities and counts](observed.json).
