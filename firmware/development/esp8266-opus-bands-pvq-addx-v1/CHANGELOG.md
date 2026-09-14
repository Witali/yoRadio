# Experimental PVQ ADDX4 — 2026-09-14

Best tell-inline ASM parent plus20 exact address fusions in decode_pulses.
CPU160 / QIO40, diagnostic raw Opus benchmark; no physical audio or stage/function profiler.
Not a production default. This image is intended for the matched A/B/A board experiment.

App: 903184 bytes. SHA256: `685d1e672a962547086fa19cb599fbf42b8d6426a212efb2c48d72fb87bb1f93`.
Linked decode_pulses:985 ->945 bytes,395 ->374 physical instructions.
Static IRAM/DRAM and48-byte stack frame unchanged; flash text -40 bytes.
200000 local register-state checks and exact object/linked control-flow proof.
18 Node tests pass. Parent host PCM exact through510kbps, PLC/reset/OOM;
host C does not execute LX106 ADDX4.

Completed 10 A / 10 B / 10 A2 physical raw runs; all PCM hashes match.
CPU192 medians: 88.112 / 88.373 / 88.116%; candidate takes 0.291-0.296%
more time (51.35-52.19 us per 20 ms audio). Other tested bitrates improve.
Preserved as the smaller alternative: app -32 bytes, function/text -40 bytes,
no static RAM or stack reduction. Not selected over tell-inline for speed;
the <=70% CPU goal remains unmet. No live audio qualification claimed.
All attempts, maxima and low-memory observations retained in comparison.json.

Restored the original esp8266-opus-live512-idle3s-20260913 radio by OTA.
Slot 0x110000 confirmed; status/WS/playlist checked, original stopped state
preserved. No UART or SPIFFS changes. See restore-ota.json/restore-snapshot.json.

Full scope: docs/ESP8266_OPUS_ASM_PVQ_ADDX.md.
