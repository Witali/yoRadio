# Opus HTTP priority control — 2026-09-09

Diagnostic source 5e96884, 882304-byte app. WebAudioPause OFF uses HTTP
priority 5 instead of the short-pause profile's priority 6. Both use audio
priority 5. Fixed-point Opus, private word ASM and PDM32 IRAM ON; ICDF word
loads and PDM batch OFF. No SPIFFS log or runtime statistics. OTA succeeded
to app1; six status polls timed out before the board returned.

The first frequent-poll run never decoded: initialization failed the 4096-byte
DRAM reserve check. It is not a valid comparison of playback priorities.
Subsequent sparse runs with a 40-second local file can cross its natural EOF,
so their reconnect pauses must not be interpreted as unexplained stalls.
TCP_INFO also recorded real retransmissions/RTO during the first two short
connections. No failed observations were discarded.

A controlled 180-second SILK 12-kbit/s mono fixture avoids EOF in the window:
after five seconds warmup, two health samples 27 seconds apart measured
27613 ms on the board, 1328640 PCM frames (27680 ms), 38 short DMA underruns,
and minimum sampled free heap 5776 bytes. No terminal RX reason was latched.
Strict continuity still FAILS: the 64-word retry-silence blocks total about
50.6 ms. This does not establish an HTTP-priority improvement.

The fixture is a looped, re-encoded copy of our own tone/noise test, not a
recorded station. Reproduce with ffmpeg: input tests/fixtures/opus_native/
mono-12.opus, stream_loop -1, t 180, ar 48000, ac 1, libopus 12k, vbr off,
frame_duration 20, application voip. Serve through serve_fixture.cjs with
--tcp-info --hold-open-ms 60000; the deliberate FIN delay keeps the server's
socket observable but does not change the body or Content-Length.

Keep this profile experimental. Next controls: PDM batch A/B and SDK RX/TX
allocation/drop counters. No production default was changed.
