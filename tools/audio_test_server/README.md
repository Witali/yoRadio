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

For FLAC depth and stereo-mode qualification:

```powershell
python tools/audio_test_server/generate_flac_depths.py --physical --output .build/flac-depth-tones
python tools/audio_test_server/generate_flac_depths.py --physical --dense-lpc --depth 24 --seconds 64 --output .build/flac-dense-long
python tools/audio_test_server/generate_flac_high_depth.py --seconds 64 --output .build/flac24-stress
python tools/audio_test_server/generate_flac_high_depth.py --seconds 12 --block-size 8192 --output .build/flac24-large
```

The first command creates 8/12/20/24-bit low-level tones. Without `--physical`,
it creates short arithmetic fixtures with full-scale boundary values; use those
for host comparison, not listening. The FFmpeg generator preserves 24 source
bits and exercises all four stereo modes. Manifests include encoded hashes and
the expected signed-16 PCM hash. Serve any manifest with `--fixture-manifest`;
these generators do not control or flash boards.

`--dense-lpc` uses all 32 predictor coefficients; `--seconds` controls physical
tone duration and repeatable `--depth` restricts source depths. Use at least
63 seconds of continuous input for a 60-second load test. Short EOF tests alone
cannot establish real-time decoding under sustained load.

C3-specific control, verification and the complete test plan are documented in
[ESP32C3_TESTING.md](../../docs/ESP32C3_TESTING.md). Other boards can reuse this
server with their own playlist/WebUI or test controller unchanged.

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

Run `python tests/test-audio-delivery-stats.py` for delay accounting, overflow,
and real localhost HTTP payload comparisons with timing enabled/disabled.
