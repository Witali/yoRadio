# Двусторонняя сверка Small TV, 2026-10-20

Просмотрены все 16 файлов доступной декомпиляции и все 26 прикладных C-файлов
реконструкции: от заводских точек входа к нашим функциям и обратно. Это исходный
код Ghidra с ошибками типов и неполным набором функций, а не C производителя.
Результат — карта переноса и список пробелов; полной эквивалентности программы
эта проверка не доказывает.

Точная карта: [correspondence.json](correspondence.json). В каждой заводской
строке указаны адрес, файл reference, конкретные `file#function` и оговорки.
Обратный список со строками, вызовами и хешами строится командой:

```powershell
python Small_TV/src/tools/audit_correspondence.py --output .build/correspondence/report.json
python Small_TV/src/tests/correspondence_test.py
```

Скрипт не обновляет карту автоматически. Добавление/удаление функции, опечатка
в цели или изменение проверенных исходников останавливает проверку. Хеши надо
обновлять после повторного просмотра изменённых мест. `passed` означает
целостность инвентаризации; `semantic_equivalence_proved=false` сохраняется.

## Объём

| Область | Результат |
|---|---|
| 176 экспортированных функций | 120 прикладных сопоставлены; 56 оставлены явными границами SDK/libc |
| 170 функций в 26 наших C-файлах | 93 связаны с заводскими строками; 77 учтены как поддержка, дополнения или оставшиеся API |
| TJpgd | 13 определений; отдельно сопоставлены 11 заводских точек из ассемблера `0x42011040..0x42012092` |
| cJSON | 116 определений библиотечной замены; не утверждается совпадение с заводской версией |
| Вызовы вне выбранных 176 тел | 198 прямых `FUN_ram_*`; в прикладном диапазоне — JPEG prepare/decomp, учтённые отдельно |
| Входы просмотра | 277 файлов: C/H, сборочные настройки, ассемблер, HTML, шрифты и данные часовых поясов |

Список определений не равен списку достижимых функций: условные ветки
препроцессора и удаляемые линкером API тоже присутствуют. Call graph не учитывает
все callbacks/indirect calls и не доказывает отсутствие других задач во всём
заводском образе. Подготовленная libjpeg ещё не подключена; её upstream-код
и инструменты хостовых проб не являются переносом заводских функций.

Новые `storage/jpeg_nor.c` и `storage/jpeg_guard.c` — подготовленные unlinked компоненты для расширения
JPEG, не перенос отдельной factory функции. Он проверяется собственным
[NOR contract](../tests/JPEG_NOR_STORAGE.md) и
[ownership guard](../tests/JPEG_OWNERSHIP_GUARD.md); при production integration их
нужно включить в source inventory и привязку сборочных входов. Это новые
REQUESTED_CHANGE helpers, не найденные пропущенные factory functions.

## Найденные пробелы

1. **HTTP-404, исправлено и проверено.** Заводская `0x4200d4be` читает
   `Host`: для адреса AP отдаёт корневую страницу, для другого имени отправляет
   абсолютный `Location: http://192.168.43.1/`. Наша `captive_redirect` всегда
   возвращала относительный `/`; два старых теста закрепляли наше поведение.
   Новый тест сначала воспроизвёл ошибку на C8FD. Исправление восстановило AP
   контракт и устранило factory substring bug с AP-похожим чужим именем.
   5608 host checks и 15 настоящих HTTP-запросов в factory AP/native AP/native
   STA прошли; 59 входов QEMU неизменны, все три собственные ВМ закрыты.
   Дисплей отсутствовал. [Доказательства](../../qemu/parity/captive-portal-validation-20261020.json).
   Это не полный прогон новой 54F4 и не аппаратная проверка.
2. **CITY-REINIT, исправлено и проверено.** `0x4200f3cc` внутри `/updateCity`
   очищает theme-init latch `0x3fcc39e9`. Новый `settings_update_city` публикует
   город/страну и команду под одним mutex даже для прежнего города; другие
   свежие настройки не заменяются старым HTTP snapshot. Identical city не
   требует повторной flash-записи. 5806 native checks, четыре QEMU темы/8 city
   commands и отдельный active-fade gate прошли. Заводской blank bug наблюдён;
   наша следующая фотография совпала с literal replay по всем 57600 pixels.
   [Подробности и допустимые отличия](../tests/CITY_REINIT.md).
   Это scoped приёмка app `3e030c1c…`, не full/24h/hardware acceptance.
3. **HTTP-LIFETIME, намеренная разница с пробелом тестирования.** Заводские AP
   peer events запускают/останавливают HTTP. У нас один сервер живёт с загрузки.
   Это предотвращает повторный запуск и исчезновение сервиса при отключении
   одного клиента, но многоклиентский AP и zero→one reconnect требуют теста.
   Привязка stop-функций к `web_start` обозначает замену жизненного цикла,
   а не наличие скрытого stop.
4. **GPIO-PULLS, аппаратно не проверено.** Заводская конфигурация RESET/DC
   включает pull-up, наша оставляет их выключенными. Кадры в QEMU не проверяют
   электрическое состояние при старте/reset. Без проверки не считать эту разницу
   ни доказанной поломкой, ни доказанной эквивалентностью.
5. **STALE-MAP, устаревшая навигация.** `symbol-map.json.native_module`,
   заголовки reference и старый `organize_decompilation.py` указывают файлы до
   разделения модулей. Пользоваться новой картой конкретных функций.
   `send_http_json_number` в действительности заменяет `{{STATE}}` в HTML;
   `draw_large_digit` рисует температурную единицу; `load_animation_frame_table`
   также выбирает и рисует кадр. Адреса надёжнее этих старых названий.

## Обратная проверка

- Отдельные timer/photo/GIF, UI, UTF-8, цвета, JSON/body, raw settings и
  mutex/atomic helpers реализуют разделение по назначению. Отношение функций
  один-к-одному здесь не требуется.
- Заводской JPEG output callback содержит запись пикселей во flash. Просмотренный
  `draw_jpeg` перед вызовом выключает этот режим. Активирующий caller не найден
  **в выбранном экспорте**; для всего образа это не доказано. Добавлять запись
  только из-за наличия этой ветки не следует.
- NETWORK/SLOW timer flags выставляются без потребителя в просмотренных телах.
  `browser_time` и `clickCount` также читаются/сохраняются без найденного рабочего
  эффекта. Нужны full-image references, прежде чем называть их окончательно
  мёртвым кодом или придумывать отсутствующую функцию.
- Наши `display_text` и `settings_generation` не имеют текущих production callers.
  Новый row RGB565 converter готовится для JPEG, но в C8FD удалён section GC.
- Native BMP снаружи доступен через 18 фиксированных weather slots и ограничен
  их 60×60/24-bit форматом. Поддержку произвольных BMP с отрицательной высотой
  или другими размерами, которую содержит factory helper, перенос не доказывает.

## Категории просмотра

| Категория | Сверенные данные/переходы и допустимые отличия |
|---|---|
| Старт/таймеры | preset 2025-09-19 17:04:40; 181 startup ticks, 11 ticks/second, description/photo/minute/weather; SPI перенесён из ISR, готовые часы стартуют раньше |
| Настройки/цвет | raw 0x1bc ABI, bounds/defaults, маски, five photo lengths, RGB565 truncation/replication; NVS migration/валидация и debounce являются изменениями |
| SPI/backlight | GPIO4/6/5/1/18, SPI2 mode3/40MHz, ST7789 commands/windows, 13bit/1kHz, integer duty/night boundaries; исправлены inclusive end, clipping и fade duty cache |
| Шрифты/графика | LSB-first padded fonts, symbols, transparent spacing, Bresenham/circles/float dial angles; исправлены stroke geometry/Unicode/границы полей |
| Темы | init/active paths, GIF cursor, ten description steps, six fade phases, setup/footer; исправлены Sunday/minute/calendar/clear/fade-reset, добавлена прокрутка |
| Фото/HTTP | 34 method/path, GET shapes, POST keys/ranges, пять слотов, multipart/start/chunk/finish; privacy, ordered retry, expiration и decode validation усилены |
| Wi-Fi/DNS | APSTA scan без STA netif, fixed AP/DHCP/DNS, four retry, lease/error latches; версии SDK и HTTP lifetime не приравниваются заводским |
| Погода | endpoint/10s timeout, Kelvin truncate-before-Fahrenheit, 16 half-open wind sectors, icons/labels; bounded JSON/URL/error/stale-cache/async исправления |
| SNTP | three servers, callback validity, country/region, setup; исправлены year validity/retry starvation/US-default DST через pinned IANA |

Машинные `classic/control/calendar/weather_render/text/jpeg*_oracle.py` дают
отдельные сравнения. Сеть, дисплей, browser, flash и долгий runtime остаются
независимыми проверками; их успешность не закрывает каждый путь этой карты.
Полный B50D прогон завершился 2026-10-20 10:56:30 UTC с exit 0; он не
сертифицирует C8FD или следующие правки. H10 на момент просмотра продолжался;
новую ВМ/второго debugger для него не запускали.
