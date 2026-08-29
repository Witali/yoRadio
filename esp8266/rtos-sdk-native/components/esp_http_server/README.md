# ESP HTTP Server for ESP8266

This component is based on the `esp_http_server` component shipped with
ESP8266 RTOS SDK v3.4. WebSocket support is backported from Espressif's
ESP-IDF v4.2.5 implementation so the HTTP pages and `/ws` endpoint can share
the same server and port 80, matching the ESP32-C3 OLED firmware.
