# Actual CYD Ogg gain metadata and PDM output diagnostic

This new sibling compiles complete current audio service, output renderer,
state, health, decoder registration, output metrics, settings and normalizer
translation units. Real SDK tasks, queues, allocations and client ownership
remain active. Synthetic HTTP transport and public PDM/GPIO hardware calls are
the seams. Forwarding output wrappers invoke the actual production functions.
No control state, ACK, generation or decoder internals are injected.

Three lifecycle fixtures exercise real EOF, partial Stop/discard/reopen and
maintenance/token/stale-token/resume. Fourteen complete gain/volume cases and
one nine-link same-HTTP chain cover zero, +/-6 dB, +20/+48 dB, signed extrema,
mute, final saturation and the +48 dB/low-volume anti-early-clipping case. The
chain changes gain and includes Vorbis and zero-gain links without an
intermediate PCM terminal. Original core/priority/stack profiles are required.

The wrapper's unchanged complete stereo PCM is checked against the frozen
stock references. Complete mono PDM driver bytes are compared with independent
Decimal combined-gain hashes; zero gain follows the exact legacy Q15 rules.
Bias ramp/preload and final zero padding are observed separately. The first
Vorbis playback also captures every unchanged stock integer PCM byte locally,
requires its established full hash, and lets the outer controller derive and
compare independent legacy mono goldens after execution. Native completion is
explicitly pending that oracle; the controller cannot mark PASS before it.
No PCM/hex console payload or executable is suitable for public evidence.

Settings disable the actual adaptive normalizer through its public API for
this deterministic gain matrix. This does not qualify enabled-normalizer DSP,
physical PDM timing, external HTTP/TLS/TFT resources, or general codec quality.
Canaries, light heap poisoning, integrity checks and both idle watchdogs remain
enabled. Public-driver writes and heavy UART observation yield diagnostically.

Use a fresh ignored output directory. The resulting image is diagnostic only
and must not be flashed or handed off as production firmware.

```text
python -B tests/run-cyd-ogg-gain-task-qemu.py --preflight-only --output .build/<fresh-campaign>
python -B tests/run-cyd-ogg-gain-task-qemu.py --output .build/<fresh-campaign>
```
