# 2026-09-13 — diagnostic Opus ASM pulse lookup, отрицательный результат

Опциональный `bands-pulse-lookup-asm`, default C не изменён. Inline lookup
в quant_partition, 6372 B таблиц flash, исходный поиск как fallback.
CPU160/QIO40, raw RAM fixtures, без физического аудиовывода в бенчмарке.
Image 909504 B, SHA256 в manifest.json; сборка не предназначена для слушания.

10 свежих контролей + 10 кандидатов, точный PCM, RAM/stack без роста.
192 кбит/с: 92,896 → 104,139% CPU, **замедление 12,10%**. Не принят.
128 кбит/с: замедление 8,85%; остальные значения в comparison.json.
Host PCM/PLC/reset/OOM и 25/25 регрессионных Node-тестов пройдены.

Документация: `docs/ESP8266_OPUS_ASM_BANDS_RESULTS.md`.
Все 10 запусков кандидата — runs/, контроль — соседний
`esp8266-opus-bands-control-v1/pulse-lookup-20260913/`.
control-ota.json / ota.json — загрузки эксперимента; restore.json подтверждает
восстановление обычной `esp8266-opus-live512-idle3s-20260913` через OTA,
I2S PDM GPIO3, состояние stopped. Wi-Fi/плейлист/SPIFFS не перепрошивались.
