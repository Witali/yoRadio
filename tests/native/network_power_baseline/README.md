# Historical audio/Wi-Fi power interleavings

```text
python tests/run-network-power-baseline.py --out .build/network-power-baseline-01
```

This is executable historical negative evidence, not a current firmware test.
The default source is exact Git `af8700e2e1d09fa3560544658d1f86b7223f26bb`.
All historical sources and fixture dependencies are frozen before composition
or execution. The full historical audio module runs with its real stream,
decoder and output owner loops, adaptive queue, reader and native state code.
The actual historical `network_service_set_streaming` body executes too.

A preprocessor call boundary pauses the stream only after its actual generation
guard and before its actual bool network call. It forwards the unchanged bool
argument to the original network function. No fixture sets an audio generation,
publishes a command, sets an owner ACK, or invents the expected power state.
Commands enter through actual `audio_service_play` and `audio_service_stop`.
The modeled driver records the mode requested by the actual network body.

The old stream receives one synthetic FLAC chunk then actual EOF, drains its
normal terminal path and disposes the HTTP client. With its terminal `false`
call paused, a new Play is accepted and advances generation. Resuming the old
call incorrectly switches to MIN_MODEM. The second schedule pauses the old
stream's initial `true` after its generation check, accepts Stop, then resumes
the obsolete call: it incorrectly switches back to NONE. Each known-bad safety
assertion must fail with exit 42 and its exact marker. A sequential control
executes the same old EOF path before accepting the next Play and must pass.

Historical maintenance-test RTOS, HTTP, codec, allocator, DMA and LED boundaries
are reused explicitly. The focused HTTP seam supplies a finite old stream and
an active new stream. Codecs and PCM values are synthetic; no decoder fidelity,
real SDK Wi-Fi power effect, hardware timing, RF or SMP-safety claim is made.
ASan/UBSan cover execution. Expected failing processes stop at the violated
assertion with live owners; leak detection is disabled there. The sequential
positive performs actual cooperative maintenance cleanup and joins all owners.
