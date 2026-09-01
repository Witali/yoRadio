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
Audio defaults to mono SPI-PDM on GPIO13/D7, leaving UART0 RX GPIO3
available. HSPI clocks the PDM stream at 769.23 kHz, the closest hardware rate
to 48 kHz x 16; GPIO14/D5 carries the unused SPI clock and should not be wired
to the audio filter. The optional legacy I2S profile uses the ESP8266 fixed
outputs: DATA GPIO3, BCLK GPIO15, LRCLK GPIO2. The default optional SSD1306 bus
is SDA GPIO4/SCL GPIO5.

For SPI-PDM, connect GPIO13/D7 through a low-pass/AC-coupling chain for a
one-bit DAC, then feed a high-impedance amplifier input. The output is mono:
stereo streams are scaled with their individual balance gains and then
averaged. Do not connect GPIO14/D5 to the amplifier. Select
`YORADIO_AUDIO_OUTPUT_I2S` only when fixed-pin I2S is explicitly required and
the USB-UART adapter does not drive GPIO3.

The network layout intentionally matches the ESP32-C3 OLED native target:
WebUI HTTP resources use the standard port 80 and the persistent WebSocket is
the `/ws` route on that same server and port. Static gzip responses close their
short-lived sockets after transfer; there is no second WebUI or WebSocket port.

The project is under active implementation; use the repository setup/build
scripts once they are added rather than invoking a globally installed SDK.
