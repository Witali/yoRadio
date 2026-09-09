# SDK network diagnostics on physical Opus — 2026-09-09

Source 4fa9043, 882704 bytes. OTA app0 to app1 passed. PDM batch OFF;
word ASM and PDM IRAM ON; ICDF word OFF. Normalization/output unchanged.
SDK overlay is diagnostic-only, pinned by hashes in sdk-rxdiag-manifest.json.
Target ELF confirms exactly 32 bytes of counter state. The three generated
SDK copies were compiled instead of their originals; installed SDK untouched.
Host overlay tests passed 6/6, including actual injected control flow and
ASan/UBSan; HTTP/profile tests passed all 8 JSON flag combinations.

Frequent HTTP polling of the local 180-second SILK12 file reproduced
RX timeout (4/errno116) and multi-second TCP reconnects. All five observed
error counters stayed ZERO throughout: custom pbuf setup/allocation,
RX message allocation, RX mailbox full, TX transform and TX driver return.
Custom wrapper peak was 6. Sampled DRAM at the initial timeout was 7672
bytes. Server TCP_INFO showed retransmission/RTO; this is not proof that
the closed Wi-Fi driver received those packets. Driver-internal loss and
RF conditions remain outside these counters' observation boundary.

Later status showed generation=0 and uptime about23 seconds, indicating
another boot without an OTA command from this test. RSSI then was -82dBm.
Cause is unknown. The following sparse capture was therefore STOPPED,
not a valid playing-priority or audio-performance measurement. A subsequent
source commit exposes the SDK boot reset reason, but THIS binary does not
yet contain that field and cannot retroactively identify the reset cause.

Continuity remains FAILED; no network delays or missing requests were
discarded to claim success. Next: capture reset reason and RSSI with an
uninterrupted stream; repeat PDM batch A/B after transport stabilizes.
