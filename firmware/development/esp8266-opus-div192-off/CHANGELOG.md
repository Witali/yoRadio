# Single-reciprocal control, 2026-09-10

Experimental raw Opus benchmark, NOT a production release or continuous-radio
qualification. Source `ccfe023`, app902768 bytes. CPU160/QIO40, corpus
12/24/64/128/192kbps; no runtime bitrate cap. `OpusDivOnce` OFF, rotation ASM
and CELT decoder-only specialization OFF. FIR/ICDF/word helpers ON.

Application-only OTA succeeded (`ota.json`). Ten attempts completed; every
attempt and observation is retained in `attempt*.json` / `.log`.
`run*.json` are exact copies of the completed attempts for the A/B reader.
All five PCM hashes match their expected fixtures on every attempt. Each
case decodes120 preloaded packets after warmup:2.4s PCM per measured run,
24s across ten runs. No audio HTTP, demux, normalization or physical output;
Wi-Fi/WebUI remain active. Task timing includes charged ISR/instrumentation.

Median CPU budget (% of PCM duration):23.192 /55.026 /65.015 /80.392 /94.337.
Minimum sampled free DRAM6820 bytes; lifetime free stack1660 bytes.
These observations are not a worst-case heap/stack proof.

See [candidate and paired report](../esp8266-opus-div192-on/CHANGELOG.md).
This binary is kept only to reproduce the negative experiment.
