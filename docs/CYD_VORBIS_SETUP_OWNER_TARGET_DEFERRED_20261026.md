# Exact setup-owner target preparation remains unqualified

2026-10-26. The new metadata/lifetime owner passes its independent host tests,
but its separate ESP32 SDK/QEMU qualification did not start.

The target agent created seven project files: two CMake files, main.c, an SDK
launcher, SDK defaults, partitions and README. Its controller-write call
(`functions.exec` wrapping `apply_patch`) returned exactly `aborted before
dispatch`, without a reason or process handle. Read-only checks confirmed the
controller was absent. One identical retry, with the same tool/content and no
reformulation, returned the same result. A README update also failed with that
tool response. No explicit approval or cybersecurity rejection was supplied;
the cause is unknown and must not be described as confirmed cybersecurity
blocking.

The controller and protocol-test files were never created. No SDK build,
merged image, QEMU process or native runtime case exists for this owner. No
different agent, path or execution tool completed the failed controller write.
The seven surviving files are retained as an unrun prototype in the checkpoint
archive, with exact member hashes. Its README refers to an intended controller
that does not exist; those instructions are not an executable qualification.

The initial prototype selected `prefix_sweeps=0` and priority0/core1 with a
16 KiB stack, keeping watchdog and idle checks. That narrower metadata subset
would not close the full owner target gate. Future qualification must preserve
all335 host cases and all valid-header prefix sweeps, yielding through
`owner_test_poll`; it must retain actual UART/SDK/configuration/stack evidence
and all failures. The archived prototype is not counted as a pass.

The host qualification remains valid. Neither production application selects
the new component. Previous DSP scheduling, packet-target, floor0-amplitude,
old vendor/Ogg and other deferred scopes remain separate and unchanged.
