# minimp3

This directory vendors `minimp3.h` from the official
[`lieff/minimp3`](https://github.com/lieff/minimp3) repository.

- Upstream commit: `ea99364f61c14656440e8d77e9c233ccf3124633`
- License: CC0 1.0 Universal (see `LICENSE`)
- Build options used by YoRadio: `MINIMP3_ONLY_MP3`, `MINIMP3_NO_SIMD`

YoRadio uses only the low-level, frame-by-frame decoder API. Incoming frame
headers and frame lengths are validated by the YoRadio decoder selector before
the frame is passed to minimp3.
