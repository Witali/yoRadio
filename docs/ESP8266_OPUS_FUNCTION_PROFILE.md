# Opus: function-call profile on ESP8266

Diagnostic-only `-OpusFunctionProfile`, CPU160/QIO40, raw benchmark, PCM48k
mono. The baseline Opus GCC-ASM objects and algorithm are unchanged. GNU
linker `--wrap` measures14 selected cross-object symbols. Same-object,
static/inlined functions are NOT independent observations: their work is
included in the nearest measured parent's self time. In particular, bands
contains quant_partition/quant_band and vector rotations can remain inline.

Every row reports call count, inclusive/self CPU and wall microseconds,
maximum inclusive CPU and wall duration. CPU is the SDK accumulated task
runtime plus current running slice, read coherently with its own timer;
other tasks are excluded, ISR time charged to the task is not. Wall includes
preemption. The downloaded SDK is untouched: the build-local tasks.c adapter
includes the original and appends only a getter. Its archive member basename
is preserved, so SDK linker rules still apply. Counter wrap/overflow, broken
nesting and longjmp-unwound scopes invalidate the profile.

The outer decode wall window also uses this getter in function-profile
builds. SDK runtime statistics use esp_get_time(), whereas esp_timer_get_time()
combines g_esp_os_us and CCOUNT. They must not be treated as one identical
clock for strict nested-window checks. The first three v1 pilot reports are
retained separately: the third failed that check (538 us excess over120
packets); none of the pilot series is used in the final function statistics.
No decoder/PCM error occurred in those pilots. The ordinary control timing
path remains unchanged.

Self time subtracts measured direct children. Consequently all self rows sum
to100% of the measured root; inclusive rows overlap and must not be summed.
Root self includes unmeasured functions and measurement bookkeeping, not
just the source statements of the root wrapper. Counts per second refer to
one second of decoded audio (samples/48000), NOT wall execution speed.

One bounded392-byte row array (14x28) is reused across fixtures. Only the last
completed fixture remains in the report (the selected corpus ends in192kbps).
The warmup round is excluded. No PCM/packet buffer or additional task is
allocated. Completed data are exposed by the existing benchmark endpoint;
live partial rows are hidden.32 empty clock pairs characterize minimum/maximum
clock cost, not full wrapper/cache overhead; no speculative cost is subtracted.
A matching uninstrumented control and repeated board trials are required.

Tests cover nesting, preemption, timestamps wrapping, totals overflowing,
OOM unwinding, disabled instrumentation, ABI and full exact PCM for five
fixtures plus mixed-mode PLC/reset. Host timing is synthetic, not LX106 speed.
Production remains uninstrumented and no playback qualification is implied.

```powershell
node --test tests/esp8266-opus-function-profile.test.js
node tools/esp8266_opus_profile/run_function_regressions.cjs
```

Physical results and measured instrumentation overhead will be appended after
the on-device series. Restore ordinary radio by OTA after profiling.
