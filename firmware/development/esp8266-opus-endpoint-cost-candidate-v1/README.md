# Experimental Opus ASM endpoint-cost candidate

CPU160 / runtime QIO40; raw RAM-packet benchmark, audio output OFF.
Eight same-width instruction replacements over accepted bits-fourth preserve
q/cost/ABI, all other code addresses, static RAM and stack. Both cached
endpoint costs are reused; no algorithm approximation or bitrate limit.

app903216 bytes, SHA256:
85af3677670a985918bb17affef136ed291f5bcd030494dba932fd378e752dbc

preflight.json records linked proof and parent hashes; host.json records24
exact PCM/state/PLC/reset/OOM cases through510kbps. Parent ELF and patch ELF
are retained for independent verification. All30 physical A/B/A completed:
CPU19286.47023 /85.96527 /86.49377%, both high-bitrate gates PASS.
Accepted experimental raw baseline, no static RAM/frame increase.
All attempts/maxima retained; candidate maximum19226.714ms.
Ordinary radio restored OTA with matching station/playlist and HTTP/WS.
Not production and not a continuous audio qualification.

See docs/ESP8266_OPUS_ASM_ENDPOINT_COST.md for scope and protocol.
