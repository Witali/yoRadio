# Exact setup-owner host qualification

2026-10-26. Parent: `0373fb09d24450e6bce02f73348de179f55517af`.
The new optional owner passes its complete host lifetime/failure corpus.
**Native SDK/QEMU qualification and decoder integration remain open.**

See the [owner contract](../../../docs/CYD_VORBIS_SETUP_OWNER_DESIGN.md) and
[target preparation record](../../../docs/CYD_VORBIS_SETUP_OWNER_TARGET_DEFERRED_20261026.md).

## Implementation scope

`native_vorbis_setup_owner` owns four actual-size arrays from the unchanged
`native_vorbis_numeric` parser. It retains original packed VQ fields, active
Huffman entries, multiplicands and configuration after incoming packets are
freed. It does not expand floating tables or retain packet pointers.
Validation and object-byte checks precede allocation; empty pools are skipped.
Failure preserves prior handles/borrows/bytes. Success publishes the new owner
before freeing old allocations through their original saved allocator. Clear
nulls the handle before callbacks. The API requires external synchronization
and allocator-context lifetime; replacement temporarily holds both owners.

The resource port and both production decoder selections are unchanged.
Comment/header sequencing, Ogg transport, Xiph setup handoff, numeric route
selection and synthesis remain separate. This is not a complete decoder pass.

## Actual host results

GCC 13.3.0, x86_64-linux-gnu, C11/O1, active assertions, `-Wall -Wextra -Werror`,
ASan/UBSan, `-fno-sanitize-recover=all`, `-fno-fast-math`, and
`-ffp-contract=off`. All ten owned commands returned0, child process groups
were reaped, and execution stderr was empty.

| Result | Count |
| --- | ---: |
| Corpus cases | 335 |
| Valid identification/setup pairs | 295 |
| Full-header failures | 40 |
| Original Xiph header pairs retained | 31 of31 |
| Successful opens/replacements | 5378 |
| Incomplete-header prefix refusals | 399770 |
| Total parse refusals | 399810 |
| Allocation refusals | 2982 |
| Runtime assertions | 19038727 |

The corpus reuses all300 prior setup rows and adds all31 pinned original Xiph
pairs plus three empty-pool combinations and an explicit sparse-index case.
The independent setup oracle constructs109844 expected uint32 field values.
The C fixture compares every retained layout, book, original sparse entry,
word, raw packed VQ field, multiplicand, configuration and typed getter after
both copied header buffers are overwritten and freed. Pointer checks require
all retained storage to belong to the expected allocator's live allocations.

Every required allocation ordinal is refused during initial creation and
replacement of a live owner, with a successful retry. Tagged old/new/independent
allocator contexts expose wrong-context frees; full byte snapshots and borrowed
pointers remain unchanged after failure. The caller allocator descriptor is
overwritten after a successful open, verifying that callbacks/context were
copied. Clear/null-view/invalid-callback controls and all zero-size skips execute.

Every bit prefix below233 identification bits and below the measured setup end
is rejected without any allocator callback, preserving the live owners. The
reported totals can be reconstructed from the predeclared model: two baseline
owners per case, each valid case's measured3–5 allocation sites, and all declared
prefix cuts. The offline verifier performs that reconstruction.

RANGE object-addressability rejection is reviewed in source and is not
dynamically qualified by this finite host corpus. No incomplete huge-count
header is relabelled as a RANGE test. No audio, DSP, transform or PCM executes.

## Two retained runs and Clang

`host01/` is a complete successful host pass. The first six-unit Xtensa Clang
analysis (`lint01/`) reports one padding warning in the generated constant
case descriptor and no other warnings/errors. The generator then reordered
that metadata and used designated initializers. Component/fixture arithmetic,
input cases and expected values did not change.

`host02/` repeats the complete host qualification with the final generator.
Both runs have identical model bytes and operation/assertion counts. The final
six-unit Xtensa Clang run (`lint02/`) reports **zero warnings and errors** in
quant.c, codebook.c, setup.c, setup_owner.c, portable fixture and host wrapper.
This is source analysis with explicit Xtensa/Picolibc flags, not an SDK build.
The initial padding diagnostic remains archived; no suppression was added.

## Native preparation did not run

The independent target agent's controller write and its identical retry
returned `aborted before dispatch`, with no reason or handle. No explicit
safety rejection was reported. Seven project files were preserved, but the
controller/protocol tests, SDK build, merged image and QEMU runtime do not exist.
Root confirmed absence of the controller/campaign and verified the seven source
files against the archive before removing only their task-created working copy.
They remain under `target-prototype/` for inspection.

That initial prototype selected `prefix_sweeps=0`; it is an unrun subset, not
the full owner target gate. Future qualification must run all335 cases with
prefix sweeps enabled and preserve actual SDK/UART/stack evidence. Its archived
README describes an intended absent controller, not a runnable command.
Previous deferred scopes were not resumed or bypassed.

## Evidence identities

- Final host report:
  `9e14708c3e6cbcd072600295e829adb94ee4696f554a676d17a1913f106eb417`.
- Corpus:
  `20784be2c4ab258db9c543b67af9dad44f09472a05e4193bbbb505a7017773ba`.
- Final generated oracle header:
  `ab270cbe0e004b0bb66e4a01a3715e69ae9a2ec69d0eca77373695013f10c7f8`.
- Runner:
  `c4dd5c80cd61b6807a59908baf5dcee025814a7125cacf60b2b3a6e69521740d`.
- Independent setup oracle:
  `ce69b4136ac1b1a4b71e185e6c600330e46cfb8b2b14c3d4a1e54c044afb02ff`.
- Owner implementation:
  `ebc1212cbbdc74fd07b29393baa174e0cd80e793ccc70e958251faf56ac88429`.
- Owner public header:
  `28237d467a3bae3950f83a52d93f69b686851601c01f71ce67a64a2dce680106`.
- Portable fixture:
  `9a9fb24f879101526cb62d6beaa71779805fb2eb788db2795e21b32ad2445c84`.
- Offline verifier:
  `4201a4794b756036c1d2cfb4e9e40742522a293e8d5d8fca797a531d7d04448d`.
- [captures.zip](captures.zip):2072391 bytes /222 members, SHA256
  `5b90e1a242036f1c86fbbec6f76dea52b4c6e4837a39941b779f051a9d7d28c6`.
- [manifest.json](manifest.json): exact member extents/hashes, SHA256
  `5f4244d60247c93f3dd7fdc90b7437c09e750f687254e6f3a339f7dca6ed0b93`.

The archive retains complete frozen sources, independent oracle, original31
header model, generated expected literals, objects/binaries, raw diagnostics,
owned requests/receipts, outer command results, both Clang analyses, prototype
and provenance observations. Host binaries are tests, not production firmware.
The separate publication receipt records successful read-only archive verification.

From the task worktree:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 tests/verify-vorbis-setup-owner-checkpoint.py
```

A fresh host run uses the existing WSL/GCC runtime:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 tests/test-vorbis-setup-owner.py --output .build/vorbis-setup-owner-host-fresh
```

Physical qualification, target stack/heap/watchdog, actual decoder lifetime
wiring, full VQ/floor-to-IMDCT range and the three radio outputs remain open.
Production core bindings, stacks, priorities and hardware choices are preserved.
