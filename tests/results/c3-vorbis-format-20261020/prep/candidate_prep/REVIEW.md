# Independent C3 candidate source preparation

This variant is derived from the qualified C3 baseline. Only the two-line
default rate/block coupling is removed from setup.c; the explicit
LIMIT_TO_64kHz option and ordinary header checks remain byte-identical.
The minimal CMake's setup SHA is updated to the reviewed candidate SHA.
Caller, fixture, SDK, output.c, C3 ABI and archive/tool identities are unchanged.
candidate-relation.json and candidate.diff give the complete change.

No canonical source is modified and no SDK/compiler/QEMU command is executed
by this preparation. The root will independently build this variant with
ExpectedRejection 0 and the untouched baseline variant with ExpectedRejection 0
as an exact old-guard control, preserving the full original/vendor prerequisites.
The source test scope remains public opaque raw open/decode/close only.
No radio/Ogg/EOF/reset/OOM/private owner work is included.
