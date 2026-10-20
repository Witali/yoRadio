# CYD TLS allocation-failure input reclaim

This is one part of [stage 13](ESP32_CYD_C3_TRANSFER_PLAN.md), following
[completed GET TX release](CYD_MEMORY_TRANSFER_DESIGN.md). It adapts the donor
idea to the CYD startup transaction and SMP lifetime. The feature is initially
opt-in through `CONFIG_YORADIO_TLS_INPUT_RECLAIM`. Physical qualification still
gates default activation and numerical memory tuning.

## Production entry points

- [native_input_reclaim.c](../idf/esp32-cyd2usb-native/main/native_input_reclaim.c)
  and [public contracts](../idf/esp32-cyd2usb-native/main/native_input_reclaim.h)
  implement the allocator wrapper and non-owning pool registry.
- [audio_service.c](../idf/esp32-cyd2usb-native/main/audio_service.c),
  `audio_service_start`, binds immediately after the existing `READY` commit
  and before task notifications. No rollback follows publication. Rejection
  retains successful startup and the existing registry owner. Stop, EOF and
  maintenance keep the successful pool alive.
- [The CMake helper](../idf/esp32-cyd2usb-native/main/compat/input_reclaim/enable.cmake)
  adds the service and linker wrapper only when selected. The
  [Kconfig option](../idf/esp32-cyd2usb-native/main/Kconfig.projbuild) requires
  adaptive input, SDK mbedTLS internal allocation, no custom allocator and
  recoverable allocation failures. Unsupported forced combinations stop
  configuration. The installed SDK remains unchanged.
- [Canonical adaptive input](../idf/components/native_stream/adaptive_input.c)
  already supplies `release_one`, protected leases and the unchanged minimum.
  Its allocation/free operations remain outside queue critical sections.

## Allocation and ownership

The wrapper first calls the original `esp_mbedtls_mem_calloc`. Success returns
immediately. Zero/overflow requests and ISR calls keep original SDK semantics
and never reclaim. Delegation does not make the TLS allocator ISR/cache safe.
Only a valid task-context allocation that actually returned NULL can pin the
current pool and try recovery.

Each call fixes its retry budget from the initial target minus minimum slot
counts. One successfully released IDLE slot permits one original allocator
retry. It stops on success, no eligible slot or budget exhaustion, even if a
producer concurrently restores slots. WRITING, READY, READING and caller-owned
control storage remain intact. The original calloc zeroing and ordinary SDK
free pairing apply. No reserve, largest-block heuristic, allocator callback,
free wrapper, logging or blocking work is added to this path.
Existing health counters retain each failed original allocation attempt,
including an attempt later recovered; this does not turn recovery into a
fatal stream failure.

The registry lock only protects pointer admission, pin count and retirement.
Queue operations and allocation occur after unlocking it. Detach by the wrong
owner has no effects. BUSY closes new admission but retains the owner until an
explicit retry observes zero pins; new binds remain rejected during drainage.
The last unpin does not clear ownership automatically.

Successful detach proves only that allocator users drained. Any future actual
teardown must separately quiesce producer/consumer leases, blocked queue users,
restore allocations and health readers. The current application does not add
runtime pool destruction or replacement. Startup rollback still destroys only
an unpublished pool while all new tasks remain notification-gated.

## Qualification boundary

The dedicated host gate compiles the complete real service and queue with
explicit SDK/RTOS/allocator seams. Startup tests execute actual publication,
rollback and notification order. The CMake gate checks enabled, disabled,
early-expansion and incompatible allocator profiles. Exact semantic controls
must fail the intended assertions; sanitizer crashes and timeouts are not
successful detections.

The separate ESP32 QEMU gate must use actual SDK heaps, FreeRTOS cores and the
public `mbedtls_calloc` route, observe a real NULL before recovery, preserve
nonidle bytes/floor/control, retain health failure callbacks, and exercise
retirement and bounded retries under producer refill. Synthetic allocator
failure alone cannot establish this target gate.

Full opt-in Clang passes; actual production application links remain necessary.
Physical HTTP/HTTPS, radio/WebUI/OTA contention, largest blocks, stack margins
and prolonged audio tests remain distinct. No requested-byte count, static
map delta or emulator result is a claim of measured CYD heap savings.

The current host checkpoint passes 21 service/queue cases and 17 exact semantic
controls, 12 startup configurations with four publication controls, and eight
actual CMake helper configurations. The full opt-in Clang run covers 54 units,
with 86 baseline warnings and no errors; the new service has no diagnostics.
Actual SDK OOM/QEMU and production application qualification remain separate.
