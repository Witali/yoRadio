# Actual SDK/Xtensa fixture

```
python -B -X utf8 tests/run-cyd-tls-static-rx-qemu.py --sdk <SDK6.0.2> --tools <IDF-tools> --qemu <qemu-system-xtensa.exe> --powershell <pwsh.exe> --output .build/rx-target
```

Use `--preflight-only` for read-only requirements, or `--freeze-only` to capture
unbuilt/unrun sources. Neither proves target execution. `--compile-only` keeps
runtime qualification false. A normal run freezes all variants first, binds
source/tool/SDK hashes, builds the real SDK, verifies ELF94/source/header/allocator
and lifecycle-hook closure, merges flash and runs QEMU without a NIC. No device
or network is contacted. Production Kconfig is sourced exactly once, and the
actual canonical helper resolves paths inside a preserved repository-layout copy.

The proposed default matrix has12 variants: four positive reserve/reclaim
combinations plus eight exact controls for missing init/free hook, eviction,
revocation releasing a live loan, exclusivity, phase-scoped early publication,
heap-freeing a static buffer and bypassed reclaim. Disabled variants compile
original SDK TLS source without the reserve module/static slot/RX or diagnostic
wrappers. The ISR task-lock mutation stays host-only because an SDK panic cannot
count as a named target failure.

Enabled profiles exercise real public config/init/defaults/setup/reset/free,
numeric/pointer userdata, cleanup/address reuse while an old loan lives, full
registry fallback, two pinned cores sharing/distinct configs, erase handover,
actual esp_timer ISR initialization, pre-RX validation failure, four labelled
calloc-NULL injections and separate real heap-NULL/reclaim observations with live
input leases. Scoped callback-return injection follows the real certificate
provider and tests revocation only, not certificate validation or a TLS handshake.

Every heap-pressure predicate is captured before restoring memory. Only test
pressure blocks are freed before diagnostic/restart code, preventing its lazy
lock allocations from contaminating controlled failures. The strict no-panic
oracle is unchanged. A marker followed by a panic remains nonpass. No production
SDK lock workaround is part of this fixture.

Actual Xtensa/ISR/OOM behavior, full TLS protocol support, physical memory savings,
fragmentation, playback and default activation cannot be inferred from source
preparation or host results. Keep those limits in every archived report.
