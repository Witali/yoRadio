# Public HTTPS FLAC: intermittent output failure

## Quiet candidate evidence

The fresh public-file campaign on `idf61-tailq-20261015` reports **15/16**.
Automatic FLAC, both Opus cases and both Vorbis cases pass. Explicit FLAC
records **three new DMA completion-queue drops** and zero write errors in
the fixed 56.148-second steady observation. Its first decoded format is at
5.571 seconds; the increments occur between observations at 8.820 and 9.372
seconds, after the existing three-second decoded-playback warmup.

This is a real output-counter failure, distinct from the earlier FLAC
three-sample memory comparison. The unchanged memory, format, natural EOF,
decoder and settled-recovery checks now pass. Expected duration is 60.480 s;
observed decoded playback is 60.568 s. The same image's immediately preceding
automatic FLAC case has zero new drops over 56.049 s. Neither pass erases the
failed explicit case.

Around the event, the board reports FLAC 44.1-kHz stereo, RSSI about -59 dBm,
60–71 KB free heap and largest blocks of at least 43,008 B during the case.
Maximum paired WebUI response is 542.695 ms. Across all 863 campaign health
samples there are zero allocation, decoder and watchdog faults, one boot and
no failed traced HTTP request. These measurements do not identify whether
incoming data, decoding or scheduling caused the lost completions.

[Original reports, independent replay and event neighborhood](../tests/results/esp32c3-input-tail-quiet-20261015/final/)
retain the failed gate, exact boundaries and source hashes. Original firmware
and settings were restored, with playback stopped. The controller did **not**
run OTA after the failing file suite. The candidate remains unqualified.

## Diagnostic image

The diagnostic build starts from the exact quiet candidate configuration and
changes only `CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC=n→y`. Codec/DSP, TLS,
input capacity, output priority, QIO and clock settings remain the same.

| Identity | Value |
| --- | --- |
| Firmware version | `idf61-flacdiag-20261015` |
| Firmware source | `24201688` |
| App SHA-256 | `3b58c6eda0c9abc374e1b21321ce5a2810f07c383ed94aac826dee95c6d3a36b` |
| ELF SHA-256 | `6402283ef8db4472a5a756c1bddca4eb9592c3ce809b2c05666a1a910241bbf0` |
| App bytes | 1,476,608 |
| Added static data | 544 B, including the 540-B recorder |

The existing recorder exposes phase counts, the last 16 DMA-overrun events,
ages of output/PCM/input/network checkpoints and numeric queue occupancy.
There is no console output, sampler task or audio-data logging. It changes ISR
work and layout: success on this image cannot qualify the quiet image.
Build/link audits and the one-option configuration comparison pass.

[Saved diagnostic artifact](../firmware/development/esp32c3-idf61-flac-output-diagnostic/)
and [build evidence](../tests/results/esp32c3-flac-output-diagnostic-20261015/build/)
are retained. The physical controller runs up to three pairs of AUTO/explicit
FLAC observations on the same boot, stopping the campaign after the first
failed pair. Each pair completes its observations and recovery checks before
restoration. Preserve every failure and report overwritten events explicitly.
Use the ISR evidence to choose a targeted fix; do not increase input capacity
or change task priority without evidence of the bottleneck.

## Diagnostic public repeats

All three planned pairs complete: **24/24 checks pass**, covering six public
HTTPS FLAC observations on one boot. The six fixed steady windows total
338.530 seconds and have zero new completion drops or write errors. There are
no overwritten overrun events within those windows because no overrun occurs.
All 1,016 health samples have zero allocation, decoder and watchdog faults.
Minimum sampled free heap / largest block is 59,648 / 40,960 B. Natural EOF,
memory recovery, settings and final restoration pass.

The input pool has eight resident slots during every measured FLAC interval;
sampled occupancy ranges from two to eight. In the first pair, all 232 sampled
nonempty READY queues use their packet capacity fully (weighted and median
fill both 100%). Packing partial slots cannot improve those observations.
These samples do not identify the cause of the earlier quiet-image failure.

[Raw public repeats and ISR analysis](../tests/results/esp32c3-flac-output-diagnostic-20261015/physical/)
preserve the source/configuration references, each verdict and restoration.
The diagnostic timing/layout and live network differ from the failed quiet run;
do not treat these passes as a fix or as production qualification.

Next compare the same reference FLAC bytes over local HTTP, first without
intentional delay and then with 100/250/500-ms host pauses at fixed byte offsets.
Use unpaced file delivery and a requested 4-KiB socket send buffer, so average
bitrate pacing does not itself starve variable-bitrate frames. This isolates
controlled delivery gaps from TLS and the public server, but cannot by itself
attribute the original HTTPS fault. Keep failed output gates and actual host
pause durations, including any overwritten ISR events.

## Controlled delivery: input starvation reproduced

Both runs use the same independently decoded 6,663,512-byte FLAC reference,
unpaced local HTTP and requested/actual 4,096-byte host send buffers. Both
deliver the complete file, reach natural EOF, recover memory and preserve
settings. The unchanged diagnostic firmware stays on one boot. The no-pause
control passes **8/8**, with zero output increments over 55.281 seconds.

| Requested host pause | Measured host pause | Byte offset | New completion drops |
| --- | ---: | ---: | ---: |
| 100 ms | 106.340 ms | 2,097,152 | 0 |
| 250 ms | 261.781 ms | 3,670,016 | 4 |
| 500 ms | 504.150 ms | 5,242,880 | 26 |

The paused run is **7/8**, retaining its output failure. All three pauses pass
the original timing tolerance (-5/+50 ms), and their observation intervals
are separate. The phase histogram records 25 overruns with OUTPUT_WAIT +
DECODER_WAIT + STREAM_READ and five OUTPUT_WAIT-only events during refill.
Of 30 events, 26 retain detailed timestamps; **four details were overwritten**.
Output checkpoints are only 0.314–4.999 ms old. A sampled input queue is empty
during the longest pause, and retained HTTP-read ages reach 404.270 ms. Together
these observations support exhausted input/PCM buffering in this experiment,
rather than an output task that is not being serviced. They do not identify
the cause of the earlier public HTTPS fault.

All 298 health samples have zero decoder, allocation and watchdog faults.
Minimum sampled heap / largest block is 63,984 / 47,104 B. Original application
and private settings are restored, stopped. The
[controlled evidence](../tests/results/esp32c3-flac-output-diagnostic-20261015/controlled/)
includes raw pauses, full transfer statistics, source hashes and ISR analysis.

Next test `CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS=8` versus the current value 4:
up to 12 resident slots after FLAC initialization, subject to the saved target
and the existing allocation guard. Four additional slots provide 8,240 bytes
of packet storage, plus allocator overhead. AAC expansion stays zero and the
TLS reserve is unchanged. Compare this exact file and pause schedule before
considering a default change, then verify HTTP/HTTPS, FLAC→AAC replacement,
EOF/Stop memory recovery and the quiet image. A finite queue cannot cover
arbitrarily long delivery outages.

## Capacity experiment: compiled limit is not the allocated capacity

The first `FLAC_INPUT_EXTRA_SLOTS=8` image passes its build/link checks and
changes no other configuration option from the diagnostic baseline. However,
both physical runs still have **eight resident slots** throughout their fixed
steady windows. The no-pause control passes 8/8 with zero drops; the paused run
passes 7/8 with 29 drops (3 around the 250-ms pause and 26 around the 500-ms
pause). There are no allocation, decoder or watchdog faults. Original firmware,
settings and stopped playback are restored. This is **not** an 8-versus-12-slot
comparison and does not demonstrate the effect of increasing input capacity.

[Original capped run and exact test sources](../tests/results/esp32c3-flac-input12-20261015/controlled/)
retain the failed output gate. The artifact directory uses the original
`input12` experiment name; that name is not a measured allocation count.

The saved WebUI setting `abuff` determines the queue's target at boot:
`ceil(abuff * 1600 / 2060)` slots. `adaptive_input_set_limit()` clamps the
FLAC limit to that target. The supported setting is 5..14 blocks, so the
largest user-configurable target is **11 slots**, not 12. Raising only the
build option cannot bypass this cap. The running queue is created once;
changing `abuff` requires rebooting before measuring its capacity.

The matched experiment temporarily uses `abuff=14` for both images: the
baseline permits 4 minimum + 4 extra = 8 slots, while the candidate permits
up to 12 but is capped at 11. Three additional slots contain **6,180 bytes**
including packet headers (6,144 audio-data bytes), plus allocator overhead.
AAC growth, TLS reserve and DSP remain unchanged. Each run explicitly checks
that the expected resident capacity was actually reached. Private settings
stay in memory; the controller restores the original setting and application
even if an output test fails. The temporary setting is an experiment, not a
new production default.

### Matched target results

Both images use the same temporary 14-block setting, reference bytes, host,
unpaced delivery and pause byte offsets. The measured resident count stays at
8 or 11, respectively, throughout each fixed steady observation window.

| Resident slots | Delivery | Passed checks | Completion drops | Write errors | Minimum sampled heap / largest block |
| ---: | --- | ---: | ---: | ---: | ---: |
| 8 | No imposed pauses | 9/9 | 0 | 0 | 64,260 / 49,152 B |
| 8 | 100/250/500-ms pauses | 8/9 | 51 | 0 | 63,972 / 45,056 B |
| 11 | No imposed pauses | 9/9 | 0 | 0 | 57,208 / 40,960 B |
| 11 | 100/250/500-ms pauses | 8/9 | 303 | 0 | 57,432 / 40,960 B |

All 578 health samples have zero allocation, decoder and watchdog faults.
Each image remains on one boot for its two cases. EOF/Stop recovery checks,
settings equality and final restoration pass. These are sequential physical
trials, not identical network delivery traces.

The 11-slot paused case fails the original three-sample natural-EOF check:
its last two samples show `stream ended` at 7.471 and 7.976 seconds into the
eight-second EOF observation, while the preceding sample still shows playback.
This is late confirmation, **not evidence of a permanently stuck EOF status**.
Because that assertion precedes the output assertion, the raw case reports EOF
failure first. Independent replay of the unchanged steady window also finds
303 completion drops; the earlier assertion must not hide them. Neither the
deadline nor the required confirmation count was relaxed.

The paused trials also have unexpected input starvation outside the deliberate
250/500-ms delays. With eight slots, 19 drops occur around playback seconds
14.847–16.092, before the first imposed pause at 19.768 seconds. With eleven
slots, 283 drops span 19.365–26.882 seconds; the imposed 100-ms pause near the
start of that interval actually lasts 110.530 ms. Input occupancy repeatedly
reaches zero. Most phase counts include output wait, decoder wait and HTTP
read; these phases are not scheduler states and do not identify a Wi-Fi,
host, TCP or firmware root cause. Retained event details cover 43/51 and
119/303 drops respectively; **8 and 184 event details were overwritten**.
RSSI ranges from -71 to -59 dBm in both paused trials, which alone cannot
explain the difference.

Consequently, 51 versus 303 is an observed result, **not a measured causal
regression from adding three slots**. The extra capacity costs approximately
6 KiB of packet memory but has not demonstrated reliable improvement here.
Keep production defaults unchanged. Next isolate the unplanned delivery
stalls and reproduce the original quiet HTTPS fault before choosing a buffer
policy; do not use successful control runs to qualify this candidate.

[Matched reports, ISR replay, delivery timing, exact sources and restoration](../tests/results/esp32c3-flac-input12-20261015/matched/)
retain both failures. The saved diagnostic image remains unqualified.

## Sender TCP_NODELAY comparison

The previous long starvation interval coincides with host writes accepted at
roughly 43–79 KB/s instead of the usual 110–120 KB/s. Almost all wall time is
inside socket writes; the measured outside-write time is approximately
0–1 ms per window, except for the deliberately inserted pauses. This argues
against long pauses in the Python loop between writes. It does **not** separate
receiver backpressure, network delay, TCP behaviour or host scheduling during
the blocking calls.

The fixture server writes 1-KiB pieces. To test sender coalescing, it now has
an optional `tcp_nodelay` policy and records the actual socket option. Its
default behaviour is unchanged. The option affects only that server socket;
see [Microsoft's description](https://learn.microsoft.com/en-us/windows/win32/winsock/ipproto-tcp-socket-options).
Fourteen host tests pass, including HTTP/HTTPS byte identity and exact pause
positions. An initial restricted-sandbox attempt could not access local sockets
or temporary certificate directories; the saved successful run used the normal
host environment. No OS TCP settings or trust stores were modified.

All four physical cases use the **same eight-slot diagnostic image on one
boot**, original saved settings, reference bytes, send buffer and pause offsets.
The socket option is read back in every case; the maximum and steady resident
capacity remain eight.

| TCP_NODELAY | Delivery | Passed checks | Completion drops | Write errors |
| --- | --- | ---: | ---: | ---: |
| Off | No imposed pauses | 9/9 | 0 | 0 |
| Off | 100/250/500-ms pauses | 8/9 | 30 (0/4/26 around the pauses) | 0 |
| On | No imposed pauses | 9/9 | 0 | 0 |
| On | 100/250/500-ms pauses | 8/9 | 30 (0/3/27 around the pauses) | 0 |

All 596 health observations have zero allocation, decoder and watchdog faults.
Minimum sampled heap/largest block is 63,996/47,104 B. Every file reaches
confirmed natural EOF and passes memory recovery; original firmware/settings
are restored, stopped. The two failed output gates remain failed. Detailed ISR
history retains 20/30 and 19/30 events, with 10 and 11 overwritten respectively.
No earlier unexpected multi-second starvation recurs in these four trials.

**No benefit from disabling Nagle was demonstrated.** This comparison does not
explain the original quiet HTTPS fault or qualify the candidate. Ordinary
approximately 100-ms blocked writes cannot alone be called a network defect:
FFprobe finds 578 FLAC packets of 104.490 ms and one final packet of 84.898 ms
in this reference (encoded frame sizes 7,119–13,965 bytes), so frame decoding
and output backpressure can also produce bursty input demand.

The pinned ESP-IDF `esp_http_client_read()` source exposes another testable
latency mechanism: it tries to fill the requested length, returning partial
bytes on timeout, EOF or error. Our caller requests 2,048 bytes with a 250-ms
read timeout. A partial body can therefore wait inside that call before being
offered to the decoder. This is source-based reasoning, **not proof that it
caused the observed fault**. Next compare returning smaller reads or a shorter
read timeout, one change at a time, retaining fatal-TLS handling, HTTP framing,
EOF, Stop responsiveness, full codec support and memory checks. Do not change
the connection timeout or discard authenticated partial bytes.

[Reports, host tests, socket policies, frame sizes and pinned reader source](../tests/results/esp32c3-flac-tcp-20261015/)
preserve the failed comparisons and restoration evidence.
