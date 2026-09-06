# KaRadio Helix PDM for ESP8266

This is a separate ESP8266 RTOS SDK firmware target inspired by KaRadio's
producer/consumer audio pipeline. It does **not** use a VS1053 or copy the old
KaRadio decoder path. Network input and software decoding run as independent
FreeRTOS tasks and communicate through one fixed compressed-audio ring.

## Default data path

```text
HTTP/ICY TCP worker (priority 6)
  -> 4096-byte static compressed ring (75% startup prebuffer)
  -> yoRadio Helix MP3 SSO worker (priority 5)
  -> mono delta-sigma conversion
  -> two 512-word circular SLC-DMA buffers
  -> I2S PDM DATA on GPIO3 at nominal 1.536 MHz
  -> RC low-pass filter and amplifier input
```

The TCP worker receives directly into the writable section of the ring. The
decoder reads directly from the ring into the Helix input window. Playback
does not allocate or release stream buffers. Backpressure sleeps the network
task when the ring is full; the decoder sleeps when it is empty. ICY metadata,
HTTP redirects and chunked transfer parsing reuse the native yoRadio protocol
code. HTTPS is intentionally not linked on this RAM-constrained target.

The first profile is MP3-only to leave enough RAM for the extra worker stack
and ring. AAC can be enabled later after physical heap/stack measurements.

## Build

Use the official Espressif ESP8266 RTOS SDK v3.4 environment:

```powershell
cmake -S esp8266/karadio-helix-pdm `
  -B .build/esp8266-karadio-helix-pdm -G Ninja `
  -DSDKCONFIG_DEFAULTS="$PWD/esp8266/karadio-helix-pdm/sdkconfig.defaults"
ninja -C .build/esp8266-karadio-helix-pdm
```

Flash the bootloader, partition table and application using the addresses in
the generated `flash_project_args`. The WebUI and persistent data layout stay
compatible with `esp8266/rtos-sdk-native`.

GPIO3 is also UART0 RX. Do not transmit UART data from the computer while PDM
audio is active. UART0 TX logging on GPIO1 remains usable.

## Relationship to KaRadio

The scheduling model follows the useful part of KaRadio for ESP8266: network
producer above the audio consumer, bounded prebuffering and explicit
backpressure. The implementation uses current Espressif RTOS SDK APIs and the
repository's Helix/I2S-PDM modules; no VS1053-specific code is included.

- Original KaRadio: <https://github.com/karawin/Ka-Radio>
- ESP8266 RTOS SDK: <https://github.com/espressif/ESP8266_RTOS_SDK>
