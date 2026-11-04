# Prepared final CYD production and donor regression campaign

Preparation only. No campaign phase, worktree, SDK/configure/build/lint/WSL test,
download, compression, device operation, commit or publication has been launched.
The read-only sparse-size helper is the only prepared helper run so far.
Root owns the release decision and the active native04 session 83610.

## Release gate

Copy `release.example.json` to a new local `release.json` only after review.
Fill the exact 40-character FINAL_COMMIT, source-release/campaign identities,
baseline task-profile commit, final committed evidence files, explicit older
C3 host baseline report and reviewed SHA-256 of `campaign.py`,
`invoke-build.ps1` and this README. Set `released: true` only after root releases
the final source. Current branch HEAD and documentation commits are never
selected automatically. All inputs must already be local.

`ordinary_flac_watchdog_evidence_files` is an explicit optional input for the
future ordinary FLAC production-watchdog successor. If supplied, every named
file is retained, frozen and included in all six export receipts. Empty means
that evidence is absent; it is not inferred from native03 or another NONPASS.
The controller's diagnostic history retains its original outcomes.

The first isolated task defaults to its own branch
`codex/cyd-ogg-production-20261101` at
`C:/Work/yoRadio/.worktree/cyd-ogg-production-20261101`. A corrected release
uses a fresh campaign ID plus a new bounded date/suffix, for example
`.../.worktree/cyd-ogg-production-20261101-r2` and the matching
`codex/cyd-ogg-production-20261101-r2` branch. The driver requires a new worktree,
branch and phase directories, and never deletes or reuses earlier captures.
Every phase requires the
released request and exact reviewed recipe. No AllowDirty, setup, install,
fetch, source workaround or automatic retry is available.

## Sparse checkout and measured disk budget

Use standard non-cone Git sparse checkout, retaining every current source,
tool and live test path, excluding only old firmware and historical result
packages, and reincluding every explicitly released evidence package:

```text
/*
!/tests/results/*
!/firmware/*
/tests/results/<each exact released capture>/
```

The create phase uses `git worktree add --no-checkout -b <own branch> <path>
<FINAL_COMMIT>`, then `git sparse-checkout set --no-cone --stdin`, then checkout.
GIT_LFS_SKIP_SMUDGE=1 prevents network hydration. Required actual build/test/
evidence inputs cannot be substituted with LFS pointers: any required missing
local object must be resolved through an explicitly reviewed offline checkout,
not a download. No mutable source hardlinks are used. Git's standard
extensions.worktreeConfig is already enabled; preparation changed no config.

Read-only actual `git sparse-checkout check-rules` matched the proposed rules at
observed commit `7d1df0ec2a3c668931187c0b0a23edb7ac45b02d`:

| Scope | Files | Git blob bytes | Estimated 4 KiB allocation |
|---|---:|---:|---:|
| Full tracked tree | 110,597 | 2,922,286,822 | 3,207,528,448 |
| All source/tests plus mapped-output and TLS evidence | 7,290 | 127,546,781 | 144,441,344 |

`sparse-size.json` and `retained-git-paths.json` bind this measurement. A separate
read-only stat of all 7,290 selected files in the current source worktree found
zero missing files, 132,768,458 actual raw bytes and 149,639,168 bytes rounded to
4 KiB. This distinguishes actual CRLF/hydrated file sizes from Git blob sizes;
it is an observation of the current checkout, not a released final source.
The
released full-task/optional FLAC package adds its actual size. Git blob size is
not a hydrated-LFS estimate. The create phase recomputes rules, sizes and free
space at FINAL_COMMIT before creating the worktree.

Operational **minimum free-space estimate: 5 GiB with this sparse checkout**;
the previous full-checkout estimate is 8 GiB. The executable budget includes
six retained GCC trees at 256 MiB each (measured earlier full build 176,250,044 B),
six Clang configurations at 96 MiB each, two C3 configurations/objects at 256 MiB
each, host fixtures 128 MiB, deduplicated raw input snapshots 512 MiB,
logs/reports 256 MiB, six handoffs 64 MiB and operational reserve 1 GiB, plus the
new checkout's rounded file sizes. It rounds the total upward to whole GiB.
These are conservative planning allocations, not a guarantee against concurrent
disk usage. Each phase records free space and stops below the1 GiB reserve.
Root manages storage; this campaign never deletes, compresses or cleans builds.

The canonical exporter is sparse-compatible: its source_snapshot uses Git's
complete index/blob identity for unchanged clean paths, without requiring
historical payloads to be materialized. Source cleanliness uses Git's clean
filters, not raw SHA-1 comparisons. CRLF-normalized baseline task/board assertions
are separate from the exact raw SHA-256 snapshots of compiler-consumed inputs.

## Canonical GCC route and process evidence

All six rows invoke the unchanged `build-production.ps1` end-to-end. That script
invokes export_cyd_production.py build mode and the unchanged build.ps1; all
canonical clean-source, isolated-config, GCC, original profile, SNTP, image,
ELF, SDK, partition/OTA and immediate handoff checks remain in force.

`invoke-build.ps1` only loads a typed JSON invocation and splats its arguments
into the canonical script. This preserves Evidence/IdfArguments arrays, literal
quotes and backslashes. It does not proxy Start-Process or monkeypatch Python.
Before SDK phases, `wrapper-test` runs actual host array/quote and throw/exit
propagation controls, then the unchanged `tests/run-cyd-production-wrapper.py`.
No old assertion or golden is changed. These controls are prepared, not run.

The campaign owns and records each real root child PID, original argv, start/
terminal times, exact stdout/stderr and exit status. Canonical builder source
retains its actual Wait/PassThru/ExitCode propagation. Original compiler logs
and their exported copies are authenticated against each other and the receipt.
Nested SDK PIDs and kernel start/stop events are **not independently observed**;
this limitation is explicit and no descendant status is fabricated. Optional
future read-only telemetry must be host-qualified and remain supplementary,
not a new prerequisite for valid canonical builds.

No observation timeout causes a restart or kill. Every phase directory is
create-once, including failures. Inspect the original owned handle when a UI
poll times out. Coordinate the SDK slot with root; do not overlap native04.

## Exact six export profiles

The canonical calls are below, expressed with `$W` equal to the new worktree,
`$D=C:/Work/yoRadio/.idf` and `$E` the exact released evidence array. The driver
uses typed JSON splatting to preserve that array. Every isolated config starts
fresh from the appropriate current CYD defaults/backend overlay, with only its
FLAC choice and explicit default-OFF memory/diagnostic selectors seeded.

```powershell
& "$W/idf/esp32-cyd2usb-native/build-production.ps1" -DependencyRoot $D -AudioBackend pdm -BuildDirectory "$W/idf/esp32-cyd2usb-native/build-ogg-final-gcc-vendor-pdm" -Sdkconfig "$W/idf/esp32-cyd2usb-native/build-ogg-final-gcc-vendor-pdm/sdkconfig" -Variant esp32-cyd2usb-native-ogg-final-vendor-pdm -Evidence $E
& "$W/idf/esp32-cyd2usb-native/build-production.ps1" -DependencyRoot $D -AudioBackend continuous -BuildDirectory "$W/idf/esp32-cyd2usb-native/build-ogg-final-gcc-vendor-continuous" -Sdkconfig "$W/idf/esp32-cyd2usb-native/build-ogg-final-gcc-vendor-continuous/sdkconfig" -Variant esp32-cyd2usb-native-ogg-final-vendor-continuous -Evidence $E
& "$W/idf/esp32-cyd2usb-native/build-production.ps1" -DependencyRoot $D -AudioBackend legacy -BuildDirectory "$W/idf/esp32-cyd2usb-native/build-ogg-final-gcc-vendor-legacy" -Sdkconfig "$W/idf/esp32-cyd2usb-native/build-ogg-final-gcc-vendor-legacy/sdkconfig" -Variant esp32-cyd2usb-native-ogg-final-vendor-legacy -Evidence $E
& "$W/idf/esp32-cyd2usb-native/build-production.ps1" -DependencyRoot $D -AudioBackend pdm -BuildDirectory "$W/idf/esp32-cyd2usb-native/build-ogg-final-gcc-custom-flac-pdm" -Sdkconfig "$W/idf/esp32-cyd2usb-native/build-ogg-final-gcc-custom-flac-pdm/sdkconfig" -Variant esp32-cyd2usb-native-ogg-final-custom-flac-pdm -Evidence $E
& "$W/idf/esp32-cyd2usb-native/build-production.ps1" -DependencyRoot $D -AudioBackend continuous -BuildDirectory "$W/idf/esp32-cyd2usb-native/build-ogg-final-gcc-custom-flac-continuous" -Sdkconfig "$W/idf/esp32-cyd2usb-native/build-ogg-final-gcc-custom-flac-continuous/sdkconfig" -Variant esp32-cyd2usb-native-ogg-final-custom-flac-continuous -Evidence $E
& "$W/idf/esp32-cyd2usb-native/build-production.ps1" -DependencyRoot $D -AudioBackend legacy -BuildDirectory "$W/idf/esp32-cyd2usb-native/build-ogg-final-gcc-custom-flac-legacy" -Sdkconfig "$W/idf/esp32-cyd2usb-native/build-ogg-final-gcc-custom-flac-legacy/sdkconfig" -Variant esp32-cyd2usb-native-ogg-final-custom-flac-legacy -Evidence $E
```

Every successful qualified app is immediately retained at
`$W/firmware/development/<literal Variant>/app.bin`, alongside the canonical
config/partition/flash/log/manifest handoff. Existing releases are never touched.
The driver re-qualifies the actual build against its saved receipt, preserves
ELF/map/compile database, and verifies linked custom_flac_decoder_feed versus
esp_flac_dec_register. All three optional TLS memory helpers and diagnostics
must be OFF; hardware MPI/AES/SHA, RX 16384/TX 4096, dual 240 MHz, QIO 80 MHz/4 MiB,
GPIO/TFT/stack header and original task core/priority/stack profiles remain.
OTA remains app0 at 0x10000/app1 at 0x1C0000, both 0x1B0000 B. Resource totals are
actual ELF/image observations with no physical heap or performance attribution.

## Matching six real Clang profiles

For each of vendor-pdm, vendor-continuous, vendor-legacy, custom-flac-pdm,
custom-flac-continuous and custom-flac-legacy, `clang-configure --row <row>`
copies only that row's final GCC sdkconfig into fresh
`build-ogg-final-clang-<row>/sdkconfig`, then uses unchanged build.ps1 with
IdfArguments `-D IDF_TOOLCHAIN=clang reconfigure` and its matching backend.
It replaces the cached toolchain string and derived libc selections with
Clang/Newlib/nano. Production GCC remains Picolibc and is never rewritten.

The entire newly generated typed JSON delta, including absent versus false,
is saved. No historical14/13 count is a gate. Root must supply a separate file:

```json
{"approved":true,"source_commit":"<FINAL_COMMIT>","delta_sha256":"<actual typed-config-delta.json SHA256>","reason":"Review of every actual compiler/libc transition"}
```

`clang-check --row <row> --delta-approval <file>` authenticates that exact delta
and actual configs/database, discovers and freezes consumed source/header/
response-file bytes, then runs the existing full lint command:

```powershell
& "$D/python-3.12.10/tools/python.exe" -B -X utf8 "$W/tools/run_native_lint.py" --build-dir "$W/idf/esp32-cyd2usb-native/build-ogg-final-clang-<row>" --clang-tidy "$D/tools-v6.0.2/tools/esp-clang/esp-20.1.1_20250829/esp-clang/bin/clang-tidy.exe" --output "<fresh row evidence>/full-lint" --jobs 2 --include-httpd-overlay
```

Coverage is derived from the actual compile database, not a remembered count.
Both patched HTTPD units are included. Additional exact-row frontend checks
cover generated native-http-request-buffer/esp_http_client.c, the actual SDK
esp_tls_mbedtls.c with its EOF compile-definition redirect, unmodified SDK
ssl_tls.c for the OFF RX profile, and the borrowed 5.5.4 i2s_legacy.c for legacy.
Dependencies are discovered before analysis and rehashed afterward. GCC uses
actual valid Ninja consumed dependencies and actual object identities for the
complete production compile database. Raw source/header snapshots use a single
content-addressed local byte store, not repeated large source-tree copies.

## Own-SDK C3 regression

C3 remains pinned to its own 6.1 commit 9a97f6c54ec638111ce55cd36581b3c192f15207,
RISC-V GCC 15.2, own esp-clang 21.1.3_20260408, single 160 MHz, own defaults,
OLED/audio pins and ESP32-C3 vendor archives. No CYD board/backend option is
ported. Direct-DMA target activation remains OFF; its old unsupported guard is
not loosened. CYD remains SDK 6.0.2 commit 7101770dc6db2667b3c477cc31365dd1acd6db4e,
Xtensa GCC 15.2 and esp-clang 20.1.1_20250829. Tool/archive identities are frozen.

`c3-gcc` does one fresh own-SDK configure, selects the exact three new database
rows for shared AudioNormalizer.cpp, C3 native_audio_normalizer.cpp and selected
native_audio_output.c, then compiles only their actual Ninja output targets.
`c3-clang-configure` and `c3-clang-check` perform one own-SDK complete project
lint and SDK frontend closure, with their own full typed-delta approval.
`c3-host` runs the unchanged run_output_dma_host.py --profile ASan/UBSan/leak,
staged/DMA/profile/chunk regressions and compares exact legacy variants and
normalizer result to the explicitly supplied pre-change baseline. It records
actual host compiler/internal compiler/sanitizer library identities. This is
host seam/legacy behavior evidence, not physical DMA or codec conformance.

## Reviewed launch order, not executed

Use pinned bootstrap Python for each separate phase; do not run an aggregate
background script. `$R` is the explicit released JSON and `$P` this directory.

```powershell
& "$D/python-3.12.10/tools/python.exe" -B "$P/campaign.py" create --release $R
& "$D/python-3.12.10/tools/python.exe" -B "$P/campaign.py" freeze --release $R
& "$D/python-3.12.10/tools/python.exe" -B "$P/campaign.py" wrapper-test --release $R
# For each of the six literal rows above, one owned native child at a time:
& "$D/python-3.12.10/tools/python.exe" -B "$P/campaign.py" gcc --release $R --row vendor-pdm
& "$D/python-3.12.10/tools/python.exe" -B "$P/campaign.py" clang-configure --release $R --row vendor-pdm
# Review the actual full typed config delta, then:
& "$D/python-3.12.10/tools/python.exe" -B "$P/campaign.py" clang-check --release $R --row vendor-pdm --delta-approval <exact-row-approval.json>
# Repeat the three row phases for the other five rows. Then the donor:
& "$D/python-3.12.10/tools/python.exe" -B "$P/campaign.py" c3-gcc --release $R
& "$D/python-3.12.10/tools/python.exe" -B "$P/campaign.py" c3-clang-configure --release $R
& "$D/python-3.12.10/tools/python.exe" -B "$P/campaign.py" c3-clang-check --release $R --delta-approval <exact-c3-approval.json>
& "$D/python-3.12.10/tools/python.exe" -B "$P/campaign.py" c3-host --release $R
& "$D/python-3.12.10/tools/python.exe" -B "$P/campaign.py" warning-catalog --release $R
# Root reviews every exact warning with a reason/reference, then:
& "$D/python-3.12.10/tools/python.exe" -B "$P/campaign.py" finalize --release $R --triage <exact-triage.json>
```

SDK/WSL launches must use normal reviewed escalation in this Windows workspace;
do not repeat the known un-escalated DLL623 probe or install a workaround.

Warning triage binds warnings.json SHA-256, FINAL_COMMIT and one item per exact
warning ID with disposition accepted-existing/accepted-scoped, concrete reason
and reference. Dangerous issues require a corrected committed source and a new
campaign, not a waiver. Parser/tool errors, incomplete coverage or changed raw
inputs fail. Finalize recomputes the warning corpus and rechecks every original
log, frozen input, configuration and firmware artifact. A complete run with
reviewed warnings is not a warning-free-code claim.

All raw binaries, ELF/PCM, tool payloads and unreviewed or contact-bearing logs
remain local. No stage/push/upload operation exists in this runner. Raw privacy
inspection of exact outgoing bytes/history/refs is still mandatory before any
later publication; flagged whole payloads stay local with hash/size omissions.
No diagnostic CA/key/certificate bundle/image seeds the production matrix.
