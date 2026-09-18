# 2026-09-18: local scalar candidate

23 same-address three-byte MOVI replace only proven local0/1 reads;
ctx flag reads remain unchanged. Original frame, RAM and all instruction
addresses retained.24 exact host PCM/state/sanitizer scenarios pass.
Raw CPU160/QIO40 benchmark; physical speed gate pending, not production.
See docs/ESP8266_OPUS_QUANT_LOCALS.md and commented patches.s.
