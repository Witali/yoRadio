# Experimental PVQ ADDX4 — 2026-09-14

Best tell-inline ASM parent plus20 exact address fusions in decode_pulses.
CPU160 / QIO40, diagnostic raw Opus benchmark; no physical audio or stage/function profiler.
Not a production default. This image is intended for the matched A/B/A board experiment.

App: 903184 bytes. SHA256: `685d1e672a962547086fa19cb599fbf42b8d6426a212efb2c48d72fb87bb1f93`.
Linked decode_pulses:985 ->945 bytes,395 ->374 physical instructions.
Static IRAM/DRAM and48-byte stack frame unchanged; flash text -40 bytes.
200000 local register-state checks and exact object/linked control-flow proof.
18 Node tests pass. Parent host PCM exact through510kbps, PLC/reset/OOM;
host C does not execute LX106 ADDX4. Physical speed/result gate still pending.

Full scope: docs/ESP8266_OPUS_ASM_PVQ_ADDX.md.
