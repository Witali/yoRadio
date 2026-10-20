# CYD output telemetry and HTTP buffer production checkpoint

All six complete GCC applications were built/exported from clean source `0f2a37c89e59e1b7b23a7bfbfb2eb5fb579a2f96`.

The production exporter independently checks ESP32/Xtensa identity, image/ELF hashes, image checksum and appended SHA256, both OTA slots, pinned tools/configuration and raw evidence receipts. No board operation was performed.

| Backend / FLAC | App bytes | OTA free bytes | Compiler warnings |
| --- | ---: | ---: | ---: |
| pdm / vendor | 1543968 | 225504 | 0 |
| continuous / vendor | 1537584 | 231888 | 0 |
| legacy / vendor | 1543488 | 225984 | 3 |
| pdm / custom | 1517504 | 251968 | 0 |
| continuous / custom | 1511312 | 258160 | 0 |
| legacy / custom | 1517200 | 252272 | 3 |

Each `firmware/development/esp32-cyd2usb-native-output-telemetry-<variant>/` contains the successful hand-off application, configuration, partitions, flash recipe, logs and manifest. Existing development checkpoints and versioned releases were preserved.

Relative to each matching N5 image, the only sdkconfig change is the added default-enabled `YORADIO_HTTP_REQUEST_BUFFER_RELEASE`. Hardware clocks/pins, DMA geometry, codec selections, quiet diagnostics profile, cores/priorities/stacks and OTA partitions retain their baseline. The three-owner task table and board configuration are checked against `edccc3ac`.

Final ELF symbols verify both PDM callback and metrics queue-drop helper in IRAM, plus the 64-byte state and 8-byte lock in DRAM. Both DAC variants retain the state/lock and driver counters. These static sizes do not measure heap savings, runtime overhead or IRQ latency. Quiet/diagnostic helper object evidence remains in the initial archive.

All six actual SDK compile databases select the hash-audited build-local HTTP source, byte-identical to the separately compiled whole-source Xtensa checkpoint. The linked release symbol and correct vendor/custom FLAC symbols are present. SDK installations were not patched in place.

If legacy driver warnings are present, they are exclusively the three known IDF 5.5.4 APLL deprecation diagnostics; their exact raw lines are retained in `SDK.json`. No new warning was suppressed. The complete Clang53 checkpoint remains 86 baseline warnings and zero errors.

The vendor PDM environment log also records one SDK activation cleanup warning: a temporary file was already absent (WinError 2). Pinned `tools/export_utils/shell_types.py` only warns while removing old activation files and continues; the SDK source is copied in `appendix-tools`. This is recorded separately from compiler diagnostics. The first local qualification attempt rejected it because its warning classifier was too broad; only that classifier changed, without rebuilding or modifying any image.

Physical playback/HTTP/HTTPS/WebUI/OTA, live memory savings, DMA/IRQ behavior, audio quality, watchdog/resource margins and prolonged operation remain open. This appendix does not close stages 12, 13, 14 or physical acceptance.

`SDK.json` retains all six receipts, configuration differences, selected ELF symbols/addresses, compile rows and hashes. `appendix-tools/` preserves the exact local qualification/build helpers used. The raw initial archive files and bound README/HOST reports were not changed.
