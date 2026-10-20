# Early MPI: seven production application exports

This additive archive records 7 linked applications built from
the same clean committed source `1190aebce400375c382a5ad54211e2400f98161d`:
vendor and custom codec profiles on PDM, continuous DAC and legacy DAC, plus a
vendor PDM control with early MPI disabled. Each export starts from its matching
committed TLS-input-reclaim baseline. The only configuration delta is the new
MPI bool, absent → true or, for the control, absent → false. Reclaim and HTTP TX
release remain enabled. The production Vorbis bridge remains unconnected.

The exact two-PDM qualification SHA is
`7c2007b1a33a3dfedde6be0ee13e09b463403d6ffdd9d6506fbe1edbbb29a1f4`.
The five-profile/full-seven qualification SHA is `e3c38cfb48ee19652ba1935bce3b1ab4a5e12db5e831c51750adb40e86a4b8f9`.
Both reports, pre-build markers, seeds, exporter receipts, raw compiler/CMake
logs, nm/disassembly evidence, actual build flags and canonical source snapshots
are retained without rewriting their bytes. Deterministic gzip and a
content-addressed map keep large text and long original paths compact.
Selected canonical text sources retain both actual compiler-working bytes and
raw HEAD Git blobs. Their relationship is required to be byte equality or exact
uniform LF/CRLF conversion, reconstructing the working bytes without any other
change. Mixed line endings and other changes are rejected. Raw baseline,
evidence, receipt and archive payload bytes are never normalized.

The linked-image checks cover Xtensa ELF machine 94, application checksum and
OTA fit, exact configuration scope, the canonical whole module, first actual
`app_main` call before logging/health/state/NVS, one public MPI acquire/release
pair, ordinary allocator/free/reclaim ownership, the canonical HTTP overlay,
unchanged task/core/stack and board settings, and PDM-specific callback IRAM.
`warnings.json` distinguishes the existing native_ota/native_stream CMake
dependency warning, the original long-object-path warnings, known legacy APLL
deprecations and environmental cleanup messages. The dependency warning remains
an explicit buildgraph follow-up; this archive does not fix it.

Run `python -B verify.py` for a standalone offline integrity and selected-entry
check. It validates the complete manifest, decompressed original hashes,
marker/report links, exact seven profiles, initial/config deltas, recorded ELF
metadata and recomputed disassembly call traces. It reads only this directory.
The file table excludes `manifest.json` itself; its external handoff SHA binds
the root table. Every archive file uses local `-text` attributes.

Firmware stays under `firmware/development/<variant>/app.bin` and Git LFS.
Selected ELFs, firmware, tool executables, objects, archives and local LFS
binary objects have explicit SHA/size/role omission records and are not copied
here. The path map covers the selected marker/qualification closure and history;
unreferenced replaceable SDK working artifacts are outside that scope.

The original `cyd-early-mpi-20261020/README.md` and `HOST.md` are unchanged
historical evidence: their then-pending export gate is closed by this additive
archive. Earlier readiness and the failed first LFS prepare are preserved with
their original limits, including the absence of a saved raw stderr stream.
`HOST.md` describes reproduction and omission details; `SDK.json` summarizes
the seven images.

This is static linked-application qualification. Default MPI remains off.
Physical playback, actual radio pre-app mutex observation and measured memory,
fragmentation or speed benefit remain open. No application runtime, crypto or
network operation was performed by this archive packager. Deferred codec
extensions and AAC investigation are excluded.
