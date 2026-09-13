# Opus ASM: первые результаты CELT bands

2026-09-13. [Рабочий план](ESP8266_OPUS_ASM_BANDS_OPTIMIZATION_PLAN.md).

## Итог

Два независимых изменения проверены на Wemos D1 mini / ESP8266, 160 МГц,
QIO 40 МГц, O3, фиксированная точка. Полный декодер собран из сохранённого
GCC ASM; изменены только отдельные reviewable overlays. Эталон не переписан.

| Поток, кбит/с | GCC-ASM CPU, % | Intensity shortcut, % | Block shifts, % |
|---|---:|---:|---:|
| Mono 12 | 22,780 | 22,808 | 22,877 |
| Mono 24 | 54,702 | 54,621 | 54,616 |
| Stereo 64 | 65,539 | 64,360 | 65,954 |
| Stereo 128 | 80,729 | 77,723 | 79,114 |
| Stereo 192 | 92,852 | 89,397 | 90,654 |

Это медианы 10 физических запусков на вариант. После intensity повторены ещё
10 контрольных запусков: 192 кбит/с снова 92,911%. Итого **40 запусков**,
все сохранены, без удаления выбросов/ошибок. Полученный выигрыш intensity
на 192 кбит/с — 3,72% времени относительно первого контроля и 3,78% относительно
повторного, или около 3,5 процентного пункта CPU.

Сохранить `bands-intensity-asm` как полезный эксперимент. Небольшой рост mono 12
(0,028 процентного пункта, 0,12% относительно контроля) явно указан, а не скрыт.
`bands-blocks-asm` выигрывает 2,37% времени на 192 кбит/с, но проигрывает 0,63%
на 64 кбит/с и 0,43% на mono 12. По уточнённому критерию пользователя
**принимаем и blocks**: ускорение высоких битрейтов важнее небольшого замедления
низких и превышает его. Комбинация требует отдельного A/B, production пока не меняем.

Цель 70% ещё не достигнута. Непрерывность настоящего воспроизведения и
совместная стоимость demux/нормализации/PDM этим тестом не квалифицированы.
Максимальный wall-вызов на 192 кбит/с: intensity 24,346 мс, blocks 22,049 мс;
это включает вытеснение, а не только инструкции декодера. Заявлять отсутствие
всех пропусков или соблюдение deadline каждого 20-мс кадра пока нельзя.

## Что именно изменено

### Intensity

В stereo-only clone `compute_theta` внутри `quant_all_bands`, если decode и
`i >= intensity`, выполняется переход в существующий путь qn=1 до software
division и exp2 lookup. Сохранённые m/i/bandE/N/b остаются корректны; tell,
inversion entropy, qalloc и gain обновляются исходным кодом. Encoder не затронут.

Новых вызовов, stack slots или маскирования IRQ нет. Функция в объекте +12 байт;
полный image +32 байта с учётом линковки/выравнивания. Backend по умолчанию — C,
опция доступна только в diagnostic.

### Block shifts

Три decoder-сайта: N/B в `quant_band`, len/B и N/B в `alg_unquant` (встроенные
rotation и collapse mask). Проверка B!=0 и B&(B−1)==0, NSAU, точный unsigned
shift. Нестепенной/неизвестный B идёт в исходный `__udivsi3`; произвольный stride2,
qn и entropy divisions не затронуты. Показатель считается на вектор, не на sample.

Новых stack slots/буферов нет; image +96 байт. GAS изменил padding и местами
MOV density encoding в соседних функциях. Инструкции, операнды и граф переходов
проверены независимо от адресов, а данные/relocations проверены отдельно.

## Корректность и память

- Host ASAN/UBSAN: 5 fixtures, смешанная последовательность/PLC, reset,
  восстановление после OOM; PCM побитно совпадает, ошибка 0, SNR к эталону ∞.
- Intensity: 51744 сочетания N/budget/intensity/mono/stereo/encode.
- Block shifts: 3,2 млн сравнений для unsigned 32-bit и всех степеней двойки,
  включая старший бит; нестепенные делители сохраняют fallback.
- На плате совпадают все 5 golden FNV PCM hashes, samples/packets и scratch.
- DRAM data 1652 B, DRAM bss 18752 B, IRAM text 22900 B, IRAM bss 4044 B,
  vectors 128 B — одинаковы во всех трёх сборках.
- Audio stack 5120 B, минимальный остаток 1660 B во всех вариантах.
- На 192 кбит/с scratch DRAM peak 5488 B из 6144 B; общий IRAM arena peak
  15600 B из 16384 B. Никаких новых постоянных RAM-буферов.
- Минимум DRAM в замерах: контроль 3796 B (один краткий выброс), intensity
  8020 B, blocks 7684 B. Это наблюдения разных моментов, **не экономия RAM**.
  После cleanup оставалось примерно 26,1–26,7 КБ; ошибки наблюдения отсутствуют.

В первой локальной модели blocks было +32 B DRAM scratch. Причина — тестовая
копия vq.c искала component/config.h вместо celt/config.h и теряла WORD_SCRATCH.
Исправлена приоритетность include только для копий CELT, тесты повторены: пики
стали одинаковы. Это дефект harness, не результат ASM на микроконтроллере.

## Следующий кандидат: обратная таблица

`pulse_inverse.cjs` проверяет все 23 строки и b=−256..16383 (382720 комбинаций)
против **настоящей функции bits2pulses из rate.h**, а не только JS-модели.
Точное совпадение, включая повторы и tie-breaking. Предполагаемые runtime
таблицы: 5980 B packed lookup + 392 B offset map = 6372 B flash. Reference arrays
в host harness нужны только тесту. ASM-интеграция, custom-mode fallback и замер
скорости ещё впереди; выигрыша по скорости этому прототипу не приписываем.

## Воспроизведение и сохранённые результаты

Fixtures: `firmware/development/esp8266-opus-asm-library/fixtures`, 12 пакетов
по 20 мс на поток, 10 измеряемых раундов после warmup — 120 пакетов / 2,4 с
аудио в каждом случае каждого запуска. Пакеты заранее в RAM. Wi-Fi/WebUI
включены; загрузка радиопотока, demux, нормализация и PDM исключены. Task CPU
исключает другие задачи, но включает начисленные ISR и измерительные издержки.
Function/stage profiler отключён. Серии A/B/A/C последовательные, не randomized.

- `firmware/development/esp8266-opus-bands-control-v1/{initial,repeated}` — 20 запусков.
- `firmware/development/esp8266-opus-bands-intensity-v1` — app, manifest,
  sdkconfig, 10 запусков, comparison.json с SHA256 и host результатами.
- `firmware/development/esp8266-opus-bands-blocks-v1` — аналогично.
- `firmware/development/esp8266-opus-bands-pulse-inverse/prototype.json` — проверка таблицы.

Сборка через `tools/esp8266_audio_profile/build_i2s_pdm_production.ps1`:
`-Diagnostic -EnableOpus -OpusBackend bands-intensity-asm` (или `bands-blocks-asm`),
`-OpusWordAsm -OpusIcdfFlashWord -OpusFirFlashWord -NoSpiffsCache -Pdm32Iram
-Pdm32Batch -OpusBenchmark -OpusBenchmarkFixtures <fixtures>`.
Явно задать RuntimeRoot, SdkPath и отдельный Variant как в существующих профилях.

Рецепты: `bands.cjs intensity <gcc.exe>` / `blocks.cjs <gcc.exe>`.
Host: `node tools/esp8266_opus_asm/check_bands.cjs intensity` / `blocks`.
Плата: `run_raw_series.ps1 -Directory <новый каталог> -Fixtures <fixtures>
-Attempts 10 -IntervalMs 15000`. Использовать только OTA, не UART на GPIO3.
Архивация: `report_bands.cjs intensity` / `blocks` (пути этой серии явно заданы).

После тестов восстановить исходную обычную radio-сборку
`esp8266-opus-live512-idle3s-20260913`, I2S PDM на GPIO3, состояние stopped.
Доказательство восстановления сохраняется вместе с контрольной серией.
