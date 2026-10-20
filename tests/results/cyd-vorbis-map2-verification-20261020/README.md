# CYD Vorbis setup checkpoint verification

Actual collection03, stage verification and final canonical verification all
completed with exit0. The final read-only verification ran from C:/Work/yoRadio,
a different cwd from the task worktree. Exact argv, owned process facts and
stdout/stderr identities are retained in the corresponding command files.

The final canonical bundle is ../cyd-vorbis-map2-20261020/. Its manifest SHA256 is
c3e1fa16adb85d25f90339a9d4c74b6c0cbc9feac3d4097624bbe1d6553bd11c.
All4183 stored files match the stage byte-for-byte. Root annotation adds only
CHECKPOINT.md and its generated inventory identity; original reports/payloads
remain unchanged. Earlier collection failures and their exact source corrections
are preserved inside the main bundle, separate from SDK/runtime outcomes.

Integrity verification preserves numerical NONPASS: wideD16 and floor0 are still
open, as are the full25 and books16 bounded results. It does not certify format,
fullG6, production firmware or physical hardware. See the main CHECKPOINT.md.
