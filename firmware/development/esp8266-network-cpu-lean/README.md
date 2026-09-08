# ESP8266 diagnostic: receive-only runtime statistics with reduced probe overhead

This is NOT the normal radio image. It automatically runs the selected
network benchmark after Wi-Fi connects, then returns to the radio task.
CPU160/QIO40, I2S PDM32 GPIO3/RX, two 512-word DMA payloads.
App-only OTA; do not erase SPIFFS or stored Wi-Fi settings.

Exact hashes, configurations and limitations are in
[the network report](../../../docs/ESP8266_NETWORK_BENCHMARK_2026-09-08.md).
The controlled LAN source and test fixtures must be available on the PC.
Restore esp8266-i2s-pdm-production/app.bin after measurements.
