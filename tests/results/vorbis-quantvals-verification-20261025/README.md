# Lookup1 publication checks, 2026-10-25

The [final checkpoint](../vorbis-quantvals-20261025/CHECKPOINT.md) passes the
offline arithmetic/evidence verifier from the parent checkout. Actual terminal
chunk `8abf83` exits0. The checker independently verifies all35975 root values
per host model, both2179-row native target results,18 native command terminals,
the original UBSan witness and the separate before/after reader tests/replay.
It launches no compiler, SDK, QEMU or decoder.

Final manifest SHA256:
`8d6bc4a4245ebfb8bc14d9c660e543af54e41e55f6cb9382044851e2e14faedf`.
The archive contains291 aliases,158 objects and33 explicit omissions. Actual
collection02 terminal `72f129` exits0; its original receipt and both streams are
saved here alongside the actual offline verification receipt/streams.

The initial collector exits1 before publishing a manifest (chunk `85cf9c`).
It incorrectly compares Windows Path sort order with normalized relative-string
sort order. The original collector and its receipt/streams are retained as
`attempt01-*`; the partial archive is preserved locally at
`.build/vorbis-quantvals-archive-attempt-01` and is not qualified. Collector02
changes only the initial inventory to use the same sorted relative strings as
the final check. No source, runtime data or numerical result changes.

Executable/ELF/flash omissions are explicit identity-only records. Native ELF
architecture is verified from saved52-byte headers; complete binary semantics
or SDK closure are not claimed. Host GCC version/machine and actual compile/run
argv are recorded, but host test executable hashes are publication-time
identities, not independently observed launch-time hashes. All saved numerical
vectors are checked independently. These results do not establish full raw
decoder/PCM/G6, production radio integration, resources or physical acceptance.
