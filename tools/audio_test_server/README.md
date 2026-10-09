# Shared audio test server

This server works with ESP32-C3, ESP8266, CYD and other HTTP audio players.
It only serves original synthetic fixtures; it never controls or flashes a board.

```powershell
python tools/audio_test_server/server.py --host 0.0.0.0 --port 8770
```

Open `http://PC_LAN_IP:8770/manifest.json` for names, layouts and hashes. Give
any player `http://PC_LAN_IP:8770/file/mp3-320` or another listed fixture URL.
The HTTP server needs only Python's standard library. Optional HTTPS uses
`--cert`/`--key`; each board applies its own normal certificate validation.

Routes: `/file/NAME` (finite), `/stream/NAME` (continuous ADTS AAC),
`/drop/NAME`, `/stall/NAME`, `/error/NAME`, `/redirect/NAME`, `/jitter/NAME`.
No arbitrary local paths are exposed. FLAC and Ogg files are not concatenated
to pretend they are continuous streams.

### Delivery rate for memory investigations

Paced routes default to **1.02 times** the fixture's audio rate. That deliberate
surplus gradually fills receive queues; a fall in free heap during this phase
alone does not identify a decoder leak. Use `--pacing-ratio 1.0` for a control
with no deliberate rate surplus, or retain `--pacing-ratio 1.02` for the existing
stress condition. Clock differences and burst delivery can still fill queues.
The event log records the selected ratio. Compare both conditions with unchanged
playback, allocation-failure and memory-recovery checks.

`--unpaced-files` overrides this rate only for finite file downloads; live AAC
and fault routes remain paced. The C3 `tools/esp32c3_tests/run.py` runner accepts
the same option for its built-in HTTP and HTTPS servers. An external
`--https-origin` must be configured separately. These settings do not alter the
specialized `tls_records.py` server.

Generate additional continuous files with FFmpeg/FFprobe:

```powershell
python tools/audio_test_server/generate.py --output .build/audio-60s --seconds 60
python tools/audio_test_server/server.py --fixture-manifest .build/audio-60s/manifest.json
```

Use `--codec`, `--rate`, `--channels` to select the matrix. Manifest output
layouts come from FFprobe, including Opus's 48 kHz decoded rate. The existing
FDK fixtures cover HE-AAC/v2; the generator's native AAC encoder produces LC.
Large soak fixtures belong in ignored `.build/`, not versioned firmware.

For high-bitrate 48 kHz stereo stress files with explicitly 16-bit PCM input:

```powershell
python tools/audio_test_server/generate_stress.py --output .build/audio-stress-60s --seconds 60
python tools/audio_test_server/server.py --fixture-manifest .build/audio-stress-60s/manifest.json
```

This uses fixed-seed noise plus tones, MP3 320 kbit/s, FLAC level 8, Vorbis q10
and Opus 510 kbit/s. The manifest records source/encoded hashes, encoder options
and FFprobe layouts. Use a new output directory to preserve earlier fixtures.
These transport/load fixtures supplement the general format matrix; they do
not replace 24-bit FLAC or other depth/rate qualification.

## Full-sized TLS record tests

`tls_records.py` serves continuous ADTS AAC with measured TLS 1.2 AES-GCM record
sizes. `/small/NAME` uses 1024-byte plaintext records, `/large/NAME` uses the full
16,384 bytes, `/grow/NAME` changes from small to large after 30 seconds, and
`/alternate/NAME` alternates. TCP packet sizes are not TLS record sizes.

```powershell
python tools/audio_test_server/record_test_ca.py --host PC_LAN_IP --output .build/record-ca
python tools/audio_test_server/tls_records.py --host PC_LAN_IP --cert .build/record-ca/server.pem --key .build/record-ca/server.key --output .build/tls-records.json
```

The generated CA is valid for two days. Add `.build/record-ca/ca.pem` only to a
dedicated laboratory firmware's extra certificate bundle, retaining normal
certificate and hostname verification. Do not install it into the OS or ship
it in a production image. The CA signing key is not saved; the server key stays
in ignored local storage. Keep the normal public roots and restore the normal
firmware after testing. A stock production image must reject this local CA.

The server contains no board commands and can be used by other boards with
their own test-only trust configuration. It retains only record types/lengths,
phase timestamps and socket-write counters. `python tests/test-tls-record-server.py`
checks actual encrypted record lengths (1048 and 16,408 bytes for this cipher),
exact audio bytes across repeated fixtures, and rejection with ordinary trust.
Host writes are not proof of bytes received or decoded by a board.

Normal server completion sends TLS `close_notify`; the host test disables
Python's suppression of abrupt TLS EOF and requires the closing alert. An
intentional Stop can still interrupt a write, recorded separately. The C3
record runner accepts `--seconds 600` for a complete ten-minute observation;
the server allows an additional 15 seconds so it does not end the stream before
the observation finishes. Its total duration is bounded to 615 seconds.

Both the standalone record server and C3 record runner accept
`--pacing-ratio 1.0` for real-time AAC delivery. The default remains `1.02`
to reproduce historical tests. Specify the ratio explicitly in new reports;
2% excess delivery can fill receive queues during long tests. This option
changes delivery deadlines only, preserving encoded bytes, record sizes,
TLS verification and the HTTP body. Each connection records the selected
ratio and target audio bytes per second. Socket backpressure may slow actual
delivery, so declared pacing alone is not a board-consumption measurement.

The 16 KiB plaintext bound follows [RFC 5246 §6.2.1](https://www.rfc-editor.org/rfc/rfc5246#section-6.2.1).
The test measures the encrypted lengths too; the TLS 1.2 GCM record construction
is specified in [RFC 5288 §3](https://www.rfc-editor.org/rfc/rfc5288#section-3).

For FLAC depth and stereo-mode qualification:

```powershell
python tools/audio_test_server/generate_flac_depths.py --physical --output .build/flac-depth-tones
python tools/audio_test_server/generate_flac_depths.py --physical --dense-lpc --depth 24 --seconds 64 --output .build/flac-dense-long
python tools/audio_test_server/generate_flac_depths.py --physical --irregular-lpc --depth 24 --seconds 64 --output .build/flac-irregular-long
python tools/audio_test_server/generate_flac_high_depth.py --seconds 64 --output .build/flac24-stress
python tools/audio_test_server/generate_flac_high_depth.py --seconds 12 --block-size 8192 --output .build/flac24-large
```

The first command creates 8/12/20/24-bit low-level tones. Without `--physical`,
it creates short arithmetic fixtures with full-scale boundary values; use those
for host comparison, not listening. The FFmpeg generator preserves 24 source
bits and exercises all four stereo modes. Manifests include encoded hashes and
the expected signed-16 PCM hash. Serve any manifest with `--fixture-manifest`;
these generators do not control or flash boards.

`--dense-lpc` uses 32 alternating coefficients with equal magnitude.
`--irregular-lpc` uses 32 nonperiodic nonzero coefficients and exercises the
general predictor without the rolling-sum shortcut. Benchmark both when
evaluating LPC optimizations; they are different workloads.
`--seconds` controls physical
tone duration and repeatable `--depth` restricts source depths. Use at least
63 seconds of continuous input for a 60-second load test. Short EOF tests alone
cannot establish real-time decoding under sustained load.

C3-specific control, verification and the complete test plan are documented in
[ESP32C3_TESTING.md](../../docs/ESP32C3_TESTING.md). Other boards can reuse this
server with their own playlist/WebUI or test controller unchanged.

## HTTPS body completion fixtures

From the repository root, run a server usable by any board:

```powershell
python -m tools.audio_test_server.tls_framing --host 192.168.100.253 --cert <server.pem> --key <server.key> --seconds 600 --output .build/framing-events.json
python tests/test-tls-framing-server.py
```

Use the laboratory certificate workflow in the TLS-record section; keep
certificate and hostname verification enabled. Routes are
`https://<host>:8773/<mode>/<fixture>`. The eight modes are `length-notify`,
`length-raw`, `length-short`, `chunked-notify`, `chunked-raw`, `chunked-short`,
`close-notify`, and `close-raw`. All send the complete fixture audio. The
`length-short` mode promises one extra byte; `chunked-short` omits the terminal
chunk. Both send a TLS close alert. The `raw` modes deliberately omit that alert.

The host test checks exact HTTP bytes and TLS closure using a verifying client
that rejects ragged EOFs. Saved server events describe the sent bytes/records,
not their reception or playback by a board. A fresh output path is required;
the server never saves private keys or received request headers.

## Optional delivery timing

Use `--delivery-stats --events-output .build/audio-delivery.json` to save bounded
per-request timing when the standalone server exits with Ctrl+C. The C3 load
runner accepts `--delivery-stats` and retains these events in `report.json`.
This works for any board and preserves payloads, pacing, routes and TLS behavior.

Each roughly one-second window records completed socket-write bytes/count,
total and maximum write time, and maximum lateness against the pacing schedule.
Absolute timestamps use the host's monotonic clock, allowing comparison with
the controller's status/serial observations on the same host. Unpaced files
have no scheduled delivery deadline. A long blocked write creates a longer
window; gaps are not filled with invented samples.

These are writes accepted by the host socket API, **not TCP acknowledgements or
bytes decoded on the board**. A failed partial write may have sent some bytes
that cannot be counted as a completed write. Combine this evidence with the
board's compressed-input/CPU/TCP statistics before attributing a playback gap.
At most 4096 windows are saved per request; `dropped_windows` reports truncation.
An interrupted worker can leave `finished=false`. Reject incomplete captures
when comparing full-stream totals. Timing is disabled by default.

## Reproducible delivery pauses

`--delivery-pause BYTE_OFFSET:SECONDS` pauses before sending the byte at an
exact position in the response body. Repeat it in increasing byte order;
at most 64 pauses of more than zero and at most two seconds are allowed.
Positions count encoded bytes, not PCM samples or TCP bytes. Chunk boundaries
are split when necessary; payload bytes and their order are unchanged.

```powershell
python tools/audio_test_server/server.py --fixture-manifest .build/audio-stress-60s/manifest.json --unpaced-files --delivery-stats --send-buffer-bytes 4096 --delivery-pause 2000000:0.05 --delivery-pause 4000000:0.10 --delivery-pause 6000000:0.20 --events-output .build/audio-pauses.json
python tests/test-audio-server-pauses.py
```

This works over HTTP or HTTPS and with any board. Each connection starts a
fresh schedule; continuous ADTS counts bytes across repetitions and changing
segments. A pause at or beyond finite EOF is not executed. Compare requested
`pause_schedule` with actual `pauses`, their byte positions, completion flags
and elapsed durations. Stopping the server interrupts a pending pause.

Pauses do **not** shift normal pacing deadlines. Paced delivery catches up
after a pause; unpaced file delivery resumes as fast as TCP permits. This
avoids the persistent rate deficit of repeatedly adding delay to every
deadline. Existing `/jitter` behavior and all default settings are unchanged.

`--send-buffer-bytes` optionally requests `SO_SNDBUF` (1 KiB to 1 MiB).
Events record both the requested and actual OS value. This reduces host
buffering but does not eliminate in-flight TCP/TLS bytes or receiver queues.
A host send pause is **not proof of an equal pause at the board**. Correlate
these events with decoder-input, DMA and playback observations. Event start/
end timestamps use the existing monotonic clock; pause elapsed durations
use the higher-resolution `perf_counter` clock, without mixing their epochs.

Run `python tests/test-audio-delivery-stats.py` for delay accounting, overflow,
and real localhost HTTP payload comparisons with timing enabled/disabled.

## Short PCM tail fixtures

Generate 30 deterministic lossless FLAC files without contacting a board:

```powershell
python -m tools.audio_test_server.generate_pcm_tails --output .build/pcm-tail-fixtures
```

FFmpeg must be available on PATH, or supplied with `--ffmpeg <path>`. Use a new
output directory. The generator checks an exact signed-16 PCM round trip and
saves encoded/PCM hashes in `manifest.json`. Cases combine 1, 127, 511, 512 and
513 source frames, mono/stereo, and 8/44.1/48 kHz. These fixtures exercise very
short EOF and partial output blocks; they do not measure sustained playback.

A FLAC final block may contain fewer than 16 samples, while STREAMINFO block
bounds remain at least 16; see [RFC 9639](https://www.rfc-editor.org/rfc/rfc9639.html#section-4.1).
Any board can use these files through the existing server's
`--fixture-manifest .build/pcm-tail-fixtures/manifest.json` option.
The C3-specific [PCM-tail runner](../../docs/ESP32C3_TESTING.md#pcm-tail-submission-and-eof)
also checks the driver-submitted frame count and final playback status.
