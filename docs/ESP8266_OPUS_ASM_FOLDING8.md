# Opus ASM: точная таблица folding scale

2026-09-14. Независимый эксперимент, backend `bands-folding8-asm`, default OFF.

## Основание и границы

На192 кбит/с исходный `celt_sqrt(N0<<22)` вызывается260 раз за240 мс аудио,
не на каждом сэмпле. Все эти вызовы имеют N0, кратное8 и не больше176.
Поэтому проверяется таблица23 выровненных uint32 (92 B flash), вместо полной
таблицы21 полос ×4 LM. Для остальных N0 остаётся исходный sqrt. Это не
лимит битрейта/режима; короткие кадры и другие полосы сохраняют fallback.
Снижение вычислений небольшое, влияние размещения flash заранее неизвестно.

Счётчик `profile_folding.cjs` работает только на host, без модификации
firmware. `constant_N2_calls` в census обозначает все вызовы с размером2,
а не точное число попаданий в конкретный GCC-inlined call site. Этот site
в `quant_all_bands` в данном эксперименте не меняется; N2 нет у192 fixtures.

| Поток | Вызовов | Табличный путь | Аудио, мс |
|---|---:|---:|---:|
| mono12 | 0 | 0 | 240 |
| mono24 | 36 | 36 | 240 |
| stereo64 | 255 | 255 | 240 |
| stereo128 | 260 | 260 | 240 |
| stereo192 | 260 | 260 | 240 |
| stereo320,2.5 мс | 1164 | 97 | 242.5 |
| stereo320,5 мс | 980 | 245 | 245 |
| stereo320,10 мс | 580 | 348 | 250 |
| stereo320,20 мс | 260 | 260 | 260 |
| stereo510 | 1280 | 1280 | 1220 |

## Проверки

- [x] Коэффициенты получены компиляцией исходного **fixed-point** celt_sqrt.
  Probe явно включает config.h и имеет #error без FIXED_POINT. Это важно:
  без конфигурации mathops.h выбирает системный sqrt; например N0=8 даёт
  5792 вместо правильных для исходного Opus5793. Такая промежуточная ошибка
  host-probe исправлена до сборки/прошивки; тест закрепляет это различие.
- [x] Все84 штатных сочетания21 полос ×LM0..3;20 разных N0 и fallback.
- [x] Host PCM побитно одинаков до510 кбит/с, mixed/PLC/reset/OOM под ASan/UBSan.
- [x] Реальный linked ASM:108193 значений/ABI/границы, таблица ELF проверена.
  После схлопывания одного нового блока к исходному call0 CFG/стек совпадают.
- [x] Статическая RAM прежняя; app903216 ->903344 B (+128 B flash).
- [ ] 10 контрольных +10 folding8 +10 повторных контрольных физических запусков.
- [ ] Сохранить все попытки, максимумы и решение по128/192.
- [ ] Вернуть обычную прошивку, проверить HTTP/WS. При реальном выигрыше —
  отдельное живое I2S PDM/WebUI воспроизведение не менее20 секунд.

Вход блока: a14=N0, a2=исходный N0<<22. Выход a2. Fast path использует
только call0-volatile a3/a4; сохраняет a0/a1/a12..a15, не пишет память.
Unsigned bound перед загрузкой исключает отрицательный/слишком большой N0;
прочие значения вызывают оригинальный celt_sqrt с оригинальным аргументом.
Сохранён GCC ASM и C backend; меняется один вызов в `quant_band`.

## Воспроизведение

`node tools/esp8266_opus_asm/profile_folding.cjs` создаёт census и точные
коэффициенты. Результат сохранён в `tools/esp8266_opus_asm/folding-census-results.json`.
`node tools/esp8266_opus_asm/folding8.cjs <LX106 gcc.exe>` создаёт overlay.
`node tools/esp8266_opus_asm/check_bands.cjs folding8` проверяет host PCM.
`node tools/esp8266_opus_asm/report_folding8.cjs --preflight` проверяет ELF.
Без --preflight последний скрипт архивирует/сравнивает физические A/B/A.

Сборщик `tools/esp8266_audio_profile/build_i2s_pdm_production.ps1`:
`-Diagnostic -EnableOpus -OpusBackend bands-folding8-asm -OpusWordAsm
-OpusIcdfFlashWord -OpusFirFlashWord -NoSpiffsCache -Pdm32Iram -Pdm32Batch
-OpusBenchmark -OpusBenchmarkFixtures firmware/development/esp8266-opus-asm-library/fixtures
-WebAudioPause off`. Контроль — тот же набор с backend bands-tell-inline-asm.
CPU160/QIO40/cache16. Новые прошивки сохранены в firmware/development:
`esp8266-opus-folding-control-v1` и `esp8266-opus-folding8-v1`.
Это raw-профили; пока не подтверждают ускорение и не достигают цели70%.
