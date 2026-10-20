# CYD request-buffer release qualification (2026-10-20)

This archive records the M13 C3-to-CYD memory-policy audit and bounded HTTP
request TX-buffer release candidate for pinned ESP-IDF 6.0.2. The audit is a
historical snapshot: production integration and output telemetry intentionally
changed some live firmware/configuration inputs afterward. Its original
"unchanged after" fields describe the original run, not today's checkout.

- [Memory audit](audit/report.json): donor/current configuration, SDK source
  comparisons, map-symbol observations, ownership risks and measured-policy gates.
- [SDK-source host proof](host/report.json): 17 cases and 8 exact semantic
  controls under ASan/UBSan, with selected actual SDK functions/header utilities.
- [Whole SDK Xtensa object compile](target/report.json): exact existing CYD
  compile row, unchanged flags/includes/config, 248 dependencies captured before
  compile and 264 total recorded inputs; exit0, no compiler diagnostics.
  [Retained object](target/esp_http_client.c.obj) is ELF32 ET_REL EM_XTENSA94;
  `nm` defines the new API once. This is not a linked production application.
- [Radio/CMake integration proof](integration/report.json): 31 enabled plus31
  disabled actual `open_stream` cases, identical observable HTTP traces,
  6 exact semantic controls and 9 configure-time helper scenarios.
- [Failed attempt metadata](failed-attempts.json) retains the precompiler import,
  postcompile CRLF validator and missing WSL CMake failures without recasting them
  as successful test runs.

The radio config requests **4096 TX payload bytes**. This is neither a measured
usable allocation size nor a guaranteed 4096-byte free-heap gain. No physical
heap, fragmentation, TLS runtime, audible playback or performance result is
claimed. The installed SDK was not modified: the exact-source patch is used on
a build-local copy and preserves unrelated SDK bytes. Other TLS reserve/IRAM
configuration changes from C3 remain separate candidates with measurement gates.

The bounded production integration is present in the captured integration
snapshot, default-enabled behind `CONFIG_YORADIO_HTTP_REQUEST_BUFFER_RELEASE`.
The production application build/link/placement gate is pending separate parent
evidence and is not bound by this archive. No firmware image or device test is
included here. See [HOST.md](HOST.md) for seams and replay limits.

Run `python -B verify.py` from this directory. [manifest.json](manifest.json)
hashes every archived payload and metadata file except itself; publish its own
SHA256 alongside the bundle. [catalog.json](catalog.json) maps original artifact
paths to short `objects/<sha256>` payloads or explicit binary omissions. Reports
and root commands/logs keep their original bytes. Long dependency/source paths
are flattened; Windows tool executables and Linux host binaries have hashes and
sizes only. Actual Xtensa relocatable objects are retained. `.gitattributes`
disables text conversion so Git preserves the byte hashes.
