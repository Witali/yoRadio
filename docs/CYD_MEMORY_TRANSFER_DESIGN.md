# CYD memory-policy transfer

Stage CYD-C3-13 of the [transfer plan](ESP32_CYD_C3_TRANSFER_PLAN.md) requires
separate ESP32/Xtensa evidence. The donor uses IDF 6.1 and dynamic TLS buffers;
CYD uses pinned IDF 6.0.2 with its existing TLS policy, TFT/SPI DMA and two cores.
Neither donor SDK patch hashes nor its measured savings apply automatically.

## Completed GET request-buffer release

[audio_service.c](../idf/esp32-cyd2usb-native/main/audio_service.c), `open_stream`,
releases request TX storage only after the existing deadline/length checks,
final successful 2xx response and valid ICY headers. The owning stream task
performs the call. Rejection retains the allocation and successful playback.
Redirects, errors and unfinished requests do not take this branch.

[The build helper](../idf/esp32-cyd2usb-native/main/compat/http_request_buffer/enable.cmake)
selects a build-local SDK source overlay when the default-enabled
`CONFIG_YORADIO_HTTP_REQUEST_BUFFER_RELEASE` option is set. The installed SDK
is unchanged. [The patcher](../tools/patch_cyd_http_request_buffer.py) accepts
only the audited IDF 6.0.2 source hash with uniform LF/CRLF and inserts two
spans. Version/source-count/content mismatches stop configuration.

The extension guards synchronous GET, no body or pending write, and the actual
SDK response-data-start state. It frees only request-buffer data, retains RX,
header dictionaries and borrowed body ownership, and clears the prepared-line
flag. A subsequent request restores the entire configured TX capacity;
allocation failure returns `ESP_ERR_NO_MEM` with unambiguous errno.

The configured request capacity is 4096 bytes. This is not a measurement of
usable allocator bytes, total heap savings or TLS peak improvement. TLS RX
record capacity remains 16 KiB and the existing TX setting remains 4 KiB.

[Qualification](../tests/results/cyd-http-request-buffer-20261020/README.md)
covers actual audited SDK sender/cleanup spans, 17 host cases and eight exact
semantic controls, whole patched source compilation against real Xtensa SDK
headers, 62 actual `open_stream` cases with six controls, and nine actual CMake
helper configurations. Private host response/transport preparation is an
explicit seam; target compilation establishes layout/API compatibility. The
six-image [production application matrix](../tests/results/cyd-http-request-buffer-20261020/SDK.md)
also passes; physical HTTP/TLS behavior remains separate. The full-pipeline
FLAC QEMU test deliberately disables release because
its synthetic transport does not enter the SDK response state.

## Opt-in idle-input reclaim

The [implementation and contracts](CYD_INPUT_RECLAIM_DESIGN.md) now provide
allocation-pressure reclaim of IDLE adaptive-input slots with post-READY
publication, SMP pin/retirement and an immutable retry budget. The option stays
default off. Host/service, actual startup and CMake guards pass; full opt-in
Clang adds no warnings. The actual SDK/QEMU gate passes five cases and four
exact semantic controls, including real allocator NULL/recovery and dual-core
retirement/refill. The [seven production exports](../tests/results/cyd-input-reclaim-20261020/SDK.md)
pass from clean `a1b9d5a1`, including all vendor/custom output combinations and
a disabled PDM control. ELF allocator/free words, configuration deltas, saved
images, OTA capacity and unchanged task bindings were checked. Physical
qualification remains open.

The earlier [frozen proposal](../tests/results/cyd-http-request-buffer-20261020/plan/idle-input-reclaim/README.md)
is retained as historical evidence from before implementation. Its status must
not be read as the current implementation checkpoint.

## Opt-in early MPI mutex initialization

[The early-MPI module](CYD_EARLY_MPI_DESIGN.md) is now called first at
`app_main` entry through a default-off option. It acquires/releases the existing
SDK mutex through the public API, preserving its lifetime and all task profiles.
Whole canonical startup tests pass with strict ASan/UBSan and the real board
header. The actual SDK/Xtensa fixture passes its two-core case, both exact
omission controls and the real-heap void-API OOM gate. Independent review found
and closed a duplicated board constant in the initial host fixture.
[The immutable qualification archive](../tests/results/cyd-early-mpi-20261020/README.md)
retains the canonical reports, inputs, controls and review closure.
The [seven full production exports](../tests/results/cyd-early-mpi-sdk-20261020/README.md)
also pass from clean `1190aebce`, covering all vendor/custom output combinations
and a disabled PDM control. Final ELF checks confirm first-call ordering,
allocator/free/reclaim pairing and unchanged task/board profiles. The only
configuration delta against the matching reclaim images is the MPI bool;
minimum OTA headroom is 224912 bytes. Actual radio pre-application observation
and physical benefit/default activation remain open. The source audit below
is historical evidence from before this implementation, rather than its
current status.

## Remaining work

- Implement and qualify a CYD-specific TLS/full-record RX reservation after the
  [read-only SDK audit](../tests/results/cyd-tls-reserve-mpi-audit-20261020/README.md).
  CYD uses static TLS buffers; the donor dynamic-RX allocation sites and capacity
  formula do not apply. Preserve the SDK full-record capacity expression,
  ordinary allocator/free pairing and input reclaim; verify cleanup, OOM,
  reconnect and concurrent clients. Complete the early-MPI radio-boot and
  physical gates; its SDK void API does not offer recoverable OOM. Its seven
  full-application exports are already qualified.
- Measure internal/DMA heap, largest blocks, TLS peaks, stack margins and
  scheduler latency on CYD with TFT, network and audio active. Select input
  pool sizes, IRAM placement and stack changes from those results.
- Run HTTP/HTTPS and codec changes across all three output backends, including
  WebUI/OTA traffic and prolonged playback. No numerical donor saving or speed
  claim closes these gates.
