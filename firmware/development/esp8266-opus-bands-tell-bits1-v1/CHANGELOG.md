# 2026-09-13 — эксперимент Opus ASM tell-inline + bits1

Исходник `5a96989a`, backend `bands-tell-bits1-asm`, CPU160/QIO40.
Три constant-one чтения entropy заменены коротким ASM-путём с прежним
GCC refill fallback. App 903296 B (+80 к tell-inline); RAM/арены/стек без роста.

**Отклонён по скорости, не для обычного слушания.**
30 физических запусков: 10 tell-inline, 10 bits1, 10 повторных tell-inline.
192 кбит/с: 88,123→92,332→88,138% CPU; кандидат медленнее примерно на4,8%.
На128: 77,381→79,885→77,373%. Остальные битрейты также замедлились.
Цель70% не достигнута. Default не менялся.

Все PCM hashes точны; host ASAN/UBSAN, PLC/reset/OOM/guards прошли,
43 Node-регрессии PASS. Все попытки, максимумы и минимумы RAM сохранены
в runs/controls и comparison.json; preflight.json содержит linked-проверки.
Ни один неудачный или медленный результат не исключался; ошибок не возникло.

После измерений через OTA восстановлена обычная
`esp8266-opus-live512-idle3s-20260913`, app0 0x10000, I2S PDM32 GPIO3,
радио остановлено. restore-radio.json и restored-snapshot.json подтверждают
восстановление; главная HTML HTTP200 за100мс (web-smoke.log).
Это не полная browser QA и не проверка20секунд непрерывного live-аудио.
UART, разделы flash, Wi-Fi и SPIFFS не менялись.

[Полный разбор](../../../docs/ESP8266_OPUS_ASM_TELL_BITS1.md).
