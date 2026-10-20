# CYD TLS reserve / early MPI audit — 2026-10-20

**Read-only next-step evidence. Both suggestions are unimplemented, default-off
candidates.** No production source, configuration, SDK or Git state was changed
by the audit or this archive. No build, preprocessor, network, crypto operation
or device run was performed. Deferred AAC/private owner-view investigation,
repair and circumvention remain excluded.

The accepted [raw report](raw/report.json), SHA-256
`e37862e39ea2b612eae72a660bc83454f8a8fbbf658a29dc6c0de33e40423001`,
is preserved byte for byte, together with its initial report, capture metadata,
source/header/config snapshots, helpers, source diffs and existing compile-row
metadata. All 82 input identities and their historical before/after checks are
retained. These describe the captured audit, not the current working tree or a
new production build. The captured `build-c3-transfer` profile had opt-in input
reclaim enabled; the source Kconfig default remained `n`.

The captured CYD profile uses **static TLS buffers**, full RX content 16384 and
TX content 4096, with dynamic buffers and variable buffer length disabled.
Static RX is allocated directly by `mbedtls_ssl_setup`. The C3 reserve targets
four dynamic-adapter RX sites with a different header/capacity formula; it
cannot be copied into this profile. The proposed bounded option instead uses
the SDK's `MBEDTLS_SSL_IN_BUFFER_LEN` expression, a narrowly tagged static RX
allocation and strictly paired release through the actual mbedTLS allocator.
It must preserve the existing input-reclaim service. No constant such as 17058
is proposed or qualified. A static slot consumes permanent RAM; no RAM saving,
improved fragmentation or successful concurrent-TLS behavior is established.

The examined normal SDK startup initializes common libc and PSA objects, but
does not explicitly initialize the separate lazy MPI peripheral mutex. Early
public acquire/release is therefore a candidate for moving first allocation
before application services. Actual pre-`app_main` first-use tracing is still
required. The public API returns `void`; the SDK lazy constructor calls
`abort()` on allocation failure. No recoverable OOM return, actual runtime MPI
result, allocation-size value or fragmentation/timing benefit is claimed.

The report preserves exact SDK source/header guard hashes and entry lines,
including the difference between the historical donor patch guard and the
captured SDK snapshots. This is a source compatibility observation, not an
executed donor build failure. R1–R4 and M1–M4 remain **unrun**: actual Xtensa
compile/guards, allocator/free pairing, reserve OOM/concurrency, full-record and
resource validation, fresh-boot MPI first-use observation, actual SDK mutex
startup/contention, void-API OOM controls, and useful-effect/production gates.
No early-MPI implementation is included in this archive.

[path-map.json](path-map.json) maps every original payload/input and absolute
Markdown line link to its archived snapshot or explicit omission. Raw paths
have not been rewritten. [omitted-binaries.json](omitted-binaries.json) records
each omitted SDK build archive and tool executable with its original path,
role, byte count and SHA-256. No `.a`, ELF object or executable bytes are stored
here; the original audit recorded these artifacts as hash-only metadata.
Offline verification cannot independently reproduce omitted binaries or prove
that the SDK runtime follows a proposed integration.

Run using Python 3.9 or newer; no SDK, packages, network, Git or hardware needed:

```text
python -B tests/results/cyd-tls-reserve-mpi-audit-20261020/verify.py
```

The verifier checks the full manifest, accepted raw-report identity, all source
and omission mappings, entry tokens at their captured lines, guard identities,
profile values, seven unexecuted compile rows and eight pending gates. These
are archive integrity and selected source-entry checks, not implementation or
runtime qualification. Local `* -text` attributes cover every archived file.
