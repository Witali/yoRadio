# Autonomous continuity measurement

Diagnostic Opus PCM-queue builds only.48 static bytes, no new task, timer,
heap allocation or flash writes. Record a point after each committed PCM
callback and close a window after25 seconds of FreeRTOS tick time. Keep
decoded-frame and actual DMA-underrun counter deltas. Do not omit stalls:
if PCM resumes after60 seconds, that entire60-second interval is retained.
Generation change invalidates previous station results; counter/tick wrap
is handled modulo32. Reading never resets the counters or starts a window.

GET `/api/native/audio?quiet=1` reads the last completed window in a separate
small JSON response. It may be stale after a stop, so the test requires
valid current generation, age<=20s, duration25..27s, nonzero48k PCM,
PCM/wall ratio0.98..1.03 and exactly zero underruns. A valid snapshot alone
does NOT mean playback passed. These are not CPU utilization measurements.

`node tools/esp8266_opus_profile/run_quiet_window.cjs --output NEW.json`
waits65 seconds without any requests of its own, then reads the result.
Keep other clients closed when investigating HTTP measurement interference.
This does not replace WebUI-under-load tests, nor erase earlier failed runs.
It also does not replace acoustic verification of the analog output.
