# Opus ASM: обмен IRAM между entropy-кодом и PDM32

Дата: 2026-09-14. Эксперимент, выключен по умолчанию. Не production.

## Гипотеза

После отрицательного [ROM/flash-helper опыта](ESP8266_OPUS_ASM_FROZEN_DIV.md)
проверяем другой путь: исполнять самые частые небольшие entropy-функции из
IRAM, не добавляя RAM и не меняя арифметику. Основа — прежний лучший полный
GCC ASM backend `bands-tell-inline-asm`, а не медленный small-div.

Опция сборки `-OpusEntropyIramSwap` /
`YORADIO_OPUS_ENTROPY_IRAM_SWAP=ON` переносит только code/literals:

| Функция | Размер linked code | Назначение | Кандидат |
|---|---:|---|---|
| ec_decode | 63 B | Частное диапазона entropy decoder | IRAM 0x40105824 |
| ec_dec_update | 171 B | Обновление интервала/нормализация | IRAM 0x40105864 |
| ec_dec_bit_logp | 172 B | Декодирование бинарного символа | IRAM 0x40105910 |
| i2s_pdm_pack32 | 456 B | Task-only формирование PDM32 | flash 0x4021a0ec |

Все инструкции происходят из защищённого ASM snapshot. Call0 ABI, аргументы,
состояние entropy decoder, стек и C fallback не меняются. Дальние вызовы
линкер вправе превратить в L32R/CALLX0; CFG-проверка разрешает только такое
эквивалентное изменение, разрешает literal addresses и сравнивает ветви.
Это **не** делает функции безопасными при выключенном flash-cache:
их вызываемые функции могут оставаться во flash.

`nodac_slc_isr` и Wi-Fi ISR не переносятся. PDM packer вызывается задачей,
не DMA ISR. `-Pdm32Iram` остаётся обязательным: его `pdm32_iram.lf` уже
перенёс cold `__moddi3` (959 B) во flash. Выключение этого флага без сохранения
mapping вернуло бы959 B в IRAM. Реальные callers — только adjtime/SNTP,
что дополнительно проверено по SDK/object relocations.

## Память

| Секция | Контроль | Кандидат | Разница |
|---|---:|---:|---:|
| IRAM text | 22900 | 22844 | −56 B |
| IRAM vectors | 128 | 128 | 0 |
| IRAM bss | 4044 | 4044 | 0 |
| DRAM data | 1652 | 1652 | 0 |
| DRAM bss | 18752 | 18752 | 0 |
| App binary | 903216 | 903152 | −64 B |

Арена16 КиБ, scratch, PCM/DMA, стеки и входные буферы не уменьшаются.
Приоритет — скорость192 кбит/с, а не эта небольшая экономия сама по себе.

## Воспроизводимость

```powershell
tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 `
 -SdkPath C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk `
 -RuntimeRoot C:/Work/yoRadio/.build -Variant esp8266-opus-entropy-iram-v1 `
 -Diagnostic -EnableOpus -OpusBackend bands-tell-inline-asm -OpusEntropyIramSwap `
 -OpusWordAsm -OpusIcdfFlashWord -OpusFirFlashWord -NoSpiffsCache `
 -Pdm32Iram -Pdm32Batch -OpusBenchmark -WebAudioPause off `
 -OpusBenchmarkFixtures firmware/development/esp8266-opus-asm-library/fixtures
```

Для контроля убрать только `-OpusEntropyIramSwap`, использовать отдельный
variant `esp8266-opus-entropy-control-v1`. Сохранённые результаты не
перезаписывать при изменении исходников; для нового опыта менять variant.
`node tools/esp8266_opus_asm/entropy_iram.cjs --preflight` проверяет обе
прошивки/manifest, RAM и linked ASM, включая сравнение со старым лучшим
контролем. Без `--preflight` собирает все30 физических A/B/A результатов.

- [x] Сборка двух профилей, guard неверных конфигураций, actual linked graph.
- [x] Реальный PDM packer:493216 побитно точных слов/состояний под UBSan.
- [x] Отдельно запустить прежний SDK/linker тест на свежем control build:
  `pdm-placement-check.json`. Старый тест сам пропустил этот пункт, поскольку
  его прежняя `.build/esp8266-opus-live-join` отсутствует.
- [ ] 10 контрольных /10 IRAM /10 повторных контрольных физических запусков;
  CPU160/QIO40/cache16, 12/24/64/128/192 кбит/с, пакеты в RAM,
  output/function/stage profiling OFF; все попытки и максимумы сохранить.
- [ ] При выигрыше — отдельная live-проверка с I2S PDM и WebUI не менее20с:
  перенос паковщика во flash может ухудшить вывод, даже если raw быстрее.

Предварительно7 PASS,0 FAIL,1 SKIP; пропущенная placement-проверка выполнена
отдельной командой. Измерения скорости ещё не завершены, ускорение и цель70%
не заявлены. Артефакты: `firmware/development/esp8266-opus-entropy-{control,iram}-v1/`.
