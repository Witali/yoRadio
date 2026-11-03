# Ogg family1 word storage: HOST integration checkpoint

The classic ESP32 family1 adapter can store large PCM plane sets through aligned
32-bit integer accesses. This checkpoint qualifies the current storage contracts
and dispatcher on HOST using real creator Opus synthesis. Its allocator and
close-status refusals are explicitly scripted HOST seams.

Both the original byte configuration and the explicit word-storage configuration
pass the same **43 schedules / 12 controls / 12,983,296 exact creator PCM samples**.
The complete original 20 ms fixtures, stereo 120 ms fixture, active C8/120 ms
fixture and both chaining orders remain in that baseline. The word configuration
adds **19 controls / 307,192 exact samples** and reaches 16 simultaneously live
old/replacement planes through the separately tracked allocator.

| Storage contract | Retained evidence |
| --- | --- |
| Initial allocation refusal | Requests 1/4/8 in the reservation contract and the full wrapper; error `OGP_MEMORY/92160`, no decode/publication, real creator-handle cleanup. |
| Byte upgrade and word growth refusal | Requests 1/4/8 preserve old pointers, capacities and exact contents; only partial replacement candidates are freed. These are synthetic storage-contract cases, not encoded packet-duration claims. |
| Alignment, replacement and reuse | An unaligned fourth candidate is rejected before access; successful replacement holds all old/new allocations until commit; reuse avoids allocation and fresh storage is cleared. |
| Gather | Odd offset, unaligned ordinary DRAM destination, duplicate/silent channels, output guards and bounds. |
| Complete creator trim/alias/silence | Unchanged complete C8/120 ms packet bodies with legal mapping `[0,7,0,7,255,5,6,255]`, pre-skip313 and exactly four unique word planes; every logical PCM sample is exact. |
| Close retention | Three complete C8/120 ms cases cover close retry, cancellation and reset refusal while retaining all live plane pointers/data, held EOS page, prefix and configuration. Successful cleanup does not replay output. |

Both configurations were built and run with ASan/UBSan. The final04 original
report, all command logs, dependency records and exact consumed source snapshots
are retained as unchanged text records in `captures.zip`. Identical text records
are deduplicated by SHA256 without rewriting their bytes. The manifest binds all
36 source/input records of the final run, the unchanged lower component harness,
production headers/helper, compiler/library observations and fixture provenance.

Earlier attempts remain distinct:

- **01 NONPASS:** the unchanged byte baseline passed; the new word test did not
  compile because its new callback initializer used the dispatcher callback type.
  The original failing compiler log and source are retained. This was a new HOST
  harness error, not a production decoder or SDK failure.
- **02 PASS:** both baselines and16 extra storage controls; no full-wrapper word
  allocation-refusal controls yet.
- **03 PASS:**19 extras, including full-wrapper refusals; aliases/silence in word
  storage still had synthetic coverage only.
- **04 PASS:** strengthens the existing full-creator odd-trim case to exercise
  the four-plane duplicate/silence mapping. It is the current qualified source.

Executables and encoded-media fixtures remain whole in their original local
captures. Their logical path, original path, size, SHA256 and reason for omission
are recorded. No executable, object, PCM or encoded-media payload is published;
the verifier never reads those omitted originals or decodes audio.

```text
python -B tests/results/cyd-ogg-family1-word-storage-host-20261103/verify.py --require-current
```

The verifier reads data only: it authenticates archive bytes, original reports,
logs, source/input identities, the unchanged two baselines, all19 extra contracts
and terminal sanitizer invocations. `--require-current` additionally checks current
repository source code and installed vendor public headers. Historical01–03 are
authenticated against their own snapshots, not relabeled as current runs.

This does **not** qualify ESP32 allocation success, IRAM access, native OOM,
complete application memory headroom, real task scheduling, physical hardware or
throughput. Those require their separate SDK/QEMU and board gates.
