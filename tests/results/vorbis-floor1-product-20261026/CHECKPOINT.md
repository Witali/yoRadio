# Exact floor1 spectrum product qualification

2026-10-26. Parent `036efc389e629ddf5c13be26e343b24e19317ada`.
**Host arithmetic and packet integration PASS; source-only LX6/C3 compile
PASS. SDK/QEMU execution, floor0 product, transform/PCM and radio integration
remain open.** See the [design](../../../docs/CYD_VORBIS_FLOOR1_PRODUCT_DESIGN.md).

The new component multiplies coupled residue by the unchanged256-entry Xiph
binary32 inverse-dB table. Original literals and complete BSD license are
retained. Residue is never narrowed to float; products are exact signed limbs
on a movable binary point. At most36 words suffice, derived from the original
residue domain and at most47 additional alignment bits. Ordinary curves use
their measured width. This is floor1 only, not a completed decoder.

## Generic exact arithmetic

`math03/` is the final capture, GCC13.3.0/x86_64-linux-gnu, C11/O1, assertions,
Wall/Wextra/Werror, ASan/UBSan/no-recover, no-fast-math and ffp-contract=off.
All six owned commands return0; process groups are reaped and execution stderr
is empty. The independent oracle parses original Xiph decimal literals as
rational numbers and rounds directly to binary32 with ties to even. Expected
products use Python integers, not production arithmetic.

| Measurement | Result |
| --- | ---: |
| Cases | 1663 |
| Coefficients | All256 |
| Magnitude widths | All1–1087 |
| Signed endpoint combinations | 556544 |
| Exact samples | 619540 |
| Exact uint32 product words | 11816765 |
| Maximum output limbs | 36 |
| Refused rows | 23 |
| Refusal controls | 663 |
| Runtime assertions | 33603855 |

The helper's1087-bit arithmetic shape includes every34-limb signed domain;
the actual encoded residue bound is1079 bits. Synthetic shapes do not claim
to be complete valid encoded streams. Constant/mixed quiet/unity curves,
zero/tiny/carry/pattern values, exponent boundaries, late invalid sign domains,
selected-channel isolation, source/output capacities, NULL and object-byte
RANGE controls are covered. Failures preserve output/result; complete retries
succeed. Inputs, source descriptor, guards and unused output tails are checked.

`math02/` is the earlier complete PASS with identical arithmetic and663 refusal
controls, before adding source-descriptor and unused-tail assertions. Its
assertion count is22968025; all capture bytes except that final counter are
identical. Both exact limb sequences hash to
`16774851bb1d577c9d66d0e1e980645fdf81f9dee88cb45a431890c36e18bf21`.

## Real packet composition

`frame03/` runs the unchanged setup owner, packet coordinator and existing
floor1 reconstruction/curve, then the new product wrapper. Ten C units and
fourteen owned commands succeed with the same sanitizer/warning flags.
The previous1311 cases, including all434 original unmodified packets, remain;
two additional packet rows exercise quiet/unity and absent coupled channels.

| Measurement | Result |
| --- | ---: |
| Cases | 1313 |
| Original packets | 434 of434 |
| Floor1 channels | 1750 |
| Curve indices compared | 275808 |
| Exact uint32 product words | 297056 |
| Absent floors with nonzero residue | 75 |
| Present floors over implicit-zero residue | 78 |
| Quiet index0 channels with nonzero output | 2 |
| Expected floor0-specific API refusals | 972 |
| Refusal controls | 11237 |
| Runtime assertions | 862469 |

Independent bit/setup/entropy parsers, closed-form floor curves and integer
products compare every captured field, index and limb. Wrong-floor-type
refusals test the floor1-specific API; they do not reject floor0 streams from
the eventual dispatcher. Original presence silences absent channels after
coupling. Index0 stays positive. Zero-residue skipping relies on finite floor1
factors and establishes no floor0 pole policy.

The test guards all owner/input/workspace data and zero live allocations at
exit. One-short curve/output and NULL/RANGE controls preserve published output
and metadata; full retries are canonical-hash-identical. `frame02/` also passes;
the final oracle replaces binary64 intermediate literal conversion with exact
rational rounding. Models, inputs, expectations, captures and measurements
are byte-identical across these two runs.

## Lint and compiler profiles

Final `lint03/` analyzes the new component and both final fixtures with the
repository clang-tidy configuration and explicit Xtensa/Picolibc includes.
There are0 errors. The component has0 warnings; fixtures have10 warnings:

- Nine byte-comparison warnings deliberately compare an object with its own
  pre-call byte snapshot, including padding, to enforce exact preservation.
  They are not equality tests between separately initialized structures.
- One `.c` include warning: the frame fixture reuses the unchanged guarded
  packet fixture with its main renamed. That main is compiled but not executed;
  the new main owns this capture. No production source includes a C file.

No diagnostics are suppressed. Initial `lint01/02` and their frozen sources
remain in the archive. The existing source dependencies are unchanged from
their earlier checkpoints.

`gcc02/` has ten successful installed GCC15.2.0 commands, four ELF32 relocatable
objects: C component and C++17 public-header probe for ESP32 LX6 and ESP32-C3
RV32IMC/ILP32. Pointer and long widths are32 bits. O2/no-inline stack records
show prepare_frame own frames448B on LX6 and416B on C3, and product wrapper64B
on both. These are individual function frames, not whole-chain stack usage,
SDK links, task high-water measurements or native execution.

`math01/` and `frame01/` retain WSL E_ACCESSDENIED before the compiler-version
child ran; no host tests ran in those attempts. `gcc01/` retains the Windows
DLL launch failure before compiler startup. Fresh authorized tool launches
then succeeded. These are local tool-launch failures, not evidence of a
cybersecurity policy rejection. Existing deferred scopes were not resumed.

## Evidence and independent verification

`captures.zip`:583 members,15803828 bytes,270246886 uncompressed bytes.

- Archive SHA256: `3b74cc7425b315997011040b6b6a8924b908cdff0404e0d0601cbb81a68a93ea`.
- Manifest SHA256: `2542e701020ade4ae7b3c005f807e8f1ca712da9b67a90d9c313afd0f23c111e`.
- Final generic report: `7a4c7c4a2797d8f732e99e198416382d15b0e2eca9936e0c858a984b62014745`.
- Final frame report: `1a2fdca6ebffdbfb022f7d232d71436aeee95380ab534658b32d45e361045bd3`.

Run `python -B tests/verify-vorbis-floor1-product-checkpoint.py`. It checks
archive/member hashes, current versus executed source bytes, independently
regenerated models and inputs, both complete captures, real terminal receipts,
raw unfiltered lint logs, compiler objects and stack records. Five partial,
corrupted or semantic-mismatch controls are rejected. It imports only pinned
local pure readers, starts no child processes and extracts no archived code.

Production CMake lists, firmware selection, pins, outputs, task affinities,
priorities and stacks are unchanged. Pinned Xiph and the existing numeric,
setup-owner and packet-frame components remain byte-identical. No production
firmware was built by these tests. Physical/resource and all previous deferred
gates remain open.
