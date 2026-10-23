# Owned-book unit runtime: source-only proposal

This is a fresh successor to `cyd-vorbis-owned-book-unit-prep-01` and the frozen
source-only `cyd-vorbis-owned-book-runtime-prep-01` and `-02`. Nothing in
this directory has been compiled, linked, run in QEMU or executed as a unit,
test, decoder or reference. The preparation performs only source copying,
AST parsing, raw-byte hashes and source diffs. Root owns review and execution.
There is no successful runtime result, fabricated PID or assumed terminal0.

The original unit proposal is retained at `unit-source/`. `source-origins.json`
binds each original byte copy, including the SDK launcher/controller and the
unchanged Windows macro helper from `cyd-vorbis-format-expanded25-prep-02`.
`predecessor/` contains that reviewed launcher's/controller's source history.
`project-revision.diff`, `launcher-revision.diff` and `controller-revision.diff`
make the adaptation explicit. A controller rewrite is intentionally not a
claim that its new runtime gates have already executed successfully.

## Exact source and unit scope

Production setup SHA256 remains
`6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c`.
Production ABI SHA256 remains
`e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60`.
`book_unit.c`, `unit_data.h`, `protocol.py`, every public declaration header
and the fixture contract remain byte-identical to the original unit proposal.
The existing `app_main` flushes COMPLETE and returns into SDK idle; it does
not reset or pretend to terminate the emulator.

Runtime-only project changes are `-fno-inline` to retain the static parser
symbol for actual nm verification, an explicit DIO/40MHz/4MB flash profile,
the fixed partition table and the isolated SDK launcher. No production source,
consumer seam, fixture expectation or production configuration is changed.
There are no codec component paths, imported archives, vendor stubs, decoder
implementations, opaque handles or radio application dependencies.

The source protocol retains exactly16 named vector books,59 active codewords,
61 probes including both consumed single-entry bits,97 events and2 wide pairs.
See `PROVENANCE.md` and `unit-source/README.md` for the bounded public Tremor
consumer seam and vector-only claim. A future passing unit would establish
our exact parser publication plus that explicit public consumer. It would
not qualify the vendor backend, wide PCM, floor0, full G6, physical behavior
or production radio integration. The existing25-case numeric NONPASS and
bound2 are unaffected.

## Reviewable future command

From this worktree, use the root-owned SDK Python and a new campaign path:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 `
  '.build/cyd-vorbis-owned-book-runtime-prep-03/run-owned-book-unit.py' `
  --output '.build/cyd-vorbis-owned-book-unit-capture-02' `
  --readiness-sha256 '<independently reviewed readiness.json SHA256>' `
  --qemu 'C:/Work/QEMU-ESP32/bin/qemu-system-xtensa.exe' `
  --powershell 'C:/Users/rudol/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
```

The placeholder must be replaced with the reviewed raw hash. The controller
requires the complete manifest file set and pins its immutable code, fixtures,
helper and public runtime identities. It rejects existing output directories,
overlaps with source/runtime paths and a campaign nested under prior results.
It snapshots all inputs before any SDK action and rechecks those exact bytes.
It never edits canonical files, the old preparation, previous campaigns or Git.

The pinned SDK6.0.2 HEAD is
`7101770dc6db2667b3c477cc31365dd1acd6db4e`. Configuration and build run as
separate owned hidden PowerShell/SDK child processes. Both retain actual argv,
cwd, PID, logs and terminal receipts; the launcher has no codec parameter and
removes inherited application component variables. No SDK command contacts a
board or uses a COM port. Component-manager downloads are disabled.

Revision02 fixes a source-review finding before any runtime execution: the
outer PowerShell command now uses `sdk-configure-launcher.stdout/stderr.log`
and `sdk-build-launcher.stdout/stderr.log`. The actual Python SDK child keeps
`sdk-configure.stdout/stderr.log` and `sdk-build.stdout/stderr.log`, with its
separate `sdk-<action>-process.json` actual PID/argv/terminal receipt. Thus the
outer capture and child no longer attempt `CreateNew` on the same path.
`revision02.diff` records the one-line controller change; original01 receipts
are preserved under `history01/`, and runtime01 itself remains unchanged.

Revision03 follows root's actual capture01 NONPASS before compilation/QEMU:
the legal GCC dependency output repeated five SDK headers (109 rows,
104 unique paths), while revision02 incorrectly required unique spellings.
`revision03.diff` removes only that uniqueness condition. Every original row
is preserved in order, every path remains bounded and hashed, and the entire
raw GCC output must still match after the build. Repeated paths reuse the
same frozen identity; the controller neither deduplicates nor loses rows.
Source-only02 receipts are under `history02/`. Runtime02 and failed capture01
remain unchanged. This preparation has not executed any SDK/compiler/QEMU
or unit test; actual capture01 belongs solely to root's retained evidence.

Between configure and build, the controller binds the actual direct compiler
row for the single unit TU. It uses the unchanged reviewed Windows quoting and
generated six-line `@cflags`/picolibc helper. It executes and retains actual
macro and GCC `-M` dependency probes, including the included production setup,
ABI, fixture header and all four public codec declaration headers. Every
dependency is scoped, copied and hashed before compilation, with matching
macro/dependency output required after build. Configured sdkconfig, config
header, compilation database, description, CMake cache and Ninja graph are
also frozen before build. Declared tool and esptool source hashes are checked
before and after. This is a declared-input record, not a hermetic operating
system or toolchain supply-chain proof.

The actual macro gates require ILP32, little-endian Xtensa ESP32,240MHz,
two cores, absent `CONFIG_FREERTOS_UNICORE`, main affinity CPU0 and16384-byte
main stack. Here SMP means the normal IDF dual-core kernel; this preparation
does not select the separate experimental Amazon `CONFIG_FREERTOS_SMP` kernel.
Both kernels are SMP-capable in this SDK's retained FreeRTOS Kconfig.

After build, actual ELF32/machine94, nm, map, generated Ninja commands and
verbose actual compile/link logs must agree. The static real parser/clear
symbols and app_main must exist. Vendor decoder/register/wrapper symbols and
vendor codec archive/component linkage must be absent. The exact whole setup
TU has unreachable wrappers; section GC must genuinely remove them. A link
failure stays NONPASS; no vendor stub/archive may be added to make it pass.
The flash recipe must contain only bootloader0x1000, partition0x8000 and app
0x10000 with DIO/40MHz/4MB. A padded local4MB image is used only for QEMU.

## Actual terminal closure, never COMPLETE alone

`owned_qmp.py` owns one newly created QEMU process. QEMU runs with no NIC,
no audio backend, no display, no monitor, snapshot flash and no reboot.
Serial is a scoped `qemu.serial.log` file. QMP is **only stdio pipes created
by this controller**, with no listener/socket, external session or user device.
The only transmitted commands are `qmp_capabilities` and `quit` with unique IDs.

Raw actual JSON stdout, actual sent requests, actual greeting, acknowledgements
and events are retained. The controller first requires the real greeting and
capabilities acknowledgement. It then observes COMPLETE in the serial file,
sends its own quit, waits for the real quit acknowledgement, exact non-guest
`host-qmp-quit` SHUTDOWN event, pipe EOF and its own process's terminal exit0.
Only after those gates may `protocol.validate_log` examine the complete actual
serial/stderr log and require all16/61/97 exact records. No synthetic log,
assumed exit code, precomputed greeting, retry or shortened corpus is accepted.

An explicit failure/panic/reset may be stopped with the same owned quit for
diagnostics. It remains NONPASS even if shutdown is clean. Timeout,
interruption, forced cleanup, nonzero exit, early process exit, partial log,
missing QMP acknowledgement/event/EOF or COMPLETE alone cannot pass. Emergency
tree cleanup addresses only the actual Popen-created PID, is recorded and
unconditionally prevents qualification. Root must inspect real logs and
resolve any runtime/source defect in a fresh successor without rewriting a
failed campaign.

No actual terminal or unit evidence exists in this source-only preparation.

