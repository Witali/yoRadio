# Native OTA component dependency

This archive records fresh actual ESP-IDF 6.0.2 ESP32 CYD configuration and
native_ota component compilation, plus isolated actual ESP-IDF 6.0.2/6.1
component-present and component-absent projects. The shared component uses an
optional PRIVATE native_stream target dependency when already present. When
absent it keeps the existing private header fallback without discovering or
compiling native_stream. All three actual OTA translation units compile in all
four cases. The earlier SDK include-owner warning is in original-warning.log.

The complete CYD present-case normalized sdkconfig is preserved. The C3 checks copy
the baseline sdkconfig and actual main Kconfig definitions, but run an isolated
component project: full donor configuration would execute an excluded codec
patcher. Differences for unavailable full-radio symbols are reported; this is
not a full C3 app/configuration qualification. Existing C3 component discovery
and compatibility translation units are unchanged. Full application linking is
not qualified by this component check.

The first two SDK builds succeeded, while their initial Python runner later
failed on a cache-parser bug. Their original FAIL reports remain byte-exact;
separate read-only qualification reports inspect the original pre-build markers,
logs, three compiled objects, headers and static archives without rebuilding.
One CYD harness object-path advisory and one C3 missing isolated-partition CSV
advisory are explicitly retained. The latter also has partition-inspection
tracebacks. Neither is treated as OTA/compiler evidence or full app/partition
qualification. Five existing SDK6.1 Wi-Fi include-owner warnings match the
immutable C3 baseline. The gate requires zero new source/compiler warnings;
it does not claim zero total warnings. The two remaining combinations use fresh
short build directories and exact copied partition CSVs.

The initial builds identify installed tools after the build, comparing the
actual compiler to the immutable earlier firmware manifest. They do not claim
a newly captured pre-build identity for every tool. The two fresh builds also
capture before/after tool identities. All original SDK tracked-state pins and
scoped source snapshots are preserved.

review/report.json preserves a final read-only audit and four byte-exact selected
Ninja application link metadata rows with offsets and original database hashes.
Those rows show optional stream archives outside whole-archive spans; the full
application linker was not executed. history.json keeps the two original runner
errors separate from actual successful SDK builds and later qualifications.
The original failing check.py and first failed qualification tool are retained
as provenance; run.py and qualify.py record the later workflow. These are
checkout-bound evidence tools; only verify.py is a standalone offline command.

No application image, hardware operation, OTA update, decoder behavior, core
binding, or memory saving is qualified here. Ninja builds the native_ota static
archive and its ordinary build prerequisites; full application linking is not run.

Reports and logs are copied byte-for-byte. Payload names are content addressed;
large textual payloads use lossless gzip. SDK headers, installed tools, generated
objects/libraries and large command/graph databases have explicit byte/SHA-256
identities rather than duplicate binary copies. The three actual compiler rows,
selected generated metadata, source snapshots and header identities are retained.

Run `python -B verify.py` from any directory for an offline integrity and scoped
evidence check. This verifier does not rebuild or assert full application/runtime
equivalence. Root manifest excludes itself, lists every other archive file, and
binds exact stored bytes. path-map.json binds original bytes after decompression.
