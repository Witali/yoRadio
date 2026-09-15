# PVQ row-length word-load candidate

Experimental raw Opus ASM benchmark, not ordinary radio or a production default.
CPU160MHz/runtime QIO40, RAM-preloaded packets, no physical audio output.
Application-only native WebUI OTA; never use UART application commands on GPIO3.

See docs/ESP8266_OPUS_ASM_PVQ_ROW_WORD.md and manifest.json.
Local exact PCM and linked proofs passed; all30 A/B/A physical runs complete.
CPU192 A/B/A2:82.82325 /82.00615 /82.84056%; CPU128:73.78213 /73.28558 /73.80594%.
Both high-bitrate gates pass; row-word accepted experimentally. Static RAM/
IRAM/frame unchanged, image903216 B, free stack minimum1660 B.80% not reached.
All outliers retained: A2/run5+run6 observation timeouts, minimumDRAM800 B.
Candidate maximum192 call21.528ms is not a continuous-audio guarantee.
Ordinary C/I2S PDM image restored OTA; HTTP/WS/playlist verified, no UART.
See candidate comparison.json, raw runs/controls and the full report.
