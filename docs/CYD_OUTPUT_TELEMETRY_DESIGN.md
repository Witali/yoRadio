# CYD output driver telemetry

This work covers the backend observations remaining in stage CYD-C3-05 of the
[transfer plan](ESP32_CYD_C3_TRANSFER_PLAN.md). Hardware timing, sound and
full-radio resource measurements remain separate gates. The counter service,
all three backend adapters and additive HTTP snapshot are implemented.

## Entry points and ownership

| Area | Source and contract |
| --- | --- |
| Counter service | [native_output_metrics.c](../idf/esp32-cyd2usb-native/main/native_output_metrics.c), [public snapshot](../idf/esp32-cyd2usb-native/main/native_output_metrics.h); boot-cumulative, short SMP portMUX, no reset or new task |
| PDM adapter | [native_audio_output.c](../idf/esp32-cyd2usb-native/main/native_audio_output.c), `pdm_write_block` and `pdm_begin`; preserve buffers, clocks, preload, auto-clear and pause behavior |
| Continuous DAC | Same source, four synchronous driver call sites: prime, full/partial PCM and idle |
| Legacy DAC | Same source, `legacy_write_frames`; preserve x16 conversion and IDF 5.5.4 adapter |
| HTTP | [health handler](../idf/esp32-cyd2usb-native/main/web_service.c), [bounded JSON](../idf/esp32-cyd2usb-native/main/native_health_json.c); additive `output_driver` group |
| Counter tests | [runner](../tests/run-cyd-output-metrics.py), [scope](../tests/native/cyd_output_metrics/README.md); complete actual service, both build profiles |

The output task remains the sole driver owner. Its synchronous write records
requested bytes, bytes actually reported by the driver, errors, timeouts and
incomplete writes. These include prime/bias/idle traffic. They are driver-buffer
units; the DAC expansion and legacy oversampling prevent treating them as input
PCM bytes or exact physical DMA output. No counters manufacture successful
audio completion, alter errors or bypass the existing cancellation guard.

All counters saturate instead of wrapping; `saturated` reports lost numeric
range. Errors include a non-success SDK result or a mismatched byte count.
Incomplete writes include partial/error results, so the counters can overlap.
An over-reported byte count is an error and remains visible in reported bytes.
Snapshots copy a whole coherent group under one short lock. No SDK call or
clock read occurs while that lock is held.

Quiet builds record counters without clock reads. The existing diagnostic
profile adds wall time immediately around each synchronous driver API. The
duration includes driver locks, copies, waits and preemption. It must be named
driver write time; it cannot be presented as isolated DMA queue wait or CPU
time. No extra sampling task, IPC or change of task affinity is introduced.

## DMA completion queue

Pinned SDK 6.0.2 exposes PDM `on_send_q_ovf`. The classic ESP32 ISR invokes it
when its completed-buffer queue is full and it evicts the oldest queue item.
This is a completion-queue drop, not a direct count of audible underruns.
Register only that callback, preserving existing `on_sent` behavior and
auto-clear settings. Its short IRAM handler updates DRAM counters with the
ISR-safe portMUX; no clock, allocation or logging belongs in that path.

The counter becomes available only after successful registration or an actual
callback, and remains cumulative across pause/reconfigure. Callback registration
failure follows checked channel cleanup. Continuous/legacy DAC keep their
current APIs and advertise this queue observation as unavailable; zero must
not imply that these drivers measured an event they do not expose.

## Qualification and integration gate

1. Run the complete counter service with strict warnings and ASan/UBSan in
   quiet and diagnostic profiles. Include exact classification/clock/overflow
   controls and real concurrent task/ISR publishers with coherent snapshots.
2. Compile the new service with the actual Xtensa SDK and inspect ISR call
   targets and IRAM/DRAM placement. This does not prove physical ISR latency.
3. Qualify actual backend calls and checked PDM callback registration. Exercise
   all three backend implementations with explicit hardware seams and the
   actual counter service; preserve golden PCM, pause and failed-setup behavior.
4. Add bounded JSON availability/null/max-width tests. Measure the maximum
   response before deciding whether its current 2304-byte stack buffer changes.
   Keep the HTTPD stack/socket budget and all task/core/priority bindings.
5. Run affected/full CYD Clang checks and actual SDK application builds, save
   qualified production variants under `firmware/development/`, then measure
   real callback/driver overhead and output behavior on CYD hardware.

The C3 volatile fields and private DMA generator are not copied. CYD keeps its
public SDK writers, DAC implementations and original DMA geometry.

The current host checkpoint passes 16 counter-service cases with seven exact
semantic controls, 22 complete-backend quiet/diagnostic cases with eight
controls, and the existing golden PCM/gain/normalizer/pause/maintenance suites.
The actual health serializer passes all capacities with canaries in three
profiles; maximum-width live counter values and valid CPU percentages produce
2000 bytes, preserving the 2304-byte HTTP buffer. The actual health handler
forwards the driver snapshot; unavailable observations remain JSON `null`,
while an available measured zero remains numeric zero.

The complete CYD Clang checkpoint covers 53 translation units with 86 retained
warnings and no errors. Separate actual Xtensa service objects verify the
short ISR helper and its SDK critical-section callees in IRAM, state and lock
in DRAM, and no timer reference in the quiet object. These are software checks;
physical ISR latency, write overhead and full-radio margins remain open.

[Six final GCC application exports](../tests/results/cyd-output-telemetry-20261020/SDK.md)
cover vendor/custom FLAC on all three backends. Final PDM ELF symbols place
both the actual registered callback and queue-drop helper in IRAM, with
64-byte state and an 8-byte lock in DRAM. Configuration differs from each
matching N5 image only by the new HTTP request-buffer option. No hardware
measurement or performance claim follows from this static application gate.
