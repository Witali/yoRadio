# PVQ endpoint word-load candidate

Experimental raw Opus ASM benchmark; not ordinary radio or a default profile.
CPU160MHz/runtime QIO40, RAM-preloaded packets; physical audio output OFF.
Application-only native WebUI OTA. Never send UART commands or reset GPIO3.

Parent row-word accepted raw CPU19282.00615%. New upper read reuses a10
leaf; new lower fixed-continuation fragment uses a0 for SAR. Image903216 B,
four frozen-layout patches,total56 bytes; unchanged RAM/IRAM/frame/tables.
Host24 cases and actual linked search exact. All30 A/B/A physical runs passed
exact PCM. Median raw CPU19281.98187 /80.99456 /82.01310%,
CPU12873.29400 /72.59856 /73.28813%. Both high-bitrate gates PASS.
192 relative gain1.20431–1.24193%; mono12 slowdown at most0.03836%.
Static RAM/IRAM/frame unchanged; free stack1660 B; minDRAM8344 /8176 /8344 B.
Candidate192 max20.495ms,minDRAM9792 B. No decoder/HTTP observation errors.
A/run8 mono12 task>wall267us retained; no timings subtracted or filtered.
Source/proofs8b0bdc7c; preflight145PASS. All raw logs and comparison.json retained.
Ordinary C/I2S PDM32 DMA512 radio restored OTA; stopped167/playlist/HTTP/WS
checked. Root104.1972ms is not full-browser latency. No20second live ASM test.
New experimental baseline80.99456%; goal80% requires another1.22794% time
reduction. Defaults, flash/CPU clock and runtime bitrate support unchanged.
Final147 related regressions PASS/0skip in206.19seconds; independent physical
report/image and restore checks included. Full final-tests.log retained.
See docs/ESP8266_OPUS_ASM_PVQ_ENDPOINT_WORD.md, manifest.json and preflight.json.
