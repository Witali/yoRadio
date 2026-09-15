# Signed PVQ index phase-specialized ASM

Experimental raw benchmark, not production/default. CPU160/runtime QIO40,
RAM packets/no physical output in benchmark. Normal radio path is separate.
Native application-only OTA; no serial commands/reset or filesystem writes.

Three patches35 bytes,25 live helper bytes in29-byte slot. Five executed
instructions per phase instead of ten; no SAR/a0 scratch or RAM/frame growth.
Image903216 B; host24 PCM/state cases and137792 linked cases exact.
Control is accepted index-word.30 A/B/A:CPU19280.05594 /80.01998 /80.04450%.
Both high-bitrate gates pass; small gain accepted experimentally.80% and
live20second I2S/WebUI gates not reached; no firmware default change.
See docs/ESP8266_OPUS_ASM_PVQ_INDEX_HALF.md,preflight.json and host.json.
