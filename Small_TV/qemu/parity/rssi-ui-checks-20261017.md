# Исправление знака RSSI в списках Wi-Fi

В заводских HTML `setup` (flash `0x26edc`) и `settings` (`0x2963b`) подпись
сети использует `Math.abs(network.rssi)`. Поэтому измерение `-24` отображалось
как `24dBm`. Ошибка воспроизведена в настоящем браузере и в обработчиках
исходных страниц. API/драйвер возвращают signed RSSI; это отдельная ошибка
форматирования, не ошибка метаданных Wi-Fi DMA в QEMU.

`local_site/wifi_network.js` содержит общий `formatWifiNetworkLabel` с меткой
`FIXED_FACTORY`. Exporter встраивает его в обе страницы: работа без внешних
скриптов и существующие HTTP-маршруты сохраняются. Отрицательное число сохраняет
знак, числовой ноль выводится, отсутствие или нечисловое значение не получает
подпись dBm. SSID передаётся через `textContent`, значение `option.value`
и первый выбранный пункт setup не изменились. Страница фото не менялась.

`wifi_scan_test.mjs` исполняет реальные callbacks из сгенерированного HTML;
фикстуры задают только HTTP/DOM границы. Восемь случаев проверяют оба списка:
отрицательные измерения, ноль/отсутствие/нечисловое поле, буквальный SSID с HTML
символами и non-finite числа. Не относящиеся к сканированию GET настроек
удерживаются; optional legacy settings control присутствует только в фикстуре.
На прежних страницах все восемь случаев не проходят, на исправленных проходят.
Frontend gate требует один экземпляр актуального formatter в каждой странице
и фиксирует SHA модуля, обработчиков, exporter и pages manifest.

Ordinary firmware собрана: app `d78a7639…b3a37`, ELF `f5f39276…09a91`,
source `f8a3a6a8…d1b4f`; 1 169 888 байт, свободно 366 112. Среди 59 compiled
source/generated inputs изменился только `generated/web_pages.c`; C-программа
и алгоритмы firmware не менялись. Новый образ сохранён в development archive.
Повторный экспорт идемпотентен, изменены только setup/settings pages.

В реальной QEMU ВМ этого образа browser показал `yoRadio-QEMU (-24dBm)`,
`QEMU-2 (-28dBm)`, `QEMU-3 (-40dBm)`. Первый пункт выбран, реальные SSID values
сохранились, JS errors отсутствуют. Наблюдался настоящий AP flag; исходные и
исполняемые/media регионы флеша не изменились. ВМ и временная вкладка закрыты.
Сетевые labels не содержат пользовательских SSID, используются синтетические AP.

Host reduced profile прошёл: 3950 C assertions, platform 46, frontend (3 scripts,
4 JPEG, 156 crop, 23 resize, 11 transfer, 8 Wi-Fi cases), integrity 6,
timezone 9 и aggregation 14. Это проверка конкретного UI исправления; новый
общий parity pass, физический RF и H10/24h этим результатом не объявляются.

Обновлён и debug archive: app `5e468eb3…28b9f`, ELF `8fae6071…caeb2`, тот же
source `f8a3a6a8…d1b4f`. Его первый boot/reset smoke не дождался SNTP за восемь
секунд хоста: после reset было только 6,46 гостевой секунды, connected=true,
time_synced=false, нового NTP-ответа ещё не было. Этот run остаётся failed.
В SDK задан `LWIP_RAND() % 5000` перед первым запросом; фиксированное ожидание
хоста не является гарантией готовности при `icount`.

Отдельный QEMU helper commit `2a593f8d00` ждёт свежий обработанный ответ и actual
flags с пределами 15 guest / 60 host секунд; ошибка UTC по-прежнему меньше секунды.
19 unit cases и три реальных boot/reset flows прошли: ordinary 5,688 host /
3,913510 guest s; debug 8,250 / 6,415086; factory 9,031 / 7,767985. Существующие
29 consumer rejection controls прошли на обоих native вариантах. Firmware/SDK
startup delay не менялся, код QEMU устройства не пересобирался. Helper сохранён
в отдельной ветке; canonical main остаётся frozen для текущего общего прогона.
Полные scoped результаты: [rssi-ui-validation-20261017.json](rssi-ui-validation-20261017.json).

Сохранены неудачные попытки harness: в первой DOM-фикстуре отсутствовал getter
`textContent`, во второй не изолировались startup GET других settings controls.
Отдельный ранний artifact-test запуск не имел свежего native coverage report;
после выполнения native suite все шесть artifact tests прошли. Эти попытки
не считаются дефектами firmware и не заменены успешными результатами.

Проверка выполнялась в `.worktree/small-tv-rssi-label`. Текущий immutable full
на main продолжает проверять прежние EF66/81CF/8FCE/A74 с неизменными 92+92
входами. Ветку следует интегрировать после завершения и сохранения его результата.
Перед следующим full добавить `wifi_network.js` к source-freeze collector;
его SHA уже входит в новый frontend report.
