# Opus ASM: exact small division в конце flash

Эксперимент 2026-09-14, ESP8266 LX106, CPU160/QIO40.
Backend `bands-small-div-tail-asm`, выключен по умолчанию.

## Проверяемая гипотеза

[Микробенчмарк](ESP8266_OPUS_DIVISION_MICROBENCHMARK.md) показал ускорение
самого reciprocal-helper, но исходное размещение замедлило весь декодер.
Здесь меняется только размещение helper, его literal words и таблицы.
Это не новая арифметика, не увеличение кэша и не перенос в RAM.

Три вызова `rng/ft` используют тот же точный helper с четырьмя MUL16U,
коррекцией остатка и исходным ROM fallback для неподходящих делителей.
`val/ext`, исходный C и защищённый GCC snapshot не меняются.
ABI call0: a2=n, a3=d, результат a2; scratch a2..a11/SAR;
a0/a1/a12..a15 сохраняются, стек и RAM helper не использует.
Математика и ограничения описаны в [основном отчёте](ESP8266_OPUS_ASM_SMALL_DIV.md).

Helper, два literal words и таблица помещаются в `.irom1.text`.
SDK собирает эту входную секцию в конце `.flash.rodata`, в том же
cache-mapped `iram0_2_seg`; новый загружаемый сегмент не вводится.
L32R обращается назад к локальным выровненным словам.

Linked ELF подтверждает неизменные инструкции helper и все 129 слов таблицы.
Сам helper занимает 114 B, таблица 516 B. Flash text относительно свежего
tell-inline контроля вырос на 4 B, rodata на 644 B, app на 656 B
(903216 -> 903872 B). Static DRAM/IRAM, scratch и ABI прежние.

Проверенные горячие функции сохранили размеры, но **сдвинулись на 4 B**.
Полного сохранения адресов не достигнуто; скорость не доказывает количество
cache misses или отдельно стоимость инструкции. Три вызова дальнего helper
остаются L32R/CALLX. Новый опыт отделяет другое размещение от прежней
арифметики, но не изолирует полностью все эффекты компоновки.

## Воспроизводимость и проверки

- Генератор: `tools/esp8266_opus_asm/small_div_tail.cjs`.
- Рецепт и overlay: `components/opus_decoder/asm/lx106/bands-small-div-tail*`.
- `verify.cjs` проверяет hashes исходного snapshot, родителя и рецептов.
- Регрессия восстанавливает прежние секции и сравнивает весь ASM побайтно.
- Host PCM/ASAN/UBSAN до 510 кбит/с, PLC/reset/OOM наследуется только после
  проверки совпадения арифметики и hash прежнего semantic-mirror рецепта.
- Preflight/отчёт: `node tools/esp8266_opus_asm/report_small_div_tail.cjs [--preflight]`.
- Физические серии: `run_raw_series.ps1`, Attempts=10, IntervalMs=15000,
  fixtures из `firmware/development/esp8266-opus-asm-library/fixtures`.
- A/B/A2: свежий `esp8266-opus-tail-control-v1`, новый tail, тот же контроль.
  Стандартный кэш 16 КиБ. Пакеты заранее в RAM, output/function/stage profiler OFF.
- Отчёт сверяет все PCM hashes, samples/packets, полные fixtures, число раундов,
  сборки и OTA slots. Ошибки наблюдения и максимумы не исключаются.

Артефакты сохраняются в `firmware/development/esp8266-opus-small-div-tail-v1/`.
Физический результат будет записан после завершения всех трёх серий.
До этого ускорение не подтверждено; цель 70% и live I2S/WebUI не достигнуты.
