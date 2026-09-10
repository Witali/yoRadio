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
An additional16 bytes of static DRAM hold the fourth set of counters;
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
