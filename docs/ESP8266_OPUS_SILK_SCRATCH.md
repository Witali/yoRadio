# Opus: временное использование состояния SILK для CELT

Дата: 2026-09-13. Статус: **проверенный host-эксперимент, OFF по умолчанию**.
`YORADIO_OPUS_CELT_SILK_SCRATCH=0`; production/build profiles не изменены,
target CMake option пока не добавлен. На плату этот эксперимент не загружался.

## Зачем

Асинхронная очередь PCM не прошла [аппаратную приёмку](ESP8266_OPUS_PCM_QUEUE.md):
не хватает DRAM с сохранением 4096 байт heap reserve и 5120-байтного основного
стека. Даже consumer stack 1536 и DMA2×256 добавляют 1488 байт плюс служебные
структуры относительно синхронного DMA2×512. Нужна реальная экономия памяти,
а не уменьшение защитного резерва или подавление ошибок.

## Владение и найденный дефект

В основном CELT-only кадре тела двух SILK channels не используются. Временно
предоставляем их bounded scratch allocator после доступного word-only IRAM,
до отдельного DRAM scratch. SILK super-struct не заимствуется: там остаются
число каналов и стереосостояние. Два указателя `exc_Q14` сохраняются в Opus
header и восстанавливаются как при нормальном возврате, так и при OOM longjmp.
Перед следующим SILK decode channel bodies сбрасываются. Арифметика не меняется.

Первый прототип ошибочно разрешал заимствование внутри вложенного CELT PLC
при переходе CELT→SILK/Hybrid. Новый SILK state в этот момент **уже заполнен**:
его перезапись меняла следующий PCM. Регрессия `standard-mixed-plc` это выявила.
Исправление: требовать CELT-only не только в локальном `mode`, но и во внешнем
`st->mode`. Nested transition PLC и hybrid/redundancy не получают этот scratch.
При отключённом флаге новых полей и ветвей allocator нет.

## Результаты

Сравнение с независимо подготовленным pristine generic32, host GCC13.3,
`OPUS_FAST_INT64=0`, mono PCM48k. Это не 32-битный ABI ESP8266.

| Сценарий | Отдельный DRAM scratch до | С экспериментом |
| --- | ---: | ---: |
| SILK mono12 | 1808 | 1808 |
| Hybrid mono24 | 2904 | 2904 |
| CELT stereo64/128/510, чистые кадры | 5488 | 0 |
| Смешанные режимы + одиночный PLC | 5968 | 4624 |
| Смешанные packed packets до120мс | — | 4464 |

Все числа в байтах. Ноль отдельного scratch **не означает нулевую память**:
CELT использует до5488 байт существующего SILK state, плюс IRAM/PCM/прочие
данные. Word arena peak остаётся15600/16384. Host state вырос6654→6678 байт;
добавились также allocator bookkeeping и поле scratch mark на стеке. Target
стоимость ещё не измерена. Нельзя объявлять1344 байта снижения corpus peak
чистой экономией всей прошивки или универсальным максимумом4624.

- 22 phase cases: PCM exact, reset exact, guards; SILK/Hybrid/CELT,
  2.5/5/10/20мс, VBR, packed, одиночные/серийные PLC, 8/12/16/24кГц guards.
- Те же22 случая прошли ASan/UBSan без ошибок.
- 11 block cases: packed до120мс, переиспользование/изменение PCM потребителем,
  отсутствие malloc в decode и отказ re-entry; PCM exact.
- Те же11 случаев с PCM leases: отложенный потребитель, отмена и возврат
  незавершённого буфера при OOM; PCM exact.
- Native adapter: оба режима leases OFF/ON прошли headers, granules,
  pre-skip, live join, reset, отмену, повреждённые данные и память.
- **8182 инъекции OOM в72 CELT packets**: после каждого scratch allocation
  при активном loan блок намеренно перезаписывается, затем вызывается longjmp.
  `OPUS_RESET_STATE` выполняется без предварительного bind/init и снова даёт
  точный SILK PCM. ASan/UBSan чистые, decoder guards сохранены.

Старое предположение «любой CELT обязан упасть с0/8B DRAM scratch» теперь
неверно. OOM smoke использует SILK packet, требующий отдельный scratch; новый
fault probe отдельно проверяет аварии **во время** loan, включая указатели.

Сырые отчёты: [phase](../tools/esp8266_opus_profile/silk-scratch-results/phase.json),
[ASan/UBSan phase](../tools/esp8266_opus_profile/silk-scratch-results/phase-sanitize.json),
[blocks](../tools/esp8266_opus_profile/silk-scratch-results/blocks.json),
[leases](../tools/esp8266_opus_profile/silk-scratch-results/leases.json),
[OOM](../tools/esp8266_opus_profile/silk-scratch-results/faults.json).
В них сохранены входные hashes и hashes исходников; ссылки на `.build` означают
воспроизводимые промежуточные файлы, не постоянное хранилище результатов.

## Повторение

Из корня репозитория, Node и GCC (WSL на Windows), подготовленные test fixtures:

```powershell
node tools/esp8266_opus_profile/run_phase_regressions.cjs --silk-scratch --output .build/silk-phase.json
node tools/esp8266_opus_profile/run_phase_regressions.cjs --silk-scratch --sanitize --output .build/silk-phase-sanitize.json
node tools/esp8266_opus_profile/run_block_regressions.cjs --silk-scratch --output .build/silk-blocks.json
node tools/esp8266_opus_profile/run_block_regressions.cjs --silk-scratch --leased --output .build/silk-leases.json
node tools/esp8266_opus_profile/run_silk_scratch_faults.cjs --output .build/silk-faults.json
$env:YORADIO_OPUS_SILK_SCRATCH='1'
$env:YORADIO_OPUS_FAST_INT64='0'
node --test tests/esp8266-native-opus.test.js
Remove-Item Env:YORADIO_OPUS_SILK_SCRATCH
Remove-Item Env:YORADIO_OPUS_FAST_INT64
```

## Следующие обязательные проверки

- [ ] Дополнительные DRAM savings: пик SILK PLC4464 и CELT PLC4624. В trace
  видны SILK PLC temporaries и1024×int16 temporary в `_celt_autocorr`.
  Проверить отложенное выделение только при window/shift и отдельную ёмкость
  PCM transition, не меняя длительность PLC или округление.
- [ ] FEC/DTX, дополнительные malformed/OOM corpus и целевая сборка/ABI,
  stack/call depth, точная стоимость state/bookkeeping. Host mono не доказывает
  поддержку произвольного stereo output/других feature flags.
- [ ] Только diagnostic target switch, карта RAM и достаточный reserve.
  Не уменьшать реальный scratch до corpus peak без дополнительных проверок.
- [ ] OTA A/B: минимум10 сопоставимых попыток, decoder-only CPU, flash+output,
  LAN и реальные Opus станции; минимум20с непрерывного вывода, затем длительный
  прогон и смены режимов. Все startup/OOM/network errors сохраняются.

Нового измерения скорости на ESP8266 нет. Текущий результат улучшает
использование памяти, но **не доказывает непрерывное Opus-радио**.
