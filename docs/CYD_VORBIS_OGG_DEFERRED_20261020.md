# Deferred CYD Vorbis/Ogg target extension

The existing isolated raw Vorbis bridge and its
[published raw PCM/preflight qualification](../tests/results/cyd-vorbis-bridge-20261020/README.md)
remain unchanged. The additional public Ogg EOF/reset/pending-ownership work
was stopped by automatic content review with the reason:
"This content was flagged for possible cybersecurity risk." This is a tooling
restriction, not a confirmed firmware vulnerability. The work is deferred;
no rephrasing, replacement agent or alternate execution bypasses the block.

The ignored preparation is `.build/cyd-vorbis-ogg-prep-01/`. Attempt
`.build/cyd-vorbis-ogg-01/` ended with exit 1 before FFmpeg decode, target build
or emulation: a Windows path separator comparison omitted required copies.
The historical runner/manifest and report are retained. A narrow runner fix
used `relative.as_posix()`; the production bridge and SDK were unchanged.

The previously authorized attempt `.build/cyd-vorbis-ogg-02/` independently
confirmed the fixture's 528000 PCM frames and 2112000 PCM16 bytes with FFmpeg
and the EOS granule. This is count/granule evidence, not bit-exact
floating/fixed-point PCM equivalence. At the automatic flag, the agent reported
session 22303 live in SDK compilation. The parent could not access that
agent-local handle; a scoped read-only process inventory confirmed the existing
runner/build/compiler chain still live. No restart or new test was launched.
A later scoped inventory found no remaining process from that chain.

The retained nonpassing report ends with
`observer not selected media_lib_module_malloc`: SDK compilation completed,
but the ELF observer-selection check stopped the runner before QEMU. The
agent-local terminal exit code is unavailable to the parent; process absence
and the nonpassing final report are the observed end state. No new Ogg runtime
case or control was executed or qualified, and no firmware defect is inferred.

The remaining [Vorbis/Ogg gates](CYD_VORBIS_TRANSFER_DESIGN.md) include public
EOF/reset/retry lifetime, allocation errors, concurrent scopes, broader formats,
callback bindings, audio-task integration and physical acceptance. Unqualified
drafts are not connected to radio. The [transfer plan](ESP32_CYD_C3_TRANSFER_PLAN.md)
keeps this item open for a later approved continuation.
