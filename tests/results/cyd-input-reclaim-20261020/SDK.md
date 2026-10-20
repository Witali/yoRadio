# CYD opt-in TLS input reclaim: application qualification

All seven GCC applications were built/exported from clean source `a1b9d5a1e79d9433548bc0230fb15f0ea22c5584` on pinned SDK6.0.2. No board operation was performed.

| Profile | Reclaim | App bytes | OTA free bytes | Compiler warnings |
| --- | --- | ---: | ---: | ---: |
| pdm / vendor FLAC | on | 1544464 | 225008 | 0 |
| continuous / vendor FLAC | on | 1538096 | 231376 | 0 |
| legacy / vendor FLAC | on | 1543952 | 225520 | 3 |
| pdm / custom FLAC | on | 1518032 | 251440 | 0 |
| continuous / custom FLAC | on | 1511776 | 257696 | 0 |
| legacy / custom FLAC | on | 1517696 | 251776 | 3 |
| pdm / vendor FLAC | off control | 1543984 | 225488 | 0 |

Saved hand-offs are under `firmware/development/esp32-cyd2usb-native-tls-input-reclaim-<profile>/`: application, actual sdkconfig/text+JSON, partition table, flash recipe, logs and manifest. Six opt-in profiles cover vendor/custom FLAC with PDM/continuous/legacy; the seventh is a disabled vendor/PDM control. Older development images and versioned releases are preserved.

Relative to each matching immutable output-telemetry image, the only normalized configuration difference is the new `YORADIO_TLS_INPUT_RECLAIM` bool (true for six images, false for control). Production default remains off. Hardware clocks/pins, DMA geometry, quiet diagnostics, codec selections, task cores/priorities/stacks, board configuration and both OTA slots retain their baseline.

All seven actual ELF images retain ordinary SDK free. Six allocator initializers point to the production reclaim wrapper, and the disabled control points to the original SDK allocator. The exact canonical module and wrap/retention flags appear only in enabled compile/link inputs; no free wrapper or static TLS reserve is linked. Correct FLAC and HTTP-buffer-release symbols remain present. PDM telemetry helpers remain in IRAM and the prior metrics state/lock in DRAM. These checks establish linkage/layout, not physical heap savings, IRQ latency or audio continuity.

The pre-build marker freezes the complete clean exporter source snapshot, profile identities, raw prepared seed hashes, required evidence sets and exact local helper hashes. The final qualifier rechecks source content and tools before and after all seven receipts; every baseline text/JSON/receipt is byte-equal to its committed Git blob. Four pre-run metadata review gaps were corrected before any build; 14 exact invalid-data controls and the final independent review cover those guards. SDK/code/image checks still execute on the real outputs.

`appendix-tools/prepared-seed-reconstruction/` was generated after the builds from immutable baseline bytes and the frozen preparation recipe. Every byte hash equals the pre-build profile and actual exporter seed receipt. These are exact reconstructions, not a claim that new files were captured before compilation.

The complete actual-SDK QEMU allocator gate is preserved separately in `../cyd-input-reclaim-qemu-20261020/`; its five cases/four exact controls do not run full radio/TLS handshakes or output hardware. Initial host README/HOST and all raw reports remain unchanged. Full opt-in Clang remains54 units/86 baseline warnings/0errors, with no new warnings.

Any retained legacy diagnostics are the known IDF5.5.4 APLL deprecation warnings, listed exactly in `SDK.json`; environment activation-cleanup warnings are recorded separately. No new warning is suppressed.

Physical HTTP/HTTPS, WebUI/OTA pressure, fragmentation/resource recovery, stack margins, DMA/IRQ behavior, audio quality and prolonged playback remain open. TLS RX remains16KiB. This application checkpoint does not close the remaining reserve/MPI/IRAM/stack work in stage13 or stages12/14/physical acceptance.

`SDK.json` binds all seven receipt/image/ELF/config/tool/evidence identities, configuration deltas, pointer words and selected link/compile symbols. `SDK-codec-identity.json` rechecks the installed ESP32 codec archive identities. The additive manifest preserves every initial archive record.
