# Bounded pbuf failure attribution: host foundation

This diagnostic is implemented and host-qualified; target SDK/link/frame and
full-application QEMU attribution remain pending. It does not fix or relabel
the [RTC-off HE-AAC resource failures](../cyd-openeth-no-rtc-20261124/README.md).
No production firmware, network policy or audio task binding changes here.

The opt-in `CYD_OPENETH_PBUF_FAILURE_PROBE` forwards `pbuf_alloc` exactly once.
After a NULL result it records the full layer/type/length, derived RAM size
and SDK-normalized call-site PC. Four exact tuples use 128 bytes plus a
separate critical-section lock. Overflow and saturated counters are explicit.
There is no heap query, allocation, task discovery or logging in the recording
path. The existing diagnostic output owner snapshots under the lock and
prints outside it after the real PCM flush. This adds DRAM and stack overhead;
neither cost is inferred from the host ABI or described as zero.

The [portable record test](record-host-01/report.json) passes six ASan/UBSan
contract groups, including 100,000 updates and concurrent snapshots under the
same external pthread mutex. Three mutated implementations are rejected:
type narrowing, ignoring caller identity and wrapping the total count.

The [actual wrapper test](wrapper-host-02/report.json) passes ASan/UBSan with
100 successful forwarding vectors, nine NULL/type/derived-size vectors,
distinct real callers, an empty dump, snapshot immutability and 2,000 concurrent
wrapper calls. Its exact copied SDK `esp_cpu_utils.h` supplies window-bit
normalization and the three-byte call-site adjustment; synthetic cases also
check that helper. Five mutants are rejected: duplicate real allocation,
recording success, logging inside the lock, an unlocked snapshot and extra
heap work on failure. Host `struct pbuf` is 24 bytes in this run, not target16.

The [first wrapper attempt](wrapper-host-01/report.json) remains NONPASS:
the sandbox prevented WSL compiler access before compilation. The authorized
second invocation completed; the first report/logs are not replaced or
interpreted as an implementation failure. All selected logs, source/stub
copies, reports and host stack-usage files retain original bytes in the
[host manifest](host-artifact-manifest.json). Test executables remain local.
The first WSL error log is raw UTF-16LE without a BOM; its separately bound
UTF-8 inspection view preserves the text while the original log stays intact.
Instrumented host frames are not Xtensa frame or physical timing bounds.

Next, qualify actual SDK ABI/config/image/ELF and linked wrapper reach on all
three outputs. GNU wrapping can miss calls resolved inside `pbuf.c`; wrapper
symbol presence alone does not establish coverage. Symbolize captured PCs
against the new exact ELF, compare classified counts with the independent
global heap-fault count, and retain overflow or any unexplained remainder.
The original strict controller still requires zero allocation failures.
