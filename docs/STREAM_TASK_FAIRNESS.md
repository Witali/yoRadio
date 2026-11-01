# Stream-owner fairness on CYD and ESP32-C3

Continuously available HTTP input need not block its reader. The stream owner
could repeatedly read and forward short fragments without giving the lower
priority idle task an opportunity to run. The same structural gap existed in
the CYD and C3 HTTP body loops, including C3's immediate EAGAIN path.

The original local `cyd-family1-playback-task-20261101-05` capture is NONPASS:
the real SDK CPU0 idle watchdog fired during complete 120ms Opus playback with
one-byte reads. Its frozen ELF places the interrupted stack in `stream_audio`
and `stream_body_feed`. The immediate HTTP transport is a diagnostic seam;
this is an observed SDK scheduling failure, not a physical throughput or timing
measurement. The diagnostic used the unchanged 20s panic watchdog. No native
C3 reproduction or active C8/120ms application acceptance follows from it.

[Espressif's task-watchdog documentation](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-reference/system/wdts.html#task-watchdog-timer-twdt)
describes idle-task monitoring as a way to detect prolonged work without
yielding. Resetting that watchdog from the stream owner would conceal the
missing idle opportunity.

## Implementation

The shared [elapsed-time budget](../idf/components/native_stream/include/stream_fairness.h)
is local to each HTTP connection. At each loop boundary, elapsed time of at
least 20,000us requests a real one-tick `vTaskDelay`. The owner rebases the
budget after that delay and continues at the loop condition, so Stop, failure
and probe deadlines are checked before another read of the old client.

This covers positive audio reads, ICY-only fragments and immediate retries.
It imposes no read-count or byte-count cap: fragments completing within a
slice incur no fairness delay. Elapsed wall time includes time spent blocked;
a blocking operation can therefore be followed by one extra tick. A single
operation can also exceed the slice before the next loop check. The slice is
not a hard execution-time guarantee or a measured throughput improvement.

The CYD [stream task](../idf/esp32-cyd2usb-native/main/audio_service.c) remains
core0/priority3/6144B, decode core1/priority5/16384B and output
core1/priority6/4096B. The C3 [stream task](../idf/esp32c3-oled-native/main/audio_service.c)
keeps its original single-core profile. Codec bytes, queue ownership, EOF,
retry/availability policy, watchdog subscriptions and timeouts are preserved.
The helper allocates nothing and never feeds a watchdog.

## Verification

- [CYD HTTP/ICY tests](../tests/run-cyd-stream.py): 55 stream cases and 80
  settings requests pass with ASan/UBSan. New cases check exact positive-read
  audio and ICY output, no per-read delay without elapsed time, Stop during the
  actual delay with no subsequent read, and unsigned timer wrap/rebase.
- [C3 retry tests](../tests/run-stream-connection-retry.py): 42 plain, 42
  retained/adaptive and 47 growth/power cases pass with ASan/UBSan. New cases
  include positive and EAGAIN cancellation. The existing old-generation
  terminal marker remains observable; the new test does not invent a different
  production EOF contract.
- [Power-policy tests](../tests/run-audio-power.py): C3 ten, CYD nine and CYD
  receive nine groups pass. Current default-off TLS callback and output-metrics
  headers are frozen as actual dependencies of the existing test seams.
- Actual Xtensa GCC syntax-checks the complete updated CYD translation unit
  with pinned SDK6.0.2 headers; all 78 frozen inputs remain unchanged. This is
  compilation evidence, not execution of the new fairness policy.

The old missing-header and new Stop-observer failures remain separate local
NONPASS captures. Full updated SDK/QEMU tasks, production exports, own-SDK C3
compilation/lint and physical radio/TFT/audio qualification are later gates.
Do not relabel the old watchdog capture as passing after changing the source.
