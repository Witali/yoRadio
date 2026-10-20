# CYD public raw block-matrix evidence

This archive preserves completed public raw block-matrix evidence. The
standard-library collector and verifier launch no process. Collection alone
does not verify the bundle. The verifier reads only bundle files and works
from an arbitrary current directory; it evaluates the exact SHA-pinned pure
protocol module. Independent executions and their terminal receipts remain
separate from the archival consistency check.

The retained results have different scopes:

| Evidence | Retained result |
|---|---|
| Original108 host cases | NONPASS:78 dual-reference passes,30 native FFmpeg floor refusals |
| Xiph completion | All108 independently decoded; original refusals remain visible |
| Minimal floor at192000Hz | All36 size pairs passed both references |
| Generator reproduction | 144 Ogg files/432 headers/5976 audio packets identical;230/233 files exact,3 metadata files differ |
| Synthetic protocol checks | Original8 and canonical8 host methods; both profiles are synthetic |
| Actual CYD target | RAW_BLOCK_MATRIX_ACCEPTED:108 cases,5472 packet pairs,360 transition groups,32543616 PCM bytes,6056 protocol lines,worker core1 |

The target result comes from the immutable controller report and nine owned
commands, with the separate direct-tool terminal receipt for session88923,
chunk c67569, exit0. That receipt does not fabricate PID or timeout facts.
Controller-owned process states supply the actual bounded execution facts.
No ESP32-C3 target matrix was executed as part of this proof.

Collection preserves reports, raw process receipts and both streams, source
generators and their adaptation/reproduction records, canonical test sources,
the floor-range standards audit, actual frozen raw banks, target source/config,
compile database, setup macros/response/specs context, link build description,
symbols, SDK identity/clean observations, and image/ELF identities. Full text
above64KiB is losslessly gzip-compressed, except Python. Ogg source carriers and
small generated encoded input packets remain available; PCM/WAV, firmware/ELF,
libraries, tools, ROM and other build binaries are omitted with SHA256 and size.
WAV omissions additionally record the decoded PCM byte identity at collection.
These omitted bytes cannot be independently replayed or PCM-compared offline.
Only small captured ELF header metadata is retained. No production firmware is
created by this collector.

The collection command, from the worktree root:

```powershell
& C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -B -X utf8 .build/cyd-vorbis-block-archive-prep-05/pack.py --repository C:/Work/yoRadio/.worktree/esp32-cyd-c3-review --target C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/cyd-vorbis-block-target-01 --target-terminal C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/cyd-vorbis-block-target-01-terminal.json --output C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/tests/results/cyd-vorbis-block-matrix-20261020
```

The output must be fresh. Failures retain partial output; never overwrite or
silently restart. All copied/omitted inputs are rehashed before manifest
publication. Optional `--extra` preserves additional final root receipts.

Then, from outside the archive/worktree, retain stdout/stderr and terminal exit
status outside the archive:

```powershell
& C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -B -X utf8 C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/tests/results/cyd-vorbis-block-matrix-20261020/verify.py C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/tests/results/cyd-vorbis-block-matrix-20261020
```

The verifier checks exact stored file set, stored/raw byte hashes and sizes,
source/receipt/log pins, all36-pair family coverage, original78/30 classification,
Xiph108 lineage, minimal36 dual proof, canonical/proposal identities and host
checks, raw bank arrays against their encoded corpus, minimal rate-only rebind,
target source/build/config/ELF94/SDK6.0.2 identity, setup macro context, image
recipe and native CYD/core1 protocol using actual terminal states. It does not
execute generators, decoders, SDK tools or QEMU. Verified archival consistency
does not replace the recorded executions or reconstruct omitted PCM.

This qualifies the isolated CYD public raw block matrix only. Full G6,
production radio integration, Ogg/EOF/reset/OOM, resource/heap, fixed-point
conformance and physical audio gates remain open. The normative floor audit
does not certify unrelated setup/packet validity or vendor correctness.
