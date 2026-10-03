# Scoped low-QMF storage and exact pointer qualification

## Result

The QEMU adapter now retains only eight low-QMF history rows per channel and
uses one complete matrix on the decoder task's stack during each `sbr_dec` call.
The actual SBR owner allocation is smaller by **10,240 bytes**. All six retained
runs pass **2,583,444 address/range checks**, **161,368 checked SBR copies**,
and **929 allocations / 929 frees**. They exercise **4,845 scoped matrices**.

The 657,540 control PCM samples are **bit-identical** to the preceding audited
adapter. All five full station captures retain their output hash, format,
frame count and total **12,505,088 channel samples**. This adds no observed
quantization error. The previous control comparison against the original
decoder remains at most 1 signed-16 LSB; capture hashes are comparisons with
the previous adapter, not new per-sample measurements against the original.

This is a **QEMU-only experiment, off by default**. Production integration,
decode speed and physical HTTP/HTTPS, all-codec and OTA acceptance remain to be
done. It does not yet resolve the documented public HE-AAC allocation failures.

Evidence: [summary](../tests/results/esp32c3-aac-low-workspace-20261003/summary.json),
[binary patch audit](../tests/results/esp32c3-aac-low-workspace-20261003/audit.json),
[source and artifact hashes](../tests/results/esp32c3-aac-low-workspace-20261003/implementation.json).

## Memory accounting

| Quantity | Previous four-row smoothing adapter | Scoped low-QMF adapter |
| --- | ---: | ---: |
| Requested SBR owner | 45,932 B | 35,900 B |
| Allocator block, including light-poison overhead | 47,104 B | 36,864 B |
| Allocator-reported usable block | 47,092 B | 36,852 B |
| Persistent low-QMF rows per channel and plane | 40 | 8 |
| Persistent low-QMF sample payload, both channels | 20,480 B | 4,096 B |
| Additional call-local complex matrix | 0 | 10,240 B |
| Concurrent test task stack, each of two tasks | 8,192 B | 16,384 B |
| Minimum free stack in that concurrency test | 4,908 B | 2,844 B |

The requested saving is 10,032 B; allocation rounding makes the block saving
10,240 B. The right-channel PS workspace, separate PS synthesis history and
pointer tables remain present, so removing 16,384 B of low-array payload does
not save that whole amount in the owner.

The temporary matrix uses stack capacity. The QEMU concurrent test explicitly
increases its stack by 8 KiB per decoder, so the block saving must not be
presented as an equal reduction in that test's total reserved RAM. Production
already reserves a shared 16 KiB decoder stack for other codecs, especially
Opus. Its size is unchanged here; the complete physical call path must still
be measured before this allocation saving can be qualified for production.

The compiler's `compact_owner=39432` descriptor describes the intermediate
owner with an embedded PS tail. The existing owner adapter removes that tail;
the live, audited allocation is 35,900 B. These are different objects.

## Lifetime and address map

This follows the prior [low-QMF lifetime experiment](ESP32C3_AAC_LOW_QMF_LIFETIME_20261003.md)
and [full pointer map](ESP32C3_AAC_POINTER_AUDIT_20261003.md).

| Data / pointer | Set or used by | Required location and lifetime |
| --- | --- | --- |
| Eight persistent real/imaginary rows | Open/reopen, repaired reset, wrapper copy-in/copy-out | Named history fields of that channel; real-only decoding preserves imaginary history |
| Full 40-by-32 real and imaginary matrices | Analysis, SBR generation, PS and native history copies in `sbr_dec` | One current call-local matrix, 10,240 B, inside the current task's stack |
| Two relative low-QMF bindings | Wrapper before native decode; 14 native base setups | Exact real/imaginary array starts in that local object; cleared before returning |
| Channel frame prefix and header | `sbr_open`, `sbr_read_data`, `sbr_applied`, `PVMP4AudioDecodeFrame` | Compiler-derived fields after the enlarged prefix, never the old byte offsets |
| PS workspace and pointer tables | `ps_allocate_decoder`, hybrid filters, decorrelator, reset | Existing right-channel overlay; inactive right SBR data is not treated as an independent live object |
| PS right synthesis history | `sbr_applied`, native PS synthesis and repaired reset | Separate named array after the PS overlay |
| Four smoothing pointer tables | `init_sbr_dec`, envelope wrapper | After the channel union, so initialization cannot overwrite live PS storage |
| Native frame-loop terminator | `sbr_read_data` and owner adapter | Inactive PS word, aligned with the compiler-derived two-channel frame cursor |

The low bindings are unsigned RV32 **frame-relative offsets**, not absolute
heap addresses. Native code loads the offset and adds its frame base, retaining
the original arithmetic modulo 2^32. Their slots come from a target-compiled
`offsetof` descriptor. All 164 field-address immediates also come from target
layout descriptors; pinned instruction locations identify code, not fixed RAM.
Fourteen four-byte base instructions become four-byte loads. Native DSP
arithmetic and instruction positions are retained.

The audit registers the wrapper's actual local matrix independently of the
stored bindings. It checks exact equality, channel/context ownership, stack
bounds and cleanup. An arbitrary in-bounds address in the stack is rejected.
Canaries surround the matrix, and its transient part starts with a poison
pattern. This extends the existing audit of core, PS, smoothing, input/output,
Flash tables, copies, reset and free ownership.

## Negative tests and discovered error

Each run rejects the existing 21 invalid-pointer/free/boundary cases and six
new low-QMF cases: real/imaginary substitution, a one-element shift of both
planes, the persistent heap history substituted for stack workspace, a
misaligned imaginary address, the other channel's frame, and access after the
call scope ends. Addresses are restored before DSP executes.

The first low-workspace revision missed one direct header read in
`PVMP4AudioDecodeFrame`: `sample_rate_mode` remained at owner offset 212, while
the enlarged channel prefix moved it to 220. The first HE44 format assertion
failed. The missing instruction at pinned object offset `0x89c` now uses the
named `left_sample_mode` descriptor. The [rejected revision and log](../tests/results/esp32c3-aac-low-workspace-20261003/rejected-prefix/)
are retained, and a regression checks that this read is patched. This was a
bug in the new experimental layout, not evidence of the same defect in the
previous production layout.

The final tests cover synthetic AAC-LC, HE-AAC and HE-AACv2; five station
recordings; two concurrent decoder instances; forced allocation failures;
reset, restart and stream format changes. A separate rebuilt image with the
new flag disabled also reproduces the preceding control PCM exactly.
The retained Groove Salad 16 recording is mono SBR without active PS despite
its FFprobe label; ABBA and synthetic HEv2 exercise PS.

These are function-boundary, ownership and copy-span checks of the real RV32
decoder. They do not instrument every native load/store or establish safety
for every malformed AAC stream or all firmware pointers. The existing
unchanged-header implicit SBR/PS restart limitation also remains.

## Reproduce

Build a separate emulator image with these defaults, in order:

```text
sdkconfig.defaults
sdkconfig.qemu.defaults
sdkconfig.qemu-aac-compact-adapter.defaults
sdkconfig.aac-smoothing-history.defaults
sdkconfig.qemu-aac-low-workspace.defaults
```

Use `tools/codec_benchmark/run_aac_low_workspace.py` with `--build`,
`--dependency-root`, `--output`, `--qemu`, `--bios`, and `--wsl` where needed.
Supply the matching result from
`tests/results/esp32c3-aac-pointer-boundaries-20261003/<input>/result.json`
as `--baseline`, and the previous synthetic control WAV as `--previous-wav`.
Add `--input recording.aac --ffprobe <path>` for each station capture. Exact
QEMU commands and fixture/configuration/ELF hashes are retained in each result.
Compressed synthetic WAVs are retained; station audio is not added to Git.

Run `python tests/test-aac-low-workspace.py`. It recomputes PCM equality,
validates all six logs, allocation/stack totals and exact source hashes,
reconstructs all original field-address immediates, checks the 14 load
replacements, and rejects missing, contradictory or failed reports.

Next steps are to measure copy/binding overhead without audit poisoning,
integrate a separately gated production variant, and repeat physical stream,
memory/stack and OTA tests before considering any default change.
