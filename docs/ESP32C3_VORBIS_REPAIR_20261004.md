# ESP32-C3 Vorbis initialization and teardown repair

Date: 2026-10-04. Step 2 of the [repair plan](ESP32C3_VORBIS_REPAIR_PLAN.md).

**Initialization gate passed in QEMU. Hardware and full-format qualification
remain pending.** The radio image was built and saved, but not flashed.

## Changes

The pinned Espressif 2.6.2 RV32 libraries retain the decode/synthesis/MDCT/PCM
arithmetic. Audited source replaces initialization and its allocation-owning
callees: codebooks, floor 0/1, residue, mapping and DSP creation. Handles become
visible only after successful initialization; partial allocations have one
cleanup chain. Private ABI structures have named fields and compile-time size
and offset assertions. CMake rejects other archive hashes.

The source derives from [Xiph Tremor at revision
0ad0141e864cfbb130db4f22e279d421832e7336](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/),
adapted after checking the pinned vendor objects. The BSD license and details
are retained [with the implementation](../idf/esp32c3-oled-native/main/vorbis_repair/README.md).
Huffman workspace sizing follows used entries, as in the vendor library, with
explicit bounds on node writes. This agrees with the [Vorbis I codebook rule](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
that unused entries have no tree leaf. Existing header acceptance limits are
preserved; widening them belongs to format qualification.

Ogg simple-decoder initialization checks allocation before dereferencing it.
An inner Ogg memory error and a failed packet/header reallocation are preserved
through the outer parser, which previously swallowed them. A task-local scope
returns `ESP_AUDIO_ERR_MEM_LACK` instead of success with missing PCM.

Codec registration now reports failure and rolls back its registrations.
The service releases the PCM buffer even if opening the decoder failed, closes
simple/AAC decoder resources on terminal paths, and forwards the existing
generation-tagged completion marker after queued PCM. `send_pcm` gives the
queue its own copy, so freeing the decoder workspace does not invalidate it.

## Results

| Case | Original library | Repaired |
| --- | --- | --- |
| 100 normal decode/close cycles | Pass | Pass; identical PCM |
| 198 per-stream allocation failures | 189 crashes, 6 handled, 3 false successes | 198 handled |
| Four invalid/truncated headers | Four crashes | Four handled |
| Four registration allocation failures | Not in step-1 sweep | Four handled; registry rolled back |
| Two failed opens, repeated release/Stop, then valid Play | Not in step-1 sweep | Two handled; PCM released independently |

Every repaired fault case returns a defined error, leaves no stream allocations,
keeps the heap valid and successfully decodes the valid fixture immediately
afterwards. The release/Stop/Play cases execute the shared production cleanup
helper against the actual decoder; they do not simulate the entire network
task scheduler. Existing deterministic EOF tests cover terminal queue ordering,
stale generations and cancellation separately.

The fixture is the retained **48 kHz stereo Vorbis q10** file. This is an
exhaustive allocation sweep of that successful path, not every legal Vorbis
stream or every parser branch.

| Metric | Original | Repaired |
| --- | ---: | ---: |
| PCM bytes per complete decode | 2,107,648 | 2,107,648 |
| Signed-16 interleaved samples | 1,053,824 | 1,053,824 |
| Changed output samples | — | 0 |
| Allocation requests per stream | 198 | 198 |
| Peak requested stream bytes | 42,118 | 42,118 |
| Peak usable allocated stream bytes | 42,672 | 42,672 |
| Heap free before/after each normal cycle | 286,344 | 286,344 |
| Largest free block before/after | 147,456 | 147,456 |
| Unused test-task stack, final cycle | 14,604 | 14,460 |

PCM SHA-256 for both:
`eb2037928cd89a1922fd9ae9d055c03b587484b7378c55b0f319d79980976144`.
Registration's four persistent allocations total 72 usable bytes and are
accounted separately. QEMU test-ledger/static PCM memory is not a production
codec memory saving. No decoding-speed conclusion is drawn from these tests.

An [initial repair trial](../tests/results/esp32c3-vorbis-repair-first-20261004/summary.json)
still returned false success on allocation 3; all its logs and exact sources
remain saved. Capturing the inner Ogg parser error resolved it. The
[final raw evidence](../tests/results/esp32c3-vorbis-repair-20261004/summary.json)
contains **1 PASS + 208 HANDLED**, with source, config, library, image and log
identities. The original failed run is also retained unchanged.

Other validation: 53 Node integration checks; 22 Python classifier/evidence
checks, including revalidation of all retained logs; production PCM/format callbacks with
AddressSanitizer/UndefinedBehaviorSanitizer, the Helix adapter and native AAC
ownership/framing regressions; deterministic EOF queue/state tests. These
checks do not replace physical listening, CPU measurements or OTA testing.

## Radio build

Artifact: [firmware/development/esp32c3-vorbis-repair/app.bin](../firmware/development/esp32c3-vorbis-repair/app.bin).
It uses the previously tested `esp32c3-aac-pc19-netrx` configuration, including
full-rate AAC/SBR/PS, PC19, two FreeRTOS pointer slots, USB diagnostic console,
and no deep sleep. `CONFIG_YORADIO_VORBIS_REPAIR` defaults to `y`.

| Linked section/image | Before | After | Change |
| --- | ---: | ---: | ---: |
| IRAM text | 43,354 | 43,354 | 0 B |
| DRAM data | 12,620 | 12,620 | 0 B |
| DRAM BSS | 31,480 | 31,480 | 0 B |
| Flash text | 1,119,036 | 1,121,438 | +2,402 B |
| Flash rodata | 389,656 | 389,696 | +40 B |
| Application image | 1,568,016 | 1,570,464 | +2,448 B |

The new C thread-local pointer occupies four bytes in the TLS template per task,
before task-allocation alignment. It is separate from the two FreeRTOS pointer
slots already used by AAC; unchanged static DRAM does not mean zero runtime
overhead. Test heap peaks above include the actual QEMU allocator accounting.

The [linked-build audit](../tests/results/esp32c3-vorbis-radio-build-20261004/build.json)
checks the repaired open callback table, actual service calls, original Vorbis
decode/reset/close callbacks, and the existing AAC types and patch provenance.
Application and ELF identities match. No test harness is linked into the radio.
Exact sources at build/run time are retained; the final source file only had
imported trailing whitespace removed after those builds.

## Reproduction

From the repository/worktree root, using the installed project toolchain:

```powershell
$deps = 'C:/Work/yoRadio/.idf'
$python = "$deps/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe"
./idf/esp32c3-oled-native/build.ps1 -DependencyRoot $deps `
  -BuildDirectory build-qemu-vorbis-repair -Sdkconfig build-qemu-vorbis-repair/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults', 'sdkconfig.qemu-vorbis-lifecycle.defaults', 'sdkconfig.qemu-vorbis-repair.defaults') build
& $python tools/codec_benchmark/run_vorbis_lifecycle.py `
  --build idf/esp32c3-oled-native/build-qemu-vorbis-repair --deps $deps `
  --output .build/vorbis-repair-new-run --cycles 100 --wsl `
  --qemu /mnt/c/Work/yoRadio/.worktree/esp32c3-stream-format/.build/qemu-cache-host/qemu-system-riscv32 `
  --bios /mnt/c/Work/QEMU-ESP32/share/qemu
```

QEMU/BIOS paths are local installation paths, also recorded in `report.json`.
Use a fresh output directory. `--case oom-0003` allows a quick targeted check;
subset runs never satisfy the complete qualification gate.

For the radio, copy the retained `firmware/development/esp32c3-vorbis-repair/sdkconfig`
to a new build directory's `sdkconfig`, then pass that config and directory to
`build.ps1`. Preserve the PC19 configuration: a bare-default trial was stopped
by the existing AAC TLS-slot assertion. The retained build uses the tested
profile, not a workaround that disables AAC features.

**Next:** step 3, deliberately small PCM buffers and deterministic resize/retry
and EOF sample handling. Physical fragmentation, broader format coverage,
CPU/load, long playback and OTA qualification remain steps 4–7.
