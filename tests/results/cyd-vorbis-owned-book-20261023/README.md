# Focused owned-book evidence archive proposal, revision02

This directory contains **source-only** `pack.py` and autonomous stdlib
`verify.py`. Neither program has been executed in this preparation. No archive
has been materialized or verified here; no SDK, compiler, unit/test, decoder,
reference or QEMU process has been started. AST parsing and raw identity reads
are source preparation, not a claim of archive or runtime qualification.
Root owns review and all actual materialization/verification.

Revision02 follows root's actual stage verification01 failure. The original
verifier counted dependency basenames and conflated distinct include paths
such as different `stdint.h` files. It now uses `Counter(deps)` for full
`PureWindowsPath` identities, then checks the basenames of the five genuinely
repeated paths. All109 rows/104 unique paths, their order and raw before/after
GCC output requirements are unchanged. No deduplication or limit relaxation
was introduced. `counter-fix.diff` isolates these two source-line changes;
`verifier-revision02.diff` also shows the new historical-evidence gates.

The exact entire archive-prep01 source tree, actual original pack01 and failed
stage-verify01 receipts/logs, their runner source, old stage manifest and
factual CHECKPOINT are retained through `history-plan.json`. The packer copies
only those selected old-stage files; it never recursively copies the full old
stage. The old archive verification remains NONPASS. The independent actual
unit acceptance remains PASSED. No old preparation, stage or unit result is
rewritten or reclassified by this successor.

`plan.json` pins root's already terminal campaigns: original failed capture01
and actual acceptance capture02. Parent reports/terminal receipts remain
unaltered. It also binds complete unitprep01 and runtimeprep01/02/03 source
trees through their existing exact raw indexes. No pending/live outcome is
promoted to success. The acceptance report is
`aa64efbca21196b0384ce784b31cae48139baee7d3673f3d6457dab82e90a3eb`;
original failed report is
`c7d73c27e882d889306bbd3a1c89f08dbb25c3aa6ac3aaaa327ff6e73ecf9e05`.

## Finite claim

The record concerns the exact owned production parser/setup
`6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c`,
ABI `e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60`
and existing bounded public Tremor consumer seam. It covers16 vector books,
59 active words,61 probes,2 wide equality pairs and97 strict native events.
It does not qualify a vendor decoder, backend PCM, floor0, full G6, physical
behavior or production radio integration. The25-case numeric NONPASS remains.

The archive retains the failed prebuild uniqueness gate: GCC legally emitted
109 dependency rows/104 unique paths, including five repeated SDK headers.
Revision03 removes that incorrect uniqueness condition without dropping any
rows. The verifier preserves both the original failure and all actual repeated
rows in the passing campaign; it never deduplicates the observations.

## Materialization and portable verification

After reviewing source/readiness, root may execute:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 `
  '.build/cyd-vorbis-owned-book-archive-prep-02/pack.py' `
  --repository 'C:/Work/yoRadio/.worktree/esp32-cyd-c3-review' `
  --output '.build/cyd-vorbis-owned-book-checkpoint-stage-02'
```

Then review the emitted actual manifest hash and separately run:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 `
  '.build/cyd-vorbis-owned-book-checkpoint-stage-02/verify.py' `
  --root '.build/cyd-vorbis-owned-book-checkpoint-stage-02' `
  --manifest-sha256 '<independently reviewed actual manifest SHA256>'
```

The verifier is read-only, uses Python stdlib and works from another cwd with
an absolute `--root`. It never needs the original repository, SDK, compiler,
QEMU, reference decoder or filesystem paths recorded in historical receipts.
It produces stdout only, including during failure; bytecode writes are disabled.
It validates every stored/raw byte hash, exact file set, all historical source
trees, source/include/config snapshots, parent/child receipts,14 owned commands,
original GCC compile row and macro probes, all109 include rows and stable
before/after outputs, linked symbols/map/commands and the actual flash recipe.

Packing accepts a fresh separate worktree `.build` directory or exactly
`tests/results/cyd-vorbis-owned-book-20261023`. It never overwrites an archive
or campaign, runs the verifier, calls Git or executes any captured command.
Source copying requires before/after identity stability. Full object/build
caches are excluded. Original receipts/reports/logs are byte exact; larger
JSON/log data may use deterministic gzip with both encoded and original hashes.
Raw setup fixture binaries remain source evidence, rather than omissions.

Firmware/ELF/tool binary bodies are hash-only omissions. The64 actual leading
ELF bytes are retained and bound to the omitted full ELF's recorded SHA256;
the verifier checks ELF32/little endian/machine94. This cannot replay or
recompile the full original image from the archive alone. No firmware handoff
or production release is asserted.

## QMP and terminal fidelity

Raw QMP greeting, capabilities acknowledgement, own quit request, actual
non-guest `host-qmp-quit` SHUTDOWN event and quit acknowledgement are preserved,
with actual PIDs, process exit0, logs and parent terminal binding. The verifier
independently parses the exact two actual requests and four actual responses/
events and checks their byte bindings. Full97-event validation happens only
after the complete terminal/lifecycle checks. COMPLETE alone never qualifies.
Timeout/interruption/force-stop/partial/nonzero/missing event cannot pass.

The captured helper `955afd02ec32813f169b301832afb87b322701bd5fe879e6bd390f9cfbcd631e`
explicitly waits for true pipe EOF and the joined reader before setting its
actual `lifecycle_qualified=True`. It did **not** save a separate EOF boolean
or EOF JSON receipt. The archive and verifier say exactly that: EOF is enforced
by the hash-pinned executed helper and bound lifecycle result, while
`QMP_EOF_direct_boolean_recorded=False`. No new observation is invented after
termination. Raw actual JSON does not contain a QMP EOF event.

The only code executed by the future verifier beyond its own stdlib logic is
the exact SHA256-pinned pure protocol source
`c87b344b9ad84af3434e8e13f82560e988490c85edcdc53cbc8888553f5ce21c`.
That source checks recorded vectors/fields/protocol order; it never runs C,
the decoder or a process. Source controllers and captured shell commands are
data only and are never imported or executed.

The pure Windows argument parser is adapted from the reviewed local
`cyd-vorbis-uint32-rate-archive-prep-02/verify.py`; dependency spelling handling
follows the reviewed runtime03 parser while retaining repetitions. These are
explicit verifier adaptations, not newly observed compiler executions.

