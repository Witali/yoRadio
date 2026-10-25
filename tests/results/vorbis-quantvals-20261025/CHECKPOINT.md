# Exact Vorbis lookup1 value counts, 2026-10-25

Both canonical setup implementations now compute the integer root required by
[Vorbis I 9.2.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html). The old public
Tremor-derived helper multiplied two unchecked powers. Positive fields such as
entries2/dimension32 can overflow ILP32 even though the required root is only1.
Xiph's [sharedbook.c v1.3.7](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/sharedbook.c)
also bounds its power products; a field-size rejection is not the mathematical
solution.

The replacement uses an exact integer search and checks `entries/candidate`
before multiplying. Its midpoint fits the positive24-bit entry domain; every
entered search iteration has candidate at least2. A power therefore terminates
or exceeds the bound within24 multiplication steps, independent of dimensions
through65535. Dimension1 returns entries directly. No dimension clipping,
floating approximation, allocations, ABI fields or production task bindings
are introduced.

## Actual host and target checks

The final host run checks35975 complete roots per variant under ASan/UBSan:
native64-bit `long` and an explicitly labelled int32 arithmetic model. The
oracle uses Python arbitrary-precision powers with descending-bit construction,
not the production bounded-multiply search. Coverage includes exhaustive small
fields, deterministic random fields, perfect powers and adjacent integers,
dimensions1/31/32/33/63/64/65/65535 and squares4094²/4095² near the24-bit limit.
Input fields remain unchanged. The immutable old source from commit
`6b16e7f0ac5e01c58ae32aea3f9409c9ddf67e21` separately reproduces a named
signed-power-overflow diagnostic at entries2/dimension64 under native-long
UBSan. This is a host arithmetic witness, not target decoder execution.

Both separate SDK/QEMU campaigns pass all2179 selected boundary cases. They
compile the entire frozen canonical setup source, including native ABI
assertions, and call its actual static helper through a volatile function
pointer. Actual compile rows, Ninja dependencies, symbols, map and ELF machine
are checked. Only public codec headers are supplied; no codec archive or raw
stream decoder is linked. Each campaign completes all9 owned commands and its
actual SDK child normally, with0 compiler warnings:

| Target | SDK | ELF machine | Worker | Result |
| --- | --- | ---: | --- | --- |
| CYD / ESP32 | 6.0.2 | 94 | core1, priority3, stack16384 | 2179 exact roots |
| ESP32-C3 | pinned6.1 | 243 | core0, priority3, stack16384 | 2179 exact roots |

The coordinator stays on core0 in both isolated fixtures. The original
production stream/decode/output tasks, priorities and stacks are unchanged.
Target report SHA256 values are
`e8503ba056f6985a9f32eb201ce700be3e0b79a3f657ef7e608073f1116788a2`
and `7457c2d8c9ed5a516d1b9e4ef592d1a9bb34d1db4f0d1d45d547e192252dd91f`.
Actual direct terminal chunks are `a4accc` and `6c0101`, both exit0.

## History and limits

All earlier host attempts are retained: the first stopped before child execution
because of an overly strict LF/CRLF source comparison; the second reached only
a denied WSL launch; the third passed35969 roots per variant. The final host
adds the six largest-square boundary cases and passes35975. The denied WSL run
is not a numerical failure or PASS; the same test source then ran using normal
approved WSL execution. Original source snapshots and actual receipts preserve
each distinction.

Twelve pure reader/protocol methods also cover changed roots/rows/counts,
missing/duplicate/reordered events, wrong cores/data and failed terminal
markers. Their first run exposes one missing-comma input-reader weakness;
the actual C compiler would reject that header before any native PASS. A
reader-only correction then makes all12 methods pass. The already executed
SDK controller remains frozen as SHA256
`53b1d4ea705378ec3ad2d82b5ca5b371a6b0452beac0b087fb8a5455aa720849`.
The final controller differs only inside `validate_cases`, checked by AST.
A separate completed pure replay validates the final reader against both real
2179-row headers/JSON and saved QEMU logs, without a new SDK/QEMU execution.
The final reader is not misrepresented as the controller used for those builds.

The first archive collection stopped before publishing a manifest: Windows
Path ordering and normalized relative-string ordering differed in its unchanged
inventory check. A one-line correction sorts the same relative names at both
ends. The failed collector/receipt/logs are preserved in the separate
[publication history](../vorbis-quantvals-verification-20261025/README.md);
its partial archive remains local and is not an accepted archive. Runtime data
and all arithmetic measurements are unchanged by this packaging correction.

This corrects the shared lookup1 arithmetic. Finite helper checks and compiling
native ABI assertions do not establish complete setup acceptance, public raw
decoding, PCM equality or full G6. Inherited parser limits are not removed by
this change. The earlier full31 wide/floor0 NONPASS is retained as historical
evidence and is not requalified by arithmetic-only runs. Full format support,
deferred work, final Clang/exports, radio/resources and physical acceptance
remain open. Test images are isolated emulator fixtures, not production
firmware hand-offs. Omitted executable/build bytes have identity-only records;
this is not full SDK dependency closure.
