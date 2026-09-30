# Original ESP32-C3 hardware calibration fixtures

These files were recovered byte-for-byte from the original local
`.build/codec-benchmark/` directory. They were generated from the same deterministic
11-second, 48 kHz, 16-bit stereo noise/tone source by
[`generate.ps1`](../../../tools/codec_benchmark/generate.ps1). They contain synthetic
test audio, not radio recordings or configuration data.

The [manifest](manifest.json) records their current SHA-256 hashes and lengths.
Original hardware logs did not record hashes. Their file lengths and both decoded
windows' exact input consumption, PCM byte counts and decoder-call counts match
these recovered files in QEMU. Preserve the bytes; re-encoding with another encoder
version would invalidate the comparison.

AAC is embedded only in the optional QEMU instruction profile. The other codecs
are selected with `run-qemu.ps1 -CodecCalibration mp3|flac|vorbis|opus` and copied
into the disposable emulator image's unused app1 region. This is a test fixture
layout, not a firmware image to flash to a board.

See [results, limits and repeat commands](../../../docs/ESP32C3_QEMU_CALIBRATION_20260930.md).
