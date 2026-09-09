# SDK RX/TX diagnostic overlay tests

Run `node --test tests/esp8266-sdk-rx-diag.test.js` from the repository root.
The counter module runs with GCC ASan/UBSan (WSL GCC on Windows). Tests execute
the injected SDK functions with controlled allocation, enqueue and TX failures,
synchronous/asynchronous custom-pbuf release, and concurrent counter snapshots.
An ordinary tiny host CMake project checks actual target-source replacement and
OFF restoration; it does not build firmware. The installed SDK remains read-only.

The SDK-dependent tests use `YORADIO_TEST_SDK_PATH` or the native-port SDK cache;
they report a skip if that SDK is absent. Pins cover complete normalized source
files, accepting CRLF/LF only. Hash or unique-anchor mismatches abort configuration.
The generated `sdk-rxdiag/manifest.json` records original, normalized and output
SHA-256 values. The overlay only inserts counter calls, preserving SDK returns,
ownership and error handling, including the existing TX-transform `ERR_OK` path.

## Interpretation limits

The eight lifetime counters consume 32 bytes of DRAM only when explicitly enabled
with `YORADIO_ESP8266_SDK_RX_DIAG=ON` and `YORADIO_ESP8266_DIAGNOSTIC=ON`.
No malloc, print, timer or task is added. OFF does not compile the counter module
or replace SDK sources. Updates/snapshots use short FreeRTOS critical sections;
SDK `SYS_ARCH_PROTECT` is deliberately avoided because it lazily allocates a mutex.

`rx_custom_live/peak` count software custom-pbuf wrappers, not all hardware or
closed-driver Wi-Fi RX descriptors. `rx_custom_fail` includes wrapper allocation
and pbuf setup failures; `tx_transform_fail` includes allocation failure and IRAM
buffer rejection. No observed errors does **not** prove there were no Wi-Fi drops:
drops before the SDK receive callback are outside this instrumentation. Counters
wrap modulo 2^32 and are never reset on reconnect; compare beginning/end snapshots
so outstanding old-stream pbufs do not cause false underflow or a misleading peak.

The production builder exposes this diagnostic as `-Diagnostic -SdkRxDiag`.
It explicitly selects OFF otherwise and records the boolean plus a hash of the
copied SDK overlay manifest in the firmware artifact. `/api/native/audio` adds
the eight named counters only with this flag, using the existing serialized
1088-byte HTTP scratch. The health JSON host test covers both flags and maximum
32-bit values with ASan/UBSan; no additional response heap allocation is needed.

The same diagnostic JSON includes `reset_reason` from the SDK's boot-latched
`esp_reset_reason()`: 1 power-on, 3 software restart, 4 panic, 5 interrupt WDT,
6 task WDT, 7 other WDT, 9 brownout. This adds no application counter state.
A reason sampled after OTA describes that OTA reboot, not an earlier failure.
