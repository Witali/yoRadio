# LED-off control — 2026-09-17

Same synchronous radio/accepted ASM/TCP/DMA profile as txdiag, but LED OFF.
Not a tone or decoder-only benchmark. OTA succeeded.

Kultur24 windows:27.2493s PCM/28.000s with646 underruns, then
27.680s/27.995s with336 underruns. Neither qualifies as continuous audio.
First TX snapshot interval had417 completions and zero failed completions;
RSSI changed to-40dBm. This is not a controlled proof that LED caused RF
failures: source content, time and signal conditions also changed.
All observations retained in board/. Not promoted as a production fix.
