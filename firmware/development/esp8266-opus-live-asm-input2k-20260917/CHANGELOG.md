# Diagnostic input2k — 2026-09-17

Ordinary radio, all18 accepted ASM stages, I2S PDM32 GPIO3, CPU160/QIO40.
Compressed Opus input grows1024 ->2048B; scratch6144B/reserve4096B unchanged.
App885792B; exact SHA256 and effective flags are in manifest.json.
All loaded sections and accepted instruction graphs verified in preflight.json.

REJECTED:10 live Deutschlandfunk24kbps attempts,0 continuous windows.
Several starts hit the unchanged4KiB reserve guard (stage10); no guard lowered.
Not a production default. OTA and every failure are retained in board/.
