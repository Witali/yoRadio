# ESP32-C3 pipeline checkpoints at DMA overruns

`CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC=y` enables a laboratory-only probe
for the staged DMA backend. The default is disabled. It adds 516 bytes of
static DRAM, task checkpoint stores and a longer overrun ISR. It does not
change PCM arithmetic, queue sizes, timeouts or priorities. There is no
sampler task, allocation or UART output.

The existing `/api/native/health` response gains a numeric `pipeline` object.
The response uses a larger stack buffer only in diagnostic builds. The
snapshot masks interrupts while copying the bounded state, then restores
them before formatting JSON. The ordinary output-drop count and diagnostic
sequence are sampled at the same ISR boundary.

## Interpretation

`phase_drops` has eight cumulative counters, indexed by these phase bits:

| Bit | Meaning at the interrupt |
| ---: | --- |
| 1 | Output task is inside the PCM receive call |
| 2 | Decoder is inside the encoded-input receive call |
| 4 | Network task is inside the HTTP body-read call |

These are call phases, **not FreeRTOS blocked/ready states**. A task may be
ready to run but not yet have returned from the instrumented call. In
particular, phase 7 alone does not prove that the network starved the decoder.

The last 16 overrun observations are returned in chronological order as
`[sequence, timestamp_us, phases, output_age, pcm_age, input_age, network_age]`:

- `output_age`: microseconds since the output task entered or returned from its
  latest PCM receive call. It normally polls an empty queue every 5 ms.
- `pcm_age`: microseconds since the output task accepted its latest current PCM
  packet, after any sample-rate configuration.
- `input_age`: microseconds since the decoder received a nonempty encoded packet.
- `network_age`: microseconds since a positive HTTP body read returned.

All ages use the hardware system timer through `esp_timer_get_time()`, with
`timer_hz=1000000`. It measures elapsed time including WFI waits. The C3 CPU
cycle counter stops during WFI and would undercount these waits; see
[TRM register mpcER, CYCLE field](https://espressif.com/sites/default/files/documentation/esp32-c3_technical_reference_manual_en.pdf#page=39).
The [ESP Timer API](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/api-reference/system/esp_timer.html#obtaining-current-time)
documents the lightweight timer read for tasks and ISRs. The linked timer
read and its dependencies must remain in IRAM/ROM. Ages wrap modulo 2^32
microseconds, about 71.58 minutes. Do not interpret longer idle ages as elapsed
wall time. A nonempty HTTP read can contain ICY metadata,
and an encoded packet may later be rejected after a station change; select
sustained-play windows with an unchanged stream generation.

A small output-checkpoint age alongside a long PCM age shows that the output
task is still getting scheduled while waiting for fresh PCM. A large age
requires investigating scheduling or a long output call. The decoder and
network checkpoints help locate the preceding stall. These observations do
not measure the analog waveform or count missing audible samples.

## Evidence handling

The sequence and phase counters are never reset. They include startup, Stop
and intentional idle periods. Compare adjacent snapshots only within a
sustained-play interval and retain boot identity. The 16-event history can
overwrite older observations: report the number not retained rather than
treating them as zero. The phase histogram still counts those events.

`tools/esp32c3_tests/production_health.py` validates the optional diagnostic
object, including sequence/phase totals and event order across counter wrap.
Normal firmware without this field remains supported. Host tests execute the
actual C snapshot/JSON handler with ASan/UBSan and exercise phase combinations,
history overwrite, unsigned wrap and small-buffer failure. Physical tests are
still needed to determine the cause of an overrun.

```text
python -B tests/test-pipeline-health.py
python -B tests/test-production-health-native.py
python -B tests/run-output-task-boundaries.py --output .build/output-boundary-check
```

The native tests use GCC through WSL on Windows. The output directory for the
boundary test must be new so earlier evidence is preserved.
