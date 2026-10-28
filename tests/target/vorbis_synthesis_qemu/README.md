# Isolated owned Vorbis synthesis qualification

This independent fixture executes all original31 streams and434 raw audio
packets through the public setup owner, frame decoder, floor0/floor1 spectrum,
IMDCT, exact window products, joint106-bit PCM rounding and shared granule
synthesis owner. It uses no captured gain, spectrum, transform or PCM as input.
The unchanged reference contract compares every one of738560 PCM bytes at
zero lag, with maximum absolute S16 error2 and all14 original relations.

The coordinator stays on core0. The priority3 worker has16384 bytes of stack
and runs on ESP32 core1 or C3 core0. Watchdogs and idle checks remain enabled.
Packet boundaries and bounded128-sample UART chunks yield one tick. UART RLE
is lossless transport only; the controller expands and compares every sample.
The entire corpus has two channels and maximum2048-sample blocks; it does not
qualify8192-sample target memory use. Heap minima and task stack high-water
are cumulative emulator observations, not physical timing or transient peaks.

Run with the repository's explicit Python runtime from the task worktree:

```powershell
C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -B -X utf8 tests/test-vorbis-synthesis-qemu.py --target esp32 --output .build/vorbis-synthesis-esp32-fresh
```

Use `--target esp32c3` for the separately pinned SDK/QEMU. `--prepare-only`
freezes sources and the complete corpus without native execution. `--protocol-only`
checks strict full-corpus protocol parsing and malformed transcript controls.
Each campaign requires a fresh directory under `.build`. Logs, process receipts,
compiler commands, objects, images and configuration remain in that directory.

This fixture is not production firmware, physical-board qualification, complete
codec conformance or proof of earlier transcendental/IMDCT accuracy. Ordinary
floor0 gain is explicitly approximate; full PCM must pass the retained bound.
