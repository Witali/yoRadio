# Canonical isolated SDK/QEMU archive: preparation only

Proposed new destination: `tests/results/cyd-tls-static-rx-qemu-20261020/`.
No collection, plan, archive write or seal is authorized by this preparation.
Campaign `.build/rxt02`, runner session17556, is currently live. This tooling must
not treat a partial report, a child QEMU exit, a lock file, or accepted canonical
variant as runner completion. The older rxt01 is terminal1/nonpass; it must never be relabelled. Old pointer prototype and host archives stay separate.

## Terminal gate, before reading campaign outputs

Future `build_archive.py` invocation requires all three explicit arguments:
`--report-sha256`, `--terminal-receipt` and `--terminal-receipt-sha256`, plus a
fresh attempt. The receipt must be a separate root-authored file below repository
`.build`, outside `.build/rxt02`, with this exact schema (values illustrative):

```
{"kind":"root_authoritative_runner_terminal","runner_session":17556,
 "runner_terminal_exit":0,"report_path":"C:/.../.build/rxt02/report.json",
 "report_sha256":"<root-provided final raw SHA256>"}
```

This is attributed root observation, not a cryptographic signature. The exact raw
receipt SHA and report SHA must be supplied by root. Report must independently
have `passed=true`, `full_target_matrix_complete=true`, `compile_only=false`,
`all_current_inputs_match=true`, successful runtime status, all12 exact outcomes,
and no error. Root must review tools and separately authorize PLAN ONLY after
terminal evidence exists, then review the plan before any archive write.

## Bounded selected evidence

- Raw final report and every top-level freeze/build/nm/asm/dependency/ninja/merge/
  QEMU/SDK-head/SDK-state log. Complete `input-snapshots`, `sdk-inputs` and any
  source-only top-level `sources` directory, bound to raw report identities.
- All12 independent source manifests, complete `sources` recipes and complete
  execution directories. Every execution bundle, compiled-header-closure receipt,
  actual module/SDK command selection and pre-QEMU artifact reference is bound.
- Every actual compiled dependency source/header/generated config named by each
  bundle, including full19 supporting SDK source/header guards. Original tools
  and ROMs are recorded by actual size/SHA/role and explicitly omitted.
- Per working-build only `config/sdkconfig.h`, `config/sdkconfig.json`,
  `flasher_args.json`, `build.ninja`, `compile_commands.json`,
  `project_description.json`, `CMakeCache.txt`, enabled `native-tls-static-rx/ssl_tls.c`
  and optional `*.map` text. Per campaign `working-sdkconfig` and actual
  `option-disabled.defaults`. Whole working builds, SDK trees, build libraries,
  object files and tool directories are not copied.
- Actual ELF/application/flash component/merged image identities are explicit
  binary omissions. Retain both runtime copied ELF identity and original build
  ELF identity used for nm/disassembly, requiring byte-equal SHA. No duplicate
  firmware binary, ELF, archive, ROM or executable tool bytes are stored.
- New self-contained packager/verifier/spec/templates and synthetic preparation
  checks. No historical drafts or old runtime cohorts are imported, and no
  `.build` historical module is needed at runtime. Frozen preparation recipe
  status in source manifests is kept raw; execution bundle/logs establish runtime.

Raw payloads are content-addressed/deduplicated. Logs and large text use
deterministic gzip, mtime0. Original paths, raw SHA/size, encoded SHA/size and roles
remain in `path-map.json`; JSON references bind in `bindings.json`. Original raw
reports/configs/source/logs are never rewritten. Uniform LF/CRLF comparison is
explicit and never replaces raw stored identity. Whole archive has `-text` attrs.

## Offline replay

Verifier is Python stdlib only. It opens archive bytes only and launches no
SDK/compiler/QEMU/WSL/Git/network/device operation. It never imports/executes
archived runner, freeze or patcher code. Patch replay decodes literal AST constants
only and independently applies all6 unique exact replacements to the complete
pinned SDK source. Source recipes are independently reconstructed from canonical
pre-execution snapshots plus reviewed explicit mutations, including missing init/
free lifecycle hooks and phase-scoped loan/erase controls. Every source is compared.

Exactly200 unique original commands must be terminal0 and not timed out. Check
all12 isolated dual-core no-NIC QEMU invocations and independent actual build
option flags. Original SDK-head logs must equal7101770..., SDK-state logs empty.
All report/input/bundle/header/tool/artifact references must agree with stored
raw bytes or explicit omission identities. Raw compiled config and sdkconfig.h
bindings, source compilation selections, link wraps, options defaults and actual
overlay are checked, including original SDK/module/static-slot absence when off.

Canonical enabled outcomes must contain each unique entry/completion/lifecycle/
both-userdata/full8-soft-registry/actual ISR/two-core marker, actual capacity,
separate real heap-NULL observation, and option-dependent actual reclaim recovery.
Four injected rollback failures stay separately labelled and are not realOOM.
Eight negative controls require exactly their named failure + controlled stop,
no completion, panic, backtrace, timeout or generic crash. Two reserve-off runs
require16 ordinary public SDK setup/reset/free cycles (32 setups) and exact disabled markers. A unique TLS_RX_DISABLED_CAPACITY marker must independently bind content16384, storage>=content, allocated_min>=storage and setups32. Getter expectation is derived from actual configuration: MFL enabled means min(IN,OUT), otherwise IN. No storage-size constant is guessed.

Actual nm/disassembly logs bind allocator/free and lifecycle call routes and
disabled symbol absence. Packaging reads actual ELF32LE/machine94 and extracts
initialized calloc/free function-pointer words and offsets, bound to original
ELF SHA/size/nm addresses. `derived-elf-metadata.json` is conditional derived
metadata: offline verifier can check its identities and consistency against the
retained logs/bundle, but cannot independently reread omitted ELF bytes. Likewise
`derived-flash-metadata.json` records the original4MiB image/component range
comparison; offline verification does not reconstruct omitted flash/components.

Default PLAN ONLY assembles and validates the entire virtual archive using the
reviewed offline verifier before writing preparation plans. Archive write is a
later explicit `--write-reviewed-archive` action; it rechecks inputs and invokes
only the new archive's filesystem-only verifier. Failed attempts remain unchanged.

## Scope limits

This may qualify only the original isolated actual SDK/Xtensa/QEMU fixture cohort
after final authoritative PASS. It is not production audio-service/radio binding,
application/backend firmware profile qualification, physical heap/fragmentation/
playback/benefit measurement, network TLS handshake or protocol conformance, or
default activation approval. No guessed fixed storage/savings number, changed
record/pool/stack/core/timing policy, historical prototype promotion, or deferred
codec qualification is allowed. Source execution Git cleanliness is not inferred
from later commits; any root source commit note is separate provenance.

## Bounded nonpass history, only after the new final gate

After rxt02 authoritative terminal0/full12 validation and authorized PLAN, preserve
only four older raw payloads: rxt01 report
`344bdd390454d08a50822bb9283b1efefe2075d274cca728609e69d66b9d4180`,
rejected reserve-off/reclaim-on QEMU log
`7e73ae96d311b14ae6652d37c4e62d0de36e6d1da7aea1ac224188cd368e057e`,
corrected root nonpass receipt
`e36a0a15ce2529677451ea448f7f10566c102c075501a1584f04914606797aea`,
and the original disabled.c input snapshot whose complete raw SHA is resolved
from that exact old report (root reference prefix567c8da4). No old source or
SDK/tool path is imported at runtime. The old source is not the corrected source.

Replay only old nonpass report shape and rejected log:10 recorded accepted
outcomes, eleventh child terminal0 with exact
`disabled_original_full_record_payload` failure+controlled stop and no panic,
twelfth build/runtime unrun. Parent terminal1 remains attributed to root's exact
corrected receipt. No other old successful outcomes, binary/header/tool/bundle/log
references are requalified or reconstructed; they remain uninterpreted metadata
in the raw old report. The new full gate stays separate. No old history is read
or collected while preparing these tools or before new terminal/full validation.
