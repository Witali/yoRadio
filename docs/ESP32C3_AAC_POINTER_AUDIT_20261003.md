# AAC pointer ownership and address audit

## Result and scope

The current **PC18 high-history + four-row smoothing** adapter passed six QEMU
runs: six synthetic AAC files exercised through ten streaming/restart cases,
plus five retained station captures. There were **2,245,980 address/range
checks**, **161,368 checked SBR copies**, and **923 tracked allocations, all
freed**. Totals include the synthetic control sequence repeated in every run.
No invalid address was found by these checks in the final runs.

The audit covers the named, live pointer groups used by the modified AAC
core/SBR/PS path. It is a checkpoint and copy-range audit of the real RV32
library, not instrumentation of every machine instruction or a proof for every
possible bitstream. Untouched internal function-local pointers and inactive
views of reused storage are not treated as independent live objects. Older
experimental PC16 layouts and the physical radio were not exercised here.

Code: [`aac_pointer_audit.c`](../idf/esp32c3-oled-native/main/aac_pointer_audit.c).
Evidence: [summary](../tests/results/esp32c3-aac-pointer-audit-20261003/summary.json),
[exact source snapshots](../tests/results/esp32c3-aac-pointer-audit-20261003/implementation.json),
[compiler-derived binary patch audit](../tests/results/esp32c3-aac-pointer-audit-20261003/binary-patch-audit.json).

## Pointer-to-region map

Addresses are derived from the owning allocation and named fields. Heap
addresses change across streams and tasks; a fixed absolute address is not the
invariant. Pointer tables must contain the exact expected row starts.

| Pointer group | Required target / lifetime | Native setters or consumers |
| --- | --- | --- |
| SDK core, program, long/short windows, SBR stream, SBR control, shared workspace | Exact live allocation, exact requested size, same decoder context | `esp_aac_dec_open`, `PVMP4AudioDecoderInitLibrary`, frame/reset/free paths |
| SDK wrapper containing `external` | Exact live wrapper allocation; `wrapper->core` matches; no extra-output allocation with this adapter's 8 KiB output buffer | `esp_aac_dec_decode` |
| External input, output, output-plus | Actual buffers supplied for the current adapter call; output-plus is the second 4 KiB half | `native_aac_decoder_process`, `esp_aac_dec_decode` |
| Core bit-reader buffer | Current external input; length within current input capacity | `PVMP4AudioDecodeFrame` |
| Core scratch/shared | Exact fields inside its 12 KiB workspace | Initializer, transforms, SBR |
| Core mask, channel coefficient/shared pointers | Exact fields in the core spectral blocks, while that channel view is live | Initializer, Huffman decode, transforms |
| Window map and short-band widths | Correct long/short window objects and core width array | `infoinit`, `getics` |
| Window band-top pointers | Exact named `sfb_*` Flash table for the current sample-rate index | `infoinit`, spectral-band readers |
| Core SBR owner | Same compact owner tracked by the current decoder's TLS context | Patched frame decode and adapter wrappers |
| Owner PS pointer | Relocated PS object, or only the inactive detection word before PS initialization | `ps_pointer`, `ps_read_data`, `sbr_applied` |
| SBR frame and control arguments | Exact channel frame and live control of that core | `sbr_applied`, `sbr_dec` |
| High-QMF real/imaginary work pointers | Native spectral/shared workspace bindings, with complete 38-by-48 spans in bounds | `sbr_applied`, `sbr_dec` |
| Packed high-history identity tokens | Exact mantissa-field tokens and expected native copy lengths; never dereferenced as native arrays | `aac_high_history_memmove` |
| Four smoothing table bases | Exact gain/gain-exponent/noise/noise-exponent tables of that channel | `init_sbr_dec`, envelope wrapper |
| Smoothing row pointers | Permutation of four distinct row starts; fifth slot NULL outside the call | Envelope/FIR rotation |
| Temporary fifth smoothing row | That table's current stack row during this call; inside the current task's stack allocation | Scoped envelope wrapper |
| All 23 envelope arguments | Named frame/control fields, correct real-only NULL arguments, native scratch; patch descriptor inside current stack allocation | Both patched `calc_sbr_envelope` call sites |
| PS energy vectors and synthesis state | Exact right-channel overlay vectors and preserved right synthesis buffer | `ps_allocate_decoder`, `ps_decorrelate`, synthesis |
| Hybrid object, resolutions, history tables, six history rows, two scratch arrays | Exact fields of independently reconstructed hybrid allocation layout | `ps_hybrid_filter_bank_allocation`, hybrid filtering, reset |
| Four hybrid output vectors and two sub-delay tables | Exact arrays after the hybrid cursor | PS allocator and filters |
| Main PS delay tables and all 122 row pointers | Exact 2-, 14-, or 1-element real/imaginary delays; ring indices within lengths | PS allocator and decorrelator |
| Sub-delay row pointers | Exact ten pairs of two-element delay vectors | PS allocator and decorrelator |
| Serial/sub-serial table bases and row pointers | Exact three links with 3/4/5 rows; cursors finish at each workspace boundary | PS allocator and decorrelator |
| PS QMF work pointers | Exact native core overlay addresses after `sbr_dec` binds them | `sbr_dec`, `ps_applied`, synthesis |
| Non-history `sbr_dec` memmove arguments | Complete source/destination spans inside named live QMF, synthesis, hybrid-history or shared-workspace regions; element alignment checked | All 21 retained non-history memmove call sites |
| Reset and free | Core allocations remain valid at reset; PS/hybrid targets checked before PS reset clears; frees belong to the decoder that allocated them | Repaired reset and allocator wrappers |

Inactive views matter: PS deliberately reuses the inactive right core channel
as QMF workspace. Its former channel-tail pointers are then sample data, not
live pointers. Similarly, unused long-window pointer slots and the unused
analysis-only embedded window view are not dereferenced by this path. The
analysis header's MC `extension` fields have no consumers in the retained
pseudocode. These are not counted as validated active pointers.

The native initializer briefly computes a fifth smoothing-row address. The
wrapper clears it before any reader can use it. During complex envelope
processing the fifth slot refers to stack scratch; after rotation the retained
row is copied back into its owning matrix and no stack pointer escapes.

## Run results

| Input added to control sequence | Source profile | Checks, including controls | SBR copies, including controls | Allocation/free count |
| --- | --- | ---: | ---: | ---: |
| Synthetic controls only | LC / HE / HEv2 | 141,788 | 10,988 | 145 / 145 |
| ABBA 64 | HE-AACv2 | 857,133 | 72,146 | 156 / 156 |
| Groove Salad 16 | HE-AACv2 | 295,583 | 19,430 | 156 / 156 |
| Groove Salad 32 | HE-AAC | 342,938 | 23,908 | 156 / 156 |
| Groove Salad 64 | HE-AAC | 342,718 | 23,908 | 156 / 156 |
| Groove Salad 128 | LC | 265,820 | 10,988 | 154 / 154 |

Each run also exercises two forced allocation failures, two resets and two
simultaneous decoders with separate live stack rows. The concurrent tasks keep
at least **4,956 bytes free out of 8,192**. Every control run produces the same
657,540 PCM samples as the adapter without auditing, bit for bit. Against the
original decoder, those control samples differ by at most 1 LSB. Capture PCM
hashes are retained for reproducibility; this is not a new error comparison of
the captures against an original decoder.

The [reference-decoder follow-up](ESP32C3_AAC_PS_COVERAGE_20261003.md) resolves
the Groove Salad 16 coverage question: this retained recording contains mono
HE-AAC without active PS. Both FAAD modes decode 32 kHz mono; FFmpeg labels it
HE-AACv2 but produces identical left/right channels. The native PS pointer checks
are exercised by ABBA and the synthetic HEv2 file. Do not use this Groove Salad
capture as evidence of PS coverage or apply its conclusion to future live audio.

Ten negative tests reject a wrong real/imaginary delay, wrong smoothing matrix,
interior row address, duplicated row, NULL live row, wrong decoder context,
wrong allocation size, one-past-end span, misaligned span and wrong Flash table.
Pointer mutations are restored before DSP runs.

## Findings while constructing the audit

The earlier OLED failure was an undersized QEMU task stack, already
[diagnosed and fixed](../tests/results/esp32c3-aac-smoothing-adapter-20261003/rejected-stack4096/README.md).

The first memmove-range rule omitted six legitimate hybrid-history vectors.
The retained [GDB trace](../tests/results/esp32c3-aac-pointer-audit-20261003/hybrid-copy-diagnostic/gdb.log)
shows a 48-byte copy from `0x3fcad6e8` to `0x3fca3acc` for that ELF. Relative to
owner `0x3fca6a50`, the source is the right overlay's first real hybrid row.
The pinned `sbr_dec` pseudocode explicitly loads and later saves these six
12-word histories. The final rule admits each complete vector separately;
it does not admit the entire owner allocation. This was a missing audit region,
not a firmware pointer correction.

## Reproduce

Build a separate emulator image using `build.ps1` and these defaults:

```text
sdkconfig.defaults
sdkconfig.qemu.defaults
sdkconfig.qemu-aac-compact-adapter.defaults
sdkconfig.aac-smoothing-history.defaults
sdkconfig.qemu-aac-pointer-audit.defaults
```

Run `tools/codec_benchmark/run_aac_pointer_audit.py` with the build/dependency
paths, `--qemu`, `--bios`, `--wsl` where needed, `--reference-wav` for the
original control sequence and `--previous-wav` for the unaudited adapter.
Use `--input recording.aac` for a capture. Each result JSON retains exact
commands, fixture/config/ELF hashes and FFprobe metadata.

Run `python tests/test-aac-pointer-audit.py` to validate retained evidence and
failure-rejection logic. The audit flag requires the QEMU compact-adapter test
configuration. Its registries and expensive checks are absent from production;
no board firmware or production default was changed by this audit.
