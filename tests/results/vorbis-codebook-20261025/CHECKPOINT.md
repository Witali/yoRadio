# Complete owned codebooks and exact audio-word handoff

The [owned component](../../../idf/components/native_vorbis_numeric/README.md)
now parses complete public codebook descriptors and decodes their audio words
into original entry indexes and exact VQ/floor0 LSP values. It remains outside
both production application component lists and decoder registration.

The [design](../../../docs/VORBIS_CODEBOOK_DESIGN.md) follows Vorbis I sections 2/3
and the 2015 singleton erratum. The frontier assignment is independently proved
to choose the lowest unused lexical code in original entry order, including
unsorted lengths. A singleton has encoded length 1, consumes one bit and accepts
either bit value. Empty descriptors retain the public Xiph compatibility
behavior but cannot return a symbol. Lookup1/dimension0 remains explicitly
invalid because its specified greatest-root definition has no finite result.

All storage remains caller-owned. Complete validation and representation/capacity
checks precede writes. A sticky-EOP cursor preserves its position and output on
truncation. Vector/floor0 operations preflight capacity, retain cross-vector carry
and partial final vectors, and preserve the original position and all output
on aggregate failure. Transported packets include every final octet and padding;
explicit shorter test extents exercise controlled boundaries.

## Actual host and native evidence

The host campaign completes 382 generated cases and 719 fixed API controls under
strict GCC/ASan/UBSan, with all four nonce-owned commands terminal 0 and their
process groups reaped. An independent Python greedy-interval allocator and
bit-by-bit tree traversal compare every retained result exactly:

- 11653 assigned words with original entry/length/code fields;
- 5963 decoded entries and resulting bit positions;
- 24603 exact affine VQ/LSP values and every original multiplicand/layout field;
- 318030 setup truncation points and 31580 consumed-payload truncation points.

The complete successful host corpus includes unordered backfill `[2,1,2]`,
ordered zero runs, sparse mapping, depth 32 words, singleton bits 0/1, empty books,
dimension 0 scalar use, dimension 65535 VQ prefixes, partial final vectors and
three consecutive deliberately unaligned setup descriptors. The finite corpus
and controls are not an exhaustive Vorbis conformance proof.

A separate host supplement preserves that frozen corpus and adds 140 malformed
fixtures/290 guarded status assertions under ASan/UBSan: ordered overrun,
zero runs reaching length 33, all 13 reserved lookup types, 62 invalid dense/
sparse singleton lengths, 24 corrupted sync bits, seven unordered flag/length
truncations and lookup1/dimension0. Positive metadata boundaries measure a
complete 32768-entry, dimension 65535 tree before a capacity refusal, then parse
and materialize the maximum 24-bit sparse descriptor (16777215 declared entries,
dimension 65535). Its 2097162-byte packet needs only one 12-byte active word;
both singleton bit values return the original last index 16777214. No declared-
entry-sized array is allocated by the component. All four supplemental owned
commands are terminal 0 with clean sanitizer/strict compiler logs. These are
finite host assertions, separately scoped from the independent 382-case oracle
and native captures.

Each separate pinned SDK/QEMU campaign finishes 200 cases and 719 controls,
1405 ordered events and nine owned commands with exit 0 and zero build warnings.
Actual ELF machine values are 94 (Xtensa) and 243 (RV32). The coordinator uses
core0; the worker uses core1 on ESP32 and core0 on C3, priority 3/stack 16384.
These are isolated test settings; production task affinities/priorities/stacks
are unchanged.

Native capture reports deliberately remain `CHECKED_CODEBOOK_CAPTURED` with
`passed=false` and numerical qualification false. A separate checker replays
all 382 original host cases and compares every one of the 400 native cases:
10930 assigned words, 6378 decoded entries/positions and 26990 exact affine
values, plus all layouts and multiplicands. Its result is
`FINITE_CODEBOOK_QUALIFIED`. Native per-row setup/payload truncation counters
remain 0; the exhaustive-per-input cut campaign is host-only.

All three component C units and their headers are compiled for each target.
The largest own codebook compiler frame is the bounded 255-entry floor0 wrapper:
1120 bytes on ESP32 and 1104 on C3. These are compiler per-function frames,
excluding callees, libm and complete task high-water usage.

## Static analysis and tooling

Both actual cross-target Clang-Tidy module analyses are retained. The initial
run identifies seven assignment-in-if warnings in the new parser per target;
the final source moves those assignments outside conditions. The final parser
and quantization have zero warnings on both architectures. Each target retains
one pre-existing floor0 implicit-widening warning: `high` is bounded 0..72, so
`(high+1-72)*32` is within signed32 range before widening. The floor0 source and
numerical behavior are unchanged. No new full-application lint is claimed.

The new pure capture-reader suite passes 12 methods. Earlier quantization,
angle and coefficient reader suites pass 12/12/13. Their reusable launchers now
freeze the added codebook dependency closure; no historical capture is
relabelled as having executed these amended launchers. Earlier pinned archives
and historical checker identities are unchanged.

## Remaining work

This qualifies the finite standalone codebook/data-preservation layer. Remaining
setup structures (floors, residues, mappings and modes), complete audio packet
handling, wide residue/inverse coupling, floor multiplication, IMDCT/overlap,
final PCM conversion and public raw lifecycle/retry/EOF/ownership integration
remain required. The historical full31 reference PCM NONPASS is still open;
this checkpoint does not close G6/G8 or qualify physical/radio real-time behavior.
The other explicitly deferred items remain deferred. These isolated emulator
images are test fixtures, not production firmware handoffs.
