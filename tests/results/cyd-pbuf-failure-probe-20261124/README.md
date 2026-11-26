# Bounded pbuf failure attribution: host, SDK and native evidence

The diagnostic now has [three-output SDK/Clang/ELF qualification](sdk/README.md)
and [actual QEMU observations](native/README.md). Every original native
controller verdict remains **NONPASS**. These observations do not fix or
relabel the [earlier RTC-off HE-AAC resource failures](../cyd-openeth-no-rtc-20261124/README.md),
and no production default or audio task binding is changed.

| Observer output | Observed result | Attribution |
| --- | --- | --- |
| Legacy DAC | WebUI connection closed before EOF | No EOF dump; unavailable |
| PDM | WebUI/health response could not be decoded before EOF | No EOF dump; unavailable |
| Continuous DAC | Exact 614,400-frame PCM, WebUI after EOF and two WS peers; allocation gate fails | Ten recorded pbuf NULL returns at the exact qualified `tcp_write` call |

Missing legacy/PDM snapshots are not zero-failure observations. Continuous
DAC's bucket is transport layer 54, PBUF_RAM type 640, length 1,440 and derived
allocation size 1,512 bytes; its count is ten, without table overflow or
saturation. The captured instruction and inline source locations match the
frozen linked ELF. Its global allocation count is also ten in the captured
WebUI, EOF and last-reachable samples. Those samples and the cumulative
PCM-flush prefix retain their separate observation windows. The final
post-close resource samples remain absent, and no NONPASS is promoted.

The [TCP oversize disabled experiment](oversize-disabled-20261126/README.md)
also remains NONPASS: the pinned SDK requires nonzero `TCP_OVERSIZE` while
the unchanged `LWIP_NETIF_TX_SINGLE_PBUF=1` is enabled. The actual compile
reached that guard and produced no linked candidate application. Original
preparation/header-checker failures and the reviewed continuation are retained;
the SDK guard and single-pbuf policy were not changed to obtain a build.

Certificate-date validation was already disabled in these unchanged profiles
(`MBEDTLS_HAVE_TIME_DATE=false`). The disposable CA/server certificate dates
were expired at the recorded host time. The retained signature/chain/hostname
policy does not establish validity-date enforcement; these results make no
claim that certificate dates were validated. The date-policy record contains
metadata only, with keys and certificate bodies kept local.

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

The completed SDK checks retain exact configuration/header bytes, image/ELF
and OTA bounds, actual linked call reach, and explicit system-header warnings.
The observer occupies 128 bytes plus an 8-byte lock in ordinary DRAM; data
grows 136 bytes and heap-start grows 144 including linker alignment. Static
frames are measured separately from total call depth and physical stack margin.
GNU wrapping can still miss calls resolved inside `pbuf.c`; that clone bypass
is explicit in the linked proof. Host and static checks do not substitute for
the missing legacy/PDM attribution or an allocation-free native workload.

The next implementation is a bounded streaming status serializer retaining
the full JSON contract, both clients, one WS frame and the existing total send
deadline. Its DRAM saving and complete three-output resource gate remain to
be measured. Independent actual-target WS/WSS protocol qualification and
physical Wi-Fi/audio acceptance remain separate. The original strict
controller still requires zero allocation failures.
