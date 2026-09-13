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

- [ ] Полная диагностическая сборка, map/manifest/hash и проверка конечных flags.
- [ ] OTA, не менее десяти LAN попыток >=20 с непрерывного физического вывода;
  сохранить все OOM/WDT/network отказы, не считать idle DMA после отказа успехом.
- [ ] A/B чистого кодека из flash/RAM: task CPU, не wall time, и сравнение с
  исходным C. Скорость новой организации памяти ещё не измерена на плате.
- [ ] Реальные Opus станции, WebUI/Stop/Play/Next и длительные смены кодеков.

Этот результат сам по себе не доказывает непрерывное воспроизведение Opus.
