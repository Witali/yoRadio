# Bigfloat source-only native profiles

This is separate from the [host arithmetic checkpoint](CHECKPOINT.md). It
preserves actual ESP32 LX6 and ESP32-C3 RV32 compiler/linter evidence. No MCU
arithmetic was executed: there was no linking, SDK build, QEMU, flashing, gain
certification, PCM synthesis or production selection.

All four attempts are retained in `source-profiles.zip`, with no omissions:

| Attempt | Preserved outcome |
| --- | --- |
| 01 | Windows sandbox WinError623 before the first compiler child. No compiler PID or object is invented. |
| 02 | Both real SDK GCC15 compilers reject the unchanged creator's `slimb_t*` to `int*` conversion; six other objects succeed. |
| 03 | One-hunk portability copy passes compile-only checks. A later, separate host sanitizer test finds the zero-length-copy UB; compile-only success did not detect it. |
| 04 | Final two-hunk copy passes all14 commands: eight real ELF32 objects and eight compiler stack reports. |

The final source copy differs from the preserved original only by a local-int
conversion in `bf_get_limb32` and a nonzero-length guard around `bf_set`'s copy.
The pure verifier reconstructs the copied bytes by both literal replacements,
checks the exact patch and manifest, and compares final live C/header/CMake,
original creator files and portability files with the executed snapshots.

Final controller SHA256:
`a6d2ca98e4493c13c50f870fe34d15574460eb6898a2b997d799508f2ce86b12`.
Final portable source SHA256:
`158da48780e54571ae2ce56ef7049f9829f62817c005009c9018bdf74d92a378`.
Final patch SHA256:
`cd15a88f0718bb2f18e2b8b269a57983315ef28617b2e836b3bba07391389a42`.

Both compilers use `-O2 -fno-inline -fno-fast-math -ffp-contract=off`, function
and data sections, stack reports, `-Wall -Wextra`. The adapter and C++17 public
header smoke pass `-Werror`; compile-time assertions require32-bit pointers and
limbs. Actual retained objects are little-endian ELF32 relocatables with
machine94/Xtensa or243/RISC-V; RV32 uses `rv32imc`, `ilp32` and soft-float ABI.

Creator diagnostics remain visible:40 LibBF warnings plus2 cutils warnings per
target. They were not hidden or promoted to a blanket safety claim. Clang-tidy
analyzes the adapter translation unit with actual MCU headers and the unchanged
repository configuration: one warning, zero errors, no new suppression. The
warning is in the unchanged header's unsigned-to-int conversion after a0x3f
mask; the value0..63 fits `int`. This is not a full creator-code lint audit.
Compiler `.su` figures describe individual functions, not total recursive stack
depth, timing, temporary heap, linked code size or MCU memory fit.

Artifact identities:

- ZIP:891,356bytes,202 regular members,3,682,502 decoded bytes;
  SHA256 `56132fd8ec76e76fc2b6d519dc9f5cc2ceba8f92b8558c99ef3e230f8bf318cf`.
- Manifest SHA256 `1efdf113950cfb6d13cb694b92490a6bd55ebae78becc48bd64461ae8d4cb27b`.
- Final04 report SHA256 `fe56791c7a310c1039fca41f724b889231aeef3e4cc92bedbeef829190702090`.

The archive includes every frozen component/controller/config/header snapshot,
source manifest, patch, process argv/PID/terminal receipt, stdout/stderr log,
object, `.su` and tidy record from all attempts. Original creator notices remain
in the preserved source files. `source-profiles-replay.json` records the pure
verifier's result. Repeat into a fresh worktree path:

```sh
python -B -X utf8 tests/verify-vorbis-bigfloat-profiles-checkpoint.py --output .build/vorbis-bigfloat-source-profiles-replay-new.json
```

The verifier reads ZIP members as data, checks every byte and source identity,
recounts diagnostics, verifies actual object/ABI and stack-record geometry and
process outcomes, and tests corrupted ELF controls. It neither imports archived
code nor extracts files, launches a compiler or repeats native commands.
Current final executable sources and the profile controller must match; the
frozen README remains a historical design reference. Task cores and priorities
are unchanged.
