# Diagnostic TCP out-of-order OFF — 2026-09-17

Ordinary radio, all18 accepted ASM stages, I2S PDM32 GPIO3, CPU160/QIO40.
Opus input1024B, scratch6144B/reserve4096B. TCP OOSEQ disabled by SDK option.
App883712B; exact SHA256 and effective flags are in manifest.json.
All loaded sections and accepted instruction graphs verified in preflight.json.

NOT QUALIFIED:10 live Deutschlandfunk24kbps attempts,0 continuous windows.
No decoder-init failure latched, but450..3931 underruns in complete windows;
three missing HTTP measurement windows. Reduced RAM retention is insufficient.
Not a production default. OTA and every failure are retained in board/.
