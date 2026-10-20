# Standalone C3 raw-format project: source preparation only

No SDK, compiler, preprocessor, QEMU, reference decoder, test or Git command was
executed. Only this fresh ignored directory was written. Canonical source/tests,
installed SDK/libraries and root campaigns remain inputs. This is not a new
runner framework: root owns later build, merge, QEMU and result review.

The caller is copied from canonical tests/target/cyd_vorbis_format_qemu/main/main.c.
caller-relation.json lists its five exact substitutions: C3 protocol prefix,
worker check/affinity/core report 0 and matching core 0 creation diagnostic. The
coordinator remains core 0. Every packet/PCM/metadata/canary/header assertion and
per-handle info object's lifetime is otherwise unchanged. fixture.h and the
factory partition table are byte-equal copies. The fixture has 68 packets,
66 full 8192 outputs, and its complete header hash is
839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378.

variant contains byte-exact current C3 setup.c, output.c and RV32 ABI header.
The inherited default rate/block rejection remains: ExpectedRejection 1 is the
expected baseline reproduction, not acceptance. ExpectedRejection 0 preserves the
acceptance oracle but cannot qualify those unchanged sources. A corrected C3
candidate requires a separately reviewed source/pin revision; no guard change is
hidden here. LIMIT_TO_64kHz must remain absent (the caller rejects its definition).

Minimal main CMake uses only those two implementation files and the installed
codec component, with only raw open/decode wrappers. Public raw calls and public
close keep handles opaque; no simple.c, Ogg parser, reset/fault injection,
decoder-registration service, C3 application CMake/build.ps1, AAC patcher or
private-owner dependency is included. CMake positively guards C3/SDK6.1.0 and all
three C3 source hashes plus the two actual C3 vendor archive hashes. SDK6.1 source
revision is 9a97f6c54ec638111ce55cd36581b3c192f15207; no Xtensa/CYD helper is reused.

Defaults are an isolated DIO 40 MHz/4 MiB factory-only image, C3 CPU 160 MHz, one core,
main/coordinator CPU 0, checked worker CPU 0/16384 stack, main stack 6144, canary and
light heap poisoning. Minimum C3 revision 0 is intentional for the emulator's
available ROM/revision range; actual generated config and boot still need review.
This test profile is not the production C3 sdkconfig. No PSRAM or radio settings
are imported. Actual flasher_args.json must determine merge offsets; C3 bootloader
is at 0x0, not CYD 0x1000. Never copy CYD dual-core flags or OTA merge assumptions.

sdk-build.ps1 is a bounded adaptation of canonical CYD sdk-build.ps1: future
execution validates an explicit pins SHA, source/tool/archive bytes, exact SDK
revision and tracked-clean state, then copies this project/variant into a fresh
root-supplied campaign. It activates only installed SDK6.1, confirms the actual
RISC-V compiler/CMake/Ninja paths and launches that SDK Python/idf.py using
ProcessStartInfo.ArgumentList. Native child stdout/stderr are retained separately
with CreateNew, asynchronously drained, hashed and recorded with child PID and
terminal exit. A build success is labelled BUILD ONLY, never format qualification.
Source copies and all pinned external bytes are checked again after a successful
child exit. Existing campaigns are rejected; no retry/setup/download/QEMU/device
operation is present. Read-only Git provenance checks occur only if root later
explicitly launches this SDK build script; none was run during preparation.

Future root-reviewed SDK build command (not run here):

```powershell
& $powershell -NoProfile -NonInteractive -File .build/c3-vorbis-format-project-prep-01/sdk-build.ps1 `
  -Campaign C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/c3-vorbis-format-baseline-01 `
  -ExpectedRejection 1 -PinsSha256 $reviewedPinsSha
```

Root should retain its own authoritative terminal tool handle/chunk, child result
and raw logs, then independently inspect generated config/compile/link rows and
ELF machine identity (C3 must be RISC-V 243). Check that only the two intended
raw wrappers are linked and no application/simple/Ogg/AAC patch source appeared.

Only after successful SDK build and review should root independently merge the
actual factory flash using installed esptool and launch the pinned native
C:/Work/QEMU-ESP32/bin/qemu-system-riscv32.exe with -M esp32c3, snapshot/no-reboot,
no network/audio/display/monitor and C:/Work/QEMU-ESP32/share/qemu ROM directory.
Do not use the full-radio run-yoradio launcher. Exact QEMU stdout/stderr/result
oracle and nonzero exit on panic/missing protocol remain root-owned future work.
No claim about QEMU machine/SDK compatibility follows from this source prep.
