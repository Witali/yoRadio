# AAC asymmetric channel owner: another 4 KiB in QEMU

## Result

`CONFIG_YORADIO_QEMU_AAC_ASYMMETRIC_OWNER` removes the unused PS reserve from
the left SBR channel. The right channel retains the complete PS overlay and
synthesis state. This report records the initial **QEMU-only** experiment.
The [physical follow-up](ESP32C3_AAC_ASYMMETRIC_PRODUCTION_20261004.md) now adds
an ordinary firmware flag and retains hardware/OTA results and remaining failures.

| Measurement | Scoped low-QMF baseline | Asymmetric owner | Difference |
| --- | ---: | ---: | ---: |
| Requested owner bytes | 35,900 | 32,744 | −3,156 B |
| Allocator block, including instrumentation overhead | 36,864 | 32,768 | **−4,096 B** |
| Reported usable allocated block | 36,852 | 32,756 | −4,096 B |
| Decoder context | 24 | 24 | 0 B |
| Decoder stack allocation | 16,384 | 16,384 | 0 B |
| Minimum concurrent-decoder stack margin | 2,844 | 2,844 | 0 B |
| Additional error, 657,540 synthetic PCM samples | Reference | **0 LSB** | Bit-identical |
| Five complete station captures, 12,505,088 channel samples | Reference | Same counts and PCM hashes | Bit-identical hashes |

The allocation saving is measured, not just `sizeof` arithmetic. The earlier
low-QMF step saved 10,240 allocator bytes; together these two changes save
**14,336 bytes** against the four-row-smoothing owner. No additional rounding,
mantissa compression, reduced output rate or channel removal is introduced.
This comparison preserves the existing PC18 high-history representation.

## Layout and consumer audit before the reduction

The original symmetric channel union reserves the PS overlay and its 2,304 B
synthesis state in both channels, even though PS only occupies the inactive
right channel. Merely shrinking the first union would break fixed strides and
smoothing-table offsets. The implemented layout uses these named fields:

- **Left:** 16 B control/bindings, 80 B smoothing pointers, 14,680 B frame:
  **14,776 B**.
- **Right:** the same 96 B prefix, then the union of the SBR frame or full PS
  overlay plus synthesis: **17,956 B**.
- **Tail:** initialization flag, PS pointer and inactive detection word: 12 B.

Both frames begin 96 B into their channel. All four table addresses are now
negative frame-relative offsets (−80, −60, −40, −20 B), so no extra pointer
loads or calls are needed per decoded sample. Six two-byte `C.LUI` address-base
instructions become two-byte `C.LI rd,0`; the register and instruction position
stay unchanged. The native DSP calculations are retained.

| Consumer | Required treatment |
| --- | --- |
| `sbr_open` | Its old fixed stride also controlled memset length and loop termination. The existing typed PS-preserving initializer now handles both first open and reopen. Each named channel gets its header, frame size, sync and startup fields; only live PS control is excluded from clearing on reopen. The native symmetric initializer is absent from the linked test ELF. |
| `init_sbr_dec` | Builds the same five-entry tables before the frame. The existing wrapper clears each fifth entry before it can escape initialization. |
| `sbr_read_data` | First-to-second frame stride is the left extent. After the second iteration, the comparison-only sentinel is `2 * left_extent + frame_offset`; it is never dereferenced and remains inside the owner. It is now a separate compiler descriptor from the PS detection word. Header copy and right-frame readers use the actual right field. |
| `sbr_applied` | Right status, frame, high-QMF work bindings, PS pointer, flag and synthesis addresses all come from target-compiled fields. |
| `sbr_dec` / envelope | Same frame layout and low-QMF scoped bindings; shared prefix-table addresses work for either channel. Both complex and real-only envelope call sites retain their existing handling. |
| `ps_allocate_decoder` / PS readers | All right-overlay vectors, hybrid state, delay rows, allpass storage and synthesis pointers move together through named fields. No PS array is shortened. |
| Top-level decode | Left sample-rate-mode and relocated/inactive PS accesses use compiler descriptors. |
| Reset, reopen, allocation/free | Named left/right views replace indexing a fictitious equal-size channel array. The per-decoder TLS owner, failure cleanup, preserved PS fields and right synthesis reset remain checked. |
| Audit wrappers | Expected frames, regions, table bases and exact rows are derived from the actual left/right objects; they do not accept arbitrary in-owner addresses. |

The pinned archive SHA-256 remains
`311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909`.
The copied objects are changed locally at audited instruction positions;
the installed archive is untouched. Tests compare every byte of all seven
native function bodies against the listed patches, including the fourteen
existing low-base load replacements. Compiler assertions reject prefix drift.

## Verification and limits

Six QEMU runs pass: synthetic AAC-LC/HE-AAC/HE-AACv2 controls and five retained
station recordings. They include allocation failures, reset/reopen, full-rate
format changes, active PS and two concurrently live decoder instances.
Totals are **2,583,444 pointer/range checks**, **161,368 SBR copies**,
**929 allocations / 929 frees**, and **4,845 scoped low-QMF matrices**.
The existing 27 deliberately invalid pointer/free cases are rejected per run.
The two allocation-failure controls reject AAC-core fallback as expected.

A separately rebuilt profile with the new flag disabled also keeps the prior
owner size and identical control PCM. The first run's log parser rejected the
new size because its allowed-layout list had not been extended; the raw QEMU
checks had passed. That tooling failure is retained under `rejected-parser`.
It is not presented as a decoder failure or silently removed.

These checks cover the named active pointer groups and copies at function
boundaries. They do not instrument every native load/store, cover every
malformed bitstream, prove physical CPU timing or eliminate the existing
unchanged-header implicit SBR/PS restart limitation. The previous physical
image still has the [recorded public-stream failures](ESP32C3_AAC_LOW_QMF_PRODUCTION_20261003.md).
This result does not convert those failures into passes.

## Reproduce and retained evidence

Add `sdkconfig.qemu-aac-asymmetric-owner.defaults` to the preceding low-QMF
QEMU configuration. Keep the normal 16 KiB decoder test stack. Run
`tools/codec_benchmark/run_aac_asymmetric_owner.py` with the same QEMU/build
arguments as the low-QMF runner, a matching `--baseline` from
`tests/results/esp32c3-aac-low-production-20261003/qemu/<input>/result.json`,
and the previous control WAV as `--previous-wav`. Add `--input` for captures.

[Retained evidence](../tests/results/esp32c3-aac-asymmetric-owner-20261003/)
contains six raw logs/results, the disabled control, compressed control PCM,
compiler layout, original/patched objects, linked-symbol verification and
exact source snapshots. Run:

```text
python tests/test-aac-asymmetric-owner.py --compiler <riscv32-esp-elf-gcc>
```

This recomputes PCM equality, validates evidence hashes and pointer results,
checks every patched function body, rejects bad reports, and compiles a
deliberately wrong prefix to verify the layout assertions. The optional
compiler argument is needed for that last check.

The physical follow-up verifies the unpoisoned storage path, then records
CPU/heap, public HTTP/HTTPS, local all-codec and OTA tests. Keep production
defaults disabled until all acceptance gates pass.
