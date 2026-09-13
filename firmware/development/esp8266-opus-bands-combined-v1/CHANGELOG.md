# 2026-09-13 — combined Opus ASM experiment, rejected

`bands-combined-asm` объединяет intensity shortcut и block-count shifts.
CPU160/QIO40/O3, raw RAM benchmark, 10 запусков. PCM, scratch, RAM и стек без
изменений. 192 кбит/с требует 94,041% CPU против 92,852% контроля: комбинация
не принята даже при приоритете высоких битрейтов. Независимый intensity лучше:
89,397% CPU. Production/default C не изменены. Файлы сохранены для воспроизводимости.

Данные: `comparison.json`, `runs/`, `layout.json`; описание:
`docs/ESP8266_OPUS_ASM_BANDS_RESULTS.md`. Это тестовая прошивка, не обычное радио.
