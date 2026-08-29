# yoRadio ESP8266 native

This target uses the official Espressif `ESP8266_RTOS_SDK v3.4` and follows
the ESP-IDF-style component/CMake layout. It is deliberately HTTP-only and
will contain only the Helix MP3 and AAC decoders.

The default profile targets a 4 MiB ESP-12E/NodeMCU/Wemos-class module at
160 MHz. Hardware I2S uses the ESP8266 fixed outputs: DATA GPIO3, BCLK GPIO15,
LRCLK GPIO2. The default optional SSD1306 bus is SDA GPIO4/SCL GPIO5.

The network layout intentionally matches the ESP32-C3 OLED native target:
WebUI HTTP resources use the standard port 80 and the persistent WebSocket is
the `/ws` route on that same server and port. Static gzip responses close their
short-lived sockets after transfer; there is no second WebUI or WebSocket port.

The project is under active implementation; use the repository setup/build
scripts once they are added rather than invoking a globally installed SDK.
