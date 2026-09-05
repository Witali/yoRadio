# ESP8266 native audio path

## Production path

The Wemos D1 mini production firmware passes audio through these stages:

1. `audio_service.c` opens the station over HTTP/TCP and separates standard
   ICY metadata from compressed audio bytes.
2. The first valid frame signature selects MP3 or AAC from the stream content,
   not from the URL suffix or HTTP `Content-Type`.
3. `codec_bridge.cpp` feeds the compressed frame to the production Helix MP3
   SSO or Helix AAC decoder. Helix MP3 emits 32 signed 16-bit PCM frames per
   callback (mono by default); AAC retains its full-frame output buffer.
4. `native_audio_output.c` applies fixed-point normalization and volume;
   balance applies only to stereo PCM. Stereo is averaged to mono and the
   input cadence resampled to 48 kHz, preserving state across callbacks.
5. The branchless first-order delta-sigma packer converts each mono sample to
   one 32-bit PDM word (PDM32), nominally 1.536 MHz.
6. The packer writes directly into the producer-owned span reserved from
   `esp8266_nodac_i2s.c`. Full buffers or safely committed prefixes are
   published to SLC DMA; no outstanding producer loan may transfer. The
   two 512-word-capacity buffers use finite descriptors, not an unguarded
   circular ring. Underrun retries with 64 neutral words while playing;
   stop retains 512-word neutral blocks. See [recovery measurements](ESP8266_DMA_STARVATION_RECOVERY.md).
7. GPIO3 feeds the external passive RC low-pass and AC-coupling network, then a
   high-impedance amplifier input.

## Bounded diagnostic trace

`-DYORADIO_ESP8266_AUDIO_TRACE=ON` enables four snapshots at each important
boundary without changing the selected codec or audio backend:

- `AUDIO_TRACE PCM`: raw PCM returned by the decoder;
- `AUDIO_TRACE OUTPUT-PCM`: normalized, volume-scaled and mono-mixed PCM;
- `AUDIO_TRACE DMA-PDM`: the words committed into the physical DMA buffer,
  including their bit population, FNV checksum and first four words.

The option is OFF by default and compiles out of production builds.
One startup-zero snapshot is retained, then the bounded trace waits for
nonzero PCM/non-neutral PDM so the 32-frame API's startup silence cannot
consume all diagnostic snapshots. The signed-balance mute fix and current
physical trace are recorded in [PCM32/direct DMA](ESP8266_PCM32_DIRECT_DMA.md).
Always combine it with the canonical `sdkconfig.defaults`. The build entrypoint
stores the generated `sdkconfig` inside its build directory, isolating it from
any stale ignored experimental config in the source tree.

## Physical verification (2026-09-02)

On the Wemos D1 mini, station 510 (`Ретро FM`) returned HTTP 200 with an ICY
interval of 16000 bytes. Stream inspection selected MP3. Helix SSO allocated
11472 bytes of DRAM and used the preallocated 16384-byte IRAM arena. The first
four decoded blocks were stereo, 44.1 kHz and non-silent; observed PCM extrema
reached -19847 and 18834. The DMA snapshots had different checksums and roughly
half of their 2048 bits set, proving that changing audio data reached the PDM
DMA ring. During the same run WebUI advanced from `stopped` to `playing` and
reported `MP3 128 kbps 44 kHz stereo`.
A 60-second integrated rerun kept playback active while 32 WebSocket status
frames were received; after the socket timeout drained, `/api/native/status`
again returned HTTP 200 with `playing=true`, `codec=MP3`, and `bitrate=128`.

A failed earlier trace that requested a 13880-byte allocation was not the
production decoder: its generated `sdkconfig.h` had silently selected the
experimental libmad backend. The project now keeps mutable Kconfig output in
each build directory; configuring a fresh directory from the tracked defaults
restores Helix SSO and prevents this false out-of-memory failure.
