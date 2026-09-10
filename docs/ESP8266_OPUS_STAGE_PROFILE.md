# Opus: selected-stage profile

Diagnostic-only, CPU160, one stage per build. Default `0` removes all
instrumentation. No PCM/packet buffers, tasks or ISR code are added.

| Build value | Measured scope |
|---|---|
| 1–4 | SILK indices, pulses, parameters, synthesis core |
| 5 | SILK resampler calls, including the stereo-to-mono special case |
| 6 | CELT coarse, fine and final energy (three separate scopes) |
| 7 | CELT TF, dynamic and static allocation, through `clt_compute_allocation` |
| 8 | CELT `quant_all_bands`, including recursive PVQ/band work |
| 9 | CELT synthesis (spectral scaling/downmix/IMDCT/FFT) |
| 10 | Normal-frame CELT postfilter loop |
| 11 | Normal-frame CELT deemphasis |

PLC, comfort noise, history moves, anti-collapse, Opus wrapper/transitions
and unmarked branches are not a complete disjoint partition. In particular,
CELT PLC's early return has no normal-frame synthesis/deemphasis markers.
Do not sum different builds as an exact accounting of one execution.

The clock uses `esp_timer_get_time()` in a short critical section to read
the SDK's accumulated epoch and its current CCOUNT coherently. Interrupts
are not disabled during decoding. Ticks are **wall microseconds**, including
Wi-Fi/ISR/RTOS preemption, not exclusive CPU. Each scope must finish within
one32-bit microsecond revolution (71.58min). Elapsed values subtract
modulo2^32; totals are64-bit. The protocol advertises clock_hz1000000.
The existing outer `task_us` remains the separate runtime-statistics measure.
The wire format uses `stage_ticks_hi` and `stage_ticks_lo`: the SDK's
nano `printf` does not support `%llu`. Host tools join the two words with
a safe-integer check. No expensive64-bit decimal formatting on the device.
Host monotonic ticks test correctness only, not LX106 performance.

Only the audio task owns the16-byte accumulator. It resets it before each
packet, copies it afterward and publishes through the benchmark's existing
critical section. WebUI never directly reads a half-updated64-bit counter.
Only completed measured scopes are counted; failed packets remain errors.
Warmup packet counters are discarded, and every case/run starts fresh.
The fields add80 bytes across five cases before ABI padding; clock
calibration adds8 bytes. Measured target `.dram0.bss` growth is128 bytes
including the accumulator and alignment. IRAM/data sections are unchanged.

The three instrumented translation units are byte-for-byte identical in
target disassembly with stage0 and before instrumentation. The enabled
profile has clock-helper calls only in the chosen CELT scopes. Enabled
stack/flash overhead is measured separately, not inferred from stage0.

128 empty clock pairs report raw minimum/maximum cost. This does not include
all counter-update, call, stack and cache overhead; therefore nothing is
subtracted from recorded timings. Use a matching stage0 build and repeated
raw runs to assess instrumentation perturbation, not to claim acceleration.

```powershell
tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -Variant esp8266-opus-stage-sdk-bands -Diagnostic -EnableOpus -OpusBenchmark -OpusProfileStage 8 -OpusWordAsm -OpusIcdfFlashWord -OpusFirFlashWord -NoSpiffsCache -Pdm32Iram -Pdm32Batch -WebAudioPause off -SdkRxDiag
node tools/esp8266_opus_profile/run_board.cjs --interval-ms 30000 --output .build/stage8-run1.json
node --test tests/esp8266-opus-stage-profile.test.js tests/esp8266-opus-board-benchmark.test.js
node tools/esp8266_opus_profile/run_stage_regressions.cjs
node tools/esp8266_opus_profile/audit_stage_profile.cjs
```

Building does not flash. Use app-only OTA explicitly, then restore live
firmware after tests. No raw UART control on the audio pin. Stage profiles
are rejected without diagnostic Opus/raw benchmark, with physical output,
or without fixedCPU160. These tests do not establish continuous playback.

## Rejected instrumentation attempts

The first physical attempt used `%llu`; SDK nano printf produced invalid
JSON. It is archived, not used as a valid stage measurement.

The following CCOUNT attempt also failed validation: this SDK resets
CCOUNT in `xPortSysTickHandle()` on every tick (`port.c:155–161`). Simple
subtraction across a preemption therefore produces near-2^32 bogus values,
not a natural counter wrap. Those stage durations are rejected. A check now
rejects any measured scope/total exceeding its enclosing decode window.
Raw attempts and memory failures are retained, not removed as outliers.
See the local pinned SDK `components/freertos/port/esp8266/port.c` and
`components/esp8266/source/esp_timer.c`.
