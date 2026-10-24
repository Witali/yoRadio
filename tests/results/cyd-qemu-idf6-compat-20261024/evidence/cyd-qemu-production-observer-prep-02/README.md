# Production PDM observer02: source-only preparation

This standalone source revision has not been executed or imported. It adapts
the exact frozen trace observer01 into an owned-stdio observer for one separately
pinned, task-local rebuilt QEMU executable. The predecessor and its
DIAGNOSTIC_INCOMPLETE capture remain unchanged. No SDK/build/test/guest process,
Git command or physical device was started by this preparation, and no external
QEMU/SDK or production source was edited.

The parent root owns execution after source review. `readiness.json` records
the preparation's raw file identities; `provenance.json` identifies the exact
two source origins and old pins. `capture-vs-01.diff` is a complete unified
replacement diff from the original trace observer to this new standalone
source. Copies in `origins/` are record-only snapshots, never imported or
called. The new observer uses only ordinary Python standard-library imports;
it does not load a predecessor module, replace functions or rebind globals.

## Fixed input scope

- Original PDM application/source3a563324abdca56144a40d5759def0ccfe708b3c,
  app SHA66e99cfb4773bad31cd646ec22e0cdda5d1231bf9b3ea74a6940401aea98ecf3.
- Original inventory SHA
  f9cf237bbbefe7967abbb558b06beb1ed4617035769669bb770223ad01bf5b12.
- Original bootloader/partitions/OTA/SPIFFS/app bytes and exact original offsets
  in a new four-MiB scratch medium, with erased emulated NVS. No header patch,
  alternate flash mode, flash-chip substitution, SDK/config change or rebuild.
- Original ROMs and QIO80MHz/CPU240MHz/two-core configuration. The separate
  upstream CONFIG_FREERTOS_SMP option is not enabled; original config bytes
  remain authoritative.
- Original executable is still checked against its old pin, in addition to
  the new executable's separately supplied SHA256. New executable path is
  restricted to this worktree's
  `.build/cyd-qemu-rebuild-20261024-01/qemu-system-xtensa.exe`.
- All original tools, selected profile files and eighteen source-evidence rows,
  pins file, actual new executable, actual observer and the two source origins
  are checked before and after. No old input is replaced by a current fallback.

Root must supply the actual completed rebuild's SHA256. This preparation does
not invent it or assert that the build succeeded. It does not install anything
over the original emulator in `bin/`.

## Observation and lifecycle

The hidden owned child uses QMP stdin/stdout pipes, emulated UART in uart.log,
stderr in qemu-stderr.log and existing trace events in flash-trace.log. There
is no socket, host listener, NIC backend or host audio backend. Flags retain
`-S`, `-snapshot`, `-nic none`, `-audiodev none`, headless display and
`-no-reboot`. Only fresh direct children of the worktree .build directory may
be used as outputs.

The raw QMP reader uses `os.read` on the child stdout pipe, not a buffered
fixed-length read that could wait for a full buffer before delivering the
greeting. It saves raw bytes, parses complete dictionary frames and requires a
real b'' read and reader join. Parse/read errors, an incomplete final JSON
frame, forced stdout closure or missing EOF cannot yield completion.

After greeting/capabilities, a unique UUID guest name is checked before VM or
trace mutations. The six original existing events are checked disabled,
enabled individually, checked enabled and all other m25p80 events checked
disabled before `cont`. Completion requires actual named command/transfer
records, QEMU exit0 and one exact SHUTDOWN: guest-reset/guest=true for natural
termination, or host-qmp-quit/guest=false after an acknowledged root quit.

Observation lasts up to20 seconds after `cont`. A panic gets up to3 seconds
for natural guest reset within that observation window; otherwise the owner
requests QMP quit. Without panic, the owner requests quit at the20-second
deadline. No repeated guest is launched. The controller checks UART, stderr,
trace and raw QMP output sizes against32MiB during activity and at closure.
Polling is a soft stop bound; a terminal overshoot is rejected and recorded,
not represented as a successful hard-capped capture.

## Meaning of the result

OBSERVATION_COMPLETED means that the bounded controller, input closure,
artifacts and process/QMP lifecycle completed. It does not require successful
startup and does not turn a panic into boot success. The historical five
startup marker predicates are retained verbatim in meaning, using the original
I2S PDM backend string; panic, startup errors, network failure, old QIE failure
and old flash assertion are reported separately.

Full radio/startup, physical, audio output, network traffic/association,
static-RX loan and reserve performance qualification remain false. An observed
MPI return or pipeline marker is a bounded observation with its original
meaning, not a performance or physical acceptance claim. No codec input,
traffic generator, codec integration, deferred codec scope, hardware/COM or
production flash operation is part of this controller.

## Root-owned CLI, not executed here

Use the actual new executable SHA256 in place of NEW_SHA256:

    python -B -X utf8 .build/cyd-qemu-production-observer-prep-02/capture.py \
      --pins tests/results/cyd-production-radio-boot-20261020/preparation/inputs.json \
      --pins-sha256 f9cf237bbbefe7967abbb558b06beb1ed4617035769669bb770223ad01bf5b12 \
      --qemu .build/cyd-qemu-rebuild-20261024-01/qemu-system-xtensa.exe \
      --qemu-sha256 NEW_SHA256 \
      --output .build/cyd-qemu-production-observation-20261024-02

The root executor should record the actual argv, outer terminal and logs,
and allow enough host time for preflight, the20-second guest window and bounded
cleanup. Neither this command example nor source review constitutes execution.
