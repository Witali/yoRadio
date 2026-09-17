# Opus live diagnostic: restore SDK RX buffer defaults

2026-09-17. Hypothesis, not a proven playback fix.

The pinned Espressif ESP8266_RTOS_SDK components/esp8266/Kconfig defines
ESP8266_WIFI_RX_BUFFER_NUM=16 and LEFT_CONTINUOUS_RX_BUFFER_NUM=16 by default.
Its help explicitly warns that lowering the continuous RX reserve makes RX
hang more likely. Our RAM-oriented defaults use14 for both.

`build_i2s_pdm_production.ps1 -Diagnostic -WifiRxBuffers 16` restores only
these two values for an isolated live experiment. It does not change TCP,
the host adapter, codec mathematics, stacks or the4096B heap reserve.
The normal builder still selects14. The generated config is checked before
compilation and both selected values are recorded in the manifest.

Expected extra RX payload storage is approximately2x524=1048B, not a full
allocator/RAM accounting. Physical free heap and continuous PCM must be
measured; zero SDK allocation-failure counters cannot rule out RF loss or
hardware RX hangs. Keep all failed windows. Do not promote this setting on
the basis of the Kconfig warning alone.
