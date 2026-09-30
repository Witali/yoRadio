# ESP32-C3 EOF status regression, 2026-09-30

See the [correction and validation report](../../../docs/ESP32C3_EOF_STATUS.md).
Both physical images were compiled from `69410cd5`, with production logging
and deep sleep disabled. Firmware manifests retain the exact configuration,
application and bootloader hashes.

| Evidence | Scope |
| --- | --- |
| `qio80/` | Initial QIO80 EOF matrix, network faults and WebSocket checks; one HTTP observation failed |
| `qio80-retry/` | Explicit separate repeat of AAC-LC 320 kbit/s, both AUTO and AAC; both passed |
| `dio80/` | Same EOF/fault/WebSocket checks with the DIO80 image |
| `dio-stop-race/` | Old blocked stream replaced by Stop/Play; new mono stream must survive |
| `dio80-ota.json` | Exact DIO image: both OTA slots, invalid/interrupted uploads, slow upload, upload while playing and restoration |
| `dio-install.json` | DIO image identity and first reset's HTTP timeout followed by successful reset |
| `final-board.json` | Final running image, technical status and settings equality booleans |
| `reference.json` | Six AAC fixtures decoded by FFmpeg and FDK; four input chunk sizes per FDK fixture |
| `c3-webui-node.log` | 151 passing C3/shared-WebUI host checks |
| `host-node.log` | Earlier focused 54-test subset, not 54 additional unique tests |
| `summary.json` | Case counts and retained failures; restoration counts as a case, not a codec test |

The physical EOF suite checks terminal status independently of full-profile
acceptance. HE/v2 still fall back to core decoding on the complete radio.
Passing EOF does not claim full-rate HE-AAC or resolve the SBR allocation limit.
Reference tests check complete-file decoding, layouts, sample counts and drain
completion; they do not assert bit-identical PCM across different decoders.

The deterministic production-code EOF test, real Helix/stream-format/framing
tests, 16 Python acceptance tests and four firmware artifact checks also passed.
Their reproduction commands are in the linked report and testing guide.

Only technical status fields and original synthetic audio fixtures are used.
Wi-Fi/playlist/settings contents are compared in memory; no credential value,
credential hash, raw board backup or private USB log is included here.
Software reset is not a cold-power-cycle test. These checks do not replace
the outstanding full QIO qualification, acoustic or interrupt-latency tests.
