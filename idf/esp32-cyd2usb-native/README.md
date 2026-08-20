# yoRadio native ESP-IDF firmware

This is a separate firmware for the ESP32-2432S028 CYD2USB board. It uses
ESP-IDF APIs directly and deliberately does not include Arduino Core,
Arduino libraries, Adafruit GFX, or the Arduino yoRadio runtime.

The native port keeps the existing 4 MiB partition layout, so flashing only
the application image does not erase NVS or the SPIFFS web UI. The SPIFFS
image target is generated from `yoRadio/data` for explicit WebUI updates.

## Build

```powershell
.\setup.ps1
.\build.ps1
```

To reuse a previously installed dependency cache:

```powershell
.\build.ps1 -DependencyRoot C:\path\to\.idf
```

PDM is the normal build. To make a separate internal-DAC build without
changing that default:

```powershell
.\build.ps1 -BuildDirectory build-dac -AudioBackend continuous
```

The original ESP-IDF 5.5 I2S/DAC implementation is also available as an
isolated comparison build:

```powershell
.\build.ps1 -BuildDirectory build-legacy-dac -AudioBackend legacy
```

To flash only the application and preserve Wi-Fi/SPIFFS:

```powershell
.\build.ps1 -IdfArguments @('-p', 'COM8', 'app-flash')
```

To install or restore the WebUI explicitly:

```powershell
.\build.ps1 -IdfArguments @('-p', 'COM8', 'spiffs-flash')
```

The display driver is a native ESP-IDF ST7789/SPI-DMA port taken from the
HLV-codec CYD firmware and kept locally in `main/cyd_display.*`.

## Native service API

The first native port exposes small endpoints independently of the legacy
Arduino WebSocket protocol:

- `GET /api/native/status`
- `POST /api/native/reconnect`
- `POST /api/native/play?codec=auto` with the stream URL as request body
- `POST /api/native/stop`

Supported decoder selections are `auto`, `mp3`, `aac`, `flac`, `ogg`,
`vorbis`, and `opus` (Vorbis and Opus are detected inside the OGG container).
MP3 uses yoRadio minimp3 by default. Espressif MP3 and yoRadio Helix MP3 remain
available as compile-time alternatives in `menuconfig`.
Network streaming runs on core 0. Decode and audio output run as two independent
tasks on core 1. Compressed and PCM ring buffers prevent display/WebUI work
from blocking the audio pipeline.

I2S hardware PCM-to-PDM on GPIO26 is selected by default. It uses the new
ESP-IDF channel API and starts once at a fixed 48 kHz hardware rate with a
6.144 MHz carrier. Changing stations does not reconfigure PDM: input streams
below 48 kHz are linearly resampled and only the resampler state changes. The
internal 8-bit DAC remains available as the alternative
`YORADIO_NATIVE_AUDIO_OUTPUT_DAC` choice in `menuconfig`. A third
`YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC` choice compiles the final official
ESP-IDF 5.5.4 legacy I2S/DAC driver for comparison, still without Arduino.
It reuses the `idf6_i2s_compat`/`idf5_legacy_dac_backend` adapter contract from
the existing `esp32-cyd2usb-minimal` profile instead of duplicating the old
driver lifecycle inside the native audio pipeline.

The legacy DAC profile applies x16 oversampling with continuous fractional
error diffusion. A 48 kHz PCM stream therefore drives the 8-bit DAC at
768 kHz; 44.1 kHz becomes 705.6 kHz, and other supported 8-48 kHz streams use
the same `Fs x 16` rule. Each input sample is expanded on the fly into adjacent
8-bit DAC codes, so the existing 6 KiB conversion buffer is reused and no
full oversampled stream is stored in RAM. The error accumulator is preserved
between PCM samples and reset only when the input sample rate changes.

The pipeline uses 8 KiB compressed and 8 KiB PCM rings and logs free heap
after allocating them. Ring-buffer items
are acquired in place instead of being allocated for every audio block, so
continuous playback does not churn the general heap.
