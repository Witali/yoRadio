# 2026-09-13 — unchanged GCC ASM control

Копия ранее проверенного `esp8266-opus-functions-control-v2`: без function/stage
profiler, CPU160/QIO40, raw Opus benchmark. 10 запусков до intensity и 10 после.
App/manifest не изменены; сохранены для воспроизводимости A/B/A/C.
Initial 192 кбит/с median 92,852%; repeated 92,911%. Все измерения оставлены,
включая краткий минимум DRAM 3796 B. Обычную radio-прошивку после серии возвращаем OTA.
