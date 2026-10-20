# Actual SDK TLS input reclaim gate

This standalone classic ESP32 dual-core QEMU gate compiles the complete
production `native_input_reclaim.c`, canonical `adaptive_input.c` and
`native_health.c` with ESP-IDF 6.0.2. The production
`compat/input_reclaim/enable.cmake` supplies the opt-in linker wrapper.
Production `CONFIG_YORADIO_TLS_INPUT_RECLAIM` remains default off; this test
profile explicitly enables it. No physical device is used.

The SDK platform allocator function pointer is not replaced through a test
setter. An ELF proof checks its initializer points to
`__wrap_esp_mbedtls_mem_calloc`, and the free initializer points to ordinary
`esp_mbedtls_mem_free`. Tests call public `mbedtls_calloc`/`mbedtls_free`.
The `heap_caps_calloc` spy always delegates to the actual SDK allocator and
records its real result; it never fabricates NULL. Actual SDK allocator,
platform and heap source translation units/dependencies are recorded.

## Cases

- **R0:** static caller-owned pointer storage and real internal-heap filler
  allocations produce observed allocation failures. A real 1024-byte SDK
  calloc returns NULL; IDLE queue storage funds retry before any filler is
  freed. Check zeroed bytes, ordinary SDK free, preserved native-health failed
  allocation count/caps and WRITING/READY/READING/control payloads.
- **R1:** a real impossible allocation remains NULL through four releases;
  target 8/minimum 4 queue stays at its floor with protected payloads intact.
- **R2:** a real core1 allocation holds a registry pin at public queue release
  barriers. Core0 observes detach BUSY, denied binds/new pins and persistent
  retirement, overlaps a real producer restore, then explicitly detaches after
  the old allocation returns. Ordinary queue owners are quiet before destroy.
- **R3:** core0 restores after each core1 release. The original four-attempt
  budget remains fixed even while resident storage is replenished.
- **R4:** zero/overflow calls and an actual SDK timer ISR delegate to the real
  allocator without reclaiming. Real SDK tasks, semaphores, heap, timer ISR
  and the native-health allocation-failure callback execute in the emulator.

The heap pressure and task/barrier coordinator are synthetic test stimuli.
This gate exercises the allocator path, rather than a full TLS handshake or
actual audio/network workload. It establishes no production memory margin,
RF/DAC/DMA behavior, latency or performance result. It creates its own core0
coordinator/core1 worker; production task/core/priority/stack assignments are
unchanged. Physical and complete application qualification remain separate.

## Exact semantic controls

Each control compiles a separately hashed whole module with an exact recorded
source mutation: skip the first real allocation once an owner is published,
return without reclaiming, omit paired pin/unpin accounting, or extend the
initial retry budget. Detection requires its exact named failure marker,
controlled stop and clean QEMU exit. Generic abort/panic, timeout, compiler
failure or wrong-source selection never counts as detection. The failed
predicate is decided before failure cleanup releases only test-owned fillers;
this gives SDK restart enough heap for its lazy timekeeping lock. The bound
queue and SDK objects are not destroyed by failure cleanup.

## Run

Use installed SDK/QEMU tools on Windows. For this workspace:

```powershell
C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -X utf8 tests/run-cyd-input-reclaim-qemu.py --output .build/cyd-input-reclaim-fresh --qemu C:/Work/QEMU-ESP32/bin/qemu-system-xtensa.exe
```

SDK defaults are discovered from `IDF_PATH`/`IDF_TOOLS_PATH` or the nearest
`.idf/v6.0.2` and `.idf/tools-v6.0.2`; the required SDK Git commit is
`7101770dc6db2667b3c477cc31365dd1acd6db4e`. Override installed locations with
`--idf`, `--idf-tools`, `--idf-python`, `--qemu`, `--rom-directory` and
`--powershell`. PowerShell 7 or newer is required. `--preflight-only` validates
paths without creating output or running SDK/QEMU. Output must be fresh and
cannot overlap source/install trees or an earlier evidence campaign. Python
and PowerShell parent directories are protected, including custom paths.

One fresh campaign has a transient shared SDK working build. Each canonical
or control variant gets immutable copied artifacts/configuration, actual
compiler dependency closure, source mutation recipe, SDK pointer proof and
execution bundle before QEMU. All bound source/input/artifact/tool hashes are
checked afterward; changing a variant only changes the transient working
build. This avoids rebuilding every SDK object for each control.

## Qualification chronology

Fresh attempt05 completed five positive cases and four exact semantic controls
with terminal exit 0. Preflight03 passed 13 path/protection cases. Attempts01–04
are preserved historical rejected campaigns and contribute no detections to
that final count: environment-only variant selection did not trigger CMake;
an unscoped first-call control broke SDK boot; linker GC legitimately removed
an unused release function in the no-reclaim control; and SDK restart under
still-full test pressure lazily allocated a timekeeping lock and aborted.
The guards rejected each incomplete campaign.

This README was added **after** attempt05 qualification. It was not a frozen
runtime input to that run. Executable runner/C++/CMake/helper bytes and actual
production source were frozen for attempt05; adding this usage document does
not imply a new target run. The result archive retains the original reports,
source/config/log bytes and explicit binary omission hashes.
