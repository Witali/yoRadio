# CYD WebSocket status scheduling without a dedicated task

The CYD status poll previously reserved a 2,048-byte task stack solely to
enqueue HTTPD work every 100 ms. The new scheduler uses the existing ESP
Timer and default event-loop tasks. Status capture, commands and synchronous
frame sends still run on HTTPD; audio task bindings and buffer capacities
are unchanged. The optional RTC workspace placement remains independent.

## Dispatch and backpressure

The timer uses task dispatch and `skip_unhandled_events`. Its callback only
posts a payload-free application event with a zero-tick wait. The event
handler enqueues HTTPD work. The pinned SDK's HTTPD enqueue uses a socket,
so it is deliberately kept outside the timer callback. See the
[ESP Timer callback rules](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-reference/system/esp_timer.html#task-dispatch-specifics),
the [pinned event-post implementation](https://github.com/espressif/esp-idf/blob/7101770dc6db2667b3c477cc31365dd1acd6db4e/components/esp_event/esp_event.c)
and [HTTPD control socket](https://github.com/espressif/esp-idf/blob/7101770dc6db2667b3c477cc31365dd1acd6db4e/components/esp_http_server/src/util/ctrl_sock.c).

An atomic three-state owner tracks idle, event queued and HTTPD queued.
Repeated polls coalesce throughout both stages. A full event queue or failed
HTTPD enqueue returns to idle, allowing a later poll to retry. Late events
carry no server, descriptor or payload and cannot duplicate HTTPD work.
An event-post failure only releases an event-stage reservation: it must
preserve work that a concurrent late event has already handed to HTTPD.

The default event loop is already created by network startup. One handler
registration has process lifetime and is reused across failed starts and
Stop/restart. This avoids unregistering while unrelated network callbacks
hold the loop. The timer instance is created per successful start attempt
and deleted on stop; create/start/delete failures retain retryable state.
Lifecycle calls retain their existing serialized web-service startup and
rollback owner; producer callbacks can run concurrently on the other CPU.

## Stopping safely on both CPUs

Stopping an SDK timer is not treated as joining a callback. An atomic
admission bit and reference count cover both producer callbacks. Stop first
closes admission, then stops the timer and waits up to the existing 500 ms
for admitted callbacks to finish. A timeout retains the timer/server state
and rejects restart or server release until cleanup succeeds. A stopped
timer whose deletion fails also remains available for cleanup retry.

Callbacks that arrive after admission closes cannot touch the server.
After the producers drain, event-stage work can be discarded; already
queued HTTPD work remains owned by HTTPD. Its normal server-stop join still
precedes `websocket_service_server_stopped`. A late event after restart can
only trigger a current, coalesced poll rather than use an old server handle.

## Qualification boundary

Host ASan/UBSan tests pass 64 groups for the actual production core with deferred event
and HTTPD seams, a real concurrent blocked producer, bounded stop/retry,
late events, startup/delete failures, event-queue pressure and coalescing.
The failed-post/late-event interleaving first reproduced duplicate HTTPD
work, then passed after conditional reservation rollback replaced an
unconditional idle store.
Two exact negative variants omit stop drainage or event coalescing; both
fail their intended assertions. The previous task implementation still
passes its original 60 groups with the updated harness.

Actual memory savings and full TLS/HE-AAC, live-client and WebUI results
must be read from the accompanying saved SDK/QEMU observations. Removing
the nominal stack also removes a task control block, while the new timer,
handler and admission state consume memory. Neither the stack constant nor
a host result alone establishes recovered target heap or physical timing.
Physical Wi-Fi/audio and realistic network contention remain separate.

The [SDK/QEMU observations](../tests/results/cyd-ws-shared-scheduler-20261124/README.md)
show 17 initial tasks instead of 18 and 1,872–2,156 more free bytes in early
snapshots. All three outputs have a complete current-source HE-AAC pass;
one continuous-DAC output timeout is retained separately, so repeatability
is still open. [Six ordinary production exports](../tests/results/cyd-ws-production-20261124/README.md)
and [six opt-in RTC exports](../tests/results/cyd-ws-rtc-production-20261124/README.md)
are now saved from clean `b65437a1b`. Full normal Clang covers 320 project
units and 20 SDK frontend checks without new warnings or errors; the RTC
matrix additionally checks the changed whole WebSocket unit in all six
profiles. Image, ELF, OTA and static-frame checks do not replace runtime
or physical acceptance.

The [exact-length OpenETH RX follow-up](../tests/results/cyd-openeth-rx-exact-20261124/README.md)
now passes the complete TLS/HE-AAC/two-client workload on PDM, continuous DAC
and legacy DAC, plus a preselected legacy repeat, with zero allocation failures.
Only the diagnostic Ethernet driver changes; the normal network settings,
RTC-on workspace, application sources and audio task bindings stay fixed.
Earlier failures keep their original states. This does not qualify RTC-off
HE-AAC headroom, production Wi-Fi, physical DMA/audio or sleep/wake behavior.

The original final EOF health sample precedes the last asset read and peer
closure. The [new post-close controls](../tests/results/cyd-openeth-rx-exact-20261124/post-eof-native/matrix-summary.json)
now independently qualify that last interval on all three outputs: complete
TLS/HE-AAC/PCM/WebUI, zero allocation/write failures, and unchanged boot/EOF
generation. The PDM completion-notification counter rises from zero at EOF to 89
after close, separately from memory/write errors; physical timing remains open.
