# CYD isolated Vorbis bridge — 2026-10-20

This is a **partial isolated bridge qualification**, with no main-radio
activation. The final normalized-source raw02/control02 and configure02 reports
are authoritative. Earlier raw01/control01 and raw-probe reports are historical
versions. Prototype raw-probe01 failed during SDK environment activation;
raw-probe02 passed its earlier isolated gate. None is relabeled as current02.

The one raw fixture covers 535 packets, 1602 undersized-output rejections and
2,112,000 PCM bytes compared exactly with the original decoder. One exact
skip-preflight control detects changed DSP state. Ogg, OOM, SMP, broader formats,
full callback qualification, radio integration and physical qualification remain
open. There is no standard-conformance, performance, RAM or hardware claim.

`index.json` identifies final and historical reports. `path-map.json` maps each
selected original path/content version to raw bytes, lossless gzip bytes or an
explicit size/hash omission. `bindings.json` connects original JSON hash fields
to those mappings. Reports, source snapshots, codec headers, bundle data and
the actual three compile rows retain their original identities. The ABI draft
is explicitly partial; candidate alignment assertions are not vendor ABI proof.

ELF/application/full-flash/ROM/object/archive/tool binaries are omitted. The
existing Ogg fixture and generated fixture header are also not duplicated;
their original paths, sizes, hashes and generator identities remain. Nested
original manifests can reference omitted payloads. The root manifest defines
this compact archive's complete stored set. Large text/compile databases/Ninja
metadata are gzip-compressed with exact decoded-byte checks.

Run `python -B verify.py` from this directory, or pass its path from any working
directory. It requires only Python 3.9+ and reads only this archive. It checks
integrity, decoded bytes, mappings and selected report/runtime markers. It does
not recreate omitted binaries/fixtures, rebuild, decode audio or qualify any
open gate. See HOST.md for scope details.
