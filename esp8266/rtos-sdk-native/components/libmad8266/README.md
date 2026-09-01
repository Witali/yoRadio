# libmad-8266 experimental component

This component vendors only the fixed-point `libmad` core from
[ESP8266Audio](https://github.com/earlephilhower/ESP8266Audio), pinned to
commit `10d929ac01436dfe8856e0a06fd9ec35a848c6e2`.

The source under `upstream/libmad/` is the ESP8266-optimized libmad 0.15.1b
port. Its original `COPYING`, `COPYRIGHT`, `LICENSE`, and source notices are
preserved. `ESP8266Audio-LICENSE.txt` contains the upstream library license.

yoRadio does not use the Arduino `AudioGeneratorMP3` wrapper. The native
firmware feeds already-framed MP3 bytes directly to the libmad stream/frame/
synthesis API and sends interleaved signed 16-bit PCM through its existing
audio callback. Select it with `CONFIG_YORADIO_MP3_DECODER_LIBMAD=y`.

The ESP8266 component build defines
`YORADIO_LIBMAD_EXTERNAL_FRAME_WORKSPACE`. This preserves the upstream layout
for other users while replacing the two Layer III `mad_fixed_t` arrays in
`mad_frame` with pointers. yoRadio allocates the 4608-byte spectral buffer and
2304-byte reorder buffer from its aligned 32-bit IRAM arena. The byte-addressed
stream reservoir, frame header, subband samples, and overlap state remain in
8-bit DRAM.
