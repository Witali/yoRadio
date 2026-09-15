# Experimental Opus PVQ word-byte helper

CPU160 / runtime QIO40. Raw RAM-packet benchmark, audio output OFF.
Five3-byte calls and a25-byte leaf in a57-byte previously unused encoder
range; table, all other addresses, static RAM and frames unchanged.
app903216 bytes; SHA256:
a53e2684fbfbe7c52743c0fcb0ec50301b7d6106a4b055a8659d84ffe7817b05

preflight.json contains actual linked/SAR/register/table proofs.
host.json contains24 exact PCM/state/PLC/reset/OOM cases through510kbps.
All30 A/B/A complete: CPU19285.91985 /84.01121 /85.91904%; both high-bitrate
gates PASS, exact PCM, unchanged static RAM/frame. Experimental raw baseline
accepted, not production or continuous-audio qualification. Default unchanged.
Min free DRAM1252 B retained;192 maximum call21.428ms. Ordinary restored OTA.
See CHANGELOG.md and comparison.json for all rates, maxima and limitations.
See docs/ESP8266_OPUS_ASM_PVQ_BYTE_WORD.md.
