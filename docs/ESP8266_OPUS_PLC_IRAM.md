# Opus: SILK PLC в общей word-arena и диагностический scratch 4352

2026-09-13. Продолжение [SILK lending](ESP8266_OPUS_SILK_SCRATCH.md) и
[compact autocorrelation](ESP8266_OPUS_AUTOCORR_SCRATCH.md).
Host-тесты и перекомпиляция LX106 пройдены. Аппаратная приёмка этого варианта
ещё не выполнена; production по-прежнему использует scratch 6144, опции OFF.

## Изменение

`YORADIO_OPUS_SILK_PLC_IRAM` разрешает word-arena только для `sLTP_Q14` в
`silk_PLC_conceal`. Все обращения через него и алиасы `pred_lag_ptr` /
`sLPC_Q14_ptr` используют проверенные 32-битные load/store; обе копии LPC state
используют word-safe copy. Остальные SILK temporaries остаются в DRAM.
При нехватке места allocator использует DRAM, не увеличивая arena 16384 байта.
`SMALL_FOOTPRINT` с int16-алиасом, DEEP_PLC, OSCE и unbounded build запрещены
на этапе компиляции только при включённой опции. OFF сохраняет обычный C путь.

Комбинированный `-OpusLowRam` включает lending, compact autocorrelation и PLC
IRAM. Он разрешён только с `-Diagnostic -EnableOpus`. `-OpusScratchBytes 4352`
требует этот режим; 6144 остаётся default. Настоящие PowerShell/CMake гейты и
препроцессорные ограничения проверяются исполняемыми тестами, без запуска SDK.

## Сохранённые результаты

Отчёты: [phase 4352](../tools/esp8266_opus_profile/plc-iram-results/phase4352.json),
[leases 4352](../tools/esp8266_opus_profile/plc-iram-results/leases4352.json),
[IRAM fallback](../tools/esp8266_opus_profile/plc-iram-results/fallback.json),
[target stack](../tools/esp8266_opus_profile/plc-iram-results/target-stack.json).

- 22 фазовых сценария при фактической логической ёмкости scratch 4352:
  PCM bit-exact с pristine generic32, ASan/UBSan, reset и guards проходят.
  Общий наблюдавшийся пик 4168 байт, прежде с lending/compact было 4464.
- 11 lease-сценариев при 4352: точный PCM, packed packets до 120 мс,
  отложенный/изменяющий PCM потребитель, re-entry и аварийный возврат буферов.
- 8 SILK/PLC fallback-сценариев: 48/24 кГц, 1/6 PLC подряд, word capacity
  16384 либо 11232 (только persistent state). В последнем случае временные
  word allocations уходят в DRAM; пик достигает 4688 при scratch 6144,
  PCM и guards точные. Это тест fallback, не доказательство достаточности
  scratch 4352 при искусственно уменьшенной IRAM.
- Native adapter проходит с scratch 4352 и leases OFF/ON: headers, live join,
  granules, pre-skip, reset, packed packets, отмена и запрет heap allocation.
- Точная target-перекомпиляция LX106 GCC8.4/O3: отдельный frame `silk_PLC`
  256→176 байт относительно lending+compact. `_celt_autocorr` остаётся 160.
  Это не полный call-depth, ISR margin или физический stack watermark.

4352 оставляет 184 байта над измеренным пиком corpus; это не универсальная
граница для всех Opus packets. Уменьшение резервирования 6144→4352 даёт
1792 байта до учёта дополнительных state/bookkeeping. Целевую свободную кучу
нужно измерить после Wi-Fi/HTTP/decoder init. Не снижать 4096-byte Opus heap
reserve или защищённые 5120-byte основные стеки ради успешного запуска.

## Воспроизведение и следующие проверки

```powershell
node tools/esp8266_opus_profile/run_phase_regressions.cjs --silk-scratch --autocorr-compact --silk-plc-iram --capacity 4352 --sanitize --output .build/plc-phase-new.json
node tools/esp8266_opus_profile/run_block_regressions.cjs --low-ram --scratch-bytes 4352 --leased --output .build/plc-leases-new.json
node tools/esp8266_opus_profile/run_plc_iram_fallback.cjs --output .build/plc-fallback-new.json
node --test tests/esp8266-opus-low-ram-profile.test.js
$env:YORADIO_OPUS_LOW_RAM='1'
$env:YORADIO_OPUS_FAST_INT64='0'
node --test tests/esp8266-native-opus.test.js
Remove-Item Env:YORADIO_OPUS_LOW_RAM
Remove-Item Env:YORADIO_OPUS_FAST_INT64
```

- [x] Полная диагностическая сборка, map/manifest/hash и проверка конечных flags.
- [ ] OTA, не менее десяти LAN попыток >=20 с непрерывного физического вывода;
  сохранить все OOM/WDT/network отказы, не считать idle DMA после отказа успехом.
- [ ] A/B чистого кодека из flash/RAM: task CPU, не wall time, и сравнение с
  исходным C. Скорость новой организации памяти ещё не измерена на плате.
- [ ] Реальные Opus станции, WebUI/Stop/Play/Next и длительные смены кодеков.

Этот результат сам по себе не доказывает непрерывное воспроизведение Opus.

## Первая физическая проверка: low-RAM + PCM queue

Источник `c470f55`, образ
`firmware/development/esp8266-opus-lowram4352-queue256/app.bin`, 891936 байт.
SHA-256 `0e53cacbe7dd52e8327809d3aebe0413c303d193b452d3896e370ed107fef11f`.
OTA успешно переключила app с0x10000 на0x110000. CPU160/QIO40, I2S PDM32,
2x256 DMA words, 2x960 mono PCM samples, consumer stack1536, scratch4352,
idle timeout3000ms; Opus heap reserve4096 и основные стеки не уменьшены.

Собственный CELT64 файл по LAN, 10 запусков, минимум25с наблюдения каждого:
**0/10 прошли gate непрерывности**. Новый вариант не признан рабочим default.
Инициализация и выдача PCM иногда удавались, но это не непрерывное радио.

| Попытка | Сохранённый отказ инициализации | Свободно CAP8 / крупнейший блок |
| --- | --- | --- |
| 3 | State6598 не выделился | 7680 / 5552 байта: непрерывного блока недостаточно |
| 6 | Scratch4352 не выделился | 2216 / 592 байта: недостаточно и суммарной памяти |
| 8 | Scratch4352 не выделился | 6540 / 4288 байта: непрерывного блока недостаточно |
| 9 | Post-init reserve4096 | snapshot2220 / 1288 байт |
| 10 | Post-init reserve4096 | snapshot3320 / 1888 байт |

В остальных финальных init-snapshot stage0 означает отсутствие сохранённого
init failure, а не отсутствие сетевых/аудиоошибок. Были HTTP observation
timeouts, повторные подключения и остановки входа; одна измеренная попытка
дала лишь4.327с PCM за30.426с времени платы. Ошибочные/неполные окна не
исключались и не использовались для расчёта успешной скорости.

Минимум из полученных health-снимков free heap6640, но lifetime min heap
опустился до308 байт. Это разные метрики: редкие snapshots не видят пиков.
Минимальные наблюдавшиеся свободные стеки: main1416/5120, consumer1160/1536.
Они не доказывают покрытие всех error/normalizer путей. В доступных snapshots
reset reason2; отсутствие наблюдённого WDT не является непрерывной трассировкой.

Отчёты OTA/Stop/все десять запусков и TCP trace сохранены рядом с образом.
По окончании серии поток остановлен, собственный LAN-сервер завершён.
Следующий шаг — отдельный raw CPU A/B (6144 baseline против low-RAM4352)
с тем же corpus12/24/64/128/192, без удалённого аудио и физического вывода.
Для очереди нужен дополнительный реальный запас DRAM и проверка lifecycle
сети; только уменьшения scratch пока недостаточно.
