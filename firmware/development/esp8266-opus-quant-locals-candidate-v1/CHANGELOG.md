# 2026-09-18: local scalar candidate

23 same-address three-byte MOVI replace only proven local0/1 reads;
ctx flag reads remain unchanged. Original frame, RAM and all instruction
addresses retained.24 exact host PCM/state/sanitizer scenarios pass.
Raw CPU160/QIO40 benchmark; not production.
See docs/ESP8266_OPUS_QUANT_LOCALS.md and commented patches.s.

Physical 10A/10B/10A2 completed: CPU192 medians
77.868250 / 77.876125 / 77.881708%. Both speed gates fail: not adopted.
All PCM exact; no static RAM, scratch or stack-frame increase. Preserve
B/run8 and A2/run5 HTTP timeouts and 90% CPU outliers. 42 local tests pass.
Three saved-result regressions pass, including all 30 hashes and medians.
Ordinary heapreserve radio restored by OTA; HTTP/WS/playlist verified.
The raw 75% and continuous 20-second I2S/WebUI goals remain unmet.
