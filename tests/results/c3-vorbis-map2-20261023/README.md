# C3 public codebook setup checkpoint

This focused checkpoint records the C3 counterpart of the CYD public setup
correction: unused lookup2 rows, compact wide active rows, and legal single-entry
codebooks. It preserves the actual original baseline NONPASS and full25 numeric
NONPASS. Complete setup/decode capture does not imply numerical conformance.

The root's actual baseline used setup
`f3d8b3ff1cb8d2cef675eb742be35f3e6a4533b3e10fbd368aacd929a10fcac0`.
It completed six prerequisite cases/84 packets, then rejected case6
`sparse_explicit_d4_seq0` at public open with -1/null/core0. All seven actual
owned commands exited0; the strict controller exited1 (session43472,
chunk `b97a47`). No heap panic occurred. The subsequent focused C3 source at
`ce2eed3cdb80ded721623a3e57675ffeac88882d99e7a41f2d5cf9c85d3e1d87`
completed all25 cases/350 packets/623360 PCM bytes/778 events (session62556,
actual terminal0, chunk `bcdea3`). The first188 native prerequisite events are
identical. The original reports and root before/after witness remain unchanged.

The actual independent comparison measured all25 and exited1 because the
predeclared project bound2 S16 LSB fails (root chunk `5aeeed`; actual command
receipt is retained). The bound is an engineering regression policy, not a
normative Vorbis tolerance. Old books8, single/twin4, and floor1/r0 controls3
have max1; wide4 have max65535; even floor0 cases have max40664/1649/40664;
odd floor0 cases have max65535. Two wide target equality relations fail; the
other six target relations and all eight independent Xiph relations hold.
Full25 and the separately declared books16 subgroup both remain false.

The root's direct C3/CYD PCM relation reports21/25 byte-identical results. Exactly
the four wide cases8..11 differ across architectures despite identical maximum
errors. All six floor0 outputs are byte-identical across architectures. This is
finite output evidence and does not establish an opaque implementation cause or
general C3/CYD equivalence.

## Source-only archive proposal

These scripts adapt the reviewed CYD archive packer
`404b541ad58d62499166a1711d95beef73060b3d2fa31ca8bdc6d20d7d2f7722`
and verifier `74afcd06807e0377e0645069bdc1667ca0674aa1523139678fa27562c12059f4`.
The complete source diffs are retained. This directory has only prepared and
AST/hash-checked source. No packer, archive verifier, protocol, metric, policy,
SDK, compiler, emulator, reference, test, Git, or device action was executed here.
All actual packing, verification, promotion, commits and pushes belong to the
root.

`plan.template.json` selects exactly baseline01, acceptance01, numeric01, runtime
prep01/02, numeric prep01/02, root source snapshots/relation, before/after witness,
cross-architecture relation, and actual terminals. It excludes the separate
owned-book unit and every deferred scope. Historical pending fields in the
source-preparation record remain historical; the later reports are independent
facts. Current canonical production files are never substituted for snapshots.

All actual C3 input snapshots and original logs are copied into this checkpoint.
Large text/PCM/WAV files may use deterministic lossless gzip. Raw fixture .bin
files are retained. Actual app/tool/archive/ROM binaries are hash-only omissions;
ELF omissions retain the actual first64 bytes and require machine243. This
fixture/QEMU project is not production firmware.

The checkpoint explicitly depends on the existing committed archive
`tests/results/cyd-vorbis-map2-20261020`, manifest
`c3e1fa16adb85d25f90339a9d4c74b6c0cbc9feac3d4097624bbe1d6553bd11c`.
It is **not standalone**: retain both directories. Old17/new8 independent host
evidence is linked by exact original-path manifest keys, stored/raw SHA256 and
byte counts. No current-source fallback or fuzzy source search is allowed.
Only these shared historical files are reused; actual C3 snapshot copies remain
local. The verifier first runs the exact pinned committed CYD offline verifier,
then independently checks every linked file used by this checkpoint.

The future C3 verifier checks actual command and direct-tool terminals, nine
acceptance/seven baseline command logs, actual build/compile/macro/profile
context, ELF64 evidence, setup source identities, strict full25 protocol and
persisted PCM, exact negative baseline prefix, original Xiph/raw binding, all
signed-S16 packet/channel metrics, diagnostic alignment, transition nonzero
counts, eight relations per decoder, and unchanged full25/books16 policies. It
also rechecks the root cross-architecture relation against actual saved PCM in
both archives. It does not rerun a codec, compiler or emulator, or qualify full
G6, general format conformance, production radio, or a physical board.

## Root-owned commands after source review

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 .build/c3-vorbis-map2-archive-prep-01/pack.py --repository 'C:/Work/yoRadio/.worktree/esp32-cyd-c3-review' --output '<fresh .build stage>' --plan .build/c3-vorbis-map2-archive-prep-01/plan.template.json
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 '<fresh .build stage>/verify.py' '<fresh .build stage>' --repository 'C:/Work/yoRadio/.worktree/esp32-cyd-c3-review'
```

After actual verification, the root may promote byte-identically to
`tests/results/c3-vorbis-map2-20261023`, verify again using that exact path, and
publish a focused commit. No successful archive result is claimed by this source
proposal.
