# CYD early SDK MPI mutex initialization

This is one part of [stage 13](ESP32_CYD_C3_TRANSFER_PLAN.md). The optional
`CONFIG_YORADIO_TLS_EARLY_MPI_LOCK` defaults to off. It moves a possible first
allocation of the SDK-owned MPI mutex to application entry. It neither adds a
TLS reserve nor establishes a measured memory or fragmentation improvement.

## Entry points and ownership

[app_main.c](../idf/esp32-cyd2usb-native/main/app_main.c) calls
`native_tls_early_mpi_prepare()` before its first log, health/state initialization,
NVS, display or network service. The disabled header implementation is a no-op.
The enabled [module](../idf/esp32-cyd2usb-native/main/native_tls_early_mpi.c)
uses only `esp_crypto_mpi_lock_acquire()` and `esp_crypto_mpi_lock_release()`.
It performs no cryptographic operation and retains the original SDK mutex and
its process lifetime. An already initialized SDK mutex is acquired and released
normally; no private handle is read, replaced, cleared or freed by production.

[Kconfig](../idf/esp32-cyd2usb-native/main/Kconfig.projbuild) requires classic
ESP32, SOC MPI support, mbedTLS and hardware MPI. The
[CMake helper](../idf/esp32-cyd2usb-native/main/compat/early_mpi/enable.cmake)
adds the canonical module only when enabled and rejects incompatible forced
configurations. The main component explicitly requires `esp_security`.
The source also rejects incompatible enabled configurations at compilation.
Task cores, priorities, stacks, clocks, audio backends and buffer sizes retain
their existing definitions.

## Failure behavior and qualification boundary

The public SDK API returns `void`. On first-use allocation failure the pinned
SDK constructor calls `abort()`; this feature cannot return a recoverable OOM
result. It must run in ordinary `app_main` task context after the scheduler
starts, before application services. Standard SDK pre-application startup and
its existing PSA/RNG initialization are preserved.

The initial isolated prototype passed whole-module/whole-copied-`app_main`
ordering checks with ASan/UBSan, invalid configurations and exact order controls.
Its separate actual SDK6.0.2/Xtensa QEMU fixture observed a lazy mutex at that
fixture's entry, repeated acquire/release without replacement, and mutual
exclusion across both cores. Skip-acquire and skip-release variants failed their
named assertions. Real heap exhaustion reached the unchanged queue allocator's
NULL result and the exact SDK lock constructor abort site; its resolved stack
was checked against that variant's ELF. Generic panics are not accepted as
evidence for this expected void-API failure.

Those initial results used an unapplied candidate. Fresh canonical qualification
now passes for the checked-in production module and actual `app_main` bytes:
two whole startup configurations, three exact ordering controls, four invalid
compile configurations and seven CMake cases under strict ASan/UBSan; the real
frozen board header supplies the existing task-stack constants. The first host
run used an incorrect duplicated board-profile constant and is retained only
as historical ordering evidence; independent review found the gap and the
fresh corrected host gate checks actual-header inclusion.

The canonical SDK/QEMU campaign also passes the successful two-core case,
both exact omission controls and the real-heap void-OOM gate, using the actual
production module bytes and production Kconfig snapshot. The target report's
`production_integration: false` labels its isolated SDK fixture: it does not
execute the radio application's services. It does not mean that an alternate
module implementation was tested.

Full application exports, actual radio pre-application observation and physical
CYD memory/boot/audio qualification remain separate gates. The minimal SDK
fixture does not establish that the full radio firmware has the same
pre-application lock history or receives a useful resource benefit.
