# Exact Vorbis packet front end: host and source-profile qualification

2026-10-26. Parent: `d9d99a594b37a9caf6b5ed0a2463a067042249f9`.
**Host exact integration PASS. SDK/QEMU, synthesis, PCM and radio integration
remain unqualified.** See the [design](../../../docs/CYD_VORBIS_PACKET_FRAME_DESIGN.md).

## What runs

The new allocation-free coordinator calls the existing public setup prefix,
floor0/1 packet, exact residue and inverse-coupling APIs. The test constructs
setup through the previously qualified owner. It retains original floor flags
and compact affine/raw-Y pools; no float table, gain, transform, window,
overlap or PCM conversion is used. Neither production application selects it.
No existing deferred fixture/controller is modified or executed.

Measurement returns a conservative all-present reservation. Actual decode
remeasures residue after reading original floor flags. Normal unused floors,
whole-frame floor EOP and an implicit zero numeric residue grid are distinct;
the last still consumes mandatory entropy and retains present floors.
Residue EOP preserves all earlier complete VQ contributions. Whole-frame floor
EOP initializes/clears every record and skips residue/coupling, as required by
[Vorbis I 4.3.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html).

## Actual exact results

GCC13.3.0 / x86_64-linux-gnu, C11/O1, assertions and `-Wall -Wextra -Werror`,
ASan/UBSan, `-fno-sanitize-recover=all`, `-fno-fast-math`, `-ffp-contract=off`.
All thirteen final owned commands return0 with reaped process groups.
Execution stderr is empty.

| Measurement | Result |
| --- | ---: |
| Cases | 1311 |
| Original unmodified packets | 434 of434 |
| Floor-EOP whole-frame zero results | 384 |
| Residue-EOP partial results | 420 |
| Exact residue words after inverse coupling | 411520 |
| Exact affine coefficient values | 2769 |
| Raw floor1 Y values | 2224 |
| Actual workspace-pool refusals | 3332 |
| Final runtime assertions | 1631165 |

The corpus includes all original31 streams'14 packets,56 synthetic base rows
and821 bit-cut rows from13 selected integration packets. It covers mixed
floor/residue types, channel order across submaps, coupling chains, absent
floors that still need residue, actual versus conservative classification
capacity, zero numeric grids with mandatory reads, order0, empty active books,
invalid selectors/modes and prefix/floor/residue boundaries. Floor0 uses the
ordinary fixture width8; this is not a new Xiph amplitude-width campaign.

Independent Python bit/context parsers, lexical entropy lookup, exact affine
terms and rational residue reconstruction compare every captured field and
limb. No tolerance, fit, trim or alignment adjustment is applied. This is a
front-end exact comparison, not a new result for the original S16 PCM bound2
and14 relations, which remain separate.

The C driver guards all input/workspace/owner/snapshot allocations and verifies
immutable source bytes. One-short capacities use actual published needs, not
the larger conservative reservation. Failure preserves result/cursor except
sticky prefix EOP. Restored buffers produce canonical-hash-identical retries;
no old borrow is used after attempted scratch reuse. NULL controls and four
object-byte capacity RANGE guards also execute. All buffers/owners return to
zero live allocations/bytes, backed by ledger assertions.

## Both captures and lint diagnostics are retained

`host01/` and `host02/` both pass all1311 cases with identical models, expected
data and functional results. The only executable change between them is the
test allocator cleanup. Initial Clang reported a null/UAF path through recursive
snapshot release. Cleanup is now nonrecursive and checks distinct snapshot
identity, tag, leaf status, byte extent, canaries and byte equality. Existing
checks remain; assertions rise from1210741 to1631165.

Both nine-unit Xtensa Clang runs are preserved. The new coordinator and the
other newly used parser/owner interfaces have zero warnings. Initial totals
are8 warnings/0 errors; final totals are7/0:

- One unchanged floor0 multiplication warning. Its `high` is0..72, so the
  int expression`(high+1-72)*32` is in[-2272,32], safely representable before
  widening. Gain arithmetic is not executed by this front end.
- Five fixture warnings compare a structure with its own pre-call byte snapshot
  to enforce failure preservation, including padding; they are not equality of
  separately initialized structures.
- One remaining fixture UAF trace assumes inconsistent reciprocal list links.
  If snapshot S.next points to tail A, A.previous is S; unlinking A necessarily
  changes S.next before freeing A. If live nodes intervene, S.next names one
  of them. Prepend/removal establish both directions, and no other fixture
  operation mutates links. Snapshot identity/tag/leaf checks also prevent aliasing
  S with A. The trace's conflicting graph is not reachable under those invariants.

No diagnostic suppression or numerical relaxation was introduced. The raw
initial and final traces remain available for review.

## ESP32 and C3 source compatibility

`profiles/` retains ten actual GCC commands and four relocatable ELF32 objects:
C coordinator and C++17 public-header probe for ESP32/LX6 and ESP32-C3/RV32IMC.
Both compilers report32-bit pointer/long; C3 explicitly uses`-march=rv32imc
-mabi=ilp32`. Public signatures and affine layout compile in C++ as well.
Both `-O2 -fno-inline -fstack-usage` profiles report static own-function frames
of464 B for measure and544 B for decode.

These are source-only compiler records, not SDK links, firmware images, target
execution, whole-call-chain stack bounds or physical high-water measurements.
No production firmware handoff was built. Existing task/core/stack/priority
and display/audio configuration choices are unchanged.

## Evidence

- Final runner:
  `7c449b4b190500b0ab5931205f06e51e9f691112ebea80ac1affb7b200cb22d0`.
- Independent composition model:
  `5ed0ad7b589fc16de2d99f5aca77e179808aa0553fd22d9907b59369abcd77a9`.
- Final C fixture:
  `4152ff07aec8ad75563200b19e1baf80eb8b9164cbc4120c48a7e9eabface880`.
- Coordinator source:
  `6347050b077d7bbbb70182d32e81217ff36e37ad18ca10b084c6ac7bb242d2ea`.
- Offline verifier:
  `332b53b6766d35df612ce9ab5be7b962b5ae56807d7f3c16e808572404e513f6`.
- [captures.zip](captures.zip):1846601 bytes /314 members, SHA256
  `e23c996d8fdd4b37e34090875d5430ced460247507ff393edd725a253ae159b9`.
- [manifest.json](manifest.json): exact member extents/hashes, SHA256
  `c03368aa8787a806ea1bdb66e5ae04d715823fe3c008e54cce490d065a8a66d0`.

The archive includes both complete source/input/reference/capture sets, actual
objects/binaries, raw diagnostics, requests/receipts, command records, both lint
runs and both source profiles. Test inputs/captures named`.bin` are packet data,
not ESP firmware. Publication verification rederives the independent model,
checks all exact results, retains the earlier capture, validates source-profile
objects/stack records and rejects five corrupted/partial/semantic captures.
It imports only pinned repository readers; no archived code/process executes.

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 tests/verify-vorbis-packet-frame-checkpoint.py
```

Fresh host run:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 tests/test-vorbis-packet-frame.py --output .build/vorbis-packet-frame-host-fresh
```

Before publication, inspect the staged/outgoing source and complete archive
locally, including all new Git history/refs. Use nonpersonal commit metadata.
Any actual sensitive material must be excluded/redacted or follow the user's
two-confirmation procedure; a general push instruction is not consent.

Full native qualification, gain/range/pole handling, floor multiplication,
inverse transform/window/overlap, PCM and audio-task wiring remain open.
