# ESP8266 native audio path

## Production path

The Wemos D1 mini production firmware passes audio through these stages:

1. `audio_service.c` opens the station over HTTP/TCP and separates standard
   ICY metadata from compressed audio bytes.
2. The first valid frame signature selects MP3 or AAC from the stream content,
   not from the URL suffix or HTTP `Content-Type`.
3. `codec_bridge.cpp` feeds the compressed frame to the production Helix MP3
   SSO or Helix AAC decoder. The decoder callback receives interleaved signed
   16-bit PCM.
4. `native_audio_output.c` applies fixed-point normalization, volume and
   balance, averages stereo to mono, and resamples the input cadence to 48 kHz.
5. The branchless first-order delta-sigma packer converts each mono sample to
   one 32-bit PDM word (PDM32), nominally 1.536 MHz.
6. `esp8266_nodac_i2s.c` copies those words into the 2 x 512-word circular SLC
   DMA ring. The I2S peripheral continuously transmits DATA on GPIO3/RX.
7. GPIO3 feeds the external passive RC low-pass and AC-coupling network, then a
   high-impedance amplifier input.

## Bounded diagnostic trace

`-DYORADIO_ESP8266_AUDIO_TRACE=ON` enables four snapshots at each important
boundary without changing the selected codec or audio backend:

- `AUDIO_TRACE PCM`: raw PCM returned by the decoder;
- `AUDIO_TRACE OUTPUT-PCM`: normalized, volume-scaled and mono-mixed PCM;
- `AUDIO_TRACE DMA-PDM`: the words already copied into the physical DMA ring,
  including their bit population, FNV checksum and first four words.

The option is OFF by default and compiles out of production builds.
Always combine it with the canonical `sdkconfig.defaults`; do not copy a stale
experimental `sdkconfig` into the diagnostic build directory.

## Physical verification (2026-09-02)

On the Wemos D1 mini, station 510 (`Ретро FM`) returned HTTP 200 with an ICY
interval of 16000 bytes. Stream inspection selected MP3. Helix SSO allocated
12968 bytes of DRAM and used the preallocated 16384-byte IRAM arena. The first
four decoded blocks were stereo, 44.1 kHz and non-silent; observed PCM extrema
reached -19847 and 18834. The DMA snapshots had different checksums and roughly
half of their 2048 bits set, proving that changing audio data reached the PDM
DMA ring. During the same run WebUI advanced from `stopped` to `playing` and
reported `MP3 128 kbps 44 kHz stereo`.

A failed earlier trace that requested a 13880-byte allocation was not the
production decoder: its generated `sdkconfig.h` had silently selected the
experimental libmad backend despite a copied text `sdkconfig`. Reconfiguring
from the tracked production defaults restored Helix SSO and removed the false
out-of-memory failure.