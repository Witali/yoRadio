# Immediate refill after FULL/YIELD — 2026-09-17

Diagnostic ordinary radio, complete18-stage accepted ASM chain, I2S PDM32
GPIO3, synchronous DMA512, input1024B/scratch6144B, reserve4096B.
Same network/codec/output profile as `rxdiag-20260917`.

The parser needing input now retries recv immediately if the last refill
stopped at capacity/work budget. Only actual EAGAIN invokes input waiting.
With this profile's READ_WAIT_MS=0, the removed wait was a one-tick polling
sleep, NOT select. With positive READ_WAIT_MS the same guard avoids select.
No change to PCM arithmetic, allocation sizes or stream timeout semantics.

Ten physical DLF24 starts completed, zero qualified continuous windows.
Two incomplete windows; remaining results, including timeout/reconnect and
scratch fragmentation, are retained in board/. One near-rate window had
27.780s PCM /28.026s elapsed with278 underruns; it is NOT a successful run.
The first near-rate control was not a ten-run matched A/B series, so this
does not establish a statistical overall improvement.

Ten HTTP/input/PCM/transport tests passed without skips; readiness-wait tests
also passed after setting the actual SDK path. Accepted ASM graph and loaded
image checks passed. OTA succeeded; no UART or Wi-Fi-adapter changes.
Still experimental; the live playback goal remains unachieved.
