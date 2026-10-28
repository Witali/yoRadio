# Selected basic arithmetic: host checkpoint

The [portable fixture](../../native/vorbis_bigfloat_host.c) and
[Fraction/isqrt reader](../../test-vorbis-bigfloat.py) qualify the selected
LibBF foundation's exact imports, directed add/subtract/multiply/divide/square
root, copy/round and arbitrary-integer floor export. This is an isolated basic
arithmetic checkpoint. It does not execute a Vorbis decoder or certify general
floor0 gain, transcendental operations, SDK/QEMU runtime or production resources.
The separate [source profiles](SOURCE_PROFILES.md) retain compiler-only evidence.

Final `host05` preserves all699 earlier rows in their original order and appends
two specific fractional-carry regressions: magnitude `(2^4096)-1`, exponent-2524,
with both signs. Their floors are `2^1572-1` and `-2^1572`. Earlier NTT result
exports already exercised wider integer floors; these additions target the
all-ones fractional carry, rather than claiming that wide export was absent.

| Final host model | Cases | Allocation refusals | Capacity refusals | Alias checks | Guard controls | Assertions | Peak supplied-allocator bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Normal64-bit limbs |701|463|1643|1253|18|5682096|57216|
| Forced32-bit limbs |701|825|1643|1253|18|12587858|48752|

Both binaries execute on the installed x86-64 WSL host. The second build selects
the creator's32-bit limb implementation with `-U__SIZEOF_INT128__`; the upstream
header is unchanged. These are two arithmetic models, not native MCU execution.
Dense8192-bit operands in rows681/684 initialize actual NTT state for both
directed products. Merely requesting high precision on a small operand does not
qualify NTT execution. Precision8193 and maximum1048576 are also accepted on
small operands; the suite does not allocate or sweep million-bit dense operands.

The oracle uses Python `Fraction`, integer quotient/remainder and integer
`isqrt`, independently of the production limb algorithms. Every successful
dyadic and integer floor is checked exactly. Negative fractional floors,
unsigned2^63/UINT64_MAX imports, signed cancellation, both destination aliases,
division by zero and negative square root remain explicit cases. Precision0/1
is INVALID; requests above the selected engine envelope are ENGINE_LIMIT,
separate from a malformed Vorbis format. The current engine resource bounds
remain explicit rather than becoming a codec format restriction.

For selected sweep rows, every observed baseline backend-allocation ordinal is
refused in a fresh context. The fixture compares the destination's actual fields
and storage, checks the sticky failure without a new backend callback, clears
the latch, and captures the complete recovered dyadic/floor result. Inputs,
independent contexts, export metadata, undersized buffers and unused tails are
guarded. All contexts release their allocations. Engine requests can exceed
backend callbacks after a latched failure; the fixture does not equate them.

All executed objects retain ASan/UBSan and immediate sanitizer failure.
Adapter/fixture compilation uses `-Wall -Wextra -Werror` with zero diagnostics.
Dependency compilation keeps `-Wall -Wextra`, preserving27 LibBF+2 cutils
warnings for64-bit limbs and25+2 for32-bit limbs. No warning suppression or
sanitizer weakening was used. The fixture exports
`native_vorbis_bigfloat_fixture_run(text,length)`; file I/O/main are host-only.
That portability does not itself qualify an SDK or emulator run.

All attempts are retained:

| Attempt | Observed result |
| --- | --- |
| host01 | Pre-child `Wsl/E_ACCESSDENIED`; Windows transport4294967295, outer controller exit1. No compiler child or supervisor receipt is invented. |
| host02 | Compile NONPASS because third-party warnings were initially made errors. No arithmetic runtime occurred. |
| host03 | Actual UBSan NONPASS in creator `bf_set`: zero-length `memcpy` received NULL. The complete diagnostic and terminal receipt remain. |
| host04 | PASS699 cases on both models after the narrowly recorded portability fixes. |
| host05 | PASS701 cases on both models, adding only the two fractional-carry rows. |

The original creator source remains byte-identical. The selected
`portable/libbf.c` differs by exactly two manifested edits: an SDK
`int*`/`int32_t` compatibility temporary, and a nonzero-length guard for the
observed zero-copy sanitizer failure. `context-stock-type` retains the separate
source-only LX6/RV32 compiler diagnostics that motivated the first edit. It is
explicitly not a host or target runtime result; full source-profile evidence is
packaged separately. No failed corpus cases were removed.

The host [captures.zip](captures.zip) is3904986 bytes with SHA256
`f15f8ccdac3fed71bb5a51b037698c8e2bf083e7adaf64a54c6c02cf849d8f90`.
Its [manifest](manifest.json) has SHA256
`f9c9969b58f54e6c617b092f2bedd52c78d34ee307eeac5e47560071ea0ed1a7`.
Content-addressed aliases retain274 logical files/30430683 bytes in147 physical
members/26992059 bytes. Five rebuildable host executables are omitted with exact
size/hash receipts; source snapshots, objects, commands, stdout/stderr, inputs
and owned terminal receipts remain. Native task settings and old deferred
controllers are untouched.

Run the [pure checkpoint reader](../../verify-vorbis-bigfloat-checkpoint.py)
with a fresh task-local report path. It hashes the archive/manifest and live
trusted readers/component first, then rechecks both successful campaigns,
the exact arithmetic/recovery values, real NTT evidence, ten corruption controls
per model and all owned command outcomes. It never extracts the archive,
executes archived code or starts a child process. [replay.json](replay.json)
records its successful third attempt; the two earlier metadata-reader mistakes
are retained in [attempt01](replay-attempt01.json) and
[attempt02](replay-attempt02.json), without changing the sealed host evidence.
