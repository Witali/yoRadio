# Opus PVQ: direct32-bit prefix table

2026-09-19. Независимый вариант над принятой eBands-final ASM-цепочкой.
Packed/long-guard варианты ранее отклонены; они не входят в production parent.

## Гипотеза и ограничения

При K-N>=8 используется тот же exponent-prefix0 upper bound, затем точный
линейный поиск. Только представление таблицы меняется:352 полных32-битных
значения/1408B flash вместо352 упакованных байтов. Дополнительного long guard
и K-=5 нет: не смешивать эти гипотезы с форматом таблицы.

В helper удалены8 инструкций: выделение фазы байта, деление индекса на4,
сохранение/восстановление SAR и динамическое извлечение байта. Осталось18
инструкций/46B. Таблица в4 раза больше, поэтому cache footprint может ухудшиться.
Заранее считать это ускорением нельзя.

Адреса site/helper/table прежние; literal теперь table-384 вместо table-96.
Первым1412B доказанно недостижимого alg_quant заменяем literal+table; область
имеет1788B. Все остальные ELF-байты/адреса/размеры секций неизменны.
RAM,48B frame и размер app не растут, C fallback production не изменён.
Начальный index>=U(N,N)>0, K>=N>2; таблица ограничивает ответ сверху,
MIN с исходным K сохраняет корректность для всех доступных U-строк, без cap192.

## Проверки и критерий

- [x]337686 linked U/CLZ-граничных случаев и256 дополнительных SAR-проверок,
  все GPR/SAR, decoder-dead storage, no interior entry;18 инструкций покрыты.
- [x]24 exact host PCM/state/ASan/UBSan случая, включая320/510кбит/с.
- [x] Восемь тестов: branch/index scale/table/literal/word width мутации;
  все352 значения совпадают с packed-таблицей, site инструкции прежние.
- [ ] Новый10A/10B/10A2: принятая raw-сборка против word-кандидата.
- [ ] Сохранить все попытки, оба high-bitrate speed gate, RAM/максимумы/ошибки.
- [ ] Вернуть ordinary radio через OTA и проверить HTTP/WS/playlist.

Свежий контроль сравнивает кандидата с принятой линейной базой, а не с новой
серией packed-сборки. Сопоставление с прежними packed-цифрами — историческое,
не отдельный одновременный A/B причин упаковки. Решение о принятии только по
двум свежим контролям. Цель75% raw CPU и20s live I2S/WebUI остаётся незавершённой.

App903216B. Candidate SHA256:
`dc859ad6b216fb8fa17a9f9ccda6595e0e122157f1849f6f627db10824fcafcb`.
Контроль идентичен принятой raw-сборке:
`4155b84f57c6a87280b0f6ee2f0218aabb3d942751eb13fc01425e0b46202b81`.

Instruction census: на192119961→111543..122784 инструкций,
24259→18203..20795 чтений; на12860732→62716..67904 инструкций,
11682→9933..11120 чтений. Включены literal и word-table reads. Остаточный
index в старых трассах неизвестен, поэтому это границы, не средние CPU-измерения.

Повтор:

```powershell
node tools/esp8266_opus_asm/pvq_prefix_word.cjs
node tools/esp8266_opus_asm/check_bands.cjs pvq-prefix-word
node tools/esp8266_opus_asm/analyze_pvq_prefix_word_instructions.cjs
node --test tests/esp8266-opus-pvq-prefix-word.test.js
node tools/esp8266_opus_asm/report_pvq_prefix_word.cjs
node --test tests/esp8266-opus-pvq-prefix-word-results.test.js
```
Артефакты: `firmware/development/esp8266-opus-pvq-prefix-word-{control,candidate}-v1/`.
