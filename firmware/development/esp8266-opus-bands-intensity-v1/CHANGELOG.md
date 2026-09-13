# 2026-09-13 — diagnostic Opus ASM intensity

Опциональный `bands-intensity-asm`, без изменения default C. Ранний qn=1 путь
в intensity stereo; entropy и точность сохранены. CPU160/QIO40, raw RAM fixtures,
без физического аудиовывода в бенчмарке. 10 запусков, PCM exact, RAM/stack без роста.
192 кбит/с: 92,852 → 89,397% CPU. Полный отчёт:
`docs/ESP8266_OPUS_ASM_BANDS_RESULTS.md`, данные `comparison.json` и `runs/`.

Артефакт предназначен только для измерений, не обычного слушания радио.
