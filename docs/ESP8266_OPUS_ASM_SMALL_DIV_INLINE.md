# Opus ASM: точное деление inline

Дата: 2026-09-14. Отдельный эксперимент; по умолчанию выключен.

## Проверяемая гипотеза

Микротест прежнего reciprocal-helper дал выигрыш, но полный декодер с
отдельным flash-вызовом замедлился. Здесь убирается только этот вызов:
арифметика раскрыта ASM-макросом в трёх существующих местах rng/ft
(`ec_decode` и два GCC-inlined пути в `ec_dec_uint`). Общая таблица остаётся
одной: 129 выровненных слов, 516 байт flash, без копирования в RAM.

`bands-small-div-inline-asm` основан на лучшем `bands-tell-inline-asm`.
Не используется отвергнутый обмен IRAM или tail-helper. Для d=1 возврат n,
для 2..256 точное reciprocal-деление с коррекцией остатка, для d=0/>256
исходный ROM `__udivsi3` с исходными аргументами. Лимита битрейта нет.
Деления val/ext и другие функции не изменены. Стек и C fallback сохранены.

Вход/выход a2=n,a3=d -> a2; a2..a11/SAR допускают изменения по исходному
call0 ABI. Fast path не трогает a0/a1/a12..a15, не пишет память. Обе внешние
GCC-функции уже сохраняют a0. ROM fallback остаётся обычным call0.

## Проверки до платы

- [x] Source/recipe hashes и обратимое изменение ровно трёх вызовов.
- [x] Реальные linked expansions: 112/114/112 байт; после схлопывания
  назад к ROM-call CFG обеих функций совпадает с контролем, включая стек.
- [x] Исполнение модели реальных инструкций: 1 050 880 входных случаев,
  20 fallback, точное unsigned-частное, сохранность ABI и word-only loads.
  GAS преобразует SRLI16 в EXTUI16,16; модель учитывает машинную инструкцию.
- [x] Неизменённая семантическая C-модель: точный PCM до 510 кбит/с,
  mixed/PLC/reset/OOM. Это host-модель, не исполнение LX106 на компьютере.
- [x] Статическая RAM одинакова; app 903216 -> 904080 B (+864 B flash).
- [ ] 10 физических контрольных +10 candidate +10 повторных контрольных.
- [ ] Сохранить все попытки/максимумы, принять либо отклонить по 128/192.
- [ ] Вернуть обычную прошивку и проверить HTTP/WebSocket.
- [ ] Если ускорение подтверждено, отдельно проверить живой I2S PDM/WebUI.

## Воспроизведение

Генератор: `tools/esp8266_opus_asm/small_div_inline.cjs <LX106 gcc.exe>`.
Сборщик: `tools/esp8266_audio_profile/build_i2s_pdm_production.ps1` с
`-Diagnostic -EnableOpus -OpusBackend bands-small-div-inline-asm
-OpusWordAsm -OpusIcdfFlashWord -OpusFirFlashWord -NoSpiffsCache
-Pdm32Iram -Pdm32Batch -OpusBenchmark -OpusBenchmarkFixtures
firmware/development/esp8266-opus-asm-library/fixtures -WebAudioPause off`.
Контроль отличается только backend `bands-tell-inline-asm` и именем variant.
CPU160/QIO40/cache16; сеть и вывод не входят в raw-путь декодирования.

`node tools/esp8266_opus_asm/report_small_div_inline.cjs --preflight`
проверяет обе сборки. Без ключа собирает результаты A/B/A. Series runner:
`tools/esp8266_opus_profile/run_raw_series.ps1`, Attempts10, IntervalMs15000.
Прошивки: `firmware/development/esp8266-opus-inline-control-v1/` и
`firmware/development/esp8266-opus-small-div-inline-v1/`.

На момент подготовки скорость не подтверждена; это не production и не
достижение цели 70%. Размер кэша и частота flash не изменяются. Даже без
helper-call таблица/увеличенный код могут ухудшить полный декодер.
