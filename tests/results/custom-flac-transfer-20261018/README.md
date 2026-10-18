# Shared custom FLAC component checkpoint

The canonical adapter/API/build recipe now lives in
[idf/components/custom_flac](../../../idf/components/custom_flac).
The historical C3 component keeps thin compatibility includes. Both native
projects discover the same component; CYD runtime integration and vendor/custom
selection are still pending. The default CYD vendor decoder is preserved.

Adapter/core algorithms retain their previous bytes, including the qualified
metadata EOF fix. [Fresh actual decoding](shared-eof/report.json) passes5387
metadata/EOF groups and720 complete PCM comparisons against known encoder PCM,
fresh FFmpeg and the exact old adapter. The old adapter at `fc89b4a9` still fails
4308 EOF checks as expected. ASan/UBSan are enabled. Generated fixtures and PCM
are reproducible from archived source generators; binary fixtures are omitted.

[SDK components](sdk-components/report.json) records actual RISC-V and Xtensa
compilation of the shared adapter/core, with512 output frames and segmented
workspace, and no bytewise Rice experiment. Both static libraries build without
compiler diagnostics. This is component qualification, not application linking,
Xtensa execution or a speed/RAM claim. SDK configuration notifications remain in
the raw logs. [C3 maintenance API compatibility](c3-maintenance-api/report.json)
passes one actual custom-branch idle scenario with explicit codec/RTOS resource
seams; it does not replace the prior148-scenario owner qualification.

The supplemental C3 format/PCM harness required its missing actual JSON-writer
header after the preceding WebUI refactor. The repaired existing callback,
format, PCM/AAC ownership and framing suites pass with ASan/UBSan; their output
is preserved in `supplemental`. These logs are supplemental rather than a new
fully frozen whole-unit campaign. The three FLAC-specific Node checks pass.
The broader52-test source-assertion run records45 passes and seven failures;
the same seven fail when project source reads use exact Git blobs from
`2db2fd91`. Those checks require older probe/bitrate/queue/WebUI source shapes;
their migration remains separate, and no full Node pass is claimed here.

Next gates: CYD callback with source depth separate from PCM16, complete decoder
ownership/Stop/EOF/maintenance transitions, actual adapter lifecycle/OOM tests,
application SDK images, custom-path QEMU PCM/guard checks and physical CYD A/B.
TFT/pins, clocking, core bindings and audio backend parameters are unchanged.
The custom decoder remains one global workspace and must have one owner.

The [design](../../../docs/CYD_FLAC_TRANSFER_DESIGN.md) records format and memory
limits. [archive-manifest.json](archive-manifest.json) inventories raw sources,
reports, tools and logs. Existing versioned evidence is not rewritten.
