# Bounded static RX SDK evidence retention specification

Preparation has not read or collected a live campaign. No actual plan, archive,
SDK/configure/compiler/lint/Git/device command may run until root provides the
authoritative terminal0 of successor `repair.py close`, its exact raw summary
SHA256 and a separate root-authored terminal receipt. A `passed=true` file alone
is insufficient. The receipt schema and explicit CLI are below. Root reviews the
fresh PLAN_ONLY output SHA before separately authorizing a create-only write.

## Authoritative inputs and origin

The source checkpoint is 3a563324abdca56144a40d5759def0ccfe708b3c. The original
campaign marker is 7a2f5ed4ca33eddbd6c55d03e38a9ae9f7b7a8c689be4c3e926a0de8301ba81b;
the successor marker is 6eb0b9b6a3897278eeb847b188d8e12fc8ff089a9ba9f6c6b295056f8bbb2f22.
Only the exact final successor summary can authorize selection. Its report set
must contain seven distinct original GCC qualifications and six distinct new
successor Clang qualifications, with the exact vendor/custom × three backend
matrix plus reserve-off vendor PDM. The rejected original Clang PDM qualifier
c66e7671e6366714d76a5d275119286c0eaef19abc271109814d3ad1df2b9964 remains nonpass.
It cannot substitute for a successor qualification or be rewritten as PASS.

## Retained material

- Raw successor summary and separate root terminal receipt; all 13 qualification
  reports and original execution records with both stdout/stderr of every actual
  successful configure/build/export/lint command, plus the rejected qualifier.
- Both immutable markers, original campaign/helper/guard scripts, successor
  repair/policy/scripts, complete 81 pure policy controls and their exact fixtures,
  original preparation argv/provenance guard evidence referenced by the markers.
- All six frozen baseline metadata copies, original production receipts, seeds,
  invocation JSON, normalized configs, raw sdkconfigs, generated sdkconfig.h,
  actual CMake caches, compiler descriptions and compile databases.
- All exact JSON-referenced selected sources, compiler/header closure, 19 actual
  guarded SDK supporting sources and pinned tool identities. Sources include
  every result in each complete full-project lint run, including generated HTTPD
  sources. Preserve all original lint report/log/YAML artifacts as the qualifier
  listed them; YAML is retained when emitted, never fabricated for clean units.
- The separate accepted warning comparison/review: comparison.json
  92d5b58198522f537055b0925d6e701b0d4207ad33fd536c4f85830ec0b4a2e1,
  REVIEW.md 38cda2056bb4fb5112301c7a8a78e89c221fc903298f19d6e96e0d8db06cb2af,
  pending-history.json and review.ps1, without rerunning lint or rewriting triage.
- Explicit GCC qualifier text: nm, four SSL lifecycle disassemblies, app_main and
  MPI disassembly, actual command/link text, selected dependency logs/header
  closure, enabled-profile sizeof-array probe source/log/nm and maps. Clang keeps
  the separate actual TLS frontend log/dependency file and original command rows.
- Existing canonical host/QEMU archive manifest identities and repository links;
  their raw payload trees are not copied again. Firmware app.bin stays under its
  existing firmware/development variant and is linked with complete SHA/size.

No recursive SDK/build/tool/history selection exists. JSON identities and the
small explicitly named artifact set determine selection. The only bounded glob
selects a unique generated C/C++ compiler-description file per build. Missing or
changed required material fails; it is never silently replaced by another build.

## Storage and scope

Text is content-addressed by raw SHA256, deduplicated and stored raw or gzip with
mtime=0. Maximum individual text is 64 MiB, total unique raw text 512 MiB and
20,000 entries. A future plan reports actual size/count before root approves
write. All ELF/object/library/tool/ROM/firmware executable bytes are omitted with
their actual observed SHA/size. No omitted-binary reconstruction claim is made.
The committed host/QEMU manifests are retained; other members are external links.

Exact JSON path/size/SHA references and SDK guard SHA references have explicit
bindings. Text that the qualifier did not previously hash (such as selected nm
or disassembly output) is labelled as archive-stage observation. The archive
does not invent an earlier raw pin for it or repeat the qualification tools.
SDK revisions, compiler types, sizes, baselines, TU and warning counts come from
the actual final qualified reports/markers, not preparation-time guessed facts.
The execution record's historical seed_before_build identity is bound to the
byte-equal immutable seed copy. Its mutable working config was subsequently
normalized by the SDK; it is never rehashed as though its initial bytes were
still the final generated config.

Publication may later change Git HEAD, documentation and text attributes. The
archiver performs filesystem-only rechecks of the frozen recorded input bytes;
it neither executes original.checked()/Git nor asserts that the later checkout
still has HEAD 3a563... or is clean. Recorded clean-source facts belong to the
original qualification checkpoint and are not backdated to archival time.

The independent offline verifier checks archive manifest, encoded/decoded hashes,
reference bindings, exact matrix/origins, original nonpass, source/marker pins,
full GCC reserve-only and strict Clang 14-key config scopes, original terminals,
complete lint TU source/results/artifact identities and recorded RX nm/probe
consistency. It executes no archived SDK/test/qualifier script. Optional
--repository checks only explicit linked repository payloads. Otherwise external
payloads remain identified but unverified by this standalone archive.

The verifier does not recreate omitted ELF, recompute all ELF pointer/call facts,
authenticate the human provenance of a root receipt, establish production Clang
equivalence, or prove runtime/physical heap savings. Its trust anchor is the
externally supplied archive-manifest SHA and pinned original marker identities.
The seven production images are GCC/Picolibc. Clang/Newlib+nano is a distinct
experimental frontend/lint profile. Physical acceptance and deferred codec work
remain open. No new firmware counters or protocol/code changes occur here.

## Receipt supplied later by root

```json
{
  "schema": "cyd-static-rx-sdk-close-terminal-v1",
  "status": "TERMINAL",
  "returncode": 0,
  "observed_by": "root",
  "source_commit": "3a563324abdca56144a40d5759def0ccfe708b3c",
  "original_marker_sha256": "7a2f5ed4ca33eddbd6c55d03e38a9ae9f7b7a8c689be4c3e926a0de8301ba81b",
  "repair_marker_sha256": "6eb0b9b6a3897278eeb847b188d8e12fc8ff089a9ba9f6c6b295056f8bbb2f22",
  "summary_path": "ABSOLUTE_ACTUAL_REPAIR_SUMMARY_PATH",
  "summary_sha256": "ACTUAL_RAW_SUMMARY_SHA256",
  "cwd": "C:/Work/yoRadio/.worktree/esp32-cyd-c3-review",
  "terminal_proof": {"tool_handle": "ACTUAL_HANDLE", "tool_chunk": "ACTUAL_TERMINAL_CHUNK"},
  "argv": ["ACTUAL_PYTHON", "-B", "-X", "utf8", ".build/cyd-clang-config-repair-prep-01/repair.py", "close", "--repair-marker-sha256", "6eb0b9b6a3897278eeb847b188d8e12fc8ff089a9ba9f6c6b295056f8bbb2f22"]
}
```

The receipt must be outside both campaign and this prep directory, under .build.
The example is a schema description, not terminal proof. Do not substitute a
currently readable report, a RUNNING observation or the original close command.
Preserve the command's **raw argv** and actual execution cwd. The observed close
used the relative script argument shown above. Only that script token is resolved
against the pinned workspace cwd for comparison with the frozen absolute script
identity; argv is not rewritten. Wrong cwd/script/suffix and drive/root-relative
ambiguous script paths fail. The fresh current source proof is prep-check03;
prep-check01/02 and source revisions remain historical, not current pins.

## Preserved packaging nonpass and fresh plan02

The first packaging attempt used plan01 SHA
7b5bfc881ed27833a844829c1a9eabe4ef677f3b2d6de2ea5201c316f7c3b465.
Its write terminated0 (root session59322/chunk3f975e), manifest
dde6cdeb1bb2804ed176864da734fa36c72b640e2d70c75bc94c8293d8750646.
The advertised standalone verify command then failed terminal1/chunk29b580:
source deduplication had registered verify.py/evidence_rules.py only under raw/,
so the canonical root reader paths were absent. This is a **packaging nonpass**,
not a change to the seven/six production qualification. Root preserved that
archive intact at .build/cyd-static-rx-sdk-write01-packaging-nonpass; the archiver
does not move or repair it in place. The complete old plan and proofs remain.

Current selection registers all seven packager sources with canonical preferred
paths before any report/proof identity traversal and checks those paths again
after traversal. Pure synthetic controls reproduce the prior order defect and
verify canonical standalone reader/rules retention with the corrected order.
Only fresh plan02.json may be created by the revised planner. The same fixed
archive destination must be absent before a separately approved fresh write.

## Future commands, not executed during preparation

```powershell
$python = 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe'
$prep = 'C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/cyd-static-rx-sdk-archive-prep-01'
& $python -B -X utf8 "$prep/check-prep.py" # synthetic prep controls only
# Only after root supplies authoritative close terminal0 plus raw SHA/receipt:
& $python -B -X utf8 "$prep/build_archive.py" --summary-sha256 $rawSummarySha --terminal-receipt $rootReceipt --terminal-receipt-sha256 $rootReceiptSha
# Root reviews fresh plan02.json and authorizes its exact SHA before this separate step:
& $python -B -X utf8 "$prep/build_archive.py" write --plan-sha256 $reviewedPlanSha --write-reviewed-archive
# Root then records actual archive write + offline verification terminal results:
& $python -B -X utf8 'tests/results/cyd-tls-static-rx-sdk-20261020/verify.py' --manifest-sha256 $archiveManifestSha
```

Existing production files, prep directories, markers and reports are inputs only.
All archive output is fresh; failed partial writes are preserved for inspection.
An SDK/compiler/lint/test replay is never an archive repair or fallback path.
