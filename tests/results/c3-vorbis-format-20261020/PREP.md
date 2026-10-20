# C3 public raw8192 archive proposal

Preparation only. Neither collector nor verifier has been run. AST parsing and
raw file hashing are the only intended preparation checks. Root review and a
separate explicit execution authorization precede collection. This proposal
does not change campaign, SDK, canonical, Git or firmware files.

The collector accepts explicit repository, three completed campaign roots and
a fresh exact output directory. Optional prep-root and outer-SDK-receipt
arguments make source selection reviewable. It requires terminal0 command and
SDK receipts before creating output, retains a partial output on any failure,
and never overwrites or starts another process. All selected input bytes are
rehashed before manifest publication. Collection prints `verified: false`.

After authorization, from the worktree root, using the existing Python:

```powershell
& C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -B -X utf8 .build/c3-vorbis-format-archive-prep-01/archive_evidence.py --repository C:/Work/yoRadio/.worktree/esp32-cyd-c3-review --baseline C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/c3-vorbis-format-baseline-01 --acceptance C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/c3-vorbis-format-acceptance-01 --control C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/c3-vorbis-format-old-guard-01 --output C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/tests/results/c3-vorbis-format-20261020
```

No `--extra` arguments are needed for known final records: combined qualification,
source and test promotions, raw test-index check, source audit, canonical host8
receipt/logs, source-index newline relation/snapshot, all nine promoted test
files, root capture utility and all root C3 preparation/qualification Python
scripts are mandatory defaults. `--extra` can preserve additional final root
receipts without treating them as independently qualified evidence.

Run the copied verifier from outside the archive and worktree, retaining its
stdout/stderr and terminal exit status outside the immutable output:

```powershell
& C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -B -X utf8 C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/tests/results/c3-vorbis-format-20261020/verify_archive.py C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/tests/results/c3-vorbis-format-20261020
```

The standalone verifier checks stored and decompressed hashes/sizes, exact file
set, all pin-referenced local/external inputs, real terminal receipts/logs,
native C3/core0 protocol with actual process return/timeout facts, raw pair PCM
accounting, actual setup compile row and unchanged response/specs context,
SDK6.1/target/compiler/configuration, merge recipe and image identity, captured
RV32 ELF header metadata, source two-line removal and control restoration,
caller/fixture relation, eight-test execution records and canonical promotion.
It evaluates only the exact SHA-pinned 59-line native protocol module and
launches no process. Its own AST/source must be reviewed before execution.

The historical caller-relation original setup pin is explicitly bound to its
frozen old project-prep snapshot; current canonical setup is independently
bound to the accepted candidate. The saved LF Git-index snapshot is checked
through reversible LF-to-CRLF conversion against the executed candidate; raw
index and checkout hashes are intentionally different.

Large logs/compile databases are losslessly gzip-compressed; Python and fixture
remain uncompressed. ELF/bin/library/tool/ROM bytes are omitted with original
path, SHA256 and size. Captured ELF header metadata is not full binary replay.
No decoder library, SDK installation or firmware image is duplicated.

Expected observations: baseline285 lines/204 exact pair packets/2452224 PCM
bytes and `REGRESSION_REPRODUCED`; acceptance421/340/4631808 and
`FORMAT_ACCEPTED`; restored old guard279/204/2452224 with the exact
`legal_candidate_open_required` failure and `CONTROL_EFFECTIVE`. Baseline and
control keep `passed: false` and acceptance qualification false.

Only the isolated public raw format is qualified. There is no production-radio,
adapted canonical CMake SDK build, full G6, Ogg/EOF/reset/OOM, resource/heap,
physical audio or broad standards/conformance qualification. No new target,
reference, SDK, compiler, Git or device run belongs to this archive task.
