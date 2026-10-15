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
