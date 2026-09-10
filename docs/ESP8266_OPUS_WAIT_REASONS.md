# Opus live waits: separate cause before changing scheduling

2026-09-10. Goal remains real HTTP Opus playback for at least20 seconds
without DMA misses, plus preserved PCM and WebUI control. Raw decoder CPU
results alone do not qualify the complete output path.

Fresh DLF24 HTTP observations on the existing ff49a46 live image showed
continuing RX/PCM but795 DMA misses over27.999 seconds, only27.040 seconds
of PCM. The four-row stage profile attributed588 misses to its combined
wait row,52 to decode,77 to output and73 to refill;5 were unattributed.
No transport timeout was latched in that interval. This does not prove
network health or prove an unnecessary post-decode sleep: the combined row
also included waiting for missing compressed input. Startup was recorded
separately and failed the steady-state gate; it is not silently discarded.

## Diagnostic change only

Profile v2 keeps read/decode-exclusive/output as rows0..2 and splits waits:

- Row3 `post_decode_wait`: existing one-tick pacing after process_one succeeds.
- Row4 `input_wait`: existing wait after process_one needs more compressed bytes.

Neither wait, task priority, input/PCM/DMA size nor decoder is changed.
An additional16 bytes of static DRAM hold the fifth set of counters;
the five rows total80 bytes. No ISR, new allocation, per-sample operation
or timing call is added. The JSON snapshot is16 bytes larger on the stack.
Counters still measure wall time including preemption, NOT CPU utilization.

`run_stage_wall.cjs` accepts archived v1/four-row profiles and explicit
v2/five-row profiles, rejects mixed/unknown versions, retains every miss,
and keeps the strict continuity gate. Host C tests exercise actual counters,
exclusive nested output, both wait causes, rollover and bounded JSON under
ASan/UBSan. No change is accepted as an audio performance fix by these tests.

Next: physical repeated samples. If input waits dominate, inspect arrivals
and buffering; if post-decode waits dominate, revisit pacing with the now
faster FIR decoder. The previous pre-FIR DMA-aware-yield test did not prove
a useful gain and must not be represented as already successful.

## Clock race found during measurement

The first v2 image later reported a read maximum4294967115us (uint32(-181)).
Those microsecond statistics are not qualified; preserve the raw reports
and their independent DMA counters. This is not evidence of a71-minute stall.

The local SDK and [Espressif timer source](https://github.com/espressif/ESP8266_RTOS_SDK/blob/master/components/esp8266/source/esp_timer.c)
read the software microsecond accumulator and CCOUNT without exclusion.
The [tick handler](https://github.com/espressif/ESP8266_RTOS_SDK/blob/master/components/freertos/port/esp8266/port.c)
adds elapsed time and resets CCOUNT, so a tick between the two reads can
produce an inconsistent timestamp. This race is a concrete candidate for
the observed negative duration, not proof that it caused the audio pauses.

Diagnostic timestamps now use a critical section ONLY around the clock
snapshot; measured work/decoding/network waits remain interruptible. Host
tests require the clock call to be protected and balanced, retaining the
rollover checks. Physical qualification of the corrected clock is pending.
The report reader flags implausible maxima without discarding DMA misses.

Separate existing clock-rate mismatch: nominal48k PDM is clocked at
160MHz/(8*13*32) =48076.923Hz, ratio625/624. The current resampler uses
nominal48k. This can consume76.923 extra source samples per second and
eventually drain finite read-ahead; it cannot explain all observed large
pauses by itself. Test compensation separately, preserving modulator state
and accounting for the resulting deliberate resampling change.

## Physical checkpoint and next A/B

The first ten v2 windows completed:0/10 continuous; two have missing HTTP
observations. All eight observed windows attributed zero misses to voluntary
post-decode pacing. The other misses remain, including reconnect intervals.
[Raw attempts and clock-aware reanalysis](../firmware/development/esp8266-opus-wait-v2/CHANGELOG.md).

Source5147be3 now has matching diagnostic builds with1024 and2048 bytes of
Opus input. Production remains1024; nondefault values require
`-Diagnostic -EnableOpus -OpusInputBytes 2048`. The6144-byte scratch and4096-byte
post-init reserve are unchanged. Seventeen host tests passed, including the
actual bridge/arena lifecycle with2048 input, OOM, switches and cleanup.
The controlled physical comparison is not yet complete; no buffer increase
is accepted as a working fix at this checkpoint.
