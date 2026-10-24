# Actual GD25Q32 trace and stale-build analysis

Date: 2026-10-24. Read-only analysis of the already finished capture01. The
reviewer did not execute QEMU, SDK/build/test tools, Git, source runners or
physical devices and did not edit external QEMU/SDK or production firmware.
Only this new ignored note/extract directory was written.

## Capture status remains DIAGNOSTIC_INCOMPLETE

The unchanged report records controller failure at `Actual QMP EOF and reader
join`, actual QEMU exit0, and unchanged original inputs. Raw QMP contains the
owned UUID name, six enabled trace events before `cont`, and one complete
SHUTDOWN event with `guest=true, reason=guest-reset`. This does not substitute
for the failed strict reader-EOF/join gate. Do not relabel the capture PASS.
The UART reproduces the QIE error and SDK `init_flash:654` assertion before
application startup. No radio, network, audio, static-reserve performance or
physical qualification follows from it.

The retained trace is nevertheless a directly observed diagnostic artifact:
24015 bytes, SHA256
`e8149ab9ba699910f587f983f13cf454f3f514d013a5d424ea471c755237b281`.
The reviewer projected its actual lines without running the observer again.

## Independent CS-bounded observations

There are334 lines and48 closed segments:47 have both opening select and
closing deselect, while the initial partial segment begins after tracing was
enabled and is not used as a complete transaction. Every selected transaction
below has both boundaries. All refer to the same flash identity
`000002bac987eea0`.

| Original line ranges | Command and following wire bytes | Observed parser states / returned data |
| --- | --- | --- |
|21-30,253-262,275-284,285-294|`9f ff ff ff`|The three response clocks enter state5 and return `c8 40 16`, identifying GD25Q32.|
|55-60,73-78,95-100,153-158,295-300,329-334|`35 ff`|Both bytes enter state0. Both are decoded as new commands35 andff; no read-data event occurs inside the transaction.|
|83-88,317-322|`31 02`|Both bytes enter state0. Both are decoded as new commands31 and02; the payload is parsed as a page-program command, rather than status data.|

`status-transactions.json` preserves the twelve complete selected transactions
with original line numbers, raw text, transfer states, commands and returned
bytes. `sr2-write-context.txt` additionally retains the neighboring WREN and
status context. In the second write phase, preceding RDSR0x05 explicitly
returns0x02 (WEL set). There is no CS deassertion between the0x35 command and
its response clock or between0x31 and its data byte.

The observed failure is more specific than a QE bit failing to stick: for this
installed executable, the GD SR2 operations do not enter their required data
states at all. It is therefore not justified to repair the production firmware,
alter its mode/header, or blame its QIO initialization sequence on this basis.

## Contrast with current local source

Current `C:/Work/QEMU-ESP32/hw/block/m25p80.c`, raw SHA256
`6eecf0409bfc52ba9df31234144e4fa63af15122d0682a355e5350942585f99b`,
contains the relevant support unconditionally:

- `get_man` lines559-560 maps JEDEC manufacturer0xc8 to MAN_GIGADEVICE.
- WRSR2 decoding at1377-1383 assigns `needed_bytes=1`,
  `STATE_COLLECTING_DATA` and position0 to GD/Winbond.
- WRSR2 completion at841-846 takes data bit1 as QE and clears WEL.
- SR2 read decoding at1558-1564 sets one reply byte containing QE bit1,
  position0 and `STATE_READING_DATA` for GD/Winbond.

Given the captured correct JEDEC ID, the current source predicts state5 for
the read clock and state3 for the write payload, contradicting the observed
state0 behavior. It cannot be assumed that the installed binary contains this
source's effective GD handler. The trace is consistent with a build that
recognizes the GD part but classifies it as a generic/unsupported manufacturer
for the SR2 switches. It does not identify which exact compiled instruction or
historical source revision is responsible; no binary disassembly was done.

## Build provenance observed before the parent's separate rebuild

The reviewer recorded these actual facts in tool chunk85513c before root
started its separate build. `inputs.json` retains them as historical
observations; live build outputs were not rehashed later and presented as the
old build.

| File | Bytes | SHA256 | Observed last-write UTC |
| --- | ---: | --- | --- |
|`build/qemu-system-xtensa.exe`|72397203|`f6a5f29315d1bea5c99b74890a99c86c70886fdc0d50f24f62c24cdda43abc35`|2026-10-14T11:23:26.2863292Z|
|`bin/qemu-system-xtensa.exe`|72397203|same hash|same timestamp|
|`build/libcommon.a.p/hw_block_m25p80.c.obj`|135183|`13f71d1d77a4d3d17d37c451136673b636de92ace5f6f4264b698c9319ddc5a2`|2026-10-14T11:21:45.9855773Z|
|`hw/block/m25p80.c`|63472|`6eecf0409bfc52ba9df31234144e4fa63af15122d0682a355e5350942585f99b`|2026-10-14T13:41:41.5075524Z|

Thus both existing executable copies are identical, and the source's observed
timestamp is later than the object and executable. Timestamps alone are weak
provenance, but this ordering and the contradictory actual state transitions
together strongly support an outdated executable/object rather than a need
for an additional GD source patch.

The existing marker `bin/.qemu-esp32-commit` contains
`bca9cac8ef8d13d5af50e438d07a6a4c343f9c39`. It is not a source-content or
binary-content proof. `setup-qemu-esp32-windows.ps1` checks only Git HEAD against
this marker when deciding whether to reuse the executable; it does not check
working-tree source hashes. `-SkipBuild` skips compilation and copies the
existing build executable, so it is not a forced rebuild option. This analysis
does not assert that the cache branch caused the old build.

Root separately reports a clean QEMU source checkout at
`2a593f8d00c9be312ddc6e600dbb778f0e6459eb` and has begun a recorded direct
offline Ninja build. The reviewer did not run or independently repeat those
Git/build operations. Root's immutable `before-build.json` is retained by
reference and raw SHA256 in this audit's inputs; build outcome is not inferred
from the announcement or a live session.

## Minimal correction and existing build route

The smallest supported candidate is to rebuild the already present GD source
support into a separately identified emulator executable. No additional source
patch is presently indicated. Preserve the old installed binary and every
production component/configuration byte; test the candidate executable from a
new task-local path and record its new hash. Do not install it over `bin` or
rewrite the old capture. If the rebuilt executable still lacks the expected
state transitions, retain that new result and investigate the build/model
selection instead of adding a firmware workaround.

The existing setup script's compile route is MSYS2 MINGW64 with
`PATH=/mingw64/bin:/usr/bin`, repository `/c/Work/QEMU-ESP32`, and target
`ninja -C build qemu-system-xtensa.exe`. Existing build configuration targets
xtensa-softmmu and enables gcrypt/pixman/SDL/slirp, static linking and the
DosToEsp package name. `build/compile_commands.json` explicitly names
`../hw/block/m25p80.c` as input for `libcommon.a.p/hw_block_m25p80.c.obj`.
The configured compiler metadata says GCC16.1.0; that is recorded build
metadata, not a freshly executed compiler-version check.

The following tool files were found and raw-hashed without execution:

- `C:/Work/HLV-codec/local_tools/msys2/msys64/usr/bin/bash.exe`;
- `.../mingw64/bin/cc.exe` and `gcc.exe` (identical raw hashes);
- `.../mingw64/bin/ninja.exe` and `pkg-config.exe`;
- build Python and `meson.exe` exist under `C:/Work/QEMU-ESP32/build/pyvenv/bin`.

No package installation is established as necessary from this inspection. Root
must use the actual recorded build terminal and output identity to establish a
new executable; an existing target, dry-run or source timestamp cannot do so.
The subsequent QMP observer should use owned stdio with an actual EOF/join gate
and record the previous incomplete capture unchanged. Restoring correct GD SR2
handling is a functional emulator correction, not proof of physical QIO80MHz
timing, Wi-Fi, playback or CYD resource/performance acceptance.
