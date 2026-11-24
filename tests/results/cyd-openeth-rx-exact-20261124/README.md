# OpenETH exact-length RX host evidence, 2026-11-24

This package records **host-only** ASan/UBSan validation of the diagnostic OpenETH RX overlay. The generated SDK RX task and unchanged receive function pass 18 ownership, allocator-pressure, bounds, payload-copy, retirement, and cleanup cases. This package makes no firmware-build, QEMU-runtime, TLS/PCM/WebUI, or physical-board qualification claim.

The candidate delivers a 64-byte frame with 256 bytes of heap available. The exact pre-fix maximum-allocation negative control requests 1,522 bytes and cannot deliver that frame under identical pressure; expected exit code 17 is preserved. A valid 1,522-byte frame exercises allocation failure, descriptor retention, one-tick backoff, successful retry, one delivery, and cleanup. Zero/oversized descriptors retire without allocation or payload reads. Hardware-owned descriptors remain untouched. Changed SDK bytes are rejected; CRLF normalization is accepted.

- Pinned SDK source SHA256: `b0526b76120abffe37ee8bd87b9e204880da18a5c02383e5d39b8e001bbcbb7d`.
- Exact prior diagnostic overlay SHA256: `77827f4605a712e9057484fe5999c8a3405e3e617f3f45e52ca8933d96be6cca`.
- Candidate generated source SHA256: `e4808727b9a3a5a0e1617d57f0d39a11bdf85443b9e3556990ea4822cef60882`.
- Generator SHA256: `b57bba4efafe4fd6b388502b58622efba4eacd696c166dba04368f834f3e0d5f`.

`host/report.json`, compiler version, candidate/control logs, and frozen source/header/runner copies remain byte-identical to the successful raw run. `host/function-bindings.json` binds the exact extracted function bytes and descriptor declaration to the full SDK snapshots. Full SDK snapshots preserve their original Espressif copyright/SPDX notices; `host/sources/LICENSE-ESP-IDF` supplies the Apache license. Binaries and caches are excluded. `host/artifact-manifest.json` fingerprints the immutable host package.

The test entry point and all 18 cases are documented in [the host test directory](../../target/cyd_full_app_openeth_qemu/openeth_rx/README.md). The host uses controlled platform/allocator/descriptor stubs; it does not emulate IRQ concurrency, register layout, network timing, or actual frame arrivals. This optimization changes diagnostic OpenETH allocation behavior, so preserve prior fixed-size runtime controls and qualify a newly built diagnostic image separately. Production CYD Wi-Fi source/configuration is unchanged by this overlay.
