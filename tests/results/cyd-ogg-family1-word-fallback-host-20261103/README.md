# Ogg family1 byte-allocation fallback: HOST checkpoint

This package qualifies the HOST contract for an ordinary15360-byte PCM allocation
refusal followed by a successful word-plane fallback. The motivating native
failure remains NONPASS and its evidence stays separate; this package does not
relabel that run or establish native application fit.

The adapter now keeps its successful ordinary byte path and existing large-plane
path. If a small byte allocation fails, it tries the existing atomic word-plane
reservation. The original memory error is emitted only when both allocations
fail. Frequency, precision, packet bodies/cadence, channel layout, gain, task
profiles, watchdogs and deadlines are outside this change.

The frozen HOST successor passes both byte-only and word-enabled configurations:
**43 schedules /12 controls /12,983,296 exact creator PCM samples each**. The word
variant adds **23 controls /383,992 exact samples**, with186 word-allocation
attempts and16 simultaneous old/replacement planes.

| Contract | Evidence |
| --- | --- |
| Fatal baseline allocation refusal | Byte-only behavior is unchanged. The word-enabled fatal control explicitly refuses both allocators and requires the word attempt. |
| Successful small fallback | The complete original C8/20 ms stream uses257-byte feeds and exact independent creator PCM. Assertion-enabled output callbacks require8 live1920-byte word planes after the first refused byte allocation. Every output callback must witness that storage; all real creator handles and planes are cleaned. |
| Failed growth fallback | An existing7680-byte byte workspace is preserved at15360-byte growth when byte realloc and word candidate1/4/8 refuse. Pointer, capacity and every old byte remain unchanged; only partial candidates are freed. These are synthetic storage-contract controls. |
| Previous19 contracts | Initial/large-upgrade/word-growth refusals, alignment, atomic replacement/reuse, gather bounds, complete creator odd trim/duplicate/silence mapping, full close retention and wrapper cleanup remain. Their19 runtime event records are byte-for-value equal to the published predecessor's parsed records. |

Both configurations were built and run with ASan/UBSan, assertions enabled and
halt-on-error options. `captures.zip` retains the exact successful fallback01
report, command logs, dependency records and source snapshots as text. Identical
records are deduplicated by SHA256 without rewriting originals. It binds all36
recorded source/input identities and30 current source/header identities.

The package also retains the exact already-published predecessor manifest and
its selected final04 report/stdout records. Their identities are checked against
that manifest before comparing the original19 event records. This authenticates
the selected historical records; it does not rerun or requalify old code as
current. The predecessor package remains unchanged.

Executable and encoded-media originals remain whole/local, with original paths,
sizes, SHA256 values and omission reasons in the manifest. No executable, object,
PCM or encoded-media payload is published. The verifier never reads omitted
originals, compiles or executes archived code, or decodes audio.

```text
python -B tests/results/cyd-ogg-family1-word-fallback-host-20261103/verify.py --require-current
```

This verifies saved data, actual terminal sanitizer invocations, all23 contracts,
the two unchanged baselines and the complete current source graph. It does not
qualify native allocator success, IRAM access, full application memory headroom,
real task timing, physical hardware or performance. Fresh native acceptance
remains a separate gate.
