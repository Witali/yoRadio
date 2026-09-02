# yoRadio ESP8266 native

This target uses the official Espressif `ESP8266_RTOS_SDK v3.4` and follows
the ESP-IDF-style component/CMake layout. It is deliberately HTTP-only. The
normal profile uses the yoRadio Helix MP3 and AAC decoders; an experimental
ESP8266Audio `libmad-8266` MP3 backend can be selected at compile time with
`CONFIG_YORADIO_MP3_DECODER_LIBMAD` while AAC remains on Helix.

The default profile targets a 4 MiB ESP-12E/NodeMCU/Wemos-class module at
160 MHz and uses the external flash in QIO mode at 40 MHz. The bootloader is
initially written in DIO as required by ESP8266 RTOS SDK, then enables Quad I/O
during startup. Use DIO for modules whose flash chip does not support QIO.
The optional `sdkconfig.qio80.defaults` profile selects QIO at 80 MHz for
modules with a suitably rated flash chip. Use it instead of
`sdkconfig.defaults`; it is kept separate from the default profile because
signal integrity still depends on the particular module PCB.
For a reproducible Wemos QIO80 libmad experiment, use
`sdkconfig.libmad-qio80.defaults`. The ordinary defaults continue to select
`CONFIG_YORADIO_MP3_DECODER_HELIX`.
The `sdkconfig.helix-sso-qio80.defaults` profile keeps Helix but enables its
experimental reduced-precision 32-bit polyphase synthesis. It allocates no
additional decoder buffers and is intended for PCM-quality and physical speed
comparison before the optimization is considered for production.
The `sdkconfig.helix-sso-qio80-pdm8.defaults` profile retains the legacy
8-bit SPI-PDM selection for comparative tests. The default backend is now
continuous I2S/SLC DMA on GPIO3 with a nominal 1.536-MHz carrier; legacy HSPI
output remains selectable with `CONFIG_YORADIO_AUDIO_OUTPUT_SPI_PDM`.
The matching `sdkconfig.audio-profile-qio80-pdm8.defaults` profile also
enables FreeRTOS runtime counters. Build it with
`YORADIO_ESP8266_AUDIO_PROFILE` and
`YORADIO_ESP8266_HELIX_STAGE_PROFILE` to measure network, frame scan,
decoder internals, normalization, PDM conversion, SPI wait, CPU idle, and heap
on a physical board.
The matching `sdkconfig.aac-sso-qio80.defaults` profile keeps exact MP3 and
enables the experimental three-partial-product AAC fixed-point path for
isolated PCM, disassembly, and physical timing comparison.
The `sdkconfig.libmad-mp3-only-qio80.defaults` experiment also disables AAC;
this reduces stereo PCM storage from 4096 to 2304 bytes and the fixed IRAM word
arena from 16 KiB to 12 KiB. The arena stores the 4236-byte `mad_synth`, the
4608-byte Layer III spectral workspace, and the 2304-byte reorder workspace.
The Xtensa build uses 11152 bytes of that arena and reduces `mad_frame` in
8-bit DRAM from 20784 to 13880 bytes. It is not a full-feature replacement
profile.
Audio defaults to mono I2S-PDM on fixed DATA GPIO3/RX. Two circular SLC-DMA
buffers continuously clock one 32-bit word per 48-kHz PCM sample. Production
computes 32 genuine delta-sigma decisions per sample, giving a nominal
1.536-MHz carrier. The ESP8266 integer divider produces 1.538461 MHz (+0.16%).
A genuine PDM128 mode at nominally 6.144 MHz
is compile-time selectable but remains experimental because it cannot run in
realtime on the physical Wemos D1 mini. As in ESP8266Audio's NoDAC path, the I2S
engine also routes BCLK on GPIO15 and LRCLK on GPIO2 so its SLC-DMA clock is
started reliably. Only DATA GPIO3 is connected to the audio filter. Connect GPIO3 through the
documented low-pass/AC-coupling chain and then to a high-impedance amplifier
input. Stereo streams are gain/balance adjusted and averaged before PDM.
The PDM profile uses a small local output-only backend instead of the RTOS SDK
I2S driver. It follows the ESP8266 Arduino core architecture used by
ESP8266Audio: a circular SLC descriptor ring, an always-running companion link,
the BBPLL audio-clock gate and task notification when DMA returns a buffer.
Both 2048-byte buffers and descriptors are static, so starting or stopping
audio cannot fragment the heap. Initialization waits for the first completed
descriptor and fails explicitly if the hardware ring does not start.
The board default profile uses QIO at 40 MHz. A physical Wemos D1 mini with
verified bootloader, partition table, and application bytes intermittently
stopped immediately after the ROM loader at QIO80; the same code boots and
serves the WebUI at QIO40. The named `qio80` profiles remain available for
explicit experiments on modules whose flash and PCB are stable at 80 MHz.
ESP8266 RTOS SDK intentionally
stores DIO in the boot image header so the ROM can load it on every supported
flash chip; `CONFIG_SPI_FLASH_MODE=0x0` makes early SDK initialization enable
QIO before the application executes. Do not override the boot header to QIO.
The same default profile selects the measured faster 32-bit Helix MP3 SSO
synthesis path and the genuine PDM32 x1 I2S backend.

GPIO3 is also UART0 RX. The application intentionally never reads UART input
and routes the pin to I2S while running; UART0 TX logging on GPIO1 remains
available. The onboard 470-ohm series resistor limits contention with CH340
TXD; do not send UART data from the host while audio is playing.

Legacy mono HSPI-PDM on GPIO13/D7 can be selected with
`CONFIG_YORADIO_AUDIO_OUTPUT_SPI_PDM`; GPIO14/D5 is then an unused SPI clock.
Standard stereo PCM for an external I2S DAC remains available through
`CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PCM` and uses DATA GPIO3, BCLK GPIO15 and
LRCLK GPIO2. The optional SSD1306 bus is SDA GPIO4/SCL GPIO5.

The network layout intentionally matches the ESP32-C3 OLED native target:
WebUI HTTP resources use the standard port 80 and the persistent WebSocket is
the `/ws` route on that same server and port. Static gzip responses close their
short-lived sockets after transfer; there is no second WebUI or WebSocket port.

The HTTP/WebSocket task requires a **minimum 5120-byte stack** in this
firmware. The shared YoRadio WebUI formats playlist-backed state for
`getindex`; a physical Wemos D1 mini test with a 4096-byte stack triggered the
FreeRTOS stack canary in the `httpd` task. Do not reduce
`BOARD_TASK_STACK_WEB` below 5120 bytes without a new on-device high-water and
full Web API test.

The project is under active implementation; use the repository setup/build
scripts once they are added rather than invoking a globally installed SDK.
