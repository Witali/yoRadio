# Xiph packet allocation host checkpoint

Source change: `b790ca744` (`fix: report packet allocation failures in Xiph decoder`).
The candidate remains separate from the production CYD/C3 radio. There is no
new production firmware image or physical-device result in this checkpoint.

## Result and scope

The final host run passes **41,086 scenarios** under ASan/UBSan with assertions
enabled, leak checking and unchanged floating-point options:

| Layer | Scenarios | Required refusals | Optional refusals |
| --- | ---: | ---: | ---: |
| Transactional arena | 23 | Checked individually | Separate prior arena suite |
| Original31 packet sweeps | 27,875 | 12,930 | 124 |
| Synthetic and direct no-work controls | 13,188 | 6,192 | 72 |

All original **31 streams / 434 packets / 738,560 S16LE PCM bytes** match the
previous independent reference exactly: maximum error **0**, unchanged allowed
bound **2**, all **14** exact relations pass. No shift, gain fit, trimming,
resampling, normalization or reference replacement is applied.

This is a host packet-path qualification. ESP32 SDK/QEMU qualification is
**false**: the new target preparation was stopped before dispatch, with no reason
supplied. See the [separate deferral](../../../docs/CYD_XIPH_PACKET_TARGET_DEFERRED_20261026.md).
There is no new native project, controller, build, ELF or runtime capture here.
The older DSP fixture and its watchdog NONPASS are unchanged and unqualified.

## Change and API contract

Nine exact fragment pairs extend the separate resource port to **33 edits,
11 modified C units and four private headers**. The generated tree retains all
116 pinned baseline files and contains 132 files including `PORTING.json`.
The original Xiph source tree remains unchanged.

- Arena growth prepares a reap node and replacement buffer before publishing
  either owner or changing accounting. A refused node/buffer leaves the entire
  previous block state, chain, allocation ledger and borrowed bytes unchanged.
  Alignment/accounting overflow is rejected before allocation. Zero-byte calls
  avoid NULL pointer arithmetic and do not advance the arena.
- Required PCM, floor memo, floor0 lazy-map and residue allocations are checked.
  Checked private floor callbacks distinguish required OOM from ordinary NULL
  meaning unused floor or nominal EOP. Mapping propagates negative floor/residue
  statuses to the public synthesis caller before reporting success.
- No complete residue partition, zero stages and inactive residue2 channels
  remain successful no-work paths. Nominal truncated floor/residue packets keep
  upstream success/EOP semantics; successful decoding arithmetic is unchanged.

The port adds **`OV_EFAULT`** for required packet allocation failure. This is an
explicit resource-port extension: [Xiph's public synthesis documentation](https://xiph.org/vorbis/doc/libvorbis/vorbis_synthesis.html)
lists success, `OV_ENOTAUDIO` and `OV_EBADPACKET`. Public function signatures and
original registry callbacks are unchanged; there is no global/TLS error flag.
On any nonzero synthesis result, do not submit the partially filled block to
`vorbis_synthesis_blockin`. Recovery closes block/DSP/info/comment owners and
replays all three headers. Same-instance retry after fatal OOM is not claimed.
Nominal EOP and complete-partition behavior follow the
[Vorbis specification, sections 8.2 and 8.6.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html).

## Coverage and retained failures

The [packet fixture](../../native/vorbis_xiph_packets.c) exercises every observed
allocation ordinal in every original packet, with arena-cold and arena-warm
storage and both NULL/non-NULL zero-size allocator policies. Arena-cold clears
only block storage after the packet prefix; DSP floor caches from that prefix
remain. Original floor0 cases use both short/long modes, so both lazy maps are
targeted. Every injected required or optional refusal gets full owner cleanup,
fresh three-header replay and comparison of every output float with a successful
same-process capture. Inputs and packet descriptors have unchanged-byte checks.

The synthetic matrix comprises **36 four-channel streams**: both floors × all
three residues × active, all-unused, zero complete partitions, zero stages,
residue EOP and floor EOP. Another **48 direct registered residue controls**
assert zero allocation attempts and unchanged block/owners/guarded inputs in
no-work paths. A subsequent positive allocation must still trigger armed
refusal1, proving the callback neither consumes nor resets the allocation hook.
Synthetic and recovery float comparisons establish same-process identity;
the original31 raw S16 comparison is the separate independent numerical gate.

Three complete host histories are retained:

1. `host-first/`: runtime and original31 comparison completed, but the original
   source-identity gate rejected a concurrent fixture expansion. Its overall
   result remains NONPASS; no source or diagnostic check is removed.
2. `host-before-controls/`: the completed 36-stream version passed before the
   48 direct no-work controls were added.
3. `host/`: final fixture, including the 48 controls, passes all 62 owned
   commands. Each finite stream sweep has its own 60-second process budget.
   Nonce-bound supervisor receipts prove terminal/reaped process groups.

The `baseline/` witness reverses only `synthesis-pcm`, producing the exact
official synthesis.c, while retaining every other final host object and test.
The first required PCM allocation refusal reproduces UBSan:
`synthesis.c:82:15: runtime error: store to null pointer of type 'float *'`.
Its three commands compile/link successfully and execute with expected exit1.
The original failure and all sanitizer diagnostics are retained.

## Static analysis and limits

Clang-Tidy analyzes all **22 library + three fixture units** with explicit
Xtensa CPU flags and Picolibc/builtin headers: **308 warnings, zero errors**.
This is source analysis, not an ESP-IDF GCC build or target execution. All raw
diagnostics are retained, without suppression changes.

The 13 new fixture diagnostics concern valid C pointer conversions and deliberate
representation comparisons. Binary32 and block/PCM snapshots test exact
same-process bytes, including signed zero and guards, not portable serialization.
Struct-assignment padding could cause a spurious failure with another compiler;
the current host run passed. Serious inherited psychoacoustic/floor1-encode
findings belong to encoder paths, which this decoder work does not qualify.
The inherited floor1 decoder warning at generated line385 takes an impossible
equal-endpoint branch for valid unique/sorted X posts: `adx>0`, while equal Y
gives `err=0`. Its diagnostics remain visible. The allocator zero-byte warning
is intentional policy coverage; zero-size storage is never dereferenced.

General decoder OOM, encoder OOM, maximum channel-sized mapping/residue stack,
uint32 rate/floor0 amplitude/VQ ranges, all legal formats, native SMP/resources,
runtime integration and physical acceptance remain open. No previous vendor
NONPASS, DSP watchdog result or deferred scope is upgraded by this checkpoint.

## Evidence

- Base manifest: `897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14`.
- Final port manifest: `908348db2d68684ddb21211b7f255e54a6fa95302567aa27bbc160cca8072894`.
- Generator: `873472c0a30c955fa5d81528195ef71e4f476915b1ac8b64dd1d04dbae7f0251`.
- Final fixture: `1f0d8a34f1afac3d75ecf71f0e4d21fe5c018a1ec587d9da6a1b3eae6d1247fb`.
- Archive: [captures.zip](captures.zip), **13,795,751 bytes / 2,045 members**.
  SHA256: `f31167f2a52e8e8a8f01e20cbadb3597d1394931bd2dfd2ac67a0381e2d6985b`.
- Archive manifest: `4ffcc25005b7dd3d51f6fd16df8282de3316532211a3020f17dedaa295d43b6a`.

The [offline verifier](../../verify-vorbis-xiph-packets-checkpoint.py) checks
every member, complete source transforms, actual commands/receipts, all original
PCM samples/relations, the baseline failure, Clang streams and the explicitly
agent-reported target-preparation stop. It never extracts or executes archived
code. Verification returns host qualified true, native/DSP gate qualified false.

```text
python -B tests/verify-vorbis-xiph-packets-checkpoint.py tests/results/vorbis-xiph-packets-20261026/captures.zip
```

Actual collection and successful offline-verification receipts are retained in
[publication/](publication/), outside the archive to avoid a self-reference.
