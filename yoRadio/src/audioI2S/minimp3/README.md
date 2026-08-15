# minimp3

This directory vendors `minimp3.h` from the official
[`lieff/minimp3`](https://github.com/lieff/minimp3) repository.

- Upstream commit: `ea99364f61c14656440e8d77e9c233ccf3124633`
- License: CC0 1.0 Universal (see `LICENSE`)
- Build options used by YoRadio: `MINIMP3_ONLY_MP3`, `MINIMP3_NO_SIMD`,
  `MINIMP3_STATIC_SCRATCH`

YoRadio uses only the low-level, frame-by-frame decoder API. Incoming frame
headers and frame lengths are validated by the YoRadio decoder selector before
the frame is passed to minimp3.

The single local change to the upstream header makes the decoder scratch area
static when `MINIMP3_STATIC_SCRATCH` is defined. This avoids placing roughly
13 KiB on the Arduino loop-task stack. YoRadio has one audio decode path, so
the static scratch area is not accessed concurrently.
