# Opus ASM: no-normalize fast path ec_dec_update

2026-09-13. Отдельный diagnostic backend bands-update-fast-asm.
Цель ≤70% CPU ещё не достигнута; физическая скорость этого кандидата
до A/B неизвестна. C fallback и защищённый GCC snapshot не изменяются.

## Изменение

Два decoder call site в quant_partition/quant_all_bands заменены GAS-макросом.
Он вычисляет будущий rng в регистрах. Если rng > 2^23, записывает rng/val
без вызова и без стека. При rng <= 2^23 вызывает оригинальный ec_dec_update:
до вызова состояние и a2..a5 не изменены. Равенство порогу тоже нормализуется.
Не заменяются laplace, другие встроенные entropy-пути и общая функция.

Это не прежняя перепись всего ec_dec_update: нормализация остаётся исходной.
Цена холодного пути — повторное вычисление guard перед обычной функцией.
Комментарии описывают ABI, a6..a9 scratch, SAR, uint32 и отсутствие новых
литералов/буферов/stack slots. Сохранения caller не удаляются.

## Проверки перед платой

- Интерпретация реальных инструкций макроса: 100000 состояний и пороги.
  Проверяются uint32 через независимую BigInt-арифметику, регистры,
  неизменность состояния/аргументов при переходе к исходному вызову.
- 100000 сравнений host C-зеркала с исходным ec_dec_update:
  49360 без refill, 50640 с refill, 1549 с zero-padding; состояние и вход
  совпадают, ASAN/UBSAN включены.
- Полный PCM/PLC/reset/OOM пяти fixtures проверяет check_bands.cjs update-fast.
  Итог хранится в correctness.json; одну unit-проверку не считать полным PCM.
- LX106 object сгенерирован; семантика остальных функций и данные совпадают.
  Изменение padding соседних функций GAS допускается только вне fall-through;
  linked addresses/размеры и RAM нужно проверить после полной сборки.

## Динамические пути, не скорость

Host C, один проход по каждому 12-пакетному fixture, без self-test в счётчиках.
Полный PCM соответствует контролю. Это частоты двух bands-мест, не всех
вызовов ec_dec_update и не профиль тактов LX106.

| Поток | Вызовов | Без нормализации |
|---|---:|---:|
| mono12 | 0 | 0 |
| mono24 | 51 | 29 |
| stereo64 | 320 | 187 |
| stereo128 | 821 | 436 |
| stereo192 | 1318 | 580 |

На 192 кбит/с guard успешен в 44,01% случаев; в остальных вызов сохраняется.
Выигрыш по сокращению пролога нельзя автоматически перенести на весь декодер.

## Воспроизведение

- node tools/esp8266_opus_asm/update_fast.cjs <gcc.exe>
- node --test tests/esp8266-opus-update-fast-asm.test.js
- node tools/esp8266_opus_asm/check_update_fast.cjs
- node tools/esp8266_opus_asm/check_bands.cjs update-fast
- build_i2s_pdm_production.ps1: Diagnostic, EnableOpus,
  OpusBackend=bands-update-fast-asm, OpusWordAsm/IcdfFlashWord/FirFlashWord,
  NoSpiffsCache, Pdm32Iram/Pdm32Batch, OpusBenchmark и те же fixtures.
- По 10 fresh A/B/A через OTA, run_raw_series.ps1 IntervalMs=15000;
  сохранять все попытки, затем вернуть обычное радио.

Рецепт/manifest: components/opus_decoder/asm/lx106/bands-update-fast.json.
Проверки пути и unit: .build/opus-bands-update-fast/paths.json.
В production не включать без принятия измеренного результата и live-проверки.
