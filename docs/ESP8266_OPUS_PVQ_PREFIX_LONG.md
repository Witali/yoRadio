# Opus PVQ: prefix only for long searches

2026-09-19. Независимый эксперимент над принятой eBands-final ASM-цепочкой.
Отклонённый packed prefix0 не становится родителем основной прошивки.

## Гипотеза

Предыдущий prefix0 уменьшал количество чтений U, но тратил слишком много
инструкций на подготовку. При K-N>=8 сначала читаем U(N,K-4). Только если
index<U(N,K-4), то есть истинный ответ<=K-5, выполняем NSAU и packed lookup.
При равенстве и более коротком поиске работает прежний линейный алгоритм.
Дополнительный probe безопасен: K-N>=8 гарантирует K-4>=N.

На сохранённых трассах192 helper должен вызываться1306 вместо3159 раз,
на128459 вместо1405. Это не оценка CPU: на каждый широкий поиск добавляется
чтение U и ветвление; медленный fallback тоже нужно измерять.

## Реализация

- Три инструкции ADDI/L32I.N/BGEU занимают прежние8B padding в43B site.
- Helper,352B packed flash-таблица и адреса функций прежние.
- Общая RAM и48B frame не увеличиваются. Нет новых stores или byte loads.
- a3 мёртв на join; SAR сохраняется helper. C fallback production не меняется.
- Таблица/leaf используют доказанно недостижимый encoder-only код, не decoder.
- Отдельная C-модель проверяет математическую семантику; linked ASM проверяется
  собственным интерпретатором инструкций, а не только хостовой компиляцией.

## Проверки

- [x]337686 linked U-интервалов/CLZ-границ,256 SAR-phase проверок.
  Guard:313200 prefix,21156 fallback, в том числе1302 равенства порогу.
- [x]24 exact host PCM/state/ASan/UBSan сценария, включая320/510кбит/с.
- [x] Семь тестов: негативные offset/branch/table/SAR и decoder-dead storage.
- [ ] Новый10A/10B/10A2 на160MHz/QIO40: RAM-input, без output/profilers.
- [ ] Оба speed gate, максимумы, ошибки и все попытки без фильтрации.
- [ ] Возврат ordinary radio через OTA; проверка HTTP/WS/playlist.

Цель75% raw CPU и20s live I2S PDM/WebUI пока не подтверждена.

Сборка903216B, candidate SHA256:
`5068480b5e4e609f334676861fbfd2b7a215b930c9f01a2037113b6e6c818bab`.
Контроль побитно совпадает с принятой eBands-final raw-сборкой:
`4155b84f57c6a87280b0f6ee2f0218aabb3d942751eb13fc01425e0b46202b81`.

Instruction census по реальным трассам (index неизвестен, поэтому min..max,
не оценка циклов): на192119961→122889..128848 инструкций,
24259→20034..21414 всех чтений, включая guard/literal/packed-word.
На12860732→66438..68722 инструкций,11682→10726..11250 чтений.
1306/459 вызовов helper подтверждены linked эмуляцией. Вывод о CPU — только
по отдельной физической серии, не по этим счётчикам.

Повтор:
```powershell
node tools/esp8266_opus_asm/pvq_prefix_long.cjs
node tools/esp8266_opus_asm/check_bands.cjs pvq-prefix-long
node tools/esp8266_opus_asm/analyze_pvq_prefix_long_instructions.cjs
node --test tests/esp8266-opus-pvq-prefix-long.test.js
node tools/esp8266_opus_asm/report_pvq_prefix_long.cjs
node --test tests/esp8266-opus-pvq-prefix-long-results.test.js
```
Артефакты: `firmware/development/esp8266-opus-pvq-prefix-long-{control,candidate}-v1/`.
