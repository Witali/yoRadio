# Unaccepted DMA-size experiment

Not the default firmware. Native radio with two 1023-word DMA buffers,
3-second stream inactivity timeout, CPU160/QIO40, I2S PDM32 GPIO3.
Audio and memory profiling disabled; ordinary informational startup logs enabled.
Built from a3bb81a plus the temporary 512 -> 1023 DMA-word change (now reverted).

app.bin: 768208 bytes, SHA256
40B1D97916823D897C944BE1CC6D9C657B8FFBDD3FD78F39836DF0C19FFDC683.
App0 address 0x10000; Wi-Fi/SPIFFS were retained. Hash verification passed.
Live radio continuity did not pass: receive data stopped after initial AAC PCM.
See docs/ESP8266_CONTINUITY_2026-09-08.md. Do not mistake this image for a
successful fix or use it as the production default.
