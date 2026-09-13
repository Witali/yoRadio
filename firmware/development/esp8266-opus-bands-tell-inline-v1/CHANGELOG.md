# 2026-09-13 — diagnostic Opus ASM tell-inline

Сборка из 97b0c861, backend bands-tell-inline-asm, CPU160/QIO40.
Четыре вызова ec_tell_frac заменены точным GAS-макросом, общая исходная таблица.
App 903216 B (+224), RAM и стек без роста; default C не изменён.

30 физических запусков: 10 контроль, 10 кандидат, ещё 10 контроль.
192 кбит/с: 92,870 → 88,136% CPU, повторный контроль 92,877%.
Выигрыш около 5,10%, точный PCM. Небольшое замедление mono 12/24 явно
сохранено в comparison.json. Принят как эксперимент, цель 70% не достигнута.
28/28 Node-регрессий и host PCM/PLC/reset/OOM пройдены.

Это raw benchmark, не прошивка для обычного слушания. Полный отчёт:
docs/ESP8266_OPUS_ASM_TELL_INLINE_RESULTS.md. Все попытки и OTA-подтверждения
сохранены. restore-after-repeat.json: восстановлена обычная radio-сборка,
I2S PDM GPIO3, stopped, слот 0x110000. Разметка, SPIFFS, Wi-Fi и плейлист не менялись.
