# Experimental PVQ many-dimensions pointer reuse

Frozen286-byte range,116→103 instructions; exact reads/ABI, unchanged RAM/frame.
Raw RAM-packet benchmark at160 MHz/QIO40, no audio output. Not production.
No bitrate limit or default/C fallback change.

30 physical A/B/A runs, exact PCM; both high-bitrate gates FAIL.
CPU192 A/B/A2:87.31173 /87.31810 /87.33048%. Not accepted standalone;
retained for combinations. Ordinary firmware restored OTA, HTTP/WS checked.

[Recipe and test results](../../../docs/ESP8266_OPUS_ASM_PVQ_DIM_POINTER.md).
