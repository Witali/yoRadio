# yoRadio ESP8266 native

This target uses the official Espressif `ESP8266_RTOS_SDK v3.4` and follows
the ESP-IDF-style component/CMake layout. It is deliberately HTTP-only and
will contain only the Helix MP3 and AAC decoders.

The default profile targets a 4 MiB ESP-12E/NodeMCU/Wemos-class module at
160 MHz and uses the external flash in QIO mode at 40 MHz. The bootloader is
initially written in DIO as required by ESP8266 RTOS SDK, then enables Quad I/O
during startup. Use DIO for modules whose flash chip does not support QIO.
The optional `sdkconfig.qio80.defaults` profile selects QIO at 80 MHz for
modules with a suitably rated flash chip. Use it instead of
`sdkconfig.defaults`; it is kept separate from the default profile because
signal integrity still depends on the particular module PCB.
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
