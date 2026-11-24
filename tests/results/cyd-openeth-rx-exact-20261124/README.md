# OpenETH exact-length RX qualification, 2026-11-24

The original **host checkpoint** records ASan/UBSan validation of the diagnostic OpenETH RX overlay. The generated SDK RX task and unchanged receive function pass 18 ownership, allocator-pressure, bounds, payload-copy, retirement, and cleanup cases. That host checkpoint makes no firmware-build, runtime or physical-board claim; the separate SDK/native follow-up below now qualifies the finite QEMU workload.

The candidate delivers a 64-byte frame with 256 bytes of heap available. The exact pre-fix maximum-allocation negative control requests 1,522 bytes and cannot deliver that frame under identical pressure; expected exit code 17 is preserved. A valid 1,522-byte frame exercises allocation failure, descriptor retention, one-tick backoff, successful retry, one delivery, and cleanup. Zero/oversized descriptors retire without allocation or payload reads. Hardware-owned descriptors remain untouched. Changed SDK bytes are rejected; CRLF normalization is accepted.

- Pinned SDK source SHA256: `b0526b76120abffe37ee8bd87b9e204880da18a5c02383e5d39b8e001bbcbb7d`.
- Exact prior diagnostic overlay SHA256: `77827f4605a712e9057484fe5999c8a3405e3e617f3f45e52ca8933d96be6cca`.
- Candidate generated source SHA256: `e4808727b9a3a5a0e1617d57f0d39a11bdf85443b9e3556990ea4822cef60882`.
- Generator SHA256: `b57bba4efafe4fd6b388502b58622efba4eacd696c166dba04368f834f3e0d5f`.

`host/report.json`, compiler version, candidate/control logs, and frozen source/header/runner copies remain byte-identical to the successful raw run. `host/function-bindings.json` binds the exact extracted function bytes and descriptor declaration to the full SDK snapshots. Full SDK snapshots preserve their original Espressif copyright/SPDX notices; `host/sources/LICENSE-ESP-IDF` supplies the Apache license. Binaries and caches are excluded. `host/artifact-manifest.json` fingerprints the immutable host package.

The test entry point and all 18 cases are documented in [the host test directory](../../target/cyd_full_app_openeth_qemu/openeth_rx/README.md). The host uses controlled platform/allocator/descriptor stubs; it does not emulate IRQ concurrency, register layout, network timing, or actual frame arrivals. This optimization changes diagnostic OpenETH allocation behavior, so preserve prior fixed-size runtime controls and qualify a newly built diagnostic image separately. Production CYD Wi-Fi source/configuration is unchanged by this overlay.

## Diagnostic SDK and native follow-up
The preserved host package remains unchanged. The SDK and native packages retain every preselected case, including any NONPASS result.
| Backend/case | Original controller state | Minimum heap | Allocation failures | Exact PCM |
|---|---|---:|---:|---|
| legacy/run-he-ws2 | TERMINAL_PASS | 5580 | 0 | True |
| pdm/run-he-ws2 | TERMINAL_PASS | 6716 | 0 | True |
| continuous/run-he-ws2 | TERMINAL_PASS | 7028 | 0 | True |
| legacy/run-he-ws2-repeat | TERMINAL_PASS | 4568 | 0 | True |

See `sdk/summary.json` and `native/matrix-summary.json` for config, driver-only, Clang, image, PCM/TLS/WebUI/WebSocket and allocation observations. Raw reports and UART preserve their original bytes.

These are diagnostic OpenETH RTC-on fixtures. They do not qualify production Wi-Fi, physical-board behavior, RTC-off HE-AAC headroom, or a default codec/profile promotion. The original controller states remain authoritative; no NONPASS case is relabeled from partial successes.

All four original controllers pass. Every run receives the full 102,420-byte
HE-AAC input over TLS1.2 with full-sized records, flushes all 614,400 stereo
PCM frames at 48 kHz with SHA256 `44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362`,
and serves the identical 13,588-byte WebUI asset before, during and after EOF.
Two live WebSocket clients require fresh status and application pongs in all
three phases, then close normally. Allocation failures, output failures,
driver errors, timeouts and short writes are zero in each final health report.
The PDM completion-queue overflow counter remains **4**, as recorded; exact
decoder PCM and successful writes do not establish physical DMA timing or analog
quality. No claim that every diagnostic counter is zero is made.

The SDK comparison covers 2,855 compiled objects: only the three OpenETH
objects change. Configurations, project TUs, generated headers, core/priority/
stack bindings, watchdogs and all 24 published production app/metadata files
remain unchanged. Six matched whole-driver Clang checks retain the same 32
warning occurrences per check with zero errors or added warnings. Image, ELF,
both OTA slots, RTC geometry and static frames pass. The application descriptor
version/date were deliberately held at the original diagnostic values for the
SDK-only A/B; source/object/ELF bindings identify the new generator commit
`482a3896033a5ef2f8131a728923457b6ff25b6e`. These are not newly relabeled clean
production releases.

The [prior fixed-size control](../cyd-i2s-dma-native-20261124/README.md)
remains NONPASS: legacy delivered the full PCM/WebUI but recorded one 1,522-byte
OpenETH allocation failure. Both new legacy cases pass with the same application,
model, network and RTC settings. This validates the scoped driver change for
these inputs; it does not promote RTC or prove arbitrary network/load margins.
The old continuous-DAC timeout remains preserved and is not retroactively
attributed to START or packet allocation without direct evidence.

Public CMake configure stderr copies replace personal home-directory names with
`build`; [redaction provenance](sdk/redactions.json) records original and published
hashes and replacement counts. Original logs remain local. Native reports/UART,
compiler diagnostics, SDK source and immutable host proof remain byte-identical;
no outcome or counter was redacted. The SDK artifact manifest binds the published
copies, while original-input identities continue to identify the local originals.

### Original health-sampling boundary

The four original controllers record seven health observations representing five
distinct snapshots. The last EOF snapshot precedes the final WebUI asset read and
WebSocket EOF command/normal closure. Zero allocation/output failures therefore
means zero in every available snapshot through that EOF boundary; it is not an
independent post-close memory observation. A final post-asset/post-close health
gate and a new three-output control have now completed, as recorded below. Earlier raw PASS
states remain the results of the original controller and are not relabeled.

## Final resource check after WebUI and peer closure

The [strengthened controller](../../run-cyd-full-app-openeth.py) closes both peers,
reads final status, then records `post_eof_health` while QEMU is still live.
[Fourteen host regressions](post-eof-host/report.json), including a late allocation
failure after an initially clean EOF sample and real main/finally failure/cleanup,
pass alongside the existing thirteen PCM/EOF observer tests. Expected reclaim
allocation count remains exactly one for the separate intentional-pressure mode;
these HE-AAC cases require zero. Earlier PCM/TLS/asset/peer assertions remain.

All three fresh native controls pass with controller commit `c1f7f3abf` and the
same frozen images/configurations/model as the preceding matrix:

| Backend | Minimum heap bytes | EOF allocation failures | Post-asset/close allocation failures |
| --- | ---: | ---: | ---: |
| PDM | 6,184 | 0 | 0 |
| Continuous DAC | 6,836 | 0 | 0 |
| Legacy DAC | 4,304 | 0 | 0 |

[The final matrix](post-eof-native/matrix-summary.json) binds complete TLS input,
614,400 exact PCM frames/hash, identical WebUI assets in all three phases,
fresh two-client status/pongs/normal close, clean final fault counters,
unchanged boot/generation/EOF state and the post-close observation marker.
Reports, UART and input bindings retain their original bytes. QEMU is stopped
intentionally after the last observation; exit status 1 is not presented as a
clean guest exit 0 or a guest crash.

In this PDM control `completion_queue_drops` is zero at EOF and 89 in the final
post-close sample, with zero allocation, write, timeout or short-write failures.
This is distinct completion-notification telemetry. The pinned SDK discards an
old queue entry when the completion queue is full and enqueues the latest buffer;
our PDM configuration enables `auto_clear_after_cb`. The observed increase is
after the stream ended. Decoder PCM equality and these counters do not establish
physical DMA/analog quality. The earlier four-case values remain unchanged.

This closes the last-operation monitoring gap for these three diagnostic
RTC-on/normal-TCP HE-AAC workloads. RTC-off resources, production Wi-Fi, physical
outputs and RTC timing/sleep remain separate; no default profile is promoted.

The later [matched RTC-off controls](../cyd-openeth-no-rtc-20261124/README.md)
now complete the same full TLS/HE-AAC/PCM/WebUI/two-peer workload on all three
outputs, but fail the allocation gate: legacy 171 failures, PDM 25, continuous
DAC 35. Only RTC workspace placement changes. These new NONPASS results stay
separate from this RTC-on matrix and do not modify any original evidence.
