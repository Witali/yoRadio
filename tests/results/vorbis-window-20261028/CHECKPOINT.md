# Full Vorbis windows on scaled binary64 blocks

The [component](../../../idf/components/native_vorbis_window) implements lookup
preparation, window geometry and application. Its [design](../../../docs/CYD_VORBIS_WINDOW_DESIGN.md)
follows the Vorbis nested sine curve and pinned Xiph transition coordinates.
The separate signed64 source exponent is retained unchanged. This package
executes no overlap/history, granule trimming, floor0, PCM, SDK/QEMU or radio.
Production component lists, tasks/cores/stacks and hardware are unchanged.

Final host04, GCC13.3 with ASan/UBSan and assertions enabled:

- All36 short<=long configurations, all eight current/neighbor flag combinations,
  288 complete shapes and587,520 output values.
- All8,160 half-window coefficients independently checked with a70-digit Decimal
  sine series, plus monotonicity and power complementarity. Maximum coefficient
  error3.3306690738754696e-16; fixed absolute bound2e-15.
- Full-window scatter oracle independently places slopes around quarter centers.
  Every declared source bit is reconstructed separately, including DBL_MAX,
  signed zero, minimum subnormal and a wide finite span. Plateau bits and zero
  support are exact; products allow2e-15*abs(input)+4*DBL_TRUE_MIN.
  Maximum error/abs(input)3.764464825219074e-16.
- 5,272 refusal controls/3,494,013 assertions. Every refusal immediately checks
  the full input bytes and actual supplied descriptors, including injected
  nonfinite values, before restoring them. Output/result and guard regions are
  unchanged; successful retry and immutable lookup storage are checked.
- Three owned commands terminal0, all child processes reaped/groups gone;
  outer CLI terminal0, sanitizer stderr empty. Eight damaged captures rejected.

Source-only GCC15.2 produces four ELF32 objects: C and C++17 on LX6 and RV32IMC.
Eight source-profile commands terminate0. Window own frames at -O2/-fno-inline:
prepare48/80B, apply64/80B; callee/libm/task high-water is not measured.
Clang-Tidy window0warnings/0errors. Sixteen fixture warnings all describe its
own pre-call object-byte snapshots: these deliberately check storage, including
padding, rather than equality of independently constructed objects. No warning
suppression is added. Neither these objects nor the host fixture are production
firmware images, and no memory or real-time benefit is claimed.

History is retained: host01 WSL E_ACCESSDENIED before GCC; host02 passed;
host03 strengthened source reconstruction/corruption controls; host04 added
per-refusal input/descriptor snapshots. All three successful numerical captures
are byte-identical. Profiles01 stopped before compiler execution with Windows
DLL error623; profiles02 passed with the same sources under the normal runtime.

`captures.zip`:232 members,29,645,986 uncompressed bytes;7,728,190 compressed.
SHA256:`5ab17e02a3182fc1b00ac99cdde5bde2bae73768ee0466ae3504e0cef6cab79c`.
`manifest.json` SHA256:
`a3095be81555f9c33ffa6bb70a616e1eb54472afb090e3949bb4243a0e6bd242`.
Sources, commands/receipts, diagnostics, prior attempts, source objects and every
capture are retained. Rebuildable host executables/host object directories are
omitted, with executed identities recorded.

The [pure verifier](../../verify-vorbis-window-checkpoint.py) checks every member
against pinned archive/manifest identities, all coefficients/outputs, complete
host/source-profile outcomes and eight corruption controls. It uses a pinned
local reader, executes no archived code or commands, and extracts no files.
`verification.json` is the independent replay; `replay.json` is packaging replay.
