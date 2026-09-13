# 2026-09-13 — diagnostic Opus ASM block shifts

Независимый `bands-blocks-asm`: три guarded unsigned N/B division shortcuts,
NSAU/shift и fallback libgcc. Не содержит intensity shortcut.
CPU160/QIO40, raw RAM fixtures, 10 запусков. PCM/scratch exact, RAM/stack не выросли.
192 кбит/с 90,654% CPU, но 64 кбит/с на 0,63% медленнее контроля. Принят по
приоритету высоких битрейтов (выигрыш 2,37% > регрессия 0,63%); совместный
вариант с intensity проверяется отдельно. Production default не изменён.
Результаты: `comparison.json`, `runs/`, `docs/ESP8266_OPUS_ASM_BANDS_RESULTS.md`.

Только бенчмарк, не обычная прошивка радио.
