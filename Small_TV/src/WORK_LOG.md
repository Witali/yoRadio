# Рабочий журнал Small TV

Журнал сравнения заводской прошивки ESP32-C2 и восстановленного C-проекта.
Записи фиксируют факты, изменения и результаты с их областью проверки.
Актуальные рекомендации и следующий шаг: [WORKING_NOTES.md](WORKING_NOTES.md).
Новые записи добавляются по ходу работы; завершённые результаты не переписываются
как будто они проверялись на другой сборке. Не сохранять пароли, ключи, личные
фотографии и полные пользовательские журналы ВМ.

## 13 октября 2026

- Ранее завершённый этап: исправлен постоянный курсор GIF при смене анимации/темы.
  Сравнивались 261 набор полей классической темы, 1 545 переходов анимации и четыре
  проверки видимых битов символа у края панели. Заводское отбрасывание последнего
  `r` в `Thunderstorm` сохранено как намеренное отличие в 17 пикселей.
  Код и отчёты опубликованы в yoRadio `main` до `7993c426`.
- Метки исправлений описаны в `CORRECTION_MARKERS.md`: `FIXED_FACTORY`,
  `FIXED_RECONSTRUCTION`, `REQUESTED_CHANGE`. До текущей работы были отмечены
  17 функций. Полное соответствие всех путей и аппаратная работа не установлены.
- QEMU: ветка `codex/esp32c2-small-tv` объединена fast-forward в `main` и отправлена
  в `Witali/QEMU-ESP32` до `320055a3c0`. Рабочее дерево было чистым. Бинарник
  RISC-V сохранил SHA-256
  `18f183bcffe9603f7c36966cafacb6c76e7bd8c42bdaadbcd75f8e380ee5cf00`.
- Пользователь попросил продолжить сравнение, добавлять тесты для интересных
  случаев и допускает рефакторинг текущего участка. Попросил сохранять актуальный
  контекст и рабочий журнал; созданы эти два документа.
- Подсветка: инструкции `0x42008d62` подтвердили конфигурацию канала с duty ноль
  перед отдельными set/update; `0x42008c4c` подтвердили пропуск неизменившейся
  яркости. Предварительный машинный тест выполнил 143 245 сравнений и не прошёл:
  последовательность инициализации отличалась, повторный вызов нашего расписания
  давал лишние set/update при совпадающем итоговом duty. Локальное свидетельство:
  `.build/small-tv-parity/backlight-before.json`.
- Исправлена инициализация, общий setter хранит применённый уровень, регулятор
  пропускает повторную запись. Сохранено намеренное восстановление настроенной
  яркости после фото fade. Три функции получили метки и комментарии к причинам.
- Добавлены машинные сравнения повторных принудительных записей и ошибки создания
  LEDC timer/channel в C-тестах. Сборка сохранена; app 1 021 472 байта, SHA-256
  `3c60563a3d759d3973dd92b52d4a8f5fedd70ca00346214ed54ec8e61b7f2c78`,
  source SHA-256 `7a63db9d80d8bbfbccb8a3a92fde6e9c18f88afc3db02b2c31156bca3b26d4fe`.
  Набор `.build/small-tv-functional/backlight-traces-final` запущен; к моменту
  этой записи прошли native 3 021, 16 платформенных сценариев, JS и целостность.
  Полный итог будет добавлен отдельной записью после завершения.
- Машинный контроль новой сборки прошёл: 144 246 сравнений подсветки,
  79 296 timer ticks, 13 440 переходов слайд-шоу и 60 кадров с независимыми
  флагами простой темы. Классический oracle также прошёл прежние 261/1 545
  проверки. QEMU boot/reset/SNTP и первоначальная настройка AP→STA обеих
  прошивок прошли; погода и снимки экранов ещё выполняются.
- Исправление подсветки и новые тесты закоммичены как `794f7c5b`; отдельный
  коммит `aa552f21` сохраняет контекст и журнал.
- Итог `backlight-traces-final`: все включённые группы прошли. Native — 3 021;
  платформа — 16 сценариев / 216 899; JS — три скрипта, четыре JPEG-проверки,
  156 crop и 23 resize; целостность — шесть. Машинные проверки рендереров,
  timer/slideshow и подсветки прошли. QEMU проверил обе прошивки: boot/reset/
  SNTP, настоящий HTTP AP→STA, синтетическую погоду и пять сцен. Все тестовые
  границы и намеренные отличия сохранены в опубликованных отчётах.
- Сходство QEMU-снимков: setup 100%, classic 98,34%, simple 98,57%, photo 100%,
  dial 98,83%. Это наблюдения, а не критерий доказанной идентичности. Полное
  соответствие остаётся неустановленным; следующие кандидаты записаны в контексте.
- Архив текущей сборки и опубликованные отчёты согласованы по хешам. Размер
  app 1 021 472 байта, свободно 514 528 байт в app-разделе. Статический DIRAM
  по карте линковщика 80 346 байт; память работающей платы не измерялась.
  Отмечены 20 функций; исходный дамп сохранён без изменений.

- Поля классической темы: выполнены настоящие BMP-декодеры оригинала и C.
  Все 18 иконок совпали, но последовательная смена длинных/коротких/пустых
  подписей показала 91/182/730/106 лишних пикселей в прежнем приложении.
  Сохранено отрицательное свидетельство `weather-render-before.json`.
- Инструкции подтвердили очистку города только до y=23 при глифах y=10…33,
  отсутствие очистки краёв погодного заголовка и привязку текста к границе
  панели вместо поля. `/updateCity` сбрасывает validity, сохраняя старый указатель
  иконки. Области очищаются полностью; ошибка чтения BMP удаляет частичный значок.
- По уточнениям пользователя добавлены границы текстовых окон и независимая
  прокрутка города/описания/названия погоды туда и обратно, с паузами у краёв.
  Короткие строки неподвижны, новый текст/тема сбрасывает фазу, обновление статуса
  сохраняет её. Длинное описание удерживается до первого полного прохода.
- Добавлены host-проверки окон, несмежных пикселей, смены длинной строки короткой,
  ошибки декодера и реального цикла при загрузочной блокировке/смене темы.
  19 сценариев платформы прошли. Предварительный RV32 weather-тест прошёл
  225 случаев; final-run после добавления ready-флага запущен и ещё выполняется.
  Ассемблерный BMP-фрагмент ограничен `0x42010eca:0x42011040`; адреса SDK сверены.

- Итог `weather-fields-scroll-final`: все включённые группы прошли. Native —
  3 021; платформа — 19 сценариев / 741,941; frontend и шесть проверок
  целостности; машинные simple/dial/classic/control/backlight; weather — 225
  случаев (18 BMP, 10 обновлений, 191 кадр, два сброса, четыре ошибки чтения).
  Кадры прокрутки сравнивались с независимыми фазами и исходными bitmap, а
  вне полей пиксели оставались неизменными. Весь пиксельный буфер
  сравнивался с чистым кадром и объявленными исправлениями заводской модели.
- QEMU: обе прошивки прошли boot/reset/SNTP, настоящий HTTP AP→STA/persistence,
  синтетическую погоду и восемь равных LCD-областей. Пять сцен проверены;
  наблюдаемое сходство setup 100%, classic 98,62%, simple 99,22%, photo 100%,
  dial 99,12% не является критерием идентичности. ВМ закрыты. QEMU и старый
  отчёт совместимости CYD/C3 не изменялись и не выдаются за новый прогон.
- Код и сборка: коммит `8160ea49`; app 1,022,336 байт, SHA-256
  `d89542e62f823c0862c6e4d15b618ecc5e416ea5d87a9d21b7ae7d00cc591bd5`;
  source SHA-256 `cb3eced62ff074e180a8e61d557e169420be07781e7632b029e85a4f82e77f9c`.
  Свободно 513,664 байт в app-разделе, статический
  DIRAM 80,650. Комментарии у 141 функции, метки у 29.
  Опубликованные отчёты и архив проверены по хешам; физической прошивки не было.
  Полное соответствие всех путей остаётся неустановленным.

- Продолжение после `c151c0c3`: добавлены реальные HTTP-переходы длинного города,
  названия погоды и иконок в QEMU. Независимые font/BMP-пиксели сравниваются
  с городом/названием/иконкой и четырьмя соседними полосами; обе стороны, края,
  паузы, задержанный сервис, новое поколение погоды, возврат в тему и ошибки.
  Старое ASCII-декодирование наблюдаемого описания заменено Latin-1 для исходных
  двухбайтовых единиц; RGB565 переводится как в действующем QEMU surface.
- Полный заводской HTTP-поток может переинициализировать экран и убрать края
  коротких подписей. Это отличается от direct incremental-пути и записано
  отдельно. При отсутствии новой погоды подтверждено 382 пикселя старой иконки
  в одном заданном сценарии; неизвестная иконка в другом дала пустую область.
  Нельзя объявлять все сетевые пути одинаковыми по первому renderer oracle.
- Календарь: прежний C оставлял год/weekday при `tm_yday`-коллизии и края короткой
  даты простой темы. Подтверждение `calendar-before.json`: 48 сбоев из 96,
  максимум 411 лишних пикселей, отдельный shrink-пример — 99. Исходный app
  `d89542e62f823c0862c6e4d15b618ecc5e416ea5d87a9d21b7ae7d00cc591bd5`.
- Общая `calendar_changed` сравнивает полную дату; простая дата очищает всю
  полосу 240×24 при y=180. Исправленный машинный тест прошёл 96 случаев;
  два сценария выполняют реальный clock_task после epoch year jump без
  добавления минутного события. Отмечена новая функция; 142 entry comments,
  30 функций с метками. Код/сборка — `a3b35c8c`, новые network/gate — `0c961908`.
- Усиленный QEMU field-тест прошёл обе прошивки. Фаза проверяется после применения
  рендерером нового weather generation, а не только после окончания запроса.
  Полный `calendar-http-fields-final` запущен; окончательный итог будет добавлен
  после завершения. QEMU-репозиторий и физические платы не менялись.

- Итог `calendar-http-fields-final`: все включённые группы прошли. Native 3 021,
  платформа 21 / 741,961; JS и целостность; прежние machine/control/
  backlight/classic/weather и новые 96 calendar-сравнений. QEMU проверил обе
  прошивки: boot/reset/SNTP, HTTP AP→STA/persistence, погоду и новый field-поток,
  пять сцен. В native field-потоке 107 принятых кадров, все заявленные
  направления/паузы, поколение/фаза, тема, ошибки/повтор проверены.
- Сходство снимков setup 100%, classic 99,88%, simple 99,22%, photo 100%, dial
  99,24% — наблюдение, а не критерий идентичности. ВМ остановлены; QEMU main
  `320055a3c0` и историческая совместимость CYD/C3 не переписаны.
- Сборка и опубликованные отчёты сверены по хешам; записанные test inputs
  совпадают с закоммиченными файлами. App 1,022,416 байт, свободно
  513,584, DIRAM 80,650. App SHA-256
  `5e12da8c5b20740316f17da954b7ce8bc250e06b04e2f1e4f1095ccf484acc44`;
  source SHA-256 `fdaf71adcda5d52aa288989fa7872115c53c328c3219818272e36e4dc301246d`.
  Новые доказательства сохранены в `calendar-validation.json` и
  `field-http-validation.json`; исходный дамп и физические платы не изменены.

- JPEG: впервые исполнены оба настоящих RV32-декодера для всех 107 публичных
  изображений. Прежние 98 кадров и пять фотографий совпали; status JPEG имели
  3/33/3/3 отличающихся пикселя. Ассемблер `0x42011624..0x420116c6` подтвердил
  byte-clipped IDCT. `JD_FASTDECODE=0` восстановил цвета без переписывания
  third_party алгоритма. Оригинальные callback и bounded helper сохранены.
- При SDK-ошибке старый C оставлял частичный кадр; три MCU-stage примера имели
  1,411 / 57,598 / 57,551 пикселей вместо чистой известной области. Подготовка
  может завершиться до первого вывода и должна сохранять прежний кадр; раннее
  ошибочное ожидание очистки для read 13 исключено из отрицательной публикации.
  Новый harness наблюдает реальный `jd_decomp` entry. Заводской input callback
  `0x4200c33e` также исполнен: SDK-ошибка игнорируется, cursor и return растут.
- Исправлена очистка JPEG только после ошибки декомпрессии и только в области
  изображения. Discard-validation, ошибка подготовки и malloc экран не меняют.
  Проверяются ограниченные чтения, освобождение workspace, успешные повторы,
  truncated stream и соседние guard pixels при обычном/обрезанном размещении.
  Новый gate содержит 107 изображений, 35 ошибок/валидаций и семь размещений.
- Предварительный `jpeg-decoder-final` прошёл C/платформу/JS/целостность и machine
  renderer/control/classic/weather/calendar/JPEG. Перед публикацией обнаружен
  CRLF в изменённом assets.c; приведён к LF. App и ELF не изменились, но source
  SHA изменился. Незавершённый QEMU-прогон остановлен вместе с созданной ВМ;
  полного результата у предварительного набора нет. Новый `jpeg-decoder-verified`
  выполняется для окончательных байтов исходников и архивной сборки.
- Сборка: app 1,022,496 байт, SHA-256
  `997769839e8a016cb1c86845410297cea4097b47580b820fe0a77492267e2ded`;
  source `adfb43e8085022ccfeb7a13c8da0d3598430cb32289898416c29f23da8c72f09`.
  Документация JPEG и метки обновлены; QEMU-репозиторий и физические платы не
  менялись. Полное соответствие всех путей остаётся неустановленным.
- При полной сверке исходных байтов дополнительно найдены шесть ранее не изменённых
  production-файлов с CRLF при Git-правиле LF. Нормализованы без изменения содержимого
  и без новых смысловых Git-правок. App/ELF опять идентичны; окончательный source SHA
  `a754f79707a9f140c381c171101d5837ac9a7a62f9e6c8813c9a65491868434d`.
  Промежуточный `jpeg-decoder-verified` остановлен до QEMU; окончательный прогон
  `jpeg-idct-final` использует только байты в формате будущего коммита.
- Итог `jpeg-idct-final`: все включённые автоматические группы прошли. Native
  3,021; платформа 21 / 741,961; frontend/целостность и прежние machine/control/
  classic/weather/calendar. JPEG: 107 изображений, 6,163,200 сравнений RGB565
  пикселей, 35 ошибок/валидаций, семь размещений. Публичные ресурсы совпали с
  настоящим заводским декодером; исправления error/clip проверены отдельно.
- QEMU: boot/reset/SNTP, настоящий HTTP AP→STA/persistence, погода, field HTTP и
  пять сцен обеих прошивок прошли. Принято 106 native scroll frames. Сходство
  снимков setup 100%, classic 99,57%, simple 99,22%, photo 100%, dial 99,08% —
  наблюдение, а не критерий идентичности. QEMU main `320055a3c0` и исторический
  отчёт CYD/C3 не изменялись. Созданные ВМ закрыты; физической прошивки не было.
- Код/сборка — `04f6438e`. Архив app 1,022,496 байт, свободно 513,504; DIRAM
  80,650, 142 entry comments и 31 функция с метками. Сборка/тесты/публикация
  согласованы по хешам; все 46 production inputs сверены с Git-байтами.
  Полный отчёт, `jpeg-validation.json`, scoped negative `jpeg-before.json` и
  две картинки до исправления сохранены. SNTP/DST, произвольные JPEG и
  длительные/аппаратные/полные браузерные сценарии остаются дальнейшей работой.

- Время: выполнены настоящий заводской `tzset`/`localtime_r` и прежняя native
  libc для 109 ключей × 12 месячных выборок 2026. Буквальные результаты библиотек
  равны; 116 календарных отличий от независимого IANA TZif. Причина: неявные US
  DST-правила и устаревшие country offsets. Исходный дамп не менялся.
- Вынесены чистые country/timezone helpers. Закреплённые TZif IANA 2026e проверяются
  по SHA, преобразуются в дедуплицированные static C tables с полной историей и
  явными будущими recurrence. Не вводится выбор региона по городу; сохранены
  исходные keys/default GB. Worker revisits offset offline; UI использует
  текущий settings snapshot и не ждёт глобального TZ setter.
- Настоящий RV32 gate прошёл 36,404 сравнения всех 109 ключей с Python ZoneInfo:
  recorded/future edges, leap/century dates, fractional/negative DST, unknown key,
  пять invalid pointer/epoch inputs. Проверка обратного преобразования защищает
  от календарного переполнения libc. Named RV32 time_t ABI подтверждён objdump.
- Платформа: 24 случая прошли, включая offline DST-переходы и обе реальные темы
  при DST/стране/обратном epoch jump с прежними секундами. Раннее ожидание нового
  colon без timer event исправлено в тесте: исходная фаза должна сохраняться.
- Сборка сохранена: app 1,115,008, SHA
  `4778377602bd3c596aba9640202fd40fb9420fb7a10b3da29c949a936a72585c`;
  source `b1acb29646c238edda0018deac4e07042d5ff1187106bd4e9836fcdb4ffc875c`.
  Полный `timezone-final` выполняется. Порог 2025, SNTP callback и transport
  retry/fallback остаются отдельной работой; полного соответствия ещё нет.
- Дополнительное exploratory наблюдение настоящего `0x42010b70`: после 2025
  годовой epoch jump с теми же секундами оставляет cached year/weekday; callback
  `0x420109de` выставляет sync flag, но 2024 отвергается year gate. 21-й шаг
  обнуляет retry counter и сбрасывает initialized только при stopped SNTP.
  Синтетический `time-cache-observation.json` сохранён отдельно от passing gates.
- Итог `timezone-final`: все включённые группы прошли — native 3,021;
  платформа 24 / 742,006; JS/целостность; renderer/control/classic/weather/calendar/
  JPEG и 36,404 timezone comparisons. QEMU boot/reset/SNTP, настоящий AP→STA HTTP,
  persistence, weather/field и пять сцен обеих прошивок прошли; 110 native scroll
  frames. Сходство setup 100%, classic 98,66%, simple 98,52%, photo 100%, dial
  98,94% — наблюдение, не критерий идентичности. Снимки/отчёты связаны с новой
  app/source, старые negative JPEG и board reports не переписаны.
- Повторная проверка публикации подтвердила app/source/test hashes; app 1,115,008,
  свободно 420,992, DIRAM 80,650, 148 entry comments и 34 функции с метками.
  Полное соответствие остаётся неустановленным. QEMU-репозиторий и физические платы
  не изменены; созданные ВМ закрыты. SNTP-validity/transport остаются следующим шагом.
- Код/сборка — `1e9fac91`. Перед коммитом проверены точные Git-байты всех 48
  production source files и 106 TZif; full suite содержит 44 test inputs.
  Отчёты/контекст фиксируются отдельным коммитом. Посторонние файлы не включаются.

### 2026-10-14 — воспроизводимое обновление открытых часовых поясов

- Пользователь предложил открытый источник правды. Официальный IANA
  `https://data.iana.org/time-zones/tzdb/version` возвращает 2026e; сайт IANA
  указывает выпуск 2026-09-29. Источник правил — IANA, wheel PSF tzdata 2026.5
  используется только как готовый TZif транспорт для Windows.
- Добавлен `tools/update_timezones.py`: discovery не меняет pins; загрузка
  проверяет SHA-256, обе declared версии, все выбранные файлы и будущие правила.
  Другой выпуск требует явных IANA/package/SHA аргументов вместе. Есть локальный
  `--wheel` режим; build не получает сетевой зависимости. `--source` генератора
  проверяет кандидата без изменения committed snapshot. README содержит команды.
- Выполнены настоящий `--check-latest` и HTTPS-download в ignored
  `.build/small-tv-parity/timezone-update/downloaded`. Дополнительный тест
  настоящего закреплённого wheel воспроизвёл 106 файлов, 109 country keys и
  точный generated C header. Девять офлайн-тестов прошли: corruption, pins,
  declared версии, missing/duplicate, unsupported DST, сохранность output и
  published metadata mismatch/yanking и неверный HTTPS origin. В full runner/publisher/verifier добавлен
  обязательный `timezone_sources` с хешами инструментов, manifest и raw файлов.
  Отдельное доказательство сохранено в `tests/timezone-update-validation.json`;
  downloaded header SHA совпал с текущим build: `11e9f9f0...0947d01`.
- Временный системный TEMP оказался недоступен sandbox для вложенных файлов;
  регрессии перенесены в writable ignored `.build/.../temporary` и повторно
  прошли. Никаких TZif правил, country default или готового firmware этим
  изменением не заменено. Новый полный runtime gate пока не выполнялся: текущие
  SNTP/QEMU изменения продолжаются отдельно, прежняя публикация — baseline.
- Для продолжения SNTP: `0x42017ea0` подтверждён как restart wrapper (внутри
  enabled query `0x4201bec6`, stop/init callback `0x42017d34`). QEMU experiment
  `time-network-fourth` подтвердил stock preset после sync 2024, но затем не
  завершился; это failed наблюдение, а не passing gate. Исправления ещё не
  закоммичены и не объявлены готовыми. Физические платы не прошивались.

### 2026-10-14 — SNTP notification и настоящие UDP-переходы

- Обновлён callback/валидность: atomic sync latch выставляет настоящий SDK
  notification; будущий год/инициализация клиента не заменяют подтверждение.
  Сохранён latch при disconnect/deinit; обе темы учитывают его изменение при
  прежнем epoch. Подтверждённый 2024 теперь принимается. Time worker сохраняет
  действующий retry/fallback вместо заводского преждевременного restart.
- Экспортированы три полных helper excerpts: restart `0x42017ea0`, stop/init
  callback `0x42017d34`, enabled query `0x4201bec6`. Manifest сохраняет прежние
  записи; исторический time-cache report получил явную correction annotation.
  Новый machine gate прошёл пять literal и восемь native случаев; теперь
  проверяется точное количество SDK restart calls. Платформа — 26 сценариев,
  включая callback при неизменном времени в simple/classic.
- Failed `time-network-fifth` уточнил: SDK принял 2025, cache изменился, но LCD
  ждёт minute event. `sixth` затем показал 165 отличающихся RGB bytes после
  укороченной даты. Независимая retained-glyph модель совпала полностью;
  native должен оставаться чистым. `seventh` выявил ошибочное предположение
  теста о возврате server index на 0: SDK stop/init оставляет прежний индекс.
  Маски отказа теперь действительно принуждают выбор требуемого сервера.
- `eighth` прошёл 2024, retry/reconfigure, 2026, backward leap day, post-2038 и
  preset/no-sync после reset, но RTC offset сравнивался с QEMU lifetime time.
  Это ошибочный oracle: SDK использует guest SYSTIMER, RTC/HRT offset и system
  correction. Восстановлена формула из pinned SDK/ELF; 26 MHz -> ticks*5/52.
- Полный `time-network-ninth` прошёл обе прошивки, включая новую реальную
  синхронизацию после reset. Последняя UTC разница native около -23 ms. QMP
  только управляет внешним NTP fixture и кратко останавливает наблюдение; guest
  RAM/код/время не подменяются. Все owned VM закрыты после проверок.
- QEMU RISC-V SHA `bf98de89...33d44c`, Xtensa `f6a5f293...3abc35`: CYD boot/MMIO,
  C3 OLED legacy/modular, C2/C3 shared SPI/I2C, ESP32 two-host SPI/SD isolation
  и пять network unit cases прошли. QEMU source/docs — `b90e2131b8`, main push
  проверен. Новые controls opt-in; defaults прежние.
- Финальная LF-сборка сохранена: app 1,115,104 байт, свободно 420,896;
  source SHA `9402fd83c7cef65222685deff3fbe6a98ad9cb197413da3d6af2b90536ace019`.
  Обязательные `machine_time_state`/`qemu.time_http` добавлены в runner/publisher/
  verifier. Запущен полный `sntp-final-20261014`; пока это running, а не новая
  опубликованная проверка. Исходный dump не менялся, физических прошивок не было.
- Пока full suite исполняется, read-only RV32 probe рассмотрел следующий
  non-ASCII участок. Шесть синтетических byte cases: ASCII и A1E6/A848 совпали;
  UTF-8 «Тест»/«北京» совпали как 4/3 Celsius glyphs (248/186 lit pixels),
  неизвестная пара попадает в Celsius fallback `0x4200aae0`. Native унаследовал
  эту ошибку. Single trailing E6: stock Celsius 62 pixels, native blank.
  `text-encoding-observation.json` хранит текущее app/ELF identity и scope;
  production/test inputs не менялись. Исправление Unicode/byte truncation —
  следующий отдельный участок после публикации SNTP; наблюдение не является
  passing coverage gate.
- Итог `sntp-final-20261014`: все включённые automatic gates прошли — native
  3,021; platform 26 / 742,437; JS/integrity; timezone source 9; прежние RV32
  renderer/control/classic/weather/calendar/JPEG и 36,404 timezone; time-state
  5 factory + 8 native. Настоящий QEMU AP→STA/persistence/weather/field/SNTP и
  пять сцен прошли. Шесть native UTC observations, max absolute около 33 ms.
  Scene equality setup/simple/photo 100%, classic 98,69%, dial 98,83% — это
  наблюдение, не критерий полной идентичности. Полное соответствие не доказано.
- Публикация/повторная проверка архива прошла: app SHA `2a60eefc...35f672c`,
  source `9402fd83...ace019`, ELF `ee74d566...93a394`; 47 test inputs. App
  1,115,104, свободно 420,896; DIRAM 80,650, entry comments 151, markers 36.
  Сохранены реальные native helper/worker instructions и bounded factory SDK
  helpers; fences и guard проверены непосредственно по C ELF. Старые negative
  JPEG/timezone/board records оставлены с историческими identities. Свежая
  QEMU board compatibility опубликована отдельно в `ntp-board-validation.json`.
- Код/сборка/инструменты — `6b7a52d3`. Перед коммитом точные staged Git bytes
  сверены с passing report: 47 test inputs, 48 production inputs и 106 TZif.
  Результаты и рабочий контекст сохраняются следующим отдельным коммитом;
  посторонние `.karadio-*.patch`, `tmp/` и attachments не включаются.

### 2026-10-14 — UTF-8 / glyph widths / safe prefix, в работе

- Подтверждённая Celsius-on-high-byte ошибка заменяется общим scalar decoder.
  Из bundled Spleen подготовлены 452 non-ASCII glyphs в размерах 16/24/32;
  исходные ASCII и две unit bitmaps сохранены. Неизвестные символы используют
  '?'; malformed bytes не поглощают последующий ASCII. Width, bounds и scrolling
  разделяют token decode; Unicode ℃/℉ и °C/°F соответствуют старым unit codes.
- Weather JSON сохраняет source budget 15 bytes с полной границей UTF-8;
  added helper проверяет scalar range, overlong/surrogate/invalid/truncated bytes,
  output guards и in-place prefix. Native 3,069 и platform 26 / 1,145,647 прошли.
  Реальный RV32 text gate: 1,644 source glyph comparisons, 195 full retained
  frames/windows/transparent/bounded cases, 219 scalar decode, 240 prefix cases
  прошли против независимых raw BDF/factory source tables.
- Первая production сборка сохранялась (app 1,175,584; free 360,416); после
  URL comment/ASCII classification обновлена до app SHA `2acdf34f...80f826`,
  ELF `570d62ad...a6d2c5`. Весь текущий runtime suite ещё не подтверждён.
- `text-http-second` получил настоящий factory Load access fault при raw UTF-8
  city URL: MEPC 4203e8f0 / RA 4201098c / address c. Original init result NULL
  не проверяется перед perform. Native уже кодирует URL/проверяет handle;
  Locale-dependent isalnum заменён явными URI ASCII ranges, причина помечена.
  Fault теперь проверяется отдельным disposable factory-сеансом; Unicode JSON/
  cache/renderer original проверяется с ASCII location. Source dump не изменён.
- `text-http-third` остановился на старой HTTP-helper signature. Reflog доказал,
  что параллельный cleanup сохранил helper/test в `5520fbb787`, вернул main на
  b90e2131b8 и готовит собственное слияние. Не перезаписывались чужие ветки.
  Exact helper blob/sha взят из commit в `.build/.../utf8-http-helper`; overlay
  явно записывается в runtime provenance и имеет отдельный Python module name.
  `text-http-fourth` запущен; metadata частичного запуска не превращается в pass.

- `text-http-fourth` предварительно прошёл обе версии и отдельный factory fault;
  после заморозки inputs выполнен `utf8-final-20261014`. Guard отклонил его QEMU
  после изменения HTTP helper при параллельном merge. Failed report не исправлялся.
  Создан собственный pinned 5520fbb787 worktree, весь QEMU повторён без overlay.
  `utf8-verified-20261014` объединяет фактические passing results с unchanged
  test/app/source bytes; сохраняет rerun provenance. Все включённые
  автоматические группы прошли, включая 1,644 glyph comparisons,
  195 render, 219 decode,
  240 prefix, пять real Unicode HTTP cases + complete scroll.
- Полный AP→STA/persistence/weather/fields/actual UDP SNTP + пять сцен также
  прошёл в полном повторе. Fresh QEMU executable/profile/canonical helper hashes
  сохранились; используется canonical client pinned 5520fbb787 без overlay.
  Оригинальный NULL-client fault записан отдельно; native panic не допускается.
- Publisher и повторный artifact verifier прошли: app 1,175,584,
  free 360,416, DIRAM 80,650;
  155 entry comments,
  44 correction markers.
  App `2acdf34f68edccdfa9fd4753a22909598391ee23a6bc2e40e91737061a80f826`, source `72ad106b1276f430f7f26b5e1a7fc6660f0174919f009d3591a70d660b64e1b5`,
  ELF `570d62ad0547ae49a4bbe42b7deee586d319553f5565599d35635eaf5da6d2c5`. Позитивные отчёты обновлены на текущую сборку;
  исторические text/JPEG/timezone/legacy-board negative records не переименованы.
- Сохранены восемь compiled native text/weather helpers (Unicode/fetch inlined
  в factory_glyph/weather_task) и четыре time-sync helpers. Factory temperature
  helper 4200aae0..4200abee добавлен bounded excerpt без private DROM. Все owned
  VM/listeners закрыты; физических прошивок/reset/OTA не выполнялось.

- Код/сборка/новые gates сохранены в `5f608522`. Проверены точные staged bytes:
  49 test files, 50 production inputs, 106 TZif, source font, LFS app и native ELF.

### 2026-10-14 — синхронизация профиля с новыми сервисами QEMU, в работе

- Новый запрос пользователя: синхронизировать Small TV profile под изменения
  QEMU. Прочитаны новые configs/boards/AGENTS.md и README. Main 5e136b6eab
  поддерживает network.urls/ntp_hosts/station+AP SSIDs и generic ServicePort;
  defaults в самом emulator больше не выбирают provider/application.
- Прежний Windows canonical binary BF98.. не пересобран. Создан собственный
  worktree .worktree/small-tv-service-profile на codex/small-tv-service-profile,
  pinned 5e136b6eab. Скопированы уже закреплённые dtc/keycodemapdb dependencies;
  Windows RISC-V SDL/SLIRP успешно собран. Runtime/network/legacy проверки новой
  сборки ещё не выполнены; готовится отдельный repo-owned Small TV profile.

- Добавлены repo-owned profile + launcher, все standalone/full/comparator paths
  переведены на него, weather/fields/text fixtures используют generic service_port.
  Compiler/profile source hashes включены в runner/publisher/verifier; LF rules
  сохраняют проверяемые bytes. Actual profile checks 4, helper tests 11, packet
  regressions 6 и modular SPI/I2C/SD/CS/CYD MMIO прошли на c970591d.. executable.
- Legacy CYD/C3 source images заморожены из прежних checked copies; hashes
  unchanged. CYD boot/no panic + separate MMIO passed, C3 OLED legacy/modular
  boots passed, OLED nonempty/hashes match. Raw images/logs остаются ignored.
- Первый full `service-profile-final-20261014` прошёл host/RV/profile/boot/AP→STA,
  но qemu.weather ещё проверял deprecated weather-services=True. Assertion
  обновлён на actual service-hosts vs profile endpoints; failed run сохранён.
- Offline wrapper 5/30 sec загрузился/reset без panic, но QEMU test helper
  требовал changing animation на static setup page. Own QEMU commit 1c7e4c0512
  требует animation только при clock; real offline boot/reset passed. Emulated
  hardware/firmware не менялись. Новый full service-profile-second запущен;
  прежние опубликованные results не объявлены новым passing checkpoint.

- `service-profile-second` завершился false по ещё одному old log label:
  actual HTTP/cache scenarios прошли, DNS trace теперь service=http. Исправлено
  ожидание, target weather preflight прошёл original+native. Failed reports
  сохранены; новый `service-profile-third` не использует их как passing evidence.
- Третий attempt прошёл все host/RV/HTTP/time/UTF-8 stages, но scene seeder ещё
  принимал старые четыре args. Новый fifth argument — station SSID string;
  comparator мигрирован. Только profile gate и все пять scene pairs повторены,
  точный suite validator проверил PNG CRC/dimensions/pixels/panic/NTP. Остальные
  stages сохраняют unchanged test/app/profile/emulator/helper bytes. Failed run
  не переименован; combined verified report хранит rerun provenance. Packet 6, helper 11,
  modular SPI/I2C/SD/CS, CYD boot/MMIO и C3 legacy/modular прошли отдельно.
- QEMU source helper 1c7e4c merged FF и pushed main. Kernel compiled 5e136b6eab,
  RISC-V SHA `c970591d626c7500cccd00121ba52667998ebeb091388acd2af46c22cc10bea6` установлен canonical bin; прежний BF98..
  сохранён с marker. Штатный own launcher offline и clock boot/reset/SNTP прошёл на main.
- Published profile/compiler/launcher fingerprints и compatibility summary;
  publisher/artifact verifier отклоняют mixed/stale profile inputs. Production
  app/source/ELF прежние 2acdf34f / 72ad106b / 570d62ad, физической прошивки нет.
  Full functional correspondence ещё не объявляется: остаются regional settings,
  transport/scene/JPEG/concurrency/browser/physical/soak пути из backlog.

- Profile/launcher/test migration сохранена отдельным commit `b57996b6`.
  Перед коммитом проверены exact staged bytes: 50 test inputs, 50 production
  inputs, 106 TZif и font/LFS app/native ELF; profile/board/comparer/launcher
  fingerprints проверяются отдельно тем же staged-byte checker.

### 2026-10-16 — региональные ключи и миграция NVS, проверка в работе

- После нового чтения main `612a23d3` Small TV не менялась со времени checkpoint
  `f4c48ab1`; посторонние C3/AAC/patch-файлы сохранены. QEMU main `1c7e4c0512`
  не меняется, физические платы не прошиваются.
- В оригинале `0x4200f380..0x4200f39e` подтверждены memset(20) и копирование
  всего country suffix в `0x3fcb7c63`. В нашей прежней сборке настоящий QEMU
  с raw `AU-W` показывал 17:15 вместо независимого Perth 14:15: импорт обрезал
  ключ до `AU`. Отрицательный `regional-before-20261016` сохранён с прежними
  app `2acdf34f` и ELF `570d62ad`; он не переименовывается в успешный результат.
- Общий country capacity теперь 20; обновлены raw codec, HTTP city pair,
  time/weather task buffers и weather cache. NVS v2 = 364 bytes, исторический
  v1 = 344. Проверены все поля миграции, старый padding mode, явный v2 mode 0,
  raw precedence и отклонение неверных blobs. Host: 3,884 checks; платформа:
  прежние 26 и два новых региональных сценария. Метки FIXED_RECONSTRUCTION,
  исходный raw ABI и GB fallback сохранены. Машинные тесты читают ABI из DWARF.
- В актуальной таблице 15 региональных ключей, включая CA-* и PT-AZ, а не только
  примеры US-*/AU-W. Host проводит все 109 ключей через API/codec/persistence.
  Native QEMU preflight прошёл все 15, максимум 64 city + 19 region + UTF-8
  comma bytes, cache/invalid inputs и холодный старт. Настоящий SDK NVS generator
  создал v1 fixture: QEMU подтвердил все поля миграции и повторную загрузку из
  одного NVS v2 при стёртом raw-секторе.
- Два factory preflight сохранили буквальную задержку simple redraw: внутренний
  календарь уже Dec 31, экран ещё Jan 1. Один скачок NTP не заменяет периодический
  minute event. Для региональных factory pixels используется реальный dial→simple
  HTTP transition; native проверяется без него. AU-C/AU-E отдельно сохраняют
  установленную ошибку implicit US DST (январь без южного летнего времени).
  Native всегда обязан совпадать с IANA; эти различия не маскируются.
- Новая сборка сохранена: app `446a5c3c`, ELF `bde762ed`; исходные инструкции и
  exact native-settings/time/text snippets архивированы. Full `regional-final-20261016`
  уже прошёл host/JS/integrity/timezone-source и все RV32 groups; QEMU продолжается.
  Опубликованные старые отчёты пока не выданы за новый passing checkpoint.


- Full `regional-final-20261016` прошёл без объединения разных попыток: все
  host/RV/QEMU groups и five scene pairs. App/source/test/profile/helper hashes
  проверены publisher/verifier. Новые `regional_http` и actual NVS v1/v2 gates
  включены в обязательную публикацию. Новые positive reports относятся только
  к app 446a5c3c; historical board/negative evidence не переименовано.
- Code/build/tests сохранены в commit `f27401af`. Exact staged-byte check
  проверил test inputs, production inputs, TZif, font, LFS app и ELF. Published
  metrics: app 1,176,096, free 359,904,
  DIRAM 80,706, comments 157,
  markers 50. Owned VMs закрыты.
- Regional settings item закрыт; следующие задачи: actual calendar/DST matrix,
  exact fixed-state scene differences, adversarial JPEG, concurrency/long-run,
  browser/physical acceptance. all_functionality_verified остаётся false.

### 2026-10-16 — завершённые кадры и порядок применения яркости, проверка в работе

- Вместо процента сходства несинхронных снимков введено наблюдение реального
  входа/возврата renderer через аппаратные GDB точки. Гостевые инструкции,
  регистры и RAM не меняются. Read-only аргументы/состояние передаются отдельному
  исполнению того же RV32-кода; JPEG/BMP действительно декодируются.
- Первая проверка показала 6,034 разных пикселя native classic. Реальное чтение
  LEDC duty/timer и GPIO18 показало причину: стартовые duty 819/8192 и яркость
  901/1000. С учётом наблюдаемой аппаратной яркости геометрия/цвета совпали
  полностью, но требуемая яркость 1000 не была применена к первому кадру.
- Сопоставлены factory 0x42008e08/0x42008e32..34 и текущий compiled clock_task.
  Перед первым classic/simple render теперь применяется выбранная яркость.
  Порядок dial/photo сохранён; добавлен тест SPI-пикселей при входе в обе
  цифровые темы. Новый case прошёл 35,048 checks; все 29 platform cases прошли.
- Сборка app 9e4f856a / source 6ab9c80f / ELF 7e34a29b сохранена в firmware.
  Архивированы точные factory init/dial инструкции и native scene snippets.
  Подготовлены 24 завершённых QEMU кадра, включая real-weather HTTP и поздние
  кадры после 40 секунд, и 40 нормализованных полных сцен с реальными медиа.
- Пробные classic/dial и weather кадры совпали. Один weather preflight отклонён
  по изменившимся во время запуска test bytes; он не объявляется passing gate.
  Full scene-final-20261016 выполняется из одного неизменяемого набора тестов.
  На этой записи новый итоговый успешный результат ещё не заявлен.

- Full `scene-final-20261016` завершился успешно одним запуском: все host/RV32/
  QEMU groups и пять ordinary scenes. Native 3,884; platform 29 / 1,180,724.
  Все 24 завершённых кадра дали 0 отличающихся пикселей. В 33 canonical classic
  cases factory/native full frames идентичны; семь dial cases дают 0 относительно
  объявленной коррекции stroke geometry, literal differences сохранены.
- Publisher, evidence collector и artifact verifier подтвердили app 9e4f856a,
  source 6ab9c80f, ELF 7e34a29b. Опубликованы complete-scene results и отдельный
  negative first-frame brightness с прежним app 446a5c3c. Historical negatives
  и board compatibility не выданы за результаты новой сборки.
- Commit `caad5d3c` сохраняет исправление/тесты/сборку/ассемблер. Exact staged
  byte check проверил 54 test inputs, 50 production inputs, 106 TZif, font,
  LFS app и ELF. App 1,176,112, free 359,888, DIRAM 80,706, comments 157,
  marked functions 50. QEMU main 1c7e4c0512 чист, executable прежний c970591d;
  собственных работающих scene VMs не осталось, физического flashing не было.
- Следующий приоритет — natural midnight/Sunday/year/leap/DST transitions через
  реальные UDP packets и все time-bearing themes/formats; затем adversarial JPEG,
  concurrency/long-run, browser и physical acceptance. Полное соответствие
  не заявлено; all_functionality_verified остаётся false.

### 2026-10-16 — natural calendar transport matrix, работа над тестом

- Проверены Git/main 09ff077b и незатронутые посторонние untracked patches.
  Приложение/ELF/QEMU остаются прежними; физических действий нет.
- Добавляется calendar_qemu.py: реальные HTTP settings/NTP packets, before/after
  natural boundary без повторной синхронизации, read-only hardware breakpoints,
  independent IANA и literal Newlib, full-frame factory instruction reference.
  14 входных границ проверены по pinned TZif; используются все шесть сочетаний
  date/hour modes в каждой теме. Это scoped matrix, не exhaustiveness claim.
- Первый native simple/Sunday preflight остановился на ошибочном пути к NTP log
  внутри case folder. Путь к VM log теперь передаётся явно. Второй preflight
  остановился на HTTP timeout до отрисовки; причина ещё исследуется. Failed runs
  сохранены и не объявляются проверкой прошивки. Добавлены HTTP/QEMU diagnostics.
- После пропуска неподходящего entry harness теперь доходит до реального
  return, затем ищет следующий entry: повторная установка breakpoint на том же
  PC могла бы остановить ту же инструкцию вместо продвижения гостя.

- Factory ADV handler 0x4200e9ea не сбрасывает SNTP init; city handler сбрасывает
  его в 0x4200f3d4 и sync в 0x4200f3dc. Архивирован полный advanced handler.
  Первый повтор смешал запоздалый city reply с ADV; после ожидания initialized/
  actual-sync наблюдение подтвердило отсутствие нового reply за 3.01 guest s.
  Для следующего epoch factory использует реальный city re-entry. Native
  перенастраивает клиент по изменившемуся NTP host самостоятельно.
- Все три factory Sunday themes прошли literal full-frame replay. Native
  reference сначала выявил различие представлений int/double текущей температуры
  в самом harness; проверено truncation-to-int в production weather_parser,
  canonical observer теперь требует exact integral value. App не менялась.
- `calendar-transport-latency-20261016` прошёл native classic/simple/dial Sunday,
  обе полные картинки в каждой теме совпали с factory corrected reference.
  Один POST: 5.75 guest / 8.14 host seconds, остальные короче. Новый календарный
  HTTP helper измеряет обе длительности и имеет guest bound 6 s / host guard
  20 s. Причина задержки остаётся H09/network вопросом, не объявлена решённой.
- Full calendar-final-20261016 запущен (shell 97647), producer/test inputs
  заморожены, app/source/ELF по-прежнему 9e4f856a / 6ab9c80f / 7e34a29b.
  Host 3,884, platform 29, JS/integrity/timezone-source уже прошли; RV32/QEMU
  продолжаются. Старые опубликованные результаты пока не заменены.
- При read-only анализе найден следующий алгоритмический участок: native
  persistence debounce = 1 s, factory = 50 main-loop steps (100 ms delay плюс
  body/blocking weather), save branch только в active-clock path. Машинные
  адреса 0x420090e2..f8/0x4200916a и loop delay 0x42008fd2 проверены в bounded
  export .build/small-tv-save-delay-assembly. Требует отдельного coalescing test;
  связь с HTTP latency не установлена. Текущий application image не меняется.

- Завершённый ассемблерный аудит ADV сохранён отдельным commit `e4195bb9` и
  отправлен в main; origin/main подтверждён как e4195bb9aa86636c5b64b8bc5bcebc491b5b45a0.
  Календарный test module и новые обязательные gates остаются незакоммиченными
  до полного результата. Full process 97647 подтверждён live; прошли также
  boot/reset/SNTP и первоначальная AP→STA/persistence настройка обеих прошивок.

- Полный calendar-final завершился exit 1: factory 42/42 перехода прошли;
  reconstructed classic прошёл Sunday/year/month/leap-start/leap-end. Затем
  HTTP /SetTimeModeValue вернул 200 за 6.127902 guest / 8.718 host s, нарушив
  новый предел 6 guest s. Новый общий passing report не публикуется, оставшиеся
  native transitions и subsequent completed-scenes не объявляются выполненными.
  Сессия 97647 терминальная, повторять poll или запускать её заново не нужно.
- В собственной отдельной ветке offline-clock восстановлены active dispatch и
  retained station IP, новые 33 platform cases проходят; реальные RV32 network
  traces показывают negative старого app и pass кандидата 072135ee. Полные
  оригинальные/compiled instructions и scoped candidate reports сохранены в
  worktree. Full QEMU/natural RF loss ещё требуются; main app не заменён.
- Уточнён persistence probe: factory save на 51-м eligible pass при initial 50.
  Модель 100-ms pass даёт single 5.1 s / native 1 s; burst один / три save.
  Factory tick rate не измерялся; inactive/weather phases — explicit model
  inputs, не выполнение целого FreeRTOS main. Связь с HTTP задержкой не доказана.

- Offline candidate сохранён отдельным commit `6f10bc46` и pushed в
  `origin/codex/small-tv-offline-clock`, remote SHA сверён. Перед commit:
  50 production inputs, actual network adapters/test bytes, 24 platform/stub
  files и LFS app/ELF identity совпали с tested bytes. 33 / 1,181,610 platform
  checks. Общий main app и его published evidence остаются 9e4f856a.
- Независимый real-TCP probe с пассивным filter-dump дал 60 POST и три задержки
  около 6 guest s. В них первый SYN не дал SYN-ACK, повтор SYN через 5.82–5.94 s,
  после actual HTTP arrival headers вернулись за 42–49 ms. Это свидетельство
  транспортной фазы, не доказательство конкретного RX/SDK дефекта. Две ранние
  попытки probe завершились на имени backend и неинициализированных harness
  globals; они сохранены как failed diagnostics. Третья VM закрыта.
- Failed calendar и обезличенная TCP-сводка сохраняются отдельно. Полный passing
  отчёт не заменён; six-guest-second gate не ослаблен. Для дальнейшей диагностики
  отдельный QEMU worktree `.worktree/small-tv-wifi-link` от main 1c7e4c0512
  собирает opt-in RX logging; canonical QEMU source/executable не меняются.

- Пользователь уточнил: ненужные задержки следует удалять. Это сохраняется как
  правило дальнейшей работы; deliberate fixes документировать и проверять их
  влияние на события/таймеры/отзывчивость. TCP SYN retransmission уже локализован,
  но его конкретная причина ещё не доказана.
- Новый native-only calendar matrix запущен, shell 32961. Шестисекундный предел
  сохранён; превышения теперь агрегируются в отрицательном flow check в конце,
  позволяя собрать остальные календарные случаи. Этот запуск не полный suite.
- Factory delay напрямую измерен read-only GDB/QMP: десять vTaskDelay(10)
  составили 98.5–109.5 ms. Это проверка реального SDK delay, отдельно от времени
  body/render/weather. Источник дампа и canonical QEMU SHA прежние.
- Первый diagnostic QEMU B05E с общим guest_errors log слишком шумный: display
  startup не достиг 25 guest s за wall timeout. Его VM закрыта, это failed
  diagnostic attempt. Диагностика заменена dedicated RX trace event, не меняющим
  доставку пакетов. Повторный build завершился, installer сначала получил sharing
  violation от ещё закрывавшейся собственной VM; после её выхода устанавливается
  уже собранный бинарник. Canonical QEMU не затрагивается.

- Dedicated RX trace QEMU 8cc11913 показал no-descriptor losses в момент
  медленных соединений. Новая C2 queue не выбрасывает head frame до появления
  DMA буфера и возобновляется по RX_BASE_DESC write без polling/retry pause.
  Commit 6f3fa56a48 сохраняет trace; 9d4da15732 — queue fix и C2 packet test.
  Оба pushed в codex/small-tv-wifi-link, remote 9d4da15732 проверен.
- Candidate QEMU e8122fe2: новый C2 starvation/FIFO/limit/no-duplicate packet
  test прошёл; вместе с шестью прежними — 7 passed. На canonical c970591d новый
  тест воспроизводит потерю двух ответов, прежние шесть проходят. Первая версия
  нового harness использовала C3 MMIO base для C2: ошибочный negative сохранён,
  итоговый before/after использует реальный C2 0x60047000 из модели платы.
- 120 real HTTP POST после queue fix: все 200, max .165376 guest s. Ранний
  trace-only вариант на том же app давал 5.74/5.76 s. Actual app не менялась.
  Модульные SPI/I2C/SD/GPIO tests и unchanged CYD/C3 OLED legacy+modular boot
  прошли, собственные диагностические ВМ закрыты. Scoped candidate evidence
  сохранён отдельно; canonical binary и root native-only calendar не изменены.
- Native-only calendar shell 32961 жив, тестовые байты заморожены до результата.
  На этой записи прошли classic/simple все 14, dial Sunday/year. Это ещё не
  общий passing suite. Далее: закончить этот attempt, принять проверенный QEMU,
  прогнать полный набор; offline branch и программные паузы — отдельные участки.
- Для программных пауз начат read-only аудит: startup timer держит заставку
  181 × 100 ms даже при готовой сети; clock_task также ждёт weather_request_active,
  хотя worker имеет независимый cache mutex. Эти кандидаты на удаление лишнего
  ожидания требуют отдельных тестов и меток REQUESTED_CHANGE. ST7789 reset/sleep,
  debounce, периодический task yield и restart grace не удаляются без основания.

- Native-only calendar attempt 32961 завершился: все 42 transitions и 84
  complete frames совпали с corrected factory reference; все native calendars
  совпали с IANA. Flow failed только по settings_http_latency_bounded=false,
  max 6.195069 guest s. Scoped observation сохранён; different attempts не
  склеиваются в passing full suite. Canonical emulator ещё c970591d.
- По прямому уточнению о программных паузах в offline branch удалён weather
  wait в clock_task: worker асинхронный, published cache защищён mutex, поэтому
  UI/fade может работать до ответа. Новый host negative ловит прежнюю заморозку;
  после изменения все 37 platform cases прошли. REQUESTED_CHANGE добавлен в
  entry comment. Startup и аппаратные задержки пока отдельно от этого изменения.
- Новая branch production сборка a2b6129b / source 246397dd / ELF 00ef2763,
  1,176,144 bytes / free 359,856, сохранена в firmware/development. Before/after
  QEMU probes удерживают настоящий внешний HTTP-ответ, не меняя guest state.
  Первый harness ошибся в RUNNING mask, обе ранние попытки failed до проверки
  UI; второй читает enum из actual DWARF и ждёт natural minute boundary.

- Corrected prototype QEMU observation подтвердил программное ожидание:
  old app 9e4f856a допустил следующий кадр только после завершения/тайм-аута
  weather worker (6.535 guest s наблюдаемого ожидания); a2b6129b отрисовал новую
  минуту через .740 guest s при реально выполняющемся HTTP и удержанном ответе.
  Обе VM закрыты, app/ELF inputs не менялись. Постоянный portable regression
  создан в branch tests/weather_wait_qemu.py с DWARF enum и source/helper/code
  fingerprints; отдельный before/after repeat shell 14536 / 87620 в работе.

- Постоянный weather-wait regression завершён: a2b6129b проходит, даёт кадр
  за .932 guest s при RUNNING=1 до внешнего ответа. Прежний 9e4f856a показывает
  expected fail: 6.735 guest s до кадра, state=0 после weather timeout. All input
  hashes/code checks сохранены, ВМ закрыты. Code/build/test/scoped reports
  сохранены в branch commit e547d98a. Это намеренное удаление программного
  ожидания, не заявление полного паритета. Следующее — merge/integration
  branch, full gate для нового теста и обновление старого frozen-scroll expectation.
- Root native-only календарный результат сохранён/отправлен commit 92a38121,
  main remote SHA подтверждён. Во всех 42/84 native calendar cases совпали IANA
  и corrected frame reference; общий attempt остался failed по старому HTTP
  timing. QEMU candidate 9d4da15732/E812 остаётся отдельной веткой, canonical
  main/bin пока 1c7e4c0512/c970591d. Текущих собственных ВМ нет.

### 2026-10-16 — проверено удаление лишнего startup-ожидания

- По уточнению пользователя о software delays продолжен аудит factory/C.
  Factory timer 0x42008278..0x42008296 держал startup 181 тик даже после
  готовности сети. В branch b10ccf4c startup заканчивается по Wi-Fi/SNTP;
  фото не требует SNTP. Оставлены timeout, task yield и аппаратные паузы.
- Все 43 platform cases / 1,182,204 checks проходят, включая четыре темы,
  отсутствие IP/SNTP, старый timeout, GIF и яркость первого кадра. Negative
  classic/simple/dial воспроизводили прежнее ожидание; photo harness mutex
  был исправлен как ошибка теста, не выдан за production defect.
- Portable startup_qemu.py через hardware breakpoints измерил старый 9e4f856a:
  13.353327 guest s от actual SNTP callback до первого renderer (expected fail).
  Новый 743fa69f: .040202 s до renderer, .101856 до полного кадра (pass).
  Гостевые инструкции, RAM, PC и время не менялись; observer/helper hashes
  одинаковые, app/ELF inputs сохранены. Реальный delayed-weather regression
  повторно pass при RUNNING=1 и .971445 guest s до следующего кадра.
- Новая branch сборка app 1,176,224 / source 2583ac4c / ELF 7bda9d7d сохранена
  в firmware и отправлена в codex/small-tv-offline-clock. RV32 network тоже
  pass: четыре event traces, 16 factory dispatch states. Точные инструкции,
  отчёты и software-delay inventory находятся в этой ветке; main app не заменён.
- QEMU graceful AP control завершён и отправлен commit 962cda7a6f: восемь
  packet tests, 11 helper tests, modular devices, CYD/C3 boots и actual HTTP
  setup обеих app прошли. На real native a2b6129b подтверждены SDK disconnect,
  ход simple clock offline, station IP и reconnect; три полных кадра имеют
  0 отличий от corrected reference. Executable fde38d53 пока отдельный кандидат.
- QEMU canonical/main не заменялся, физические платы не затрагивались,
  собственные ВМ закрыты. Далее integration веток/обязательных gates, обновление
  frozen-scroll expectation и полный стабильный набор. Общий parity не заявлен.

### Дополнительный журнал из ветки исправлений

### 2026-10-16 — автономный ход часов при потере Wi-Fi, отдельный кандидат

- Создан собственный worktree `.worktree/small-tv-offline-clock`, ветка
  `codex/small-tv-offline-clock`, от e4195bb9. Основной календарный прогон не
  менялся. SDK используется через явный DependencyRoot, без junction/copy.
- Заводской main 0x42008e56 продолжает theme dispatch и update_local_time при
  offline/retry, ограничивая только weather retry. В C прежний else-if online
  замораживал экран. После восстановления active-phase dispatch платформенные
  тесты показывают ход минут/DST в classic/simple/dial и завершение фото-fade.
- Второй сбой — station IP заменялся AP адресом. 0x4200c602 сохраняет GOT_IP
  event snapshot при отключении. Добавлен atomic IPv4 cache. Тест с новым lease
  .21 при позднем SDK snapshot .15 проверяет выбор event payload, а не netif.
- До исправления реальные platform frames расходились на 713/815 пикселей;
  после исправления все 33 platform scenarios прошли. Новый network_oracle
  исполняет event/getter RV32 и 16 original active-loop states: старый app
  9e4f856a даёт ожидаемый fail, кандидат 072135ee проходит четыре event traces
  и весь dispatch. Подменяются только явно перечисленные SDK/output boundaries.
- Кандидат app 1,176,176 bytes, free 359,824; source e10dd9f6 / ELF eec972f2.
  BIN и manifest сохранены в firmware этой ветки. Exact original/main и native
  clock_task/wifi_event/network_address instructions архивированы. Результаты
  before/candidate разделены, исходный factory dump не менялся.
- machine_network добавлен в полный набор и следующий publisher/verifier.
  QEMU/full suite кандидата ещё не проходили; прежние опубликованные общие
  отчёты сохраняют старую app identity. Нужны natural virtual Wi-Fi loss/recovery,
  новый полный прогон и затем включение исправления в main. Физических действий нет.

### 2026-10-16 — удалено программное ожидание погоды

- Пользователь уточнил, что лишние программные delay/vTaskDelay и ожидания
  следует убирать. Из clock_task удалено ожидание weather_request_active:
  weather worker уже асинхронный, snapshot публикуется под отдельным mutex.
  REQUESTED_CHANGE объясняет намеренное отличие от блокирующего factory main.
- Новый platform negative воспроизводит устаревший classic frame. После
  изменения все 37 cases / 1,182,490 checks проходят: три clock themes и
  photo-fade продолжаются при queued weather. Обычный task yield и upload guard
  сохраняются. Неисследованные startup/display/restart задержки не менялись.
- App a2b6129b / source 246397dd / ELF 00ef2763 собран и сохранён в firmware:
  1,176,144 bytes, free 359,856. Exact coordinator/weather instructions
  архивированы. Старые offline app 072135ee reports сохранены отдельно.
- Portable weather_wait_qemu.py выполнен before/after. Внешний HTTP удерживается
  во время natural minute boundary. Старый app допускает кадр после weather
  timeout, наблюдаемый остаток 6.735 guest s / state=0. Candidate обновляет его
  через .932 guest s при RUNNING=1, до ответа сервера; input/code hashes прежние.
  Ранние prototypes ошибались в RUNNING bit; итоговый test читает actual DWARF
  enum. Собственные ВМ закрыты, физического flashing нет.
- Scoped code/test/build/evidence готовятся отдельным коммитом. Whole-suite
  candidate ещё не проходил; новый weather wait test надо включить в общий gate,
  а field_qemu frozen-scroll ожидание заменить проверкой отзывчивости. Natural
  station disconnect/reconnect, дальнейший software-delay audit и полный набор
  остаются обязательной последующей работой.

### 2026-10-16 — startup по готовности вместо лишнего программного ожидания

- Пользователь уточнил software delays. Исследованы factory timer
  0x42008278..0x42008296 и actual compiled clock_task. Подтверждённое ожидание
  181 тика сохранялось даже при готовом clock. REQUESTED_CHANGE завершает его
  по station lease + confirmed SNTP; photo theme не нуждается в SNTP.
- Startup latch и его event сбрасываются под ISR critical section без сброса
  остальных timer counters. При отсутствии условий остаётся старый тайм-аут.
  Yield 100 ms, дисплейные init delays и фоновые timers не удалялись.
- Новые platform cases classic/simple/dial воспроизвели старый startup. Ошибка
  mutex раннего photo prototype исправлена в самом test; этот сбой не выдан за
  дефект production. После исправления все 43 cases / 1,182,204 checks прошли,
  включая четыре темы, ожидание IP/SNTP и отсутствие возврата startup при потере
  Wi-Fi. Старый timeout и требование яркости первого кадра проверены отдельно.
- Portable startup_qemu.py наблюдает actual callback/renderer hardware GDB
  breakpoints: прежний app 9e4f856a — ожидаемый fail, 13.353327 guest s; новый
  743fa69f — pass, .040202 до renderer / .101856 до полного кадра. Guest RAM,
  инструкции, PC и время не меняются, test/helper hashes одинаковы до/после.
- Сборка app 1,176,224 / free 359,776, source 2583ac4c / ELF 7bda9d7d сохранена
  в firmware. Отдельно сохранены точные compiled instructions и отчёты.
  Actual RV32 network (4 traces / 16 dispatch states) прошёл; real external
  weather-wait regression тоже pass: RUNNING=1, frame через .971445 guest s.
- QEMU graceful AP control завершён отдельным коммитом 962cda7a6f и отправлен
  в codex/small-tv-wifi-link. Восемь packet tests, 11 helper tests, modular
  SPI/I2C/SD, CYD/C3 boots и actual HTTP setup/AP->STA/persistence обеих app
  прошли на executable fde38d53. Native a2b6129b также продолжает simple clock
  во время live SDK disconnect, сохраняет station IP и восстанавливает HTTP;
  три полных кадра имеют 0 отличий от declared corrected reference.
- Canonical QEMU не заменялся, физической платы не касались, собственные ВМ
  закрыты. Whole-suite нового app ещё не проходил: observers следует включить
  в полный gate и обновить старое frozen-scroll ожидание. Общие старые positive
  reports не переименовываются в результаты кандидата; parity остаётся неполной.

### 2026-10-16 — объединение и обязательная проверка отзывчивости

- Merge 12172b4d включил offline/weather/startup branch в main с сохранением
  календарной матрицы и обоих рабочих журналов. Посторонние untracked файлы
  не затронуты. QEMU main обновлён до 962cda7a6f и отправлен; canonical executable
  теперь fde38d53, установлен штатным SkipBuild installer из проверенной сборки.
  Старый c970591d/marker сохранён отдельно, Xtensa binary не изменён.
- startup_qemu/weather_wait_qemu включены в обязательный suite. Publisher и
  artifact verifier проверяют app/ELF/QEMU/helper identities и реальные пределы
  задержки. Последний общий positive report пока остаётся историческим 9e4f856a.
- WeatherFixture получил общий явный HTTP hold/release. Field test требует
  продолжения exact-pixel scroll до ответа и сохранения фазы после публикации
  тех же данных. Обе реальные прошивки прошли preflight; native 110 кадров,
  held offsets 8,8,10,10,12,12,12,14 при request state 1; resumed 18, generation 5.
  Никакие guest RAM/PC/clock значения не подменяются; тестовые ВМ закрыты.
- Исправлен устаревший production comment о погодной блокировке. Root build
  app 0d8b7585 / source 9d9c5c8c / ELF 97adeb91, 1,176,224 bytes, сохранён в
  firmware. Exact compiled code девяти функций сохранён отдельным manifest.
  Branch 743fa69f reports остаются привязанными к своей сборке.
- Следующий шаг — полный запуск из одного замороженного набора input bytes,
  включая все natural calendar transitions. Этот preflight не объявляет
  full parity; physical/browser/soak и прочие неохваченные пути остаются открыты.

### 2026-10-16 — полный интегрированный прогон и новые JPEG-наблюдения

- Commit ad5b8c5d сохранён и отправлен в main вместе с merge 12172b4d.
  Запущен один полный `responsiveness-full-20261016`, shell 22926. Before input
  manifest фиксирует тесты/app/ELF/QEMU. Test/source/helper bytes заморожены.
- На записи native 3,884, все 43 platform cases, JS, integrity, TZ archive
  checks, basic machine/control, classic (261 field/media + 1,545 animation)
  и weather (225) прошли. Handle жив, идёт machine_calendar. Это ещё не итог
  всего запуска; настоящий конечный результат следует получить тем же handle.
- Не меняя frozen tree, generated synthetic JPEG probe исполнил actual factory
  и native RV32 decoders на восьми новых inputs: RGB 444/422/420, 444 и 420 с
  DRI/restart markers, grayscale 240x240, odd RGB 123x117 и grayscale 23x29.
  Во всех случаях native result=0, оба decoder started, all 57,600 panel pixels
  совпали (0 differences), включая неперерисованные guards. Результат относится
  к ELF 97adeb91, не заменяет image-upload policy или полный fuzz.
- Fixtures детерминированные, без личных данных; Pillow 12.3.0, quality 83,
  optimize=True, увеличенный локальный encoder buffer MAXBLOCK 1MiB. Первый
  encoder attempt завершился ошибкой рабочего буфера; это не firmware defect.
  Повторный отдельный probe завершён. Имена/хеши/размеры и options сохранены
  в `.build/small-tv-parity/jpeg-extra-fixtures/manifest.json`, report рядом.
- После terminal full run следует включить новые JPEG cases в постоянный
  regression; текущий mandatory JPEG gate по-прежнему покрывает прежние 107
  public assets/ошибки/placements. Publication/full parity пока не заявлены.

### 2026-10-16 — отдельная JPEG-ветка: заголовки и следующий Huffman bug

- Root full run 22926 жив; все RV32 gates прошли, QEMU boot/reset, новые software
  waits, initial AP->STA setup, weather, field scroll, SNTP и UTF-8 прошли обе app.
  Региональный этап ещё выполняется; main frozen source/test/helper bytes не менялись.
- Создан sparse worktree .worktree/small-tv-jpeg-inputs, branch от main 41b972aa.
  Закреплены 8 deterministic RGB/grayscale/subsampling/restart/odd-size fixtures
  с encoder manifest и 12 header/entropy/restart mutations. Literal factory и
  прежний C принимают DQT ID 4 как 0, SOF precision 12 и extra component payload.
- Три ошибки исправлены с FIXED_FACTORY в create_qt_tbl/jd_prepare. Native actual
  ELF c2c6ae3b / app a33788db / source 731815d5 сохранён в firmware ветки:
  1,176,256 bytes / free 359,744. Все 8/12 новых cases и прежние 107/35/7 RV32
  JPEG checks проходят; host production C 3,884 тоже pass. IDCT/color/output прежние.
- Exact factory/native assembly, before/candidate/public/native reports и новый
  обязательный branch gate сохранены commit 9a59cb07 и отправлены. First staging
  check поймал текстовое правило Small_TV/src/** для JPEG: добавлен scoped -text
  override, повторный staged byte check подтвердил все source/image/fixture hashes.
  Ни corrupted binary, ни временные файлы не попали в коммит. Candidate full suite
  ещё не выполнялся; main run продолжает свой app 0d8b7585, без изменения байтов.
- Отдельный минимальный synthetic 363-byte grayscale доказал ещё один bug:
  невозможное дерево с тремя 1-bit DC codes принимается factory/native draw и
  native validation (все возвращают 0). Предыдущая random-entropy mutation падала
  позже и не доказывала проверку таблицы. Следующий приоритет — постоянный case и
  исправление Huffman builder в JPEG worktree. Before header candidate BIN/ELF
  сохранён в .build/small-tv-parity/jpeg-header-before-huffman/.

### 2026-10-16 — Huffman validation и реальные photo HTTP/cold-boot проверки

- Пока root full run 22926 остаётся живым, JPEG branch отправлена отдельными
  focused commits 49a50986 и 28bfa638. uint32 prefix-space проверка исправляет
  принятие 17 impossible trees (DC1, AC1…16) в factory и прежнем native коде.
  Четыре valid trees с 1/16-bit codes сохраняют pixels. Все 41 JPEG inputs,
  107 public assets/35 errors/7 placements и host3,884 проходят.
  Production candidate app131ce792/sourcef411bf0e/ELF9184b08b архивирован в ветке;
  root замороженные source/test/image/helper bytes не менялись.
- Permanent photo_qemu провёл actual SDK HTTP multipart/flash без app-server mock:
  21 checks на четырёх процессах, valid gray/RGB38488, ten chunks, busy/order/
  early finish/exact retry/conflicting retry, metadata и точное скачивание.
  Тот же observer на old0d8b7585 принимает malformed363, candidate даёт400/absent;
  это единственный отрицательный check старой сборки.
- Без debounce-пауз проверены cold boot сразу после successful finish и после
  start незавершённой замены: опубликованные bytes/длина переживают первый,
  частичный slot скрыт после второго и следующая загрузка доступна. Candidate
  response→stop 0/.143098 guest s, max request .298990 guest s. Все UART-фазы
  проверены, owned flash меняется, source archive неизменён, ВМ закрыты.
  settings_photo_size() уже вызывает settings_flush() синхронно: гипотеза о
  background-only сохранении опровергнута, production change не нужен.
- Общий минимальный JPEG producer выделен в helper, 41-case gate повторён.
  Новые gates обязательны в branch suite/publisher/verifier; root run их ещё
  не содержит. Последний root progress: factory42 natural calendar transitions
  pass, native classic/simple pass, dial продолжается; затем complete scenes.
  Terminal full result пока отсутствует. После него сверить frozen inputs,
  объединить JPEG branch, собрать main и проверить актуальный полный набор.

### 2026-10-16 — полный responsiveness run завершён

- Исходный session22926 завершился exit0. Все 17 automatic groups pass на
  app0d8b7585/source9d9c5c8c/ELF97adeb91/QEMUfde38d53. Сверены все 58 initial
  test hashes, BIN/ELF/QEMU и helpers; unchanged. Calendar: 42 transitions /
  84 frames для каждой app. Complete scenes: 24 frames с 0 differing pixels,
  40 normalized cases; five unsynchronized diagnostic scene pairs тоже прошли.
- Current startup wait .061207 guest s, held-weather next frame .879886 guest s.
  Сохранён task yield, hardware init, upload guard и debounce; hardware/браузер/
  long soak не объявлены выполненными. Полная equivalence всех путей не доказана.
- Strict publisher поймал изменение ISO date strings при PowerShell JSON
  aggregation. QEMU raw JSON и все реальные наблюдения корректны. Проверены все
  17 raw group files: единственные различия — 207 строк представления тех же
  timezone-aware instants. Производный aggregate сохраняет исходные строки;
  первоначальные файлы не переписаны. Аудит и hashes сохранены отдельно.
  После этого штатные publisher/verifier прошли, обновлены 23 positive artifacts
  из одного запуска; исторические negatives/board reports не переименованы.
- Далее исправить date aggregation, объединить завершённую JPEG branch,
  пересобрать root и прогнать новый полный gate с JPEG inputs/photo HTTP.

### 2026-10-16 — сохранение ISO date strings в тестовом агрегате

- Общий Read-SmallTvTestResult использует ConvertFrom-Json -DateKind String.
  Invoke-TestGroup и control/manifest читаются через него; требуется PowerShell7.5+.
  Новая обязательная report_aggregation группа проверяет 14 условий на реальном
  helper и serializer: midnight CN, повторяющийся час US DST, NP fractional
  offset и UTC subsecond timestamp остаются точными строками.
- Reduced run json-date-aggregation-20261016 завершён exit0: все шесть локальных
  групп pass, native3,884 и platform43/1,182,204. Независимый Python сравнил
  вложенный aggregation result с исходным child JSON — байтовые значения дат
  сохранились. Scoped source hashes/result сохранены в report-aggregation-checks.
  Production app0d8b7585 не менялся; полный machine/QEMU здесь не повторялся.
  Checkpoint73687652 сохраняет точный прежний 17-group набор и даты его запуска.

### 2026-10-16 — JPEG integration в main и новая архивная сборка

- Merge3aede06f включил branch28bfa638 после terminal root run. Конфликты
  обязательных списков разрешены с сохранением report_aggregation и
  machine_jpeg_inputs, всего19 groups; документы/оба журнала сохранены.
  Новые photo21-check gate и Huffman/header tests не приписываются старому run.
- Root build успешен, production sourcef411bf0e совпадает с JPEG branch;
  root appad7a9009/ELF6d7b586f,1,176,272 bytes/free359,728 архивирован в firmware.
  Actual decoder/coordinator/network code девяти функций сохранён отдельным
  native-jpeg-integrated assembly/manifest. Старые branch/root evidence не
  перепривязаны. Следом один новый полный run jpeg-integrated-full-20261016,
  с initial input pins; полный positive report пока остаётся для0d8b7585.

- Сборка/ASM сохранены commit9a7e341c и отправлены в main вместе с merge и
  report fix. Freeze_test_inputs записал63 test files, BIN/ELF/QEMU до запуска.
  Единственный live handle92411: report_aggregation14, native3,884,
  platform43/1,182,204, frontend/integrity/TZ sources pass; идёт machine.
  Нового полного результата пока нет, тестовые/source/helper bytes не менять.

### 2026-10-16 — полный photo pipeline и исправление idle brightness в отдельной ветке

- Не меняя frozen root92411, создан .worktree/small-tv-photo-frames от6a02d8c0.
  Actual84 photo/fade frames обеих app и9 canonical raw scenes проходят наAD7A;
  настоящий JPEG/glyph/LEDC code, SDK/LCD boundaries only. Затем guards требуют
  panic/immutable/code checks и10 negative mutations; selected photo обязан
  входить в real decoder и читать flash. Commits57ef94ae/31fce447.
- Найден подтверждённый C defect: между фото brightness POST50/GET50 оставлял
  duty819; factory handlers выставляют39f2, main0913c сразу пишет4095. Новый
  production C-case тоже падает на oldcode. Исправлено условие schedule update
  на idle илиfinished, active fade не меняется; FIXED_RECONSTRUCTION задокументирован.
- Build candidateE3902939/sourceB9787790/ELFD73C9146,1,176,288 bytes/free359,712
  сохранён в firmware ветки. Все44 platform cases/1,182,252 checks pass; новый
  case покрывает day/night/calendar/full brightness и silent idle без SPI/LEDC.
  Same-observer HTTP обеих app pass, native проверен4095 через.141715 guest s
  после ответа, full photo/footer0pixel differences, новой fade нет.
- Candidate84 frames/9 canonical scenes и10 guard checks повторены:pass,
  source/image/helper bytes unchanged, все owned VMs закрыты. Factory/native
  actual assembly сохранён; exact staged input+image+ELF proof прошёл.
  Commit2a949010de70 и оба родителя отправлены в codex/small-tv-photo-frames.
- Root92411 жив, в natural calendar после успешных regional/NVS stages.
  Все63 test input bytes, rootAD7A BIN/ELF/QEMU сохранены. Сначала дождаться и
  опубликовать именно его19-group result; затем merge photo branch/build/full.
  Физических действий, правок QEMU или посторонних файлов не было.

### 2026-10-16 — полные photo/fade frames в отдельной ветке

- Создан sparse worktree .worktree/small-tv-photo-frames / branch от main6a02d8c0.
  Root run92411 не затронут; сохранены exact ELF/BIN/factory ELF/ROM copies.
- Новый PhotoMachine сохраняет настоящий JPEG/фото selector/footer/LEDC code,
  SDK flash/mutex/allocation и LCD transport остаются boundaries. Девять canonical
  frames all5/skip/wrap/none и три IP дают0 pixel differences.
- QEMU baseline6 owned VMs:84 full frames,28/10/4 на вариант для all/masked/none.
  Все57,600 pixels, exact13-bit duty, phase continuity, photo order и immutable
  executable/media проверены. Factory literal replay совпал; native endpoint
  fade restore сравнивается с отдельно заявленным brightness correction.
  Phase0/1 до первого полного JPEG не считаются проверкой startup; все6 phases
  покрываются последующими кадрами. Source/observer/helper fingerprints unchanged.
- Early prototype пытался ждать SNTP перед первым фото и ошибочно требовалslot0
  после пропуска; corrected observer проверяет первый JPEG до синхронизации.
  Night profile действительно использовал duty819 до SNTP и4095 после него.
  Это test assumption fix, не production bug. Baseline архивирован отдельно,
  branch suite/publisher/verifier требуют новый gate; root92411 остаётся своим run.
- Следующий real HTTP случай — изменение яркости в idle между снимками:
  factory handlers0x4200d5ac/0x4200d66a выставляют flag3fcc39f2, main4200913c
  применяет его; C пока обновляет schedule только на finished. Проверить before.

### 2026-10-16 — защита полноты photo evidence

- Shared contract теперь требует явных panic/immutable/state-write checks и
  совпадающих normalized executable identities. Десять отрицательных mutations
  (missing variant/profile/phase/panic, wrong order/duty/window, changed code,
  missing normalized case/mixed ELF) отклонены на committed baseline57ef94ae.
- Photo replay требует настоящий decoder entry и flash reads для выбранного
  фото; все9 raw scenes повторно прошли на старом ad7a9009 ELF. Scoped hashes
  и результаты сохранены в photo-frame-guard-validation.json. Это postprocessor/
  isolated replay проверки, новый full QEMU run здесь не заявлен. Baseline84
  сохраняет прежние observer hashes и не перепривязан к новому helper.

### 2026-10-16 — подтверждённая задержка photo-idle brightness

- Новый C-case упал на old coordinator: duty4095 не применён после изменения
  day_level между fade. Реальный QEMU HTTP повторил: factory POST50→duty4095,
  old native POST50/GET50→прежний819. Source main09128..09140 применяет flag39f2
  после handlersd5ac/d66a; в C schedule стоял только на action.finished.
- Clock_task исправлен с FIXED_RECONSTRUCTION: idle или finished применяют
  cached schedule; active fade сохраняется. Build app e3902939/sourceb9787790/
  ELFd73c9146,1,176,288 bytes/free359,712 сохранён в firmware этой ветки.
  Все44 platform cases/1,182,252 checks pass, новыйcase48checks охватывает day/
  night/calendar/full brightness и отсутствие лишних SPI/LEDC writes.
- Теми же observer/helper bytes actual HTTP обеих app pass. Candidate request
  .167458 guest s, проверка duty4095/.501 brightness через.141715 guest s после
  ответа,0 differing pixels на всём photo/footer и без новой fade. ВМ этого
  stage закрыты. Before backup BIN/ELF/platform.exe сохранён отдельно.
- Следующий stage того же handle86675 — повтор84 photo/fade frames и9 canonical
  scenes на candidate; ещё live. Branch consumer gates требуют frames+idle HTTP,
  shared contract также проверяет полноту/panic/integrity и10 negative mutations.
  Root92411/его63 input bytes не менялись, выполняется региональная матрица.

- Handle86675 завершён exit0: оба HTTP flows pass, candidate84 full frames и9
  canonical scenes повторно совпали, actual JPEG entry/read assertions и10
  incomplete-evidence rejection checks pass. Все input/archive/helper hashes
  сохранились, все owned VMs закрыты. Архивированы candidate/before HTTP,
  C negative executable/hash и44-case platform result. Root92411 отдельно
  перешёл к natural calendar; его результат не приписан новому firmware.

### 2026-10-16 — постоянные JPEG inputs и baseline headers

- Создан sparse worktree .worktree/small-tv-jpeg-inputs / branch
  codex/small-tv-jpeg-inputs от main 41b972aa. Existing ignore rule подтверждён;
  root frozen full run 22926 не затронут. SDK/oracle shared; before ELF/bin/ROM
  скопированы точно, factory dump на диске не менялся.
- Закреплены 8 synthetic fixtures с manifest/generator и 12 malformed cases.
  Actual factory/native before принимает quantizer ID 4 как 0, SOF precision 12
  и extra component data. Инструкции 0x420110c4 и 0x42011d5a..8a сохранены;
  FIXED_FACTORY checks устраняют эти ошибки, IDCT/color/output прежние.
- App a33788db / source 731815d5 / ELF c2c6ae3b сохранён в firmware, 1,176,256
  bytes / free 359,744. Все 8 valid / 12 invalid, 107 public JPEG / 35 errors /
  7 placements и host 3,884 checks проходят. Exact before/candidate/native/public
  reports и factory/native snippets сохранены отдельно. Full suite ещё нужен.
- machine_jpeg_inputs включён в branch run-all/publisher/verifier, native runner
  получил PythonPath для shared SDK. UPSTREAM/README уточняют header validation.
  Старый main full run продолжает проверять свой app/test set; physical действий нет.
- Отдельный минимальный 363-byte grayscale JPEG доказывает acceptance impossible
  Huffman tree: три 1-bit DC codes, entropy использует только первый. Factory draw,
  native draw и validation возвращают 0. Это следующий bug; random entropy case
  не доказывал проверку таблицы. Probe/result сохранены в root .build для следующего
  регрессионного case и отдельного исправления.

### 2026-10-16 — Huffman prefix-space validation

- Добавлены 4 valid 1/16-bit boundary cases и 17 impossible trees (DC1, AC1…16),
  entropy намеренно не использует невозможные ветви. Actual before app a33788db
  принимает все 17 в factory/native draw и native validation; 4 valid pass.
- Factory builder 0x42011100..0x42011244 архивирован; 0x42011194..0x420111c8
  строит 16-bit codewords без prefix-space check. FIXED_FACTORY в C считает
  доступные префиксы uint32_t (включая 65536 при length16) до codeword allocation.
- Candidate 131ce792 / source f411bf0e / ELF 9184b08b собран и сохранён в firmware:
  1,176,272 bytes / free 359,728. Все 41 additional JPEG cases проходят;
  invalid trees не достигают jd_decomp и не рисуют. Public 107/35/7 и host
  3,884 pass. Before/after observer bytes одинаковы; отдельные reports/snippets
  сохранены, header-only evidence a33788db не переименовывается.
- Branch mandatory publisher/verifier проверяют все глубины. Main full run
  22926 продолжает свой неизменённый app 0d8b7585. Candidate QEMU/full suite
  пока не проходил; следующий шаг — фактический HTTP upload/download/reboot,
  затем интеграция после terminal main run. Физических действий нет.

### 2026-10-16 — реальные photo HTTP writes/download/cold boot

- Permanent photo_qemu.py исполняет actual SDK HTTP/flash без app server mock.
  Одинаковый before/after test: old0d8b7585 принимает invalid Huffman JPEG363
  (finish200, exists=true), candidate131ce792 даёт400/absent. Valid grayscale и
  RGB38488, ten4096-byte chunks, busy/early/out-of-order/conflicting requests,
  exact retry, полное скачивание и cold process проходят.
- Финальный тест усилен до 21 checks и четырёх процессов без debounce-паузы.
  Замена RGB на gray другой длины переживает остановку сразу после finish;
  незавершённая замена после start остаётся скрытой при cold boot, новая загрузка
  доступна. Candidate finish→stop 0 guest s, start→stop .143098 guest s;
  maximum observed request .298990 guest s. Все 21 candidate checks pass.
  Все четыре UART-фазы
  checked before log reuse, owned flash действительно менялся, source archive
  unchanged; ВМ закрыты. Ранний prototype проверял panic только после cold boot;
  постоянный тест усилен и before/after повторён, prototype не подменяет его.
- Общий minimal JPEG producer вынесен в jpeg_test_fixtures; повтор 41-case
  machine gate проходит. Старые scoped reports/их source hashes не переписаны.
  Photo stage добавлен в branch suite/publisher/verifier. Root full run22926
  продолжает frozen app0d8b7585 и не содержит эту новую проверку задним числом.
- Гипотеза о недолговечном RAM-only размере не подтвердилась: фактический
  settings_photo_size() уже вызывает settings_flush() синхронно. Production code
  не менялся. Первоначальные 11-check reports/prototype исторические; архивные
  photo-http-before/candidate содержат окончательный одинаковый 21-check observer.
  Не моделировался power cut посреди операции записи flash.

### 2026-10-16 — программные задержки и повторная команда темы

- Пользователь уточнил, что имеет в виду программные задержки. Явные паузы
  и циклы ожидания просмотрены в app. Ранее удалённые startup/HTTP-weather waits
  остаются в обязательном suite. Остальные vTaskDelay имеют отдельное назначение;
  новых обоснований для их удаления нет. Уточнение записано в software-delays.md.
- Photo branch отправлена до a8b119e3. Factory0x4200d854 всегда сбрасывает latch
  при выборе темы; oldE390 терял same-value command. Восстановлены transient
  command revision и согласованный snapshot под mutex, без лишних NVS commits.
  Native3909/platform45/1,182,288 pass. Candidate2eb7bb69/sourceefc9fc36 /
  ELF4dc4e444,1,176,480 bytes/free359,520 сохранён в firmware ветки.
- Terminal47090 exit0: actual same-observer negative/positive HTTP, три полных
  перехода фото1/0/1, idle brightness,84 frames/9 scenes,10 frame guards и9
  command guards проходят. Actual assembly и scoped reports сохранены отдельно,
  staged source/images/generated resources/ELF proof прошёл. Все ВМ серии закрыты.
- Root92411 жив, native classic natural calendar через fractional-midnight.
  Все63 initial test files, appAD7A/ELF6D7B/QEMU неизменны. Не интегрировать новую
  ветку до terminal и публикации root19-group result; после merge/build нужен
  полный набор с тремя новыми photo gates. Main production/tests не менялись.
  Физических действий или изменений QEMU не было; посторонние файлы сохранены.

### 2026-10-16 — полный интегрированный JPEG-прогон завершён

- Handle92411 terminal exit0. Все19 автоматических групп прошли на appAD7A9009 /
  sourceF411BF0E / ELF6D7B586F / QEMUFDE38D53: host3884, platform43/1,182,204,
  report aggregation14, все machine gates,41 дополнительных JPEG cases,
  настоящий photo HTTP21, AP→STA/NVS, weather/scroll/time/UTF8/regional,
  84 natural calendar transitions и24 completed frames без pixel differences.
  40 normalized scenes pass; пять несинхронизированных scene pairs остаются
  диагностикой, их similarity не является критерием соответствия.
- Initial/final63 test files и app/ELF/QEMU/helper hashes совпали. Новый reader
  сохранил даты строками; исправление агрегата задним числом не требовалось.
  Штатные publisher/verifier прошли; опубликованы25 positive artifacts,
  validation считает158 entry comments /52 markers, DIRAM80,714, app1,176,272 /
  free359,728. Отдельный audit jpeg-integrated-run-inputs.json сохраняет initial
  pins и hash полного raw report; ELF/app до merge скопированы в ignored backup.
- Этот19-group результат относится к AD7A, не к photo branch6BF6. Теперь можно
  объединять отправленную ветку aded56bf, пересобирать main и выполнять новый
  полный набор с четырьмя photo gates. Все VM полного прогона закрыты.
- Отдельная браузерная проверка идёт на собственном snapshot-guest6BF6/PID30908,
  state .build/small-tv-browser/controls-20261016. Настройки синтетические.
  Браузерные изменения видны после reload; QMP/DWARF подтвердил London/GB и
  dirty=false. Base flash.bin в snapshot-режиме закономерно остаётся прежним;
  его ошибочно использованный первый read не является firmware defect.
  Браузерная VM ещё нужна для продолжения приёмки, не закрывать до сохранения
  результата. Browser/physical/soak не объявлены завершёнными.

### 2026-10-16 — повторный выбор той же темы

- Factory handler0x4200d7f0 записывает тему и всегда сбрасывает39e9. Наш
  settings_replace игнорировал одинаковые bytes, coordinator не видел команды.
  Permanent same-observer negative: factory трижды меняет фото; oldE390 даёт200,
  но остаётся[0,1],57,492 different pixels через2.283872 guest s. Code/media и
  helpers неизменны, panic отсутствует; bounded result не выдаётся за60s wait.
- settings_select_theme публикует transient command revision. Единый snapshot
  preferences/configuration/theme revisions под mutex исключает рассогласование
  с HTTP. Активный coordinator подтверждает reinit, photo cursor сохраняется;
  повторные запросы до одного pass coalesce. ABI364/version2 не менялся.
- Candidate2eb7bb69/sourceefc9fc36/ELF4dc4e444 собран и сохранён в firmware,
  1,176,480 bytes/free359,520. Три actual HTTP перехода photo1/0/1 совпали по
  всем pixels/footer и duty, каждый1.04…1.12 guest s. Host3909 и platform45 /
  1,182,288 pass, включая отсутствие новых NVS commits и coalescing команд.
- Batch47090 terminal exit0: новый HTTP, прежний idle brightness и84 frames /
  9 scenes проходят на одной exact сборке;10 frame guards и9 control mutations
  отклоняют неполное evidence. Все owned VMs закрыты. Scoped before/candidate,
  host/platform reports и actual factory/native assembly сохранены отдельно;
  старые positive results не переименованы. Подробности photo-reselect-checks.md.
- Root92411 по-прежнему жив на AD7A, native classic calendar через us-spring.
  Root production/tests не менялись. Сначала дождаться terminal, сверить63 pins
  и опубликовать его19-group result, затем merge/build/full с тремя photo gates.
  QEMU/физическая плата не менялись. User clarification про software delays
  сохраняется: убирать лишние UI waits, оставлять task yield и аппаратный timing.

### 2026-10-16 — отменённый фотопереход и чёрный экран

- Установлен заводской дефект: init0x42008e08 очищает экран, init0x4200bb20
  сохраняет fade phase. Повторный HTTP выбор фототемы после её фазы2 оставляет
  только фазы3…5 и теряет картинку до следующего интервала. Permanent observer
  подтверждает саму команду на фазе3. Factory и old2EB7 после неё дают[0,1],
  duty0 и все57,600 чёрных pixels,57,594 отличия от следующей фотографии.
- Первый запуск остановился при старте QEMU из-за недоступного loopback в
  sandbox; это инфраструктурная ошибка, не firmware evidence. PID10152 исчез.
  Реальный before31895 terminal exit1 — ожидаемый native negative; factory
  known defect напрямую подтверждён, observer/image bytes неизменны, ВМ закрыты.
- Новое исправление FIXED_FACTORY сбрасывает только slideshow.fade при init
  фототемы; next_slot сохраняется. Permanent production C-case до правки падает
  на duty==2457; после неё все46/platform1,182,310 и native3909 проходят.
- Build32350 terminal exit0: app6bf6a61c/source0baa7e03/ELF7de6fec2,
  1,176,480 bytes/free359,520 сохранён в firmware. Новая RV32 запись0x4200d4c6
  проверена по assembly и сохранена отдельно. SDKconfig отличается только EOL,
  эта побочная правка убрана до runtime tests.
- Batch77905 terminal exit0: тот же active-command observer, повторные idle
  команды, brightness,84 frames/9 scenes проходят. Native новый фото/IP за
  1.094945 guest s,0 pixel differences;10 frame и10 active-contract guards pass.
  Все owned VMs закрыты. Отдельные before/candidate/C/assembly reports сохранены;
  исторические сборки не переименованы. Новый gate обязателен в branch suite.
- Root92411 пока жив на AD7A, native dial fractional-midnight. Все63 tests /
  root app/ELF сохранились; production/tests root не менялись. После terminal
  сначала опубликовать его19-group result, затем merge/build/full с четырьмя
  новыми photo gates. Физическая плата и QEMU не менялись.

### 2026-10-16 — объединение фото-ветки

- После terminal root92411 и checkpointdbbef80d объединяется photo branchaded56bf.
  Конфликты были только в WORKING_NOTES/WORK_LOG; обе истории сохранены, свежий
  контекст явно отделён от исторических live-записей. Production/test inputs
  photo branch сохранены; следующим шагом нужны root build и новый full suite.
- Browser6BF6/PID30908 ещё используется: controls после reload, cityQMP,
  mask0/10/31,interval60/3/4 и пять decoded previews наблюдались. Full H03 не
  завершён, dedicated state не закрыт. Снимок baseline flash в -snapshot не
  отражает guest writes; это объясняет ошибочную первую проверку файла.

### 2026-10-16 — root build после фото-слияния

- Merge95eddf55 завершён; build80930 terminal exit0. AppD978AAB6 /
  source0BAA7E03 / ELF8AC006E0,1,176,480 bytes/free359,520 сохранён в firmware;
  root source identity совпадает с branch6BF6, BIN/ELF сохраняют свои новые IDs.
  Actual instructions шести функций сохранены в native-photo-root-integrated.
- Новый full ещё не начат. На отдельном браузерном6BF6 обнаружен hardcoded
  NTP prefill pool.ntp.org при QMP-confirmed actual10.0.2.2. Для optional editor
  требуется подставлять сохранённый hostname с безопасным HTML attribute encoding.
  Partial browser controls и before screenshot сохранены в ignored state;
  неправильный порядок JSON keys в одном test assertion исправлен сравнением
  значений, не изменением приложения. Snapshot imagefile read тоже не был багом.

### 2026-10-16 — сохранённый NTP и корректное HTML-экранирование

- Браузер6BF6/source0BAA показал pool.ntp.org при QMP/DWARF actual10.0.2.2,
  dirty=false. Старый optional advanced_page действительно hardcodes value.
  Точечный C negative воспроизведён; final test/adapter отдельно компилируется
  с сохранённым server.c без изменения production checkout.
- advanced_page получает settings snapshot, bounded html_attribute сохраняет
  quoted attribute. Static page передаётся chunks, временный buffer390 bytes.
  Код помечен FIXED_RECONSTRUCTION. Допустимый empty NTP с fallback сохранён;
  нулевой промежуточный chunk пропускается, поскольку SDK трактует его как EOF.
- Первый nonempty prototype1E33/source0357 работал для обычного/escaped NTP,
  но новый empty case поймал premature EOF. Native adapter усилен реальным
  состоянием completion; prototype сохранён и его expected negative повторён
  с тем же final adapter. Отсутствовавший settings.h include исправлен до SDK
  сборки. Эти промежуточные проблемы не объявлены factory defects.
- Build5179 terminal exit0, native3924 pass. AppDAF5595D/sourceC83941FF /
  ELFB06CE810,1,177,568 bytes/free358,432 сохранён в firmware. SDK advanced_qemu
  beforeD978/source0BAA expected fail, afterDAF4 cases pass, observers identical.
  Ordinary/metachar/64quotes/empty, complete HTML, no key echo, raw backing,
  app/media integrity и no panic подтверждены. Обе SDK VM закрыты.
- На final browser12152/DAF direct raw body NTP10, Save/reload, harmless markup
  string без injected DOM node и empty complete page проверены. Errors нет.
  QMP подтвердил raw backend, после stop все4 source images совпали по SHA.
  CUA tab закрыт. Screenshot и scoped browser/C/SDK/assembly reports сохранены;
  final browser report не заявляет complete H03. Старый controls snapshot6BF6
  сохранён отдельным partial report, source IDs не переименованы.
- При инспекции storage выявлено: -snapshot скрывает guest writes в overlay,
  так что старый basefile unchanged check не доказывал весь guest media.
  Это ограничение теста, не установленный firmware bug. qemu_storage подтверждает
  actual raw backing и отвергает живой snapshot guest. Advanced HTTP уже использует
  его; далее усилить4 photo gates/contracts до нового full run. Pixel/PWM и
  instruction observations исторических тестов сохраняют свою область проверки.
- QEMU/physical boards не менялись, непрофильные файлы не затронуты. Общий
  успешный checkpointdbbef80d остаётся на AD7A; новый полный DAF ещё не запускался.

### 2026-10-16 — уточнение области программных задержек

- Подтверждено: пользователь имеет в виду программные ожидания. Повторно
  просмотрены все app-вызовы delay/sleep/wait и циклы: 11 vTaskDelay относятся
  к аппаратному запуску ST7789, шагу UI/защите upload и фоновым интервалам.
  Дополнительного обоснованного удаления на sourceC839 не найдено. Сокеты,
  mutex и notify не объявляются лишними паузами. Политика и область проверки
  дополнены в software-delays.md; новый код ради изменения счётчика не добавлен.
- Подготовленный NTP-коммит044e488f завершён и отправлен main. Точная staged
  проверка57 production inputs/BIN/ELF,3924 native checks, двух negative controls,
  SDK/browser/raw images и10 guards прошла. Не включённый сначала загрузчик
  3FB735A3 добавлен из того же успешного build; manifest/test artifacts совпали.
  Раннее резюме с bootloaderED59 не описывало новый DAF-комплект.
- Усиление четырёх photo storage gates выполняется отдельно. Идёт scoped
  raw-backed прогон26076 на DAF; исходники прошивки неизменны. Результат не
  объявлен полным suite. Старые snapshot reports сохраняют прежнюю область.

### 2026-10-16 — проверка настоящего гостевого флеша

- Четыре photo producers теперь создают новые собственные state dirs с
  persistent=True. Перед наблюдением общий qemu_storage подтверждает через
  query-block единственный writable raw backend именно для этой копии.
  После stop проверяются реальные защищённые диапазоны. Fingerprints включают
  helper, contracts требуют его положительный результат. Frame checks update
  сохраняет ранее записанный backing flag; publisher/verifier требуют12 guards.
- Batch26076 terminal exit0 на неизменных appDAF/sourceC839/ELFB06/QEMUFDE3:
  brightness, три повторных theme commands, active reinit,84 frames и9 scenes
  проходят. Все ВМ закрыты. Все pixels совпали; factory known blank-screen
  correction остаётся явно отделена. Не заявлен полный suite новой сборки.
- Два paused QEMU дополнительно подтверждают direct_flash_backing=false для
  настоящего qcow2 с -snapshot и true для raw. Первый probe с профилем none завершился
  до запуска ВМ; исправлен только тестовый launcher на поддерживаемый offline,
  повтор успешен. Обе ВМ закрыты, базовые копии unchanged.
- Сохранены scoped photo-direct-storage reports и отдельный backend probe;
 12 frame mutations,12 control-backing mutations и4 historical rejections pass.
  Старые reports не дополнены вымышленными raw-checks. Точный scope описан
  в photo-storage-checks.md. Source/BIN/QEMU/физическая плата не менялись.
- Freeze helper расширен initial pins семи firmware artifacts,6 QEMU helpers,
  профиля/marker/source commit, factory ELF/dump и verifier. Collector готов к
  advanced_http и четырём photo gates; далее один новый полный run после commit.

### 2026-10-16 — новый объединённый прогон DAF

- Storage65d7be99 и auditac187b10 отправлены main. После фиксации72 test files
  и дополнительных firmware/QEMU/helper/profile identities запущен единственный
  полный run controls-integrated-full-20261016, handle96792, initialHEAD65d7be99.
  AppDAF5595D/sourceC83941FF/ELFB06CE810/QEMUFDE38D53 прежние. Загрузчик3FB735A3
  соответствует manifest и реально использованному новому DAF-комплекту.
- Native3924, все46 platform scenarios, frontend, artifact integrity,
  report aggregation14 и timezone-source tests уже pass. Machine/QEMU остаются
  активными; общего результата ещё нет. Source/tests/helpers/BIN/ELF заморожены.
  Продолжать опрос того же handle; не запускать второй full. После terminal
  проверить initial/final pins и strict publisher/verifier через адаптированный
  archive_immutable_run.py. Контекстные Markdown не входят в frozen test bytes.

### 2026-10-16 — изменение фотонастроек во время fade

- Создана собственная ветка codex/small-tv-photo-settings под .worktree от
  cc65d379, чтобы не менять root72 frozen tests. Скопированы и проверены DAF
  BIN/ELFB06/factory ELF и ROM для read-only instruction replay. Production C,
  QEMU и физическая плата не изменены.
- Новый photo_settings_qemu выполняет mask disable-before/after-image, none,
  enable-next и60->3/5->9 interval changes внутри реальной active fade. HTTP
  handler publication наблюдается hardware breakpoints; guest RAM/PC/time/code
  не переписываются. Проверяются два полных кадра, state/PWM и естественный
  следующий event по фактическим ISR counters. Direct raw/media/panic обязательны.
- Первые probe failures были инфраструктурой harness: отсутствовал ROM в новом
  worktree и в digest ошибочно передавался Path. Затем исходное предположение
  counter<new_interval оказалось неверным: factory сохраняет17 после60->3,
  callback >= сбрасывает его на следующей секундной границе. Исправлена формула
  ticks=11*max(1,P-c)-subsecond. Это не bug в прошивке.
- Вторая версия30669 пропустила первый native frame после shortening: API wait
  был раньше hardware capture. Состояние[0,2] относилось уже к следующему фото.
  Capture двух кадров перенесён до ожидания response; native smoke4374 pass
  на неизменных firmware bytes. Новый контракт проверяет и хронологию наблюдений.
- Окончательный2990 terminal exit0:12 actual scenarios/24 complete frames с0
  отличающихся pixels/14 rejection checks. До него frozen74 test files; observer,
  BIN/ELF/ROM/QEMU/helpers unchanged. Все ВМ набора закрыты. Сохранены candidate,
  guard/input reports и8 actual factory/native instruction ranges с hashes.
- Новый child gate добавлен в branch suite/publisher/verifier. Main96792 остаётся
  жив на исходных72 test files; machine, early startup/weather UI, advanced NTP,
  upload,84 frames/9 scenes/brightness/theme commands/reinit/setup/weather/fields
  уже pass, идёт SNTP. Root suite не подменять scoped result; дождаться terminal
  и strict публикации, потом интегрировать новую ветку.
- Для следующего H10 изучены ELF DWARF и SDK heap/TCB/list layouts, StackType_t
  здесь однобайтовый. Layout-only metadata в root .build сохранён, но runtime
  heap/stack/soak не выполнены. Browser skill/docs перечитаны для дальнейшей H03;
  новых вкладок/браузерных ВМ в этом этапе не открывалось.

### 2026-10-16 — закрыта проверка фотонастроек при active fade

- Отдельная .worktree/small-tv-photo-settings от maincc65d379 не меняла frozen
  root. Новые real HTTP mask/interval tests, contract и child gate отправлены
  веткой codex/small-tv-photo-settings:6ae7373f. Production DAF/C839/B06 прежние.
  Commit459b93bd сохраняет LF двух новых assembly files; реальный Git checkout
  filter с core.autocrlf=true сохраняет оба manifest hashes.
- Final2990 terminal exit0:12 scenarios на обеих firmware/24 full frames с0
  отличиями/14 consumer rejections pass. Все ВМ набора закрыты,74 initial test
  files и BIN/ELF/ROM/QEMU/helpers совпали. Staged proof57 production inputs,
  образов,74 test pins и8 instruction ranges прошёл. Scoped candidate/guards/
  input audit/assembly сохранены только в этой ветке; root full не переименован.
- Предварительные ошибки касались harness: missing replay ROM/Path digest,
  неверное counter<new_period предположение и запоздалое наблюдение первого
  native frame после HTTP wait. Factory сохраняет counter17 при60->3; >=
  сбрасывает его на ближайшей секундной границе. Код C это уже делает правильно.
  Hardware captures обоих кадров теперь предшествуют response wait; отдельный
  smoke4374 и final12-case2990 проходят без изменения прошивки.
- Root96792 повторно подтверждён live; все72 initial test pins и firmware/ELF/
  QEMU/helper/profile identities неизменны. Все machine groups и QEMU startup/
  weather wait/advanced/upload/photo84/brightness/commands/reinit/setup/weather/
  fields/SNTP прошли на обеих; original UTF8 тоже pass. Далее native UTF8,
  regional/calendar/completed scenes. Не сливать branch и не менять root frozen
  inputs до terminal и strict публикации root. Опросить тот же handle96792.
- Для следующей проверки памяти изучены только DWARF/SDK layouts: heap_t36,
  multi_heap_info20, TCB96, list20; StackType_t=uint8_t. Layout-only metadata
  сохранён в root .build. Guest RAM/heap/stack/soak этим не проверены. Browser
  skill/docs перечитаны, новых browser tabs/VM не открывалось. H03/H09/H10 и
  физическая приёмка остаются; это не основание объявлять цель завершённой.

### 2026-10-16 — пауза по просьбе пользователя

- Остановлены контроллеры full-run21648/23436/16632; две оставшиеся собственные
  ВМ закрыты через QMP с проверкой имени, остановка подтверждена. Остальные32
  session уже были закрыты. Временная браузерная вкладка2 закрыта, список пуст.
  Локальный отчёт остановки: controls-integrated-full-20261016/paused-by-user.json.
- Full96792 прерван без общего pass и публикации. Замороженные результаты
  сохранены; никаких новых сборок/тестов/слияний после команды паузы не начато.
  Photo-settings459b93bd остаётся отдельной отправленной веткой.
- Браузерная H03-приёмка прервана: night=true/brightness2 сохранялись, start18
  подтверждён после клавиатурного ввода и reload; stop12 ещё без reload-проверки.
  Первое fill-изменение чисел не сохранилось, клавиатурный start прошёл; это
  промежуточное наблюдение harness, не подтверждённый дефект firmware.
- Точка остановки сохранена в WORKING_NOTES.md. Продолжать только после явной
  команды пользователя; старое указание опрашивать handle96792 отменено.

### 2026-10-17 — возобновление и браузерная приёмка текущей DAF

- После явного ответа «Возобновить проверки» создан новый собственный raw guest
  acceptance-20261017 на прежних DAF/C839/B06/QEMUFDE3.31 final browser cases и
  21 storage/identity checks pass; scoped report и2 screenshots сохранены в qemu.
  Три синтетические PNG сохранены как fixtures/browser; личных файлов не было.
- Проверены ночные18/23 и5/12, яркость2/99/off; флаги/day0/три RGB565 цвета,
  все4 темы/5 GIF/3 даты с reload; resize рамки обоими направлениями, выбранные
  RGB области240x240 без APP/COM; mobile390x844, Cancel/Escape, mask0/31 и3/60.
  Новый процесс после холодного запуска читает прежние settings и два JPEG.
  Защищённые flash regions и незатронутые slots1–3 неизменны; HTTP JPEG совпадает
  с raw; source/archive/ELF/QEMU/profile/helpers unchanged. Console errors=[]
- Два неправильных ожидания harness сохранены отдельно: исчезнувший status
  ошибочно искался как Upload complete и ожидалось сохранение8-bit RGB вместо
  заводского RGB565. Видимый успех следующей загрузки проверен точной строкой;
  нормализация цветов совпала с factory0x42008a34/0x42008a6a и прежним native test.
  Styled switches нажимались по label; networkidle timeout не считался концом
  ВМ/ошибкой UI, последующее наблюдение подтверждало все5 превью/ready controls.
- ВМ10724 закрыта перед cold boot; ВМ24764 и вкладка закрыты после отчёта,
  mobile viewport reset. General full остаётся прерванным, photo-settings branch
  ещё не merged. H03/setup/concurrency/soak/physical acceptance этим не закрыты.
- Пользователь подтвердил исправление factory bugs и разрешил оптимизации.
  Для следующей правки выявлена лишняя пауза50ms после каждого upload ACK;
  ACK следует за синхронной flash write. Baseline noise upload47837 bytes/12chunks
  pass, JPEG SHA a73dc807e3ebd4a0339641f95a0c45f587a14892a7b1ce08ebfecd73a62825dc.
  Пока код не менялся: сначала sequencing/retry regression, потом after build/UI.

### 2026-10-17 — интеграция photo-settings gate

- Ветка459b93bd объединена с main после подтверждённой остановки прежнего full.
  Конфликты только в контексте/журнале/Git-атрибутах: обе истории и оба правила
  сохранены. Production DAF/C839/B06 и QEMU не менялись; никакой scoped результат
  не выдавался за законченный общий прогон.
- На перенесённых байтах повторно исполнены14 consumer mutations. Проверены
  74 исходных test pins,57 production inputs, BIN/ELF, helpers и8 instruction
  ranges. Новый child обязателен в suite/publisher/verifier. После следующей
  production правки требуется новый полный run с этим gate и новым collector.
- PNG browser fixtures явно исключены из text normalization. Staged PNG
  декодируются, их точные SHA совпадают с report; сборка и источники не менялись.

### 2026-10-17 — стабильные переводы строк archive manifest

- Windows Set-Content создавал CRLF в manifest.json, тогда как Git хранит этот
  файл с LF. Builder теперь явно пишет UTF-8 без BOM и LF, чтобы точные хеши
  служебных метаданных сохранялись после checkout. Декодированные значения,
  source identity и бинарные образы от этой правки не меняются.
- Уже собранный manifest нормализован с проверкой равенства JSON. Первое
  browser-after evidence сохранено в ignored run; финальная браузерная проверка
  будет выполнена заново с каноническими байтами manifest до публикации отчёта.

### 2026-10-17 — upload ACK заменяет лишнюю программную паузу

- Собственная ветка codex/small-tv-photo-upload-waits от main5de17c6c. Uploader
  выделен в photo_upload.js и детерминированно встроен в photo.html. Removed
  50ms после успешного блока и2500ms после последней неудачи. Пять попыток,
  порядок, поля, размеры блоков и задержки500/1000/1500/2000 между повторами
  сохранены. Клиент по-прежнему ждёт ACK каждого блока до следующего/finish.
- Node исполняет actual generated page code:11 final cases pass, на прежнем
  HTML тот же финальный тест даёт6 ожидаемых отрицательных результатов. Таймеры
  успешных1/3/25 chunks раньше50/150/1250ms, теперь0. Это измеренные requested
  timers, не benchmark общей сети/flash. New frontend includes exact module
  inclusion and MJS fingerprint in full run inputs; metadata/crop/resize pass.
- Build74435 terminal0, архив в firmware/development: appDD4EB76E/source96A111EC/
  ELFB7BE7CCC,1 176 880 bytes/free359 120. App меньше DAF на688 bytes. Actual
  native photo_upload_start/chunk/finish/web_photo_post instructions полностью
  совпали с B06; сохранены четыре диапазона и хеши. Серверный C не менялся.
- Host57538 terminal0:3924 native,46 platform, frontend, integrity, timezone
  и aggregation pass в reduced profile. Native SDK HTTP28482 terminal0:21 checks,
  включая malformed Huffman, retries, immediate cut/cold boot, interrupted upload.
  ВМ этого набора закрыты. Это scoped, не новый полный machine/QEMU checkpoint.
- Browser-after25000 и затем final28044 на том же DD4 raw image:47 837-byte
  JPEG через12 chunks побайтово равен DAF baseline (SHA a73dc807). All22 final
  checks pass: raw=HTTP, APP/COM отсутствуют, slots1–4/защищённые regions unchanged,
  sources/archive/ELF/QEMU/helpers unchanged, console[]. Вкладки и ВМ закрыты.
  Финальный запуск использовал LF manifest; первый CRLF report сохранён ignored.
- Отчёты/actual assembly и screenshot сохранены как photo-upload-waits-*.
  Новый полный run main ещё требуется после merge/build и обновления collector/
  freeze для photo_settings/.mjs. H03/setup, concurrency, memory/soak и physical
  acceptance остаются; заводские ошибки исправляются, а не воспроизводятся.

### 2026-10-17 — main после оптимизации uploader

- c5f51a04 и de3e9ddd объединены в main через1a946c38. Root build84004 terminal0:
  appDD41A536/source96A111EC/ELFB4AF3C2A,1 176 880 bytes/free359 120,
  cached bootloader3FB735A3. Архив firmware обновлён штатным builder. Обе
  executable sections (.iram0.text/.flash.text) полностью совпадают с branch
  DD4EB76E/B7BE7CCC; сохранён отдельный main-build report без переноса runtime
  passes на другой app identity. Прежний B06 ELF/BIN/map/resources сохранён ignored.
- Full ещё не запущен. Freeze helper включает75 test sources, frontend и57
  production inputs; collector дополнен обязательным photo_settings. После
  фиксации архива выполнить один новый frozen run, прежний interrupted controls
  не продолжать и не публиковать как полный pass.

### 2026-10-17 — новый frozen full для main

- Запущен единственный run upload-integrated-full-20261017, handle62455,
  initialHEAD053337e4, appDD41A536/source96A111EC/ELFB4AF3C2A/QEMUFDE38D53.
  Зафиксированы75 test files и88 дополнительных inputs, включая все57 production
  inputs, frontend, archive, profile и helpers. Повторная проверка после host
  stages подтвердила неизменность всех байтов.
- Aggregation14, native3924, platform46, frontend (включая11 transfer cases),
  integrity6 и timezone-source9 pass. Machine renderer активен; общего результата
  ещё нет. Не перезапускать по timeout наблюдения. Source/data/ELF/BIN заморожены;
  независимая новая работа допустима в своей ветке, context Markdown не в pins.

### 2026-10-17 — браузерный proof текущего main

- Дополнительная собственная ВМ18016 main-ui-20261017 использовала DD41/B4.
  Реальный DOM inline-script совпал с generated page по SHA654c2ee3, затем
  actual browser upload47837 bytes/12 chunks дал прежний JPEGa73dc807. Все16
  browser/raw/protected/source/helper checks pass; slots1–4 не менялись.
  ВМ и tab4 закрыты, console[]. Сохранены отдельные main-ui JSON/screenshot.
- Предыдущий push доc5f4d57a завершился успешно. Full62455 продолжает machine
  stage на неизменных75+88 inputs; эти scoped browser results не его aggregate.

### 2026-10-17 — постепенное разделение модулей

Пользователь уточнил: разделять функции по назначению между файлами и модулями
по мере текущей работы; сейчас не перелопачивать весь код. Отдельные категории:
вывод на экран, сеть, настройки, хранение, конвертеры форматов. Правило добавлено
в WORKING_NOTES.md. Разрешённые оптимизации сохраняют функциональное поведение
и сопровождаются проверками затронутого участка.

### 2026-10-17 — полный прогон завершён с ошибкой задержки HTTP

Full upload-integrated-full-20261017 завершился failed; report записан13:47:20.
Все75+88 frozen inputs неизменны. Pre-QEMU18 groups pass; calendar обеих firmware:
84 natural transitions/168 full frames pass, но native /setclocktype в dial /
post-2038-midnight занял6.150371 guest s при пределе6. Ещё два ответа5.702424 и
5.882957; остальные native <=0.184099, factory max0.176792. Причина пока не
доказана. Порог оставлен прежним; начато read-only исследование HTTP/flash/сети.
Complete-scenes и diagnostic comparison не достигнуты. Новый full pass не
объявлен, прежние canonical reports сохранены. Компактный failed summary с
хешами исходного report и pins сохранён в qemu/parity; исходные журналы ignored.

### 2026-10-17 — повторная диагностика HTTP admission и история QEMU

По напоминанию пользователя проверены история и точный diff9d4da15732:
прежняя no-descriptor потеря SYN исправлена, фикс входит в962cda7a6f/FDE38D53.
Все8 packet regressions повторно pass. Прямых обходов inject timer к
Esp32_sendFrame нет; mapped16 shared POST routes и11 GET routes. Три180-request
scoped probes завершены:5.8s задержки до handler, сам handler<=11ms, повтор SYN,
валидные checksums. Dedicated RX trace0 drops. Сырые логи/PCAP ignored; компактная
сводка и call-path document подготовлены. Production firmware и QEMU не менялись.

Corrected TCP preflight60 pass как диагностическое выполнение:1.55s body case
имел быстрый SYN/admission и ненулевой PCB. Weather FIN_WAIT_2 накапливаются до13,
TCP limit16; причина5–6s ещё не доказана. Отрицательные попытки observer сохранены
как harness errors (same-PC loop; competing breakpoint), без firmware conclusions.
Запущен более узкий admission probe6201 на точных B4 адресах, каждый BP one-shot.

### 2026-10-17 — доказанный RSSI-дефект QEMU и отрицательный latency A/B

У общего new_frame отсутствовала signal_strength initialization. RSSI -25
добавлен1a142bcf51; simultaneous8 frames regression на FDE даёт2 failures
(C2/C3), на candidate62386F10 все9 pass. Первый sequential test скрывал
heap reuse; attempt с runtime-set latency был harness error, не negative control.
3279a6c2f1 выделяет passive format tracing в отдельный модуль;1646 actual TCP
identifiers совпали с PCAP. Оба commits отправлены в QEMU feature branch.
Main/installedFDE/firmwareDD41 прежние. Modules и CYD/C3 boots/pixels pass.

Four-route after240 max.214052. Однако identical five-route quiet A/B180 each:
beforeF207 max6.167475, after6238 max6.186934, оба at index117. RSSI исправлен,
но не устраняет stall. Detailed passive five-route180 max.220060/drops0
не воспроизводит этот timing; все ВМ закрыты. Следующий шаг — low-volume SYN
DMA/IRQ/CPU-context trace. Полный passing firmware checkpoint не обновлялся.

### 2026-10-17 — исправлена длительность Wi-Fi backlog в QEMU

Sparse SYN trace72f106db81 воспроизвёл6.201632s: первый SYN дошёл в DMA через
17.639ms, SYNACK появился только после retry. Detailed trace отдельно показал
до4 DMA completions в одной микросекунде. Старый MAX(now, nominal) схлопывал
просроченный FIFO вопреки bandwidth4Mbit/s. Исправление0d27a7ca98 учитывает
полный frame transfer time на всех5 RX/TX scheduling sites; calculations вынесены
в esp32c3_wifi_link.c/.h, bandwidth0 unlimited сохранён. Software sleeps/HTTP gate
и сама прошивка DD41/96A/B4 не менялись.

Новый QTest с двумя112-byte NTP frames после5s без descriptors: oldD18 failure
(оба за1ns), new30F10/10 pass (по112us на8Mbit/s). Тот же quiet180 HTTP probe:
correct-RSSI6238 max6.186934, finite-timing30F max.238274, все200/no panic/ВМclosed.
Optional PCAP в обоих quiet runs не включился (qom-type spelling); таймер QMP
работал, packet выводы основаны на отдельных корректных trace runs. SPI/I2C/SD/
GPIO и CYD/C3 legacy/modular pass, source/pixel hashes прежние; scopeCYDboot
сохранён. QEMU main и feature branch0d27a7ca98 отправлены, installed30F/marker
проверены, oldFDE backup ignored. Сохранены отдельные scoped report/doc; новый
полный firmware suite ещё нужен, прежний failed full остаётся failed.

### 2026-10-17 — новый общий прогон на исправленной QEMU

Результаты timing сохранены и отправлены af7c8c17. Начат единственный
link-timing-integrated-full-20261017, handle11075, initialHEADaf7c8c17,
appDD41/source96A/ELFB4/QEMU30F/source0d27a7ca98. Frozen75 tests/88 extras;
production и test inputs не менять до завершения. Aggregation14/native3924/
platform46/frontend/integrity6/timezone9 pass, machine выполняется. Это начало
нового прогона, ещё не общий положительный результат. Старый failed run сохранён.

### 2026-10-17 — runtime память проверена в независимой ветке

Ветка codex/small-tv-runtime-observer /9adf0fb0 отправлена. Standalone decoder
читает актуальный DWARF, heaps/FreeRTOS lists и stack fill на vTaskDelay entry;
ROM getters исполняются вне QEMU на typed header copies. 15 parser +4 ROM tests
pass. Первый40-cycle runtime-workload run имел Python HTTP name shadow доbinary
chunk; предыдущие import/unused API-deadline attempts тоже сохранены как harness
errors, ВМ без panic. Новый40-cycle -02 завершён успешно, все inputsunchanged.

121.076406 guest seconds,41 samples всех12tasks,10 JPEG uploads,240 recorded
HTTP+80 concurrent GET, max.405659s. First/last free heap87 668/86 268,
min sampled78 264, сумма SDK per-heap minima47 028. Lowest stack480bytes(settings),
ROM checks164. Это ограниченный native preflight; H09/H10/24h/leak-free/physical/
ISR stack и factory memory parity не объявлены. ВМ закрыта, snapshot memory bytes
не экспортируются. Код/документ/JSON сохранены в отдельной ветке, main frozen75+88
inputs общего run11075 не изменены. Его18 pre-QEMU groups и QEMU gates до
photo_reinit прошли, photo_settings выполняется; полный результат пока отсутствует.

### 2026-10-17 — исправление HTTP body starvation в отдельной ветке

Ветка codex/small-tv-http-body-deadline: 35b6bdce содержит исправление, тесты,
сборку и свидетельства; 79445774 закрепляет LF в ассемблерном аудите. Оба отправлены.
Старый DD41 на том же http_body_qemu.py даёт три ожидаемых отказа: второй GET
занимает 24.693549/27.605321/9.702162 s. Причина — три тайм-аута общего web_body
и очистка оставшегося тела в SDK. У factory на 0x4200d808 один вызов recv.
Новый request_body.c ограничивает чтение общим сроком 5 s и прекращает чтение
перед ответом об ошибке и cleanup. Остаток срока не превращается в нулевой,
бесконечный тайм-аут; успешное чтение восстанавливает прежнюю настройку сокета.
Четыре реальных сценария прошли; задержки 4.695327/4.703467/.204119 s,
обычные фрагментированные данные по-прежнему получают HTTP 200.

App 3C599124 / source1741EA14 / ELF342C0127: 1 177 216 байт, свободно 358 784;
все 58 production inputs совпали. Native 3950, platform 46, frontend, integrity,
timezone и aggregation прошли в reduced profile; SDK photo — 21, consumer guards — 15.
Код, сборка, ASM и отдельные JSON/документ находятся в ветке. Следующему полному
suite/publisher/verifier обязателен body_http; текущий main full11075 старой DD41
этот gate не выполняет. Его frozen75+88 inputs прежние. Он прошёл региональные
проверки обеих прошивок и миграцию NVS, переходит к календарю. Новая общая сборка
и полный прогон выполняются после завершения и сохранения текущего результата.
Отдельные проверки и старые full не означают полного соответствия нового кандидата
или прохождения физической приёмки, H09/H10.

### 2026-10-17 — concurrent clients и подготовка duration observer

HTTP branch6c5360d4 отправлена:34 native concurrent checks/16 пар/68 запросов,
max pair2.847167s, no panic/inputs unchanged/ВМclosed. Новый обязательный
concurrency_http consumer прошёл20 rejection controls. Raw preflight с ошибкой
double-stop не считается положительным результатом; финальный renderer oracle
сравнивает состояния непосредственно до/после finish.

Runtime brancha3707eb5 отправлена. 16 decoder +6 clock/journal tests pass,
synthetic read requests45→20 с теми же decoded values. Короткий4-cycle native
run:15.689122 guest s,5 snapshots/32HTTP/2 реальных AP disconnect+reconnect;
duration8s run закончен после8.135430s,4 snapshots/27HTTP. Journal count/SHA
проверены, inputsunchanged, ВМclosed. Это не24h: долгий H10 ещё не запускался.
Попытка4096-byte RSP далаE22; она сохранена как harness error, block1024 исправлен.

Новый запрос пользователя: ключ сборки для отключения лишней отладки QEMU И
Small_TV. Создана firmware worktree small-tv-debug-logging от6c5360d4; QEMU
использует прежнюю собственную worktree small-tv-wifi-link. Основной frozen
run11075 продолжает calendar; его75+88 inputs, appDD41/source96A/ELFB4 иQEMU30F
не меняются. Browser setup не запускался, собственных новых VM/tab нет.

### 2026-10-17 — immutable full на исправленном Wi-Fi timing прошёл

Link-timing-integrated-full-20261017 /11075 завершён terminal0. Все19 groups,
native3924/platform46,84 natural calendar transitions/168 frames,24 completed
frames с0 pixel differences и40 diagnostic captures прошли. Frozen75 test
files/88 дополнительных inputs повторно совпали; appDD41/source96A/ELFB4,
QEMU30F/source0d27a7ca98 прежние. Publisher и verifier6 pass;32 positive artifacts
сохранены. Entry comments161, marked functions55, DIRAM80 722; app1 176 880,
free359 120. Старые failed/negative runs сохранены, physical/H03/H10 не объявлены.

Этот passing checkpoint предшествует HTTP deadline и DEBUG: он не доказывает
прохождение нового кандидата EF66/81CF/8FCE или debug11DD/DBE5. Audit сохранён
вlink-timing-integrated-full-inputs-20261017.json. Новые функции/сборки находятся
в отдельных ветках; после публикации текущего результата их можно интегрировать
и готовить один новый общий запуск с body_http/concurrency_http.

### 2026-10-17 — DEBUG-участок сохранён в рабочих ветках

FW cf220f21 /codex/small-tv-debug-logging отправлен вместе с обоими архивами и
scope JSON/MD; включает body/concurrency/runtime merge8fecd9e1. QEMU04443f07dc
отправлен вcodex/small-tv-wifi-link. OFF/ON/OFF builds иlogging20/run, packet11
в3 состояниях, modules иlegacyboot pass. Normalpixels совпали; debugC3modular
host-timed scroller/AP phase другая — pixel equivalence не заявлена. Короткий
quietobserver/H09/body прошли; ВМ/CUA tabs отсутствуют. Root passing61d1f8ee и
QEMUmain0d27/installed30F прежние. Передquiet full требуется исправить старую
INFO-зависимую consoleboot oracle, затем интеграция и свежий frozen full.

### 2026-10-17 — общий deadline HTTP-тела вместо блокировки других клиентов

В отдельной .worktree/small-tv-http-body-deadline воспроизведён дефект DD41:
неполный JSON удерживает второй GET24.69s, trickle27.61s, oversized9.70s.
В factory0x4200d7f0 на0x4200d808 один recv, нашего retry-loop нет. SDK pending
data +3timeouts +remaining-body purge объясняют около25s. Новый request_body.c
имеет5s absolute deadline, per-read remaining timeout с ceil1ms, SHUT_RD при
отказе и восстановление original timeout при успехе; FIXED_RECONSTRUCTION.

Новый app3C599124/source1741EA14/ELF342C0127,1 177 216bytes/free358 784,
58 production inputs, сохранён в branch firmware/development. Final identical
body QEMU test наold:3 failures, наnew:4pass; задержки4.695327/4.703467/.204119s.
Host3950/platform46/frontend/integrity/timezone/aggregation reduced pass;
SDK photo HTTP21pass; consumer guards15pass. ASM/manifest и scoped report/doc
сохранены. Добавлен mandatory body_http в следующий suite/publisher/verifier.
Это не общий full pass нового app. Main DD41/75+88 frozen inputs текущего11075
не менялись; он проходит отдельную проверку на QEMU30F. Merge/build/full нового
кандидата выполнять после terminal/сохранения этого прогона, не подменяя identities.

ASM body-reader audit получил явный eol=lf в Small_TV/.gitattributes. Проверка
git cat-file --filters даёт тот же SHA, что manifest; checkout не меняет
fingerprinted bytes. Production sources, ELF/app и scoped runtime results прежние.

### 2026-10-17 — реальная конкурентная работа в QEMU

На прежних app3C599124/source1741EA14/ELF342C0127 прошёл standalone H09 scenario:
34 checks,16 paired batches,68 sequential requests. Одновременные start upload
дают ровно200/400; exact retries200/200, exact/conflicting200/400; scan+GET,
независимые настройки, chunk+GET, held weather и renderer resume проходят.
Максимальная пара2.847167guest s (scan/GET), single.306982s, порог6 прежний.
После двух restart ACK наблюдался один warm boot; настройки/готовое фото сохранились,
частичное скрыто. Cold boot — отдельная новая ВМ с тем же raw backing; новое
upload после прерывания проходит. Все protected regions/первые3photos прежние.

Первый preflight invalid: double-stop cleanup error и слабая renderer resume
oracle. Исправленный новый run сравнивает cache передfinish/после:20:00:21→29;
inputs98 unchanged, ВМ закрыты, no panic. Multipart formatter выделен отдельно,
4 protocol tests pass. Полная H09/24h H10/physical не заявлены; source/C иproduction
archive не менялись. Main frozen full11075 продолжает calendar на прежнейDD41.

H09-сценарий включён в следующий обязательный qemu.concurrency_http. Producer,
publisher и verifier требуют все 34 условия/16 пар/68 запросов и точные identities.
20 consumer mutations на captured успешном report отвергнуты, включая missing
interleaving, вторую upload session, конфликтующий retry, stale renderer,
неработающий weather worker, повреждение flash и подмену app/ELF/QEMU/test/formatter.
Это проверка потребителей исторического standalone результата; его начальные
input hashes не переписывались, C/ELF/BIN не менялись, нового full pass нет.

### 2026-10-17 — отдельный runtime observer памяти

В codex/small-tv-runtime-observer подготовлены отдельные модули DWARF/list/stack
decoder, ROM counter crosscheck и workload driver. Production appDD41/source96A/
ELFB4 не менялись. ВМ закрыты в finally; GDB только read/hardware breakpoints,
присваивания PC/RAM нет. 15 parser и4 exact-ROM tests pass, включая негативные
ABI/list controls. Module import, unused natural API deadline и HTTP name shadow
сохранены как harness errors, а не firmware defects.

Итог нового40-cycle workload:121.076406 guest s,41 snapshots всех12tasks,
10 JPEG uploads,240 recorded HTTP +80 concurrent GET, max.405659s, no panic,
inputs unchanged. Heap sampled87 668→86 268, min sampled78 264; SDK сумма
per-heap minima47 028. Lowest stack watermark480 у settings. ROM counter
crosschecks164. Короткий runtime preflight не доказывает leak-free/24h H10,
factory memory equivalence или physical/ISR stack. ВМ закрыта; осталась только
ВМ общего full11075. Его frozen75+88 inputs не затронуты. Отчёт и scope сохранены
в runtime-memory-*; standalone tests пока не включены в текущий full gate.

### 2026-10-17 — наблюдатель подготовлен к длительному запуску

Runtime_state разворачивает low32 microsecond counter и пишет последовательный
JSONL; summary ограничен первым/последними32 samples и агрегатами. Новый runner
поддерживает cycles либо duration до7дней, interval<=60s, короткие виртуальные
AP outages с реальными guest disconnect/reconnect и HTTP recovery. Проверки
переполнений/journal6 иdecoder16 pass. Сравнение старого/нового decoder на одной
SRAM даёт одинаковые heap/tasks при45→20 memory reads.

Первая реальная проба4096-byte scan дала RSP E22 до ready snapshot: transport
preflight invalid, не firmware defect. Исправлено на1024bytes, добавлен test
packet limit. Новый4-cycle run с2×1s outages прошёл за15.689122guest s:
5snapshots/32HTTP/35journal events, по1guestdisconnect+reconnect наотключение.
Отдельный duration8s завершился после8.135430s:3cycles/4samples/27HTTP/28events.
Журналы/digests иinputs unchanged/no panic, ВМ закрыты. AppDD41/96A/B4/QEMU30F
прежние; source/C/BIN не менялись. Short validation сохранена вruntime-duration-*
JSON, это НЕ24h/H10/physical и не переименование прежнего40-cycle proof9adf.

### 2026-10-17 — DEBUG в прошивке и QEMU

По уточнению пользователя оба проекта получили build-time switch, по умолчанию
OFF. FW CMake DEBUG=ON/OFF, PS -DebugLogging; SDK/app/bootloader level2/4, отдельный
debug archive, manifest boolean и LF metadata. В QEMU esp_debug исключает packet
formatter/RX-MMIO/DNS-NTP diagnostics, QOM capability read-only; сырой frame dump
выключен. QEMU04443f07dc отправлен в feature branch, canonical main30F не менялся.

Полные OFF/ON/OFF rebuilds в одних каталогах прошли. Четыре logging runs по20
проверок actualROM/Wi-Fi/SNTP/HTTP/themes/LCD прошли; OFF0 I/D/V/3W, ON79I/3883D/3W.
AppEF66/ELF8FCE и debug11DD/DBE5 сохранены, source81CF/59inputs. QEMU E210/9994/76A
прошли11 packet cases каждый; modules иCYD/C3 boot gates pass. Normal pixel hashes
прежние, debugC3modular host-timed scroller/AP phase другой — equality не заявлена.
First/final OFF PE sections совпали кроме export timestamp. Ошибки preflight
oracles/Windows cleanup/Meson define сохранены отдельно, не firmware defects.

Observer schema3 читает настоящий atomic connected flag вместо debugUART;4cycles,
16.475576s/5samples/32HTTP/2outages, minheap87576/minstack480. Parser16/state6 и
build config reuse/CRLF/idempotence test pass. Final quiet EF66 H09:34checks/16pairs/
68requests; body4cases pass, secondGET4.494401/4.539967/.133139s. AllVMs closed.
Scope JSON/документ сохранены. Root full75+88 inputs повторно unchanged; это
отдельные результаты, не общий pass нового кандидата/24h. Перед quiet full нужно
адаптировать старый boot-console gate, который зависит от INFO, затем интегрировать
ветки и запускать один новый общий набор сbody_http/concurrency_http.

### 2026-10-17 — boot/reset без зависимости от логов

Boot helper адаптирован к quiet firmware: actual connected/AP/DHCP/SNTP objects
из matched ELF вместо INFO. ELF32 converter вынесен в esp_elf.py; ABI/RAM/bounds,
BIN ELF SHA и read-only observation проверены12 unit cases. QEMU хранит3 numeric
NTP response fields (24bytes) независимо от диагностики; QMP read-only getter,
drop/malformed/reset/counter tests. По12 DMA/network tests OFF/ON и modules pass.

Все6 actual boot/reset flows прошли: ordinary EF66/8FCE clock OFF/ON QEMU,
factory clock OFF/ON, ordinary offline AP и debug11DD/DBE5. Source81CF прежний.
QEMU OFF0B3F6F69 / ONF3D7B024. UTC проверяется до/после reset с прежним <1s;
нужен новый NTP reply. Ошибочные host-wall oracle и RTC-only reset oracle
сохранены отдельно. По SDK source и factory assembly0x420b288c/0x403802da выявлены
две signed64 corrections; правильный observer читает их и UNIT0 без guest writes.
Publisher/verifier пересчитывают UTC из чисел;29 actual consumer rejection controls
pass. Helper/unit hashes включены в полный suite и15 producers. См. quiet-boot-state-*
MD/JSON. Старый общий DD41 pass остаётся историческим; нового full/24h пока нет.

### 2026-10-17 — интеграция проверенных веток

Main merge5e41962d объединяет ordinary/debug firmware, request-body deadline,
H09/runtime observer и quiet boot checks. Конфликт журнала разрешён сохранением
обеих историй. QEMU main FF доadb66701b3; canonical diagnostic build запущен,
новый full ещё не начат. OFF/ON legacy boot CYD/C3 OLED и modules прошли на
0B3F/F3D7; Xtensa unchanged. Все scoped результаты остаются с исходными hashes.

В root перенесены exact tested8FCE ELF/EF66 BIN/map;59 source/generated inputs
и BIN ELF-header binding совпали. Старые B4/DD41/map и newline-only sdkconfig
сохранены отдельно; CMake cache не переносился. Main host reduced pass:
3950 C assertions/platform46/frontend/integrity6/timezone9/aggregation14;
DEBUG reused-build/CRLF/idempotence unit pass. Артефакт promotion JSON сохранён.
Следующий full должен использовать stable installed diagnostic QEMU и заранее
замороженные test/helper/production inputs. Предыдущий DD41 full не заменяет его.

### 2026-10-17 — canonical QEMU готов; browser initial setup

Canonical main adb66701b3 собран с esp_debug=true, установлен A74F3324; marker
commit/mode проверены. На этом executable12 packet cases иmodules pass. Main
обоих репозиториев отправлен. Native ordinary EF66/8FCE/source81CF прежние,
production59 inputs совпадают; новый immutable full ещё не объявляется прошедшим.

Browser initial setup на real quiet firmware:19 conditions pass, настоящий scan,
неверный short пароль дал alert/error без записи credentials или restart.
Valid open yoRadio-QEMU сохранён через форму; один restart, modeSTA и реальная
STA web page/настройки загрузились, JS errors в новой station вкладке отсутствуют.
SDK connected/SNTP/AP-disabled/DHCP192.168.43.15 и NTP reply прочитаны отдельно,
все executable/media/source regions unchanged. ВМ закрыта. Первая вкладка после
submit не отвечала CDP; новая отобразила интерфейс. Station tab закрыта, старую
setup error page close блокирует browser URL policy; temporary auto cleanup.
Screenshot показан tool inline, архивного browser PNG нет. JSON scope сохранён;
full H03/factory browser/physical/24h не объявлены. Отдельно отмечена заводская
Math.abs RSSI dBm sign ошибка в HTML; исправить после текущего frozen full.

### 2026-10-17 — новый frozen full запущен

Debug-integrated-full-20261017 /handle67941 начал полный host/machine/QEMU набор
на ordinary EF66/81CF/8FCE и canonical diagnostic QEMU A74/sourceadb66701b3.
Frozen92 test sources и92 дополнительных inputs; после старта все184 fingerprints
повторно совпали. Pre-run HEADdef6914d. Host groups pass, machine пока выполняется;
общего результата ещё нет. Audit сохраняет только input identities, status running.
Дополнительный installed-A74 CYD/C3 boot handle85263 тоже пока не объявлен pass.
Ни BIN/ELF, ни production/test/helper inputs при этой записи не менялись.

### 2026-10-17 — signed RSSI labels в отдельной ветке

В codex/small-tv-rssi-label устранён factory Math.abs bug в HTML по flash offsets
0x26edc/0x2963b. Форматтер вынесен в wifi_network.js и встроен exporter в обе
страницы; option values/selection сохранены. Negative controls8fail наold,
8pass наnew: signed/zero/missing/malformed/literalSSID/nonfinite. Повторный export
идемпотентен, photo page прежняя. Реальный browser на SDK/QEMU показал
yoRadio-QEMU(-24dBm), QEMU-2(-28dBm), QEMU-3(-40dBm);0JS errors. ВМ/tabs закрыты.

Ordinary D78A7639/F5F39276 иdebug5E468EB3/8FAE6071 собраны, sourceF8A3A6A8;
среди59inputs изменёнтолько generated/web_pages.c. Size ordinary1 169 888,
free366 112. Оба development archives сохранены. Host3950/platform46/frontend/
integrity6/timezone9/aggregation14 pass. Первые DOM mocks исправлены (getter,
изоляция посторонних GET); early artifact run без native coverage сохранёнfailed.

Debug fixed8host reset smoke не дождался SNTP, connectedtrue/notifyfalse/NTPcount1
на6.46guest s. Source подтверждает randomized startup LWIP_RAND()%5000. Oldfailed
сохранён, отдельный probe успешен. В QEMUfeature2a593f8d00 state-based readiness
с15guest/60host deadline и прежнимUTC<1s:19units/3actual guests pass. Ordinary
5.688host/3.913510guest;debug8.250/6.415086;factory9.031/7.767985. Consumer29 checks
дляобоих native pass. SDK delay иQEMUdevicecode не менялись. Scoped MD/JSON сохранены.
Root full67941 наEF66/81CF/8FCE/A74 продолжает исполняться,184 frozen fingerprints
повторно unchanged. До terminal/save этогоfull ветки не интегрировать.

### 2026-10-17 — отдельный UART guard длительного теста

Приаудите H10 выяснено: clean_uart проверяет panic tokens, но не silent resets;
radio time сохраняется приreset, поэтому один elapsed24h не доказываетнепрерывный
app uptime. Добавлен отдельный runtime_run_guard.py: весьUART, ROM banner+Build,
count1,panic/watchdog,truncation.7unitcases pass,включаяresetпосреди незавершённой
строки иliteral embedded marker. Guardread-only, отдельныйJSON,не меняет30 H10inputs.
Первыйattach QMPtimeout: workloadдержитsoleconnection. Присоединениеисправлено
наfile-only guard, никакогоновогосоединения; этотpreflightнеfirmwaredefect.
Guard99431 работаетрядом с H10 31890 наD78A/F5F3/frozenA74+FF0819. Guardиmemory
trend обязательны дляприёмки H10; ранние samples/основнойpassed не замена.

### 2026-10-17 — независимый анализ полного runtime журнала

В отдельном analysis worktree добавлены три инструмента: runtime_evidence
проверяет полный журнал и identities, runtime_trend сравнивает heap в равных
фазах, analyze_runtime формирует отдельное заключение. Анализ файлов не требует
QMP, не останавливает гостя и не меняет входы workload. Сверяются каждый cycle,
HTTP/upload/outage, арифметика heap, ROM crosscheck, app/ELF binding, elapsed,
wraps, начальный checkpoint и terminal UART guard. Pending и короткие прогоны
не получают H10 pass. Старый preflight без guard читается в своём ограниченном
объёме, но не повышается до приёмки 24 часов.

Trend: прогрев 1 час; полные часовые окна; НОК(20, outage cadence) фаз, то есть
60 для H10 с отключением каждые 60 циклов. Неизменный SDK minimum не скрывает
убывающий free heap. Устойчивое снижение или сохранённая потеря выше начального
разброса требуют дальнейшего исследования. Результат ограничен разрешением
замеров; физическая плата, ISR peaks и непрерывный календарь не подтверждаются.

20 unit tests проходят: настоящая сериализация RuntimeJournal, фальсифицированные
идентификаторы/агрегаты/время, недостающий upload chunk, ложный reconnect,
переставленные snapshots, reset, усечённый JSONL, live prefix, phase jitter,
утечка и retained step, synthetic 24h. Первый запуск не смог создать nested
files в redirected sandbox TEMP (WinError5); повтор с TEMP внутри .build прошёл.
Реальный короткий preflight и префикс H10 успешно прочитаны, все 30 source SHA
совпали. Анализ preflight не объявлен 24h pass. H10 и полный frozen regression
продолжаются; входы выполняющихся процессов не изменены.

### 2026-10-17 — коллизия настоящего SSID manual

В отдельном worktree исправлен factory setup HTML flash offset 0x026edc:
условие ssid==manual принимало реальную сеть за команду ручного ввода. Новый
isManualWifiSelection в общем Wi-Fi module помечен FIXED_FACTORY и читает
метку selected option. Два fallback option помечаются exporter; передача
SSID/password и отмена prompt сохранены. Все 15 actual scan/submit callback
cases проходят. Negative control на заводском и прежнем native HTML показывает
лишний prompt именно для настоящего SSID manual. Первый mock run имел ошибку
фикстуры: password node создавался лениво, но тест обращался к нему напрямую.
После исправления фикстуры 14 случаев old pass, один old fail, все new pass.

Ordinary и debug production builds успешно сохранены. App A5439306/8485A233 и
D1E7660D/EB4FDFB5; source721E26BD/59 inputs, меняется только generated/web_pages.c.
SDK config прежний. Ordinary 1 169 888 байт/free366112; debug 1 230 384 байта.
Host reduced: native3950/platform46/frontend15 Wi-Fi cases/integrity6/timezone9/
aggregation14 проходят. Main frozen full не изменён, все184 identities совпали.

Browser на отдельной QEMU VM с профилем station_ssid=manual: выбран настоящий
option manual(-16dBm), manualEntry отсутствует. Submit приводит к success alert,
configuration complete и после штатного reset к STA странице с загруженными
controls. Matched-ELF SDK connected=true/AP=false/IP192.168.43.15/time_synced=true,
UTC difference0.214516163. Два ROM boots, panic нет, source images unchanged,
VM остановлена. Снимки сохранены; setup complete PNG добавлен к scoped proof.
STA tab закрыта; setup tab после исчезновения AP дал CDP timeout, затем error
page URL policy блокирует close. Он не помечен handoff/deliverable и оставлен
для штатной automatic cleanup. Это не firmware defect и не полный H03/H10.
Основной full67941 и длительный H10 31890/guard99431 продолжаются на своих
прежних images; новый app не объявлен прошедшим эти прогоны.

### 2026-10-17 — RSSI и reset readiness follow-up, запуск H10

Canonical A74 CYD/C3 legacy85263 завершёнpass. Root full67941 остаётсяжив,
прошёлhost/machine/profile, boot/reset, startup/weatherwait, advanced/body/H09,
photo family, реальную Wi-Fi setup/persistence, weather иfields; идётSNTP/time.
184 frozen inputs повторноunchanged. Полный результат пока отсутствует.

Покаmain frozen, в .worktree/small-tv-rssi-label подготовлен иотправлен56df5baf:
factory Math.abs RSSI bug исправлен общим JSformatter,8oldfail/newpass, actualbrowser
-24/-28/-40dBm/SSIDvalues/selection/errors0, host reduced pass. OrdinaryD78A/F5F3,
debug5E46/8FAE, sourceF8A3; changedonly generated/web_pages.c из59inputs. QEMUfeature
2a593f8d00 отправленотдельно: waitactualNTPreply/SDKUTC/flags послеreset вместо8host,
limits15guest/60host,UTC<1s;19unit/3actualguest/29consumer pernative pass. Reset
ordinary5.688host/3.913510guest;debug8.250/6.415086;factory9.031/7.767985.
Failed fixed8wait иprobe сохранены; SDK rand()%5000 подтверждён. ВМ/tabs закрыты.
Новые ветки main текущего full не меняют; послеterminal сохранитьpass/fail иинтегрировать.

H10 подготовлен наD78A/F5F3 с отдельной immutable копией A74+helperFF0819; canonical
QEMUбольше не его изменяемыйinput. Preflight8cycles/27.160648guest/9snapshots/64HTTP/
2outages/67events прошёл,30inputs+JSONLSHAverified,nopanic. Heap min87036,SDKmin55352,
stackmin480. Outer launcher после Python ошибся сexit\\0; raw successful workload
проверен, эта ошибочная попытка не переименована. Длительный controllerliteral.ps1.
H10 handle31890 начал86400guest seconds,interval15,outageevery60cycles/1second.
Приcheckpoint ужеесть completed cycles; этоrunning, НЕ24hpass/leak-free. Source
RSSIworktree и frozenbundle сохранять доterminal; после24h анализировать полныйjournal.

Независимый read-only UART guard99431 присоединён кH10;7unitcases pass. Source
сохранёнв RSSIbranch2e85ab8d. ОнсчитаетROM banner+Build,count1,panic/watchdog и
потерюистории; silentreset можетскрытьутечку, radio timeне сбрасывается. Guardне
открываетвторойQMP (workloadдержитsoleconnection); исходныйattachtimeout сохранёнкак
harness attempt. H10start JSON содержитguard SHA/commit/handle. Нужныterminalguard
ианализjournal; это не24hpass. Оба набора frozeninputs повторно unchanged.

### 2026-10-17 — сохранены отдельные runtime-analysis и manual-SSID ветки

Отправлен e0d276ac в codex/small-tv-runtime-analysis (worktree runtime-observer):
полный JSONL audit, равные theme/GIF/upload/outage фазы, 20 unit tests. В анализ
не подмешивается QMP или изменение workload. Реальные preflight и pending H10
успешно читаются, все30 source SHA совпадают; короткий запуск не стал H10 pass.

Отправлен c72b4b45 в codex/small-tv-manual-ssid. Factory setup HTML ошибочно
использовал реальный SSID manual как команду. Helper с FIXED_FACTORY читает метку
option, exporter помечает лишь служебные fallback варианты. 15 callback cases
pass; factory и прежний native воспроизводят лишний prompt. Host3950/platform46/
frontend/integrity6/timezone9/aggregation14 pass. Ordinary A5439306/8485A233,
debug D1E7660D/EB4FDFB5 сохранены в development архивах этой ветки; source721E26BD,
из59 inputs отличается лишь generated/web_pages.c, SDK config прежний.

Real browser/QEMU manual network: selected value manual без ручной метки,
success и complete экран, один restart, STA UI с загруженными controls.
Matched ELF SDK connected=true/AP=false/IP192.168.43.15/SNTP=true,
UTC difference0.214516163. Два ROM boots, panic нет, source images unchanged;
VM закрыта, STA tab закрыта. Старый setup tab после исчезновения AP не отвечает
CDP, затем generated error page запрещает close по browser URL policy.
Не помечен handoff/deliverable; штатная очистка конца turn. Scoped MD/JSON/PNG
находятся в ветке manual-ssid; её полный machine/QEMU/H10 ещё не выполнен.

Основной full67941 остаётся на EF66/81CF/8FCE/A74 и прежнем main helper BA400.
Все184 frozen inputs повторно unchanged. Factory42 calendar transitions pass,
выполняется native classic. H10 31890 на D78A/F5F3/frozenA74+FF0819 продолжается;
guard99431 жив. Последний независимый audit:99cycles/1632.639162guest seconds,
30inputs verified, ROMboot1, panic нет, status pending. Пока недостаточно данных
для steady trend. Ветки и installed helper не интегрировать до terminal/publish
основного full; H10 input worktree и frozen bundle сохранять до его завершения.

### 2026-10-17 — полный quiet firmware gate завершён, H10 прерван

Новая авторитетная проверка: старые tool handles больше не доступны. Full report
имеет passed=true/finished UTC17:04:52 и все19 автоматических groups passed.
Проверены все184 frozen fingerprints; publish-report и verify_artifacts прошли.
Опубликованы EF66/81CF/8FCE/A74 результаты:84 calendar transitions/168 completed
frames,24 strict scene frames/pixel diff0, native3950/platform46,162 entry
comments/56markers,DIRAM80540,app1169888/free366112. Это не полный H03/H10/hardware
и не full следующих RSSI/manual-SSID candidates. Теперь допустима интеграция.

H10 не завершился: VM PID13544 отсутствует, WMI не обнаружил runtime/guard
процессов; raw report без terminal journal/inputs_unchanged. Последние files
записаны около UTC17:10, внешний audit около17:27; причина остановки неизвестна.
Independent prefix audit:187 complete cycles,3096.125371guest s,188snapshots,
1504HTTP,3real outages,4pending events,30source SHA verified,ROMboot1/no panic.
Незавершённый elapsed нельзя засчитать как24h. Numeric journal и UART сохранены
в детерминированные gzip с SHA; отдельный interruption JSON не меняет raw report.
Guard status running был устаревшим. Следующий запуск должен проверять жизнь
workload и уметь пережить границу tool session либо закончиться в активном turn.

### 2026-10-17 — supervisor замечает исчезновение workload или guard

Добавлен Windows runtime_supervisor.ps1 с точными .NET Process handles и
структурированными arguments без shell interpolation. Контроллер живёт отдельно
от foreground exec, запускается скрытым Start-Process. Успешный worker без
terminal footer не принимается; потеря guard во время workload тоже failed.
Ошибочный запуск останавливает только свои children и VM через identity-checking
helper. Status/child logs отдельные, raw workload report сохраняется как есть.
Наличие running JSON не заменяет внешнюю проверку PID/start time/command line.

Source8c91874b: реальный preflight4 cycles/2outages прошёл; worker/guard exits0,
source hashes unchanged. Независимый audit проверил все30 inputs и полный журнал,
короткий scope не стал H10 pass. Отдельно остановлен только проверенный worker
PID25988: supervisor failed/exit -1/no terminal footer, VM cleanup0. Затем отдельно
остановлен guard33428: supervisor failed с guard error и закрыл worker/VM.
Все созданные VM и дочерние процессы этих случаев отсутствуют по process audit.
Сбой специально внедрён, не является firmware defect. Внешний boundary survival
пока не проверен. Следующий длительный запуск должен подтвердить его отдельно.
До него также нужно закрыть пробел weather workload: одни POST /updateCity и
heap snapshots ещё не доказывают повторный фактический разбор ответов сервиса.

### 2026-10-17 — в runtime workload подтверждён разбор погодных ответов

После supervisor найден scope gap: POST updateCity и heap samples не доказывали
фактическую обработку ответа сервиса. Новый runtime_weather.py читает 13 байт
числовых полей по matched ELF/DWARF: request_state, valid, generation, humidity.
Cache читается лишь при state0: weather_task ставит RUNNING перед invalidation/
fetch/copy и снимает после публикации под mutex. Active/PENDING samples содержат
только состояние worker, чтобы не трактовать частично скопированный struct как
результат. Строки/URL/keys/buffers не читаются и guest functions не вызываются.

Schema4 сохраняет эти observations, независимый auditor пересчитывает поколения
и сверяет reports с JSONL. Fixture отдельно считает настоящие synthetic200
responses/location/key. H10 требует новые parsed generations в пределах гостевого
часа от начала/конца и между обновлениями; старый валидный кеш не заменяет
24h weather activity. Schema3 остаётся читаемым в старом ограниченном объёме.
8observer+24analysis unit tests pass: ABI/bounds, busy cache, bad flags/humidity,
zero/regressing generation, repeated cache, missing weather, forged aggregates,
legacy day и два ранних refresh с последующей стагнацией на сутки.

Реальный preflight A543/8485/source721E, canonical QEMU A74/6B7F helper:8cycles,
27.549604guest s,9snapshots/9 valid generations,9synthetic200, maxgap5.009813.
31inputs unchanged, no error/cleanup error, VM отсутствует по PID audit. Полный
UART guard запускался после workload: это posthoc no-reset/panic check, а не
concurrent supervision данного case. Первая команда guard ошибочно получила
QEMU root вместо tools и ModuleNotFoundError; повтор с правильным tools path
прошёл. Новый analyzer проверил полный schema4 JSONL/ROM counters и старый
прерванный schema3 stream; короткий запуск и старый префикс не стали H10 pass.

В main уже merged91aa/8ab, точные59 production inputs совпали с manual-SSID
archive; ELF/BIN/map перенесены без CMake cache, старые backup сохранены.
QEMU main2a593f8d00 pushed; actual helper raw6B7F — CRLF представление FF0819,
normalized equality проверена.19 canonical units pass, compiledA74 не менялся.
Следующие full/H10 должны использовать новые source identities после integration.

### 2026-10-17 — восстановлена заводская цель post-setup navigation

Разобран повторный browser error после настройки: factory HTML offsets0x026edc/
0x02963b назначает timer3000ms к about:blank; local exporter подменял target на/.
После успешной configure AP выключается, и наш reload старого AP URL создавал
недоступную страницу. Прежняя классификация как исключительно tooling была
неполной. Удалена подмена, entry comments двух completion handlers помечены
FIXED_RECONSTRUCTION. Сохранён factory timer и остальные fixes:readResponse,
RSSI sign/manualSSID. Photo page byte-identical. Повторный export идентичен.

Два actual callback/timer negative controls fail на прежних страницах, проходят
на factory source; новый generated frontend проходит18 случаев, включая failed
save без timer/navigation. Ordinary922DA963/71DED1E1 иdebugC37B7B5E/BA060CE6
собраны/архивированы, source9D2367EB/59inputs: толькоgenerated/web_pages.c меняется,
SDKconfig прежний. Ordinary1169888/free366112;debug1230736bytes. Старый build
observer ELF/BIN/map отдельно backup до сборки. Host native3950/platform46/
frontend18/integrity6/timezone9/aggregation14 проходят. Controller1739 terminal0,
host25992 terminal0. Новый full machine/QEMU и H10 ещё не выполнялись.

Real browser/QEMU новогоordinary: scan/selectedyoRadio-QEMU, success alert,
dialog.dismiss через API, complete screenshot, autoURLabout:blank, close иtabs0.
Matched ELF SDK connected=true/AP=false/IP192.168.43.15/SNTP=true,UTCerr0.471598864,
STA HTTP ready,ROMboots2,no panic,sourceimagesunchanged,VMstopped. Первая probe
ошибочно использовала clock-only readiness с hardcoded10.0.2.15: timeout15guest s.
Это ошибка probe контекста, не firmware failure; direct read правильной setup
подсети прошёл. Screenshot и UI/guest observation сохранены в scoped proof.

До следующего final freeze проверить потенциальную URI query-suffix регрессию:
handlers SDK могут выбираться по path, а native dispatch использует strcmp всей
req->uri. Гипотеза ещё не подтверждена; нужны actual factory/native запросы.
H10 повторно пока не запущен: сначала закрепить новый кандидат и isolated
worktree/bundle, затем supervisor/schema4 preflight и24h. Не переносить старые
зелёные результаты на другой app/source или на прерванный187-cycle workload.

### 2026-10-17 — canonical main содержит redirect candidate; следующий transport probe

Main fast-forward до10557472, source9D2367EB. Root59 production inputs после
prepare_resources точно совпали с архивом. Перенесены ordinary922DA963/71DED1E1
BIN/ELF/map без CMake cache; прежние A543 artifacts сохранены в
.build/small-tv-parity/pre-setup-redirect-main-build-20261017. DebugC37B7B5E/BA060CE6
тоже в tracked development. Новые scoped проверки не заменяют full старогоEF66.
Все текущие реальные preflight/browser VM остановлены, browser tabs0. Новых
full/H10 пока нет. Первый старый H10 остаётся documented interrupted.

Следующий transport audit: SDK использует UF_PATH при выборе handler, но полный
req->uri сохраняетquery; наш dispatch strcmp может расходиться с factory отдельными
callbacks. Проверить на живых factory/native GET, POST и HTML pages сquerysuffix.
Не обрезать req->uri глобально: photo download зависит от query. Также проверить
absolute-form URI, поскольку SDK выделяет UF_PATH по offset. Это ещё гипотеза,
а не доказанная регрессия. После проверки/исправления подготовить окончательный
кандидат и новый frozen full плюс isolated24h H10 с supervisor/schema4 weather.

### 2026-10-17 — factory-compatible HTTP request-target dispatch

Actual factory/native probe подтвердил гипотезу: factory GET getclocktype,
getgifvalue,getsettings с query дают200 и прежнее тело;922 native давала400.
Factory /?probe=1 и /photo?probe=1 возвращают соответствующую страницу; native
ошибочно возвращала settings. Factory POST setgifvalue?probe=1 сохраняет2,
native отклоняла400 и оставляла1. Absolute HTTP request targets имеют тот же
дефект. Photo metadata с настоящим query работали в обоих вариантах.

Сверены factory registry GET0x4200dfdc/POST0x4200d8b8/photo0x4200d54c,
decompilation и полный getclocktype RISC-V body/epilogue0x4200dfdc..0x4200e074:
callback выбирает символ из сохранённой темы и передаёт req в response APIs,
URI заново не разбирает. ESP-IDF httpd_uri.c:314 использует UF_PATH/off/len,
а затем присваивает req->user_ctx из скопированного registration descriptor.
Shared native callbacks теперь используют canonical static path в user_ctx.
Это сохраняет SDK exact/case-sensitive matching и весь req->uri для photo query,
не добавляет allocation/parser/буфер на каждый запрос. Внесены entry comments
FIXED_RECONSTRUCTION; код остаётся в соответствующих web-модулях.

Native adapter теперь копирует descriptor как SDK и передаёт context. Несколько
старых прямых вызовов заменены dispatch, чтобы тестировать реальную регистрацию.
В отдельном http_targets.inc проверены все GET в AP/connected mode,16 settings
POST с теми же результатами/actions, negative prefix/case/encoded delimiter,
query с похожим route в значении. Полный photo start/chunk/finish/download
повторяется в origin/absolute forms с query и без него. До production fix новая
проверка падает на реальном GET status400, после —5531 checks/40 routes pass.
Первый test-only context assertion разыменовал NULL на старом registration;
убран как зависимость теста от реализации, отрицательный контроль повторён.

Ordinary8304F1A4/ELF62E040B5 иdebugA8C337BC/ELF86B7275D собраны и сохранены в
development archives; sourceBE5802D6/59inputs. App1169904/free366096bytes,
debug1230752bytes; SDK/app/bootloader levels2/4. DEBUG config reuse OFF/ON/OFF
unit, host native5531/platform46/frontend18/integrity6/timezone9/aggregation14
pass. Первичная sandbox toolchain activation дала Windows DLL relocation;
штатный unsandboxed build прошёл, SDK не переустанавливался. Новый debug BIN
пока проверен сборкой/configuration, actual URI ВМ использует ordinary.

Новый uri_targets_qemu.py включает реальные factory36/native124 conditions:
одинаковые ответы на семь GET во всех четырёх forms, четыре POST/readback,
четыре полных native JPEG upload/download cycles с byte equality.160 HTTP
requests, no panic, immutable inputs unchanged; owned VM PID19552/16896
остановлены и отсутствуют при внешнем OS audit. Test добавлен в обязательный
qemu_suite и publisher. Scoped JSON сохраняет before/after и identities; старый
полный EF66 checkpoint не переименован. Новый full/H10 ещё не начаты.

### 2026-10-17 — новый full и изолированный supervised H10 кандидата8304

0fe92f18 fast-forward в main и pushed вместе с feature branch; origin/main
совпадает, QEMU main2a593f8d clean. Canonical prepare_resources подтвердил59
BE5802D6 inputs, exact8304F1A4/ELF62E040B5 BIN/ELF/map перенесены из build
worktree без CMake cache. Прежняя922 сохранена в pre-uri-dispatch-main backup.

Fresh full controller90679 запущен18:21:51UTC: report directory
.build/small-tv-functional/uri-integrated-full-20261017. Freeze99test files и
93extra inputs (включая wifi_network.js),192 fingerprints unchanged после старта.
OS pwsh9896 с точной командой подтверждён, старый full не переименовывается.
На момент записи full незавершён; текущие machine oracle диагностические pixel
differences сами по себе не являются провалом: штатная verification passed.

Existing clean manual-SSID worktree переведён на новую codex/small-tv-h10-uri
из main0fe92f18. Old A543 build сохранён отдельно. В него перенесены exact new
ELF/BIN/map, resources/source manifest совпали. QEMU bundle11files скопирован
побайтово: executableA74F3324, compileadb66701b3, canonical helper6B7FF996,
source main2a593f8d. Изолированные файлы не менять до окончания нагрузки.

Combined8cycle preflight прошёл на этой exact паре:33.975877guest s,9quiescent
valid snapshots и9разных weather generations,maxfreshgap5.419394s,31inputs
unchanged. Workload/guard exit0, supervisor complete/sources unchanged. File
auditor заново проверил8циклов,weather,journal иindependent terminal guard.
Его exit1/status completed_scope_requires_review ожидаем: короткий запуск не
проходит24h duration/steady windows/start-record checks и не объявляется H10.
Scoped JSON и reproducible gzip полного JSONL/UART сохранены в parity/.

H10 started18:23:07UTC через Start-Process Hidden;86400guest seconds,interval15,
outageevery60/1guest s. Immutable start record создан18:24:08UTC после проверки
реальных ролей/времён запуска: supervisor30128,worker2252,guard18740,VM26440.
State в isolated .build/uri-runtime-24h-20261017. File-only diagnostic auditor:
pending,31inputs verified,start_record_matches=true. Наличие running файла не
доказывает process survival через конец assistant turn; следующий turn должен
повторно проверить OS identities и footer. Пока нет24h/trend acceptance. Это
новый запуск, прежний187-cycle interrupted H10 остаётся отдельным evidence.

### 2026-10-17 — H10 пережил assistant turn; helper для дальнейшей сверки готов

В начале следующего goal turn проверены OS PID/creation times/commands всех
четырёх H10 roles:30128/2252/18740/26440 совпали с initial record; workload
продолжает циклы и supervisor обновляет heartbeat. Это настоящая process
survival через завершение предыдущего сообщения, а не stale running JSON.
Повторный exact-tick audit сохранён в uri-runtime-process-survival-20261017.json.
Его первая команда наткнулась на ConvertFrom-Json automatic DateTime →
локализованную строку; повтор с DateKind String/InvariantCulture прошёл. Ошибка
была в one-off audit, не в workload или supervisor; исходный record не менялся.

File-only progress audit:35полных циклов/587.116241guest s,31source inputs
verified,36valid quiescent weather generations/maxfreshgap20.006810s, начальные
hashes совпадают. Это pending: ещё нет24h,terminal guard,60-cycle outages и
часовых steady windows. Full90679 жив, дошёл до QEMU photo fade после passing
boot/reset/SNTP/body/concurrency/URI gates. Published reports не заменены.

По прежнему запросу о скрипте переноса алгоритмов завершён отдельный tool CLI
в codex/small-tv-port-assistant/6b10c200, отправлен в origin. Worktree под .worktree
содержит отдельные16unit/CLI tests и61real assembly reports/9796instructions.
Исправлены короткие targets,gap blocks,offset-jalr return,layout validation;
добавлены bounds/names/JSON/Markdown/epilogue и fingerprints. Real getclocktype
доказывает50instructions,32-byteframe,4calls и shared backwards join без natural
loop. Область — analysis/review, не C instruction execution. Branch оставлена
отдельно до terminal/full publication, чтобы не менять frozen inputs текущих
firmware проверок. Детальный proof и CLI usage находятся в этой feature ветке.

### 2026-10-17 — браузерный checkpoint и запрошенное сохранение прогресса

На новой8304F1A4 запущен отдельный disposable persistent raw VM для реальной
browser acceptance. Первая попытка ошибочно требовала len(query-block)==1;
finally остановил PID33980, внешний OS audit подтвердил отсутствие. Во второй
использован штатный qemu_storage.direct_flash_backing: точное совпадение own
raw flash path, writable backend, без snapshot overlay. VM SmallTV-af1d9b420488,
PID18416,state .build/small-tv-browser/uri-current-20261017-2,ports18082/18083.

В IABbrowser2/tab2 видны titleWiFiConfiguration и setup для /?probe=1; scan
завершился с тремя синтетическими SSID и signed -21/-22/-39dBm, выбранyoRadio-QEMU.
Сохранены screenshot и scoped JSON с19input identities/direct raw proof;
configuration submission и station controls в этом browser flow ещё pending.
По пользовательскому запросу «закоммить и запушь текущий прогресс» вкладка
marked handoff, собственная browser VM нужна для продолжения. Full90679/H10
не останавливаются; на checkpoint H10running43cycles/noerror, full проходит
photo_reinit и продолжает photo_settings. Собственные изменения, checkpoint и
контекст сохраняются отдельно от чужих patch/tmp/untracked файлов.

### 2026-10-17 — сохранение нового браузерного прогресса и failed full

По повторному запросу commit/push проверены main и активные Small_TV worktrees:
все ранее созданные commits уже находятся в соответствующих origin branches.
QEMU main2a593f8d и его feature branch совпадают с GitHub, рабочие деревья чистые.
Чужие patch/tmp/untracked файлы не добавляются; port-assistant6b10c200 остаётся
в отдельной опубликованной ветке, код прошивки и frozen H10 inputs не меняются.

Full90679 завершился18:50:53UTC:18passed groups, QEMUfailed, manualnot_run.
Failure в time_qemu.py/reset_before_notification: displayed date не совпала
с2025/9/19, lastdecodedstate unsynced1900/1/0, boot_time_seconds2147483574.466206.
Это terminal failure без установленной причины, не новый successful full.
Проверены все192начальных fingerprints; raw report сжат воспроизводимо и
проверен распаковкой: uri-full-failed-20261017.report.json.gz. Scoped checkpoint
содержит group statuses, failure log tail, freeze и identities. Published
functional-validation/validation остаются прежними; publisher не запускался.

В реальном browser8304 выполнены setup submit и station query controls.
Success alert наблюдался, следующий UI state about:blank; old dialog dismissal
после screenshot был stale, причина не установлена. Read-only exactELF probe:
connectedtrue/APfalse/IP192.168.43.15/SNTPtrue, UTCdiff0.871993s, no panic.
Settings после reload: units flags1/dateDD/MM/YYYY,
brightness63/GIF5/Dial; colors после RGB565 quantization10aa31/3155ad/adcfef.
Synthetic cityPerth/AU-W saved; advanced night20→8/brightness12/NTP192.168.43.2
подтверждены UI. Failed initial fill+Tab22/9 и subsequent keyboard success
сохранены отдельными observations, не объявлены firmware bug. Intermediate
public API snapshotstart19 предшествует final UI20, cold-boot ещё pending.

На photo page initial interval5/mask31; две картинки natural240x240, три complete
с natural size0. Причину ещё не исследовали; photo/cold persistence acceptance
не засчитаны. Сохранены JSON и два screenshots без пользовательских данных.
Owned browser VM18416/tab2 оставлены handoff для продолжения, затем cleanup.
H10 checkpoint77cycles/1outage, no reported error, supervisor/guardrunning;
OS18:52:31UTC подтвердил exact PID/start/commands30128/2252/18740/26440.
Full9896 завершён. H10 не имеет terminal24h acceptance и не перезапускался.

### 2026-10-17 — browser8304: photo controls и настоящее cold persistence

Продолжение initial zero-size preview observation показало: сначала img3–5
не имели src, загрузка шла последовательно; позже все пять получили src и
decoded240x240, error/warn logs пусты. Это незавершённая загрузка, не доказанный
дефект прошивки. Через реальные checkbox/keyboard range controls выставлены
mask17/interval3, затем mask0/interval60; public API подтвердил оба состояния.

Owned persistent VM18416 остановлена и cold launched с тем же networksetup,
без reseed. Пока новая VM paused, полный flash hash совпал с последним guest
состоянием. Новый1960/SmallTV-37b25755c090 использует прямой writable raw.
После запуска public API11routes и выбранные raw settings совпали до/после:
units/date/GIF5/Dial/brightness63/colorsRGB565/cityPerth/AU-W/night20→8/12,
photo0/60. Bootloader/partition/app/assets byte-equal архиву;19inputs unchanged.
Реальный browser после ожидания initial loading подтвердил photo0/60+5previews,
clock controls и advanced20→8/12. Initial stale/default DOM не засчитывался.

Scoped8case JSON и screenshot сохранены как uri-browser-controls-validation-
20261017.json и uri-photo-cold-20261017.png. Failed initial numeric fill+Tab
сохранён отдельно; keyboard save плюс cold persistence теперь подтверждены.
Upload/crop/mobile здесь не повторяли, полного manual acceptance не объявляем.
Tab2 закрыт, VM1960 остановлена; external OS19:01:24UTC подтвердил отсутствие
18416/1960 и baseline time VM6624. H10 и повторный two-variant time test сохранены.

### 2026-10-17 — раздельное guest/host ожидание календаря после reset

У failed full рассмотрен сам frame: startup "Connecting to WiFi", календарь ещё
не рисовался, cache struct tm нулевой. Отдельный инструментированный baseline
на unchanged8304 прошёл весь native flow: после reset startup31→181 за15.284530
guest/19.672host s; затем preset date bytes equal, fresh UDP notification2038
и recovered calendar equal. Диагностика читает реальные timer_state/MMIO,
не меняет guest RAM/registers/functions. Не найдено оснований менять firmware.

Date capture раньше ограничивался30host s, которые при icount не гарантируют
окончания18.1guest startup. Теперь30guest с отдельным90host bound; factory
minute case90guest/270host. Оба elapsed/limits попадают в observation, low32
MMIO wrap учтён, stop всегда снимается finally; все date-band pixels остаются
обязательными. FIXED_TEST отмечает изменение теста, отдельно от firmware fixes;
новая метка добавлена в CORRECTION_MARKERS.md.

Six independent fake-clock/display cases проходят: slow host>30s с готовым
18.1guest frame, fast guest timeout, stalled virtual clock, single bad pixel,
32-bit wrap и exception resume. Старый function из HEAD на новом slow case
даёт ожидаемый failure; новая версия6pass. Первый sandbox unit invocation
использовал OS temp, cleanup получил Windows access denied, затем console
cp1252 не вывел русскую ошибку. Temp перенесён в repo .build, UTF8 test run
прошёл; это не ошибка гостя. Gate включён в qemu_suite и publisher.

Повторный real time_qemu suite71743 завершился: factory и native passed,
fallback/time corrections/year jump/backward leap/post2038/reset stages
прошли; scoped JSON сохраняет целый report, negative control и input hashes.
Все59production source inputs совпали с archive, app/ELF не менялись. Failed
full остаётся отдельным evidence; новый passing full ещё не опубликован.

### 2026-10-17 — рабочий CLI для переноса алгоритмов из RISC-V

В отдельной codex/small-tv-port-assistant завершён report-интерфейс ранее
неработающего черновика assist_c_port.py. CLI принимает decoded objdump,
точные start/stop, logical name и symbol-map; выдаёт JSON/Markdown с blocks,
dominator-proven natural loops, calls, stack save/restore hints и C conditions.
Source/tool/map fingerprints включены, input/map/tool overwrite запрещены.
Calls внутри диапазона, unknown indirect transfers,traps,gaps иexternal
branches остаются review warnings. C bodies/external calls по-прежнему требуют
ручного восстановления и сравнения; отчёт не объявляет firmware equivalence.

Независимые маленькие CFG/CLI fixtures выявили реальные дефекты черновика:
короткие hex branch targets терялись; gap склеивался с предыдущим block;
jalr zero,4(ra) ошибочно считался ret; не было layout validation/CLI/epilogue.
Old13tests:10failures/4errors (subtests), corrected16tests pass. Отдельный
case проверяет descending addresses разных ELF sections; они допустимы,
overlap/out-of-order внутри функции отклоняется. Natural loops отличаются от
irreducible backward edges; signed/unsigned C branch conditions сохранены.

Actual read_clock_theme_at_4200dfdc.asm получен pinned objdump из factory ELF
строго до0x4200e074:50instructions,12blocks,32-byteframe,4externalcalls иret
0x4200e068. Backwards jump0x4200e072 вshared completion не является циклом;
отчёт подтверждает это. Все61retained excerpts/9796decoded instructions
разобраны CLI,44natural-loop edges; это parser scope, не семантическая проверка
всех9796instructions. Separate tools/tests не меняют frozen firmware tests.
Scoped validation JSON и reference/CLI documentation сохранены в этой ветке.

### 2026-10-17 — интеграция assistant tool перед новым полным прогоном

После terminal failed full объединена готовая6b10c200; конфликты затронули только
append history в WORK_LOG/WORKING_NOTES, обе стороны сохранены. В main снова
16unit/CLI passed и real read_clock_theme50instructions/12blocks/4calls/0loops.
Production images/sources не меняются; H10 использует свой неизменяемый checkout.
Следующий verifier publication заменит прежнее stale "untested library draft"
ограничением actual review scope. Historical validation.json сейчас не меняли,
passing full не объявлен. Новый freeze должен включать updated verifier/tests.

### 2026-10-17 — fresh full193inputs и актуальный H10 prefix

На maincdc54723 зафиксирован новый freeze100test sources+93extras=193 hashes.
SourceBE5802D6/app8304F1A4/ELF62E040B5/QEMUA74 unchanged. Full запущен19:05:32UTC
в uri-bounded-full-20261017, exec42964, pwsh30656; OS identity/command сохранены
в uri-bounded-full-start-20261017.json. Повторная проверка193inputs после старта
прошла. Fresh host группы проходят, идёт machine comparison; terminal full
ещё нет, published EF66 не заменён. Не менять замороженные inputs во время run.

H10file-only auditor113полных циклов/1868.948064guest s,31inputs verified и
initial record matches;111valid quiescent weather generations,maxgap65.741273s.
UART1ROMboot/noerrors. OS19:06:07UTC подтвердил30128/2252/18740/26440 с точными
launch times. Это pending prefix без24h/terminalguard/steady windows, не pass.
H10 files/bundle не менялись; browser/NTP probe VMs закрыты. README manual
coverage исправлен: current8case8304 отдельно от historical31caseDAF; stale
«weather_wait ещё не включён» заменено actual mandatory gate description.

### 2026-10-17 — terminal bounded full: night-case закончился до SNTP

В начале turn подтверждены exact PID/start/commands30656 и четыреH10roles;
предыдущий turn дал concrete progress, оба прогона пережили границу сообщения.
Full42964 затем terminalfailed в photo_frames/native masked-night.10полных
кадров и PWM совпали с literal replay/corrections; только synchronized_night_restore
False. Обеrestore2.814699/7.163766guest s имелиclock_validFalse и preset17:04.
Два fade завершились до первой SNTP notification при разрешённом fast photo
startup. Это непроверенная night цель, не установленная ошибка яркости.

Заново verified193frozen inputs; terminal raw report сжат и round-trip проверен,
scoped JSON сохраняет все10samples/checks и subgroup statuses. Published EF66
не заменялся. Следующее исправление должно сохранять точные pixels/PWM и
обязательную настоящую night-sync proof, а не отменять этот assert.

Параллельно в .worktree/small-tv-wifi-fallback подготовлена27f1b23e: реальная
ошибка18s network fallback, не связанная с display timer.47platform cases,
4actualnetworkQEMU/23contract guards и RV32oracle проходят; twelveownedVMs
закрыты. New6324/source53D3 ещё не в main; main/H10 продолжают означать83.
Сохранение этого terminal checkpoint разрешает интеграцию до нового freeze.

### 2026-10-17 — station mode сохраняется во время DHCP, SDK failure остаётся рабочим

После revalidation mainfull30656/H10processes найдена отдельная parity ошибка:
fallback_task принимал18s безIP за отказ, хотя factory0x4200cc0e..cc22 ждёт
event group(mask3,portMAX_DELAY), а181ticks принадлежат только startup display.
Factory0x4200cc26 отдаёт приоритет success; failure0x4200ce20 сохраняет mode2.

В изолированном worktree packet-delay probe на старой8304 подтвердил: factory
через30guest s всё ещё mode1/boot1 и подключилась после release, native стала
mode2/boot2. Два host сценария также failed: pending DHCP и stale failure после
GOT_IP/reconnect. Удалён ложный timeout, GOT_IP очищает прежний failure latch.
Осталась реакция на пять реальных disconnect events(initial+4retries).

47platform cases/1182314checks проходят. Ordinary DEBUGOFF production build:
6324C55A/ELF9E2C7719/source53D38223,1169904bytes/free366096,59inputs; всё в
worktree firmware/development. New4case network regression сравнила обе
прошивки: holdDHCP30guest→STA HTTP безreset; missingAP→SDK retries→mode2/
одинreset→setup HTTP, восстановленный externalAP не подключает retained SSID.
23negative evidence controls общие в suite/publisher/verifier. RV32oracle:
4actual event traces и16factorydispatch states passed.

Первая одноразовая попытка разбора HMP backend не учла prefix "\\ #net000";
owned VM остановлена, parser исправлен. Проба missingAP сначала пыталась
изменить static link-down property послеrealize и получила штатный отказ QEMU;
перешла на поддерживаемый station-ap-online. Это harness errors, не firmware
faults. Все isolated VMs закрываются finally; исходный dump/code/media неизменны.

Существующий mainfull42964 тем временем terminalfailed на photo_frames native
masked-night:10frames/duties совпали, но обеrestore2.81/7.16guest s были доSNTP.
Night target не был проверен; не объявляем это runtime brightness bug и не
публикуем новый fullpass. H10 продолжает старый83, не подтверждает новый6324.

### 2026-10-17 — интеграция Wi-Fi fix после terminal snapshot

Feature27f1b23e pushed и объединён в main после commit346fb11e с failed full.
Конфликты затронули только рабочие notes/log; обе истории сохранены. Canonical
BIN/ELF/map заменены exact6324/9E2C из worktree, CMake cache не копировался,
старые83/62E0 в pre-wifi-fallback-main-20261017. Resources регенерированы;
production59inputs должны совпадать с new archive53D3. Следующий scoped gate —
детерминированное наблюдение настоящей night restore; затем fresh full. Existing
H10 работает со своим frozen83 и не получает новую версию/приёмку.

### 2026-10-17 — photo night observation с настоящим задержанным SNTP

Photo frame observer сохраняет первые два fade, затем при отсутствии actual
night restore продолжает целые6frame cycles, не больше6cycles всего. Ни pixels,
ни PWM, ни state continuity/round-robin не ослаблены. Contract пересчитывает
наблюдённые phases/order и отклоняет бюджет7 и отсутствие actual clock_valid.
Suite publisher/verifier требуют14negative controls; FIXED_TEST описан отдельно.

Первый scoped run6324 прошёл84frames/9normalized scenes, но его SNTP успел во
втором cycle. Поэтому fixture сделан детерминированным: native masked-night
получает ntp-drop-mask7 до окончания двухcycles, потом внешний NTP отпускается.
Новый полный photo gate69551 прошёл102frames,9normalized и14rejections;5cycles
в night case, первые4restoreclock_validFalse и пятоеTrue/duty4095. Все102full
frames имеют0different pixels и exactLEDC, slots1,3,1,3,1 идут циклически.
Контроль clock_valid читается у настоящего backlight_update через hardware
breakpoint; RAM/registers/time не подставляются. Production59inputs/app6324/
ELF9E2C/source53D3 не менялись. Scoped report сохранён; full/H10 не объявляются.

### 2026-10-17 — новый supervised H10 на6324, старый83 намеренно superseded

Создан отдельный worktree `.worktree/small-tv-h10-wifi` в собственной ветке
из `7f7dc110`. BIN/ELF/map 9E2C и 59 входных файлов совпали с архивом 53D3;
11 файлов QEMU скопированы побайтово (A74/6B7F, сборка adb66701b3). Короткий
прогон завершён: 8 циклов, 40.349966 гостевой секунды, 4 отключения AP,
8 актуальных поколений погоды, максимальный промежуток — 8.161277 секунды.
31 входной файл не изменился; supervisor, worker и guard завершились с кодом 0.
Аудитор повторно проверил журнал и guard; scope_requires_review ожидаем без
суточного наблюдения и окон памяти. Сохранены отчёт и исходные JSONL/UART в gzip.
ОС подтвердила отсутствие VM короткого прогона и 12 VM двух фототестов.

Перед плановой остановкой старого образа 83 аудит зафиксировал 230 циклов,
3800.976347 гостевой секунды и 31 проверенный входной файл. Статус — pending,
суточного результата нет. Сначала записано намерение заменить прогон образом
6324, затем проверены PID 2252, время создания и команда; остановлен только
этот worker. Supervisor 30128 завершил свои guard 18740 и VM 26440, затем вышел.
CIM подтвердил отсутствие всех четырёх процессов. Статус failed/missing-footer
ожидаем после внешней остановки и не доказывает сбой прошивки. Аудит, намерение
и исходные журналы сохранены; старые входные файлы не менялись.

Новый supervisor запущен скрыто в 19:45:25 UTC: 86400 гостевых секунд,
интервал 15 секунд, отключение AP каждые 60 циклов. Запись старта связывает
образ 6324, ELF 9E2C, QEMU A74, 31 входной файл, хеш guard и реальные идентификаторы
CIM: 21336/34036/27092/9760. Начальный аудит — pending, запись старта совпадает,
входные файлы проверены. При сохранении прогресса PID, время создания и команды
всех четырёх процессов сверены повторно: процессы работают. Контрольные суммы
обоих архивов короткого прогона и обоих архивов остановленного прогона совпали;
gzip и JSONL читаются. Полного суточного результата пока нет.

### 2026-10-18 — аудит прерванного H10 и новый полный прогон

Предыдущий этап сохранил и отправил текущие исправления и журналы в main
(`5148bd41`); это завершённая часть работы. При продолжении CIM не нашёл ни
одного исходного процесса H10. Позднее PID 34036 занял новый machine oracle:
время создания и команда отличаются от старого worker. Windows работает с
14 октября, поэтому перезагрузка ОС исключена. Причина остановки неизвестна.
Нетерминальный supervisor остался на 89 циклах; независимый file-only анализ
подтвердил 90 полных циклов, 1486.761343 гостевой секунды и 31 входной хеш.
В UART один ROM boot, panic нет; 91 свежая публикация погоды, максимальный
промежуток 19.970336 секунды. Суточной проверки, достаточных окон памяти и
терминального guard нет. Отчёт, журналы событий/UART и исходный report сохранены
отдельно; status=running не повышается до успешного результата.

В 09:41:53 UTC запущен новый полный run-all текущего производственного образа
6324/ELF 9E2C/source 53D3 с QEMU A74. Session 92602, controller PID 22772,
каталог `.build/small-tv-functional/wifi-integrated-full-20261018`. После старта
побайтово сверены 102 тестовых и 93 прочих входных файла. Запись старта включает
все хеши и реальную команду/время создания процесса. Ничего из frozen inputs
не меняется до завершения; опубликованный исторический отчёт не заменяется
промежуточными результатами. Следующий H10 требует отдельного нового каталога
и проверки способа запуска, который переживёт завершение родительского сеанса.

### 2026-10-18 — независимый запуск длительного теста Windows

В отдельной выборочной рабочей копии добавлены start_runtime.ps1 и модуль
runtime_process.psm1. Новый supervisor создаётся скрыто через CIM с
CREATE_BREAKAWAY_FROM_JOB; IsProcessInJob проверяется по реальному handle.
Команда не исполняется shell; правило Windows argv сохраняет кавычки,
завершающие backslash, пустые строки и Unicode. Запись запуска резервируется
до создания процесса, дубликаты не начинают вторую VM и не трогают прежние
данные. PID/время создания/команда и хеши launcher сохраняются отдельно.
При ошибке очистка разрешена только после проверки принадлежности процесса.

runtime_process_test.py выполнил восемь реальных интеграционных проверок,
включая выход родительского процесса до завершения ребёнка, независимую
проверку Job через kernel32, точный argv и ошибки Windows Create. Первое
выполнение выявило отказ привязки пустой строки argv; добавлен AllowEmptyString,
последующие проверки прошли. Отдельный восьмицикловый QEMU preflight через
новый launcher завершился: supervisor/workload/guard exit 0, sources unchanged.
Модуль после него дополнен защитой от PID reuse и повторно прошёл host-проверки.
Это не доказывает причину прежней остановки H10 или завершение 24 часов.

Итоговый модуль также проверен отдельным четырёхцикловым preflight: 17.171712
гостевой секунды, 32 HTTP, два отключения AP, 31 проверенный входной файл;
supervisor/workload/guard завершились с кодом 0, исходники не изменились.
Аудитор вернул completed_scope_requires_review, как ожидается для короткого
прогона. Отчёт и исходные журналы сохранены в runtime-launch-validation-20261018.json
и трёх gzip. Производственная прошивка, исходники и установленный QEMU не менялись.

### 2026-10-18 — сохранён неуспешный полный прогон 6324

Session 92602 завершился с кодом 1 в 09:51:51 UTC. Все 18 host/machine/profile
групп прошли. QEMU boot/reset/SNTP обеих прошивок и delayed-DHCP original/native
прошли, но missing-original не дождался setup HTTP на localhost:18080. Последнее
наблюдение: 15.499082 гостевой секунды, mode RAM/raw=2, AP active, connected=false,
два ROM boot; исполняемые области не изменились. Проблема возникла в заводском
образе до native missing-AP и позднейших групп. Причина пока не установлена,
ожидание не ослабляется и ошибка не приписывается нашей прошивке без анализа.
Все 195 frozen identities повторно совпали. Scoped JSON и четыре исходных
отчёта в gzip сохранены отдельным checkpoint; прежняя успешная публикация
остаётся исторической и не выдаётся за проверку текущего образа.

### 2026-10-18 — чистка завершённых worktree по запросу пользователя

Применён навык git-repo-cleanup и его Git reference. Проверены все 22 yoRadio
worktree и обе копии QEMU: index/diff, ignored/untracked файлы, Git-операции,
скрытые flags, submodule/nested Git, reflog, публикация и процессы. Origin HEAD
обоих проектов подтверждён как main; refs получены без prune. Копии ESP8266/C3
с незавершённой работой и SDK оставлены, все семь исходных staged diff сохранены.

Удалены 12 завершённых worktree Small_TV обычным worktree remove после повторной
проверки каждого пути, inventory, refs и отсутствия активных процессов. Полный
логический размер файлов этих копий — 25 889 466 492 байта. Все ignored файлы,
включая ELF/map, VM-журналы и сборки, сохранены в 12 проверенных архивах общим
размером 932 262 015 байт в `.build/worktree-retention/20261018`. Уникальный
прежний amended-коммит observer закреплён в recovery ref и incremental bundle.
Ветки не удалялись. Root, H10 Wi-Fi и новая runtime-launch копия сохранены.

В QEMU удалена одна завершённая дополнительная копия на том же 2a593f8d,
что опубликованный main. Ignored файлы сохранены в проверенном архиве,
обе вложенные зависимости — дополнительно в Git bundle. До удаления исследован
orphan из reflog: 158b65e28a отличается от принятого amend только двумя QOM
путями README. Он закреплён recovery ref и проверенным incremental bundle;
избыточный созданный полный bundle заменён компактным. Зарегистрированные ROM
submodule были неинициализированными. Установленные RISC-V/Xtensa executable
после чистки совпали по SHA-256; код QEMU не менялся, rebuild не требовался.
Точный local exclude скрывает только приватный retention-каталог.

Новые runtime launcher изменения сохраняются в codex/small-tv-runtime-launch;
рекомендуется интеграция инструментов после review, но очистка не объявляет
успешной полную функциональную или аппаратную приёмку прошивки.

### 2026-10-18 — новый H10 через независимый launcher после чистки

В 10:06:56 UTC start_runtime.ps1 запустил новый 86400-guest-second run в
сохранённом `.worktree/small-tv-h10-wifi`. Используется прежний точный 6324
образ, ELF 9E2C, source 53D3 и frozen QEMU A74. Interval=15, outage cadence=60.
Запись старта связывает 31 неизменный входной файл, реальные CIM identities
17788/23672/28632/35664, команды и хеши supervisor/guard/launcher. Все процессы
повторно сверены; supervisor действительно вне Windows Job, как проверил
launcher. Начальный независимый file-only аудит pending, start_record_matches
true. Это только начало нового прогона, не 24 часа, не доказанный memory trend
и не проверка выживания через следующий turn. Старые прерванные каталоги не
возобновлялись и их длительность этому образцу не добавляется.

## 18 октября 2026 — APSTA early restoration

- После завершённой очистки репозиториев продолжено расследование terminal full
  regression. Четыре контроля отделили ранний возврат внешнего AP от раннего HTTP:
  два early-restore запуска не ответили за 91 s, два late-restore ответили за 2.30/4.55 s.
- Инструкции 0x4200d1a0..d1c4 и AP handler 0x4200c6e2 сохранены. Factory state 5
  означает конец AP init, не подключение клиента. Старое ap_active до init было
  неверной эвристикой. AP handler пытается STA connect; GOT_IP не пишет state 2.
- Отдельный probe проверил STA HTTP и event group: ответа нет, bits=0. Успешная
  STA в сбойном запуске не установлена. Исполняемые/media области неизменны.
- Новый QTest воспроизвёл конфликт общих peer state и MAC на C2/C3 в обоих порядках
  подключения: четыре отрицательных subcase. Отчёты сохранены с raw SHA/gzip.
  QEMU fix ещё не принят; новый scoped passing gate и полный regression впереди.
- В 10:22 UTC проверены PID/creation/command всех четырёх процессов H10: совпали.
  Префикс дошёл до 44 циклов / 765.066695 guest s. Это не суточная приёмка.

- Исправление QEMU завершено и сохранено как aab05d5de6: независимые AP/STA peer
  state в отдельном модуле, общий radio/DMA, разделение входящих IP/ARP и очереди
  при отключении внешнего AP. После коммита сборка повторена: executable B44D1A05
  побайтово прежний и marker соответствует aab05d5de6.
- Пять QTest / 10 C2/C3 subcase проходят. Те же test/harness SHA дают 10 ошибок
  на прежнем A74. Прошли 12 прежних сетевых тестов, модульные LCD/SD/SPI/I2C
  и неизменённые CYD/C3 OLED boot проверки на окончательном B44.
- Обе настоящие прошивки прошли delayed-DHCP и missing-AP при раннем возврате
  сети: четыре потока. Observer ждёт state 5 после HTTP и читает отдельный
  APSTA GOT_IP event; в factory missing-AP checkpoint он false. Все 26 мутаций
  недостоверного evidence отклонены. App6324/source53D3 не менялись.
- Scoped evidence сохранён в apsta-validation-20261018.json и семи raw gzip;
  exact build bytes и Git blob hashes QEMU записаны отдельно из-за Windows EOL.
  Это не полный regression, не DEBUG-off приёмка и не суточный результат.

- 10:41:21 UTC: полный host/machine/QEMU regression начат на app6324 / ELF9E2C /
  QEMU B44 из aab05d5de6. Controller PID2448 запущен проверенным detached helper;
  реальное kernel job membership=false. В 10:42 UTC его creation/command совпали.
  121 test + 152 дополнительных файла заморожены и после старта совпали (273).
  Набор идёт без Skip; суточной/общей приёмки этим стартом не объявлять.
- Для изолированной рабочей копии создан ignored SDK junction .idf на основной
  SDK и скопированы oracle dependencies. При очистке не обходить junction.
- В 10:42 UTC повторно совпали четыре личности H10 и 31 input hash. Префикс
  103 цикла / 1737.66437 гостевой секунды, 832 HTTP и одно отключение внешнего AP.
  H10 использует frozen A74, а новый full regression — B44; области не смешивать.

- Продолжено исследование APSTA без изменения 273 frozen full inputs. По цепочке
  SDK get_handle_from_ifkey найден список 0x3fcc3c0c; getter 0x42036f98 читает
  if_key по +92. Два настоящих factory boot дали ровно STA_DEF в station и
  AP_DEF в setup, обе страницы HTTP200; code/media/UART guards прошли.
- Setup VM использует сохранённые реальным SDK синтетические credentials.
  Официальный NVS parser v5.5.4 подтвердил nvs.net80211/sta.ssid и sta.apinfo
  с верными CRC. GOT_IP event=false при отсутствии STA netif: это не потеря SSID.
  Исходные APSTA connect-вызовы сами по себе не доказывают рабочий STA IP путь.
- Characterization report и raw gzip сохранены отдельно от passing full gate.
  Scratch netif probe нужно перенести в reusable test после terminal full run.
  Кандидат оптимизации — лишние native netif/DNS в другом режиме; пока код и
  производственный app не менялись, затраты памяти и wire behavior не измерены.

## 18 октября 2026 — network role allocation, в работе

- Создана отдельная sparse worktree codex/small-tv-netif-roles от9c8a6747, чтобы
  сохранить 273 frozen входа текущего full run в другой копии.
- Изменён только network/wifi.c и его platform coverage: по одному netif на
  выбранную роль, AP-only DHCP/DNS и STA-only retry task. APSTA scan остаётся.
- Negative control прежнего C упал на лишнем STA netif в setup. Исправленный C
  прошёл 48 cases /1 182 327 checks. SDK/QEMU behavior и RAM gain ещё не измерены.
- Production compile session58887 запущен с общим pinned SDK; это не flash.
  После завершения проверить development archive перед реальными VM проверками.

- Compile session58887 завершён exit0; app26C6 / ELFFE9B / sourceD628 сохранены
  в development archive ветки. Размер1 169 872 bytes /366 128 свободно; DEBUG off.
  Ни success SDK/QEMU, ни RAM gain одним размером/компиляцией не заявляются.
- Запущены actual setup/AP scan/reboot->STA (17901), четыре Wi-Fi policy cases
  (53919) и отдельный memory baseline8cycles old6324 на B44 (20063). Старый H10
  остаётся на A74; его prefix не используется вместо before/after memory control.

- Actual setup scan/configure/reboot->STA/cold relaunch/reset новой26C6 прошёл
  (21 check). Четыре Wi-Fi DHCP/failure потока factory/native и26 evidence guards
  прошли с неизменными образами и исходными input SHA.
- Честный runtime before/after на B44: по8циклов /64HTTP /4outage /69events.
  Оба pass; task set отличается только отсутствием captive_dns в STA (12->11).
  Ready free heap87876->92036; медианный gain9samples4160bytes. Это короткий
  STA workload, не суточная приёмка и не измерение AP. Исходные отчёты сохранены.
- Проверены59 production inputs: изменён только network/wifi.c; sdkconfig один.
  Bootloader checksum/SHA валидны, исполняемый образ идентичен кроме SDK даты
  компиляции и integrity bytes. Поэтому смена bootloader hash не скрыта как
  «тот же binary». Scoped proof network-roles-validation-20261018.json +5gzip.

- 11:07:17 UTC полный app26C6 run запущен independently через проверенный CIM
  launcher, PID28968, job=false. После запуска все273inputSHA и личность совпали.
  Полный SDK/machine/QEMU набор без Skip; start не является passing report.
- В11:07:50 UTC прежний full app6324 PID2448 жив, все273inputs прежние. H10
  app6324/A74:4process identities и31input совпали;180cycles/3005.344746guest s,
  1445HTTP/3outage. Новой26C6 H10 ещё нет; области приёмки явно разделены.

- Frozen H10 copy app26C6/ELFFE9B/B44 создана atf0375b14. Detached4cycle preflight
  завершился pass, workload/guard exit0,32HTTP/2outage/31unchangedinputs.
- До любых stop действий записан replacement intent старого app6324/A74 H10.
  В11:13 UTC совпали4process identities и31input;196cycles/3267.751527guest s,
  1573HTTP/3outage. Это неполный prefix; замена нужна для нового firmware/model.
  Следом требуется revalidate worker handle, supervisor cleanup и сохранение raw.

- В11:13:48 UTC после committed intent и CIM revalidation остановлен прежний
  workload23672. Supervisor выполнил cleanup exit0; raw failed/-1 outcome
  сохранён. Независимый file-only audit подтвердил200полных циклов,
  3292.590422guest s/1605HTTP/3outage,31inputs, одинROMboot безpanic.
  Manifest network-roles-runtime-superseded-20261018.json +7rawgzip; неH10 pass.
- Новая frozen26C6/FE9B/B44 H10 запущена11:14:24UTC, supervisor21928 внеJob,
  workload20664/guard35272/VM7412. После запуска все4CIM identities совпали,
  31runtime+11frozenQEMU hashes проверены; file-only diagnostic/start binding pass.
  Start proof network-roles-runtime-start-20261018.json +2rawsnapshots. Никакой
  24h/полной приёмки пока нет. Оба full controller2448/28968 также живы.

## 18 октября 2026 — повторяемая проверка SDK netif

- В отдельной codex/small-tv-netif-observer отfe592a8b создан read-only observer:
  factory addresses связаны с dump5321; native layout читается из совпадающего
  ELF/DWARF. Ограничены pointer/key reads, list size; ошибки не подменяются пустым
  успешным результатом. Production C и build26C6 не менялись.
- Первый probe отверг NVS blob_index, второй ошибочно требовал SDK FLASH SSID
  и от native WIFI_STORAGE_RAM. Неуспешные отчёты сохранены. Уточнена фикстура:
  factory STA сам записывает public driver NVS, обе setup VM получают эту
  проверенную NVS partition; далее меняется только raw mode=2. Код/RAM не патчатся.
- Финальный v3 прошёл четыре потока: factory/native STA и setup, HTTP страницы,
  retained SSID+AP-info CRC, APSTA `/scan`, netif до/после, неизменные code/media,
  clean UART. Прежняя native6324 с теми же observer bytes/B44 упала на двух
  интерфейсах в STA, что подтверждает обнаружение исправляемого расхождения.
- 7offline observer tests и17evidence mutations pass. Новый gate обязателен
  в suite/publisher;27inputs runtime reports совпали. Старые frozen full runs
  остаются в прежнем объёме, никакой полный pass новой test revision не заявлен.

- Завершено дополнительное AP before/after измерение: одинаковые4scan+4HTTP,
  9heap/task snapshots каждого app6324/26C6 на одном B44. Оба pass,24input SHA
  каждого неизменны, по36ROM counter crosschecks, одинROMboot безpanic.
  Задач12->11 (только wifi_fallback); ready free83928->86604, gain2676bytes.
  Медиана парных фаз2672, range2332..4596: transient HTTP buffers оставлены
  видимыми, не маскируются. Raw reports/UART и one-off probe сохранены gzip
  с network-roles-ap-memory-20261018.json; это не H10/latency/leak acceptance.
- Замечены time_sync и weather_http tasks также в AP. Следующий шаг — сравнить
  service lifecycle и factory AP branch/HTTP/cache/time semantics, затем решать,
  можно ли избежать allocation. Production пока не менялся. Frozen full/H10
  не перезапускались и не получают новый netif gate задним числом.

### 2026-10-18 — station-only service allocation и сохранение результата full

- По factory AP branch0x42009032..0x42009052 разделены cache initialization
  и workers. AP не выделяет time_sync/weather_http, STA с ожидающим DHCP
  продолжает их создавать. Production delta — ровно3из59inputs; appBC68,
  ELF4FDE, source5586, app1169904bytes, запас366096. Build успешно архивирован.
- Platform50cases/1182393checks, native5531 и artifact6 pass. Исправлены три
  старых fixture, которые неправомерно посылали station GOT_IP в AP режиме.
  Оба новых AP tests с финальным harness падают на старых service modules.
- Real factory/native AP6HTTP settings routes, ≥30/45guest seconds, реальные
  tasks/cache/ROM counters и четыре полных RGB кадра прошли. Ready AP gain11508
  bytes, tasks11→9; later-workload median не заявляется. Настройка AP→STA и
  STA8cycles/64HTTP/4outages/9weather generations прошли на B44.
- Сохранены ap-services-validation-20261018.json и8raw gzip; full BC68/H10
  пока не запускались. Различие bootloader raw bytes не объявлялось изменением
  алгоритма или доказанной нормализованной идентичностью кода.
- Старый full26C6/B44: terminal_failed/exit1 в regional raw ASCII observer на
  erased0xff. Повторно проверены273frozen inputs; исходный failure сохранён
  в network-roles-full-failure-20261018.json и6gzip. Причина flash моделирования
  рассматривается отдельно; отказ не превращён в успешный результат.

### 2026-10-18 — raw observer между erase и программированием

- Проверка на byte0xff больше не падает в decode: erased/partial data pending,
  неизменный bounded timeout сохраняет отказ при постоянной порче. Native dirty
  symbol1byte из matching ELF должен быть0до/после host read. Проверка factory
  completion flag не выдумывалась; factory читает точный сохранённый key.
- 5unit controls pass и добавлены как mandatory suite/publisher/verifier gate.
  На scoped QEMU9DA прошли15+15regionalkeys, maxcity64/country19, invalidinputs,
  raw immutable media, холодный boot и SDK NVS v1 migration/v2 fallback.
- Окончательный QEMU20B с дополнительным исправлением C2dummy/QE прошёл настройку
  Wi-Fi16factory/21native checks и station isolation. Разделение бинарников и
  ограничения evidence сохранены в flash-persistence-observer-validation-20261018.json
  с2rawgzip. Эти результаты не заменяют полный прогон или H10 текущего BC68.

### 2026-10-18 — итог flash audit и ограничение CYD

- QEMU0860e568d4, final binaries20B/1845:11NOR groups на3SoC,17rows/476checks
  старой read-mode/capacity matrix и modular peripherals pass. Тот же final
  harness на прежних бинарниках даёт24failures/2errors (отсутствующая timing
  property). Исходники, положительные/отрицательные reports и scope сохранены
  в QEMU docs/validation/flash-write-validation-20261018.json +15gzip.
- Short CYD25s сначала pass, однако более длинные60s выявили esp_phy_enable
  assertion phy_init.c:332. Сопоставимый same-toolchain control со старым NOR
  blob воспроизводит тот же assertion. Старый installed control падает на QIE.
  Это не полная CYD acceptance; console pixels/no-panic25s недостаточны.
  C3 OLED и modular OLED checks pass. Firmware archives не менялись.

### 2026-10-18 — завершился исторический frozen full6324

- Старый full app6324/source53D3/B44 terminal_passed12:10:15UTC:19passed groups,
  hardware_browser_soak not_run. Все273frozen inputs повторно проверены; proof
  apsta-full-completed-20261018.json +4rawgzip. Успех не перенесён на26C6/BC68
  или новый flash QEMU; новые gates в этот старый прогон задним числом не входят.
- H10 app26C6/B44 не прерывался, file-only diagnostic status pending,
  h10_checks_passed=false. Чужие/длительные ВМ не останавливались; одноразовые
  ВМ flash audit завершены. Полного acceptance для текущего appBC68 ещё нет.

### 2026-10-18 — текущий full и замена H10 на BC68/20B

- Full запущен отдельно в codex/small-tv-flash-full, controller10836 вне Job;
 533inputs frozen, startce6a1254. После host/machine групп перешёл в QEMU.
- Новый guarded preflight8cycles/64HTTP/4outages/9weather generations pass,
 36ROM counter checks,31+11input hashes совпали, workload/guardexit0.
 Raw proof ap-services-h10-preflight-20261018.json +6gzip.
- До остановки старого workload записан и отправлен intent2f9f81e3. Проверен
 retained handle старогоPID20664, creation time/полный command line; завершён
 только этот workload12:30:54UTC. Старый supervisor сохранил failed/-1 и
 очистил собственнуюVM/guard (cleanup0). Аудирован prefix214cycles/31inputs;
 исходные report/events/UART/guard/supervisor/stop/analysis сохранены7gzip.
- Новый H10 BC68/20B запущен12:30:54UTC: supervisor23548/workload5036/
 guard22392/VM18128. CIM подтверждает все4идентичности и отсутствие4oldPID.
 Start record хранит31runtime и11frozenQEMU inputs; это start/pending, не H10 pass.

### 2026-10-18 — воспроизводимый browser/Canvas/raw photo gate

- Browser Use и Node REPL не инициализировались (kernel assets os error3).
  Реальная проверка выполнена установленным Chrome155/Playwright через CLI
  на собственной disposable BC68/20B ВМ с raw backing, без внешней сети.
- Оба Chrome/VM процесса подтвердили точный generated photo HTML.23browser
  checks и6storage checks pass: pointer shrink/grow, выбранные blue/yellow RGB,
  240×240baselineJPEG безAPP/COM, source synthetic metadata, Cancel/Escape,
  mobileviewport390×844,47773bytes noise/12chunks, cold exact JPEG readback.
- QMP подтвердил writable raw backing, slots1–3 и executable/static flash
  области неизменны. По одному ROMboot на каждый новый VM identity, panic нет;
 26inputs совпали, console warnings/errors=[]; Chrome/VM закрыты.
- Созданы browser_photo_qemu.py и browser_photo_flow.mjs; final proof
  browser-photo-validation-20261018.json +5rawgzip+2PNG. Первый development
  run также pass; final добавляет source tags и explicit ROM/VM identities.
  Production не менялся, frozen full533 и active H10 не редактировались.

### 2026-10-18 — совместимость start record с file-only analyzer

- Первая проверка нового start record получила evidence_rejected: отсутствовал
  top-level guard metadata, хотя его исходный SHA уже был в supervisor snapshot.
  Добавлены guard/source_file+source_sha256 и canonical duration field86400.
  Формат исходного ee896b31 сохранён в Git; добавлена явная reconciliation note.
  Ни workload, ни его31runtime/11QEMU inputs не менялись и не перезапускались.

### 2026-10-18 — настоящий браузер initial Wi-Fi setup на BC68/20B

- В собственной ветке codex/small-tv-browser-wifi добавлены browser_wifi_qemu.py
  и browser_wifi_flow.mjs. Установленные Chrome155/Playwright через CLI, только
 390×844 и два loopback origin каждой disposable VM; внешняя сеть запрещена.
- Три реальных scan/configure flow: обычная сеть, SSID `manual`, manual entry
  после отключения external AP. Знаковый RSSI и различение служебного option
  проверены браузером. Cancel/empty не отправляют POST. Короткий пароль400
  не меняет444raw bytes, AP role или ROM boot count. Положительные fetch и
  загрузка настроек не дают console/page errors; negative preflight содержит
  ровно две ожидаемые console errors для400 и error alert.
- Каждая настройка прошла программный restart→STA DHCP→UDP SNTP; actual SDK UTC
  с matching ELF HRT/correction отличается от wire expected менее27ms. Новый
  cold process сохраняет credentials/STA и вновь синхронизируется. По2ROM boot
  для setup flow и по1для cold. Все защищённые code/media intervals неизменны.
- Итог93browser+18storage/role checks pass;25inputs неизменны. Все6VM PID
  отсутствуют по CIM, Chrome закрыт. Proof browser-wifi-validation-20261018.json,
 13rawgzip (включая cleanup и оба failed development runs) и2actual PNG.
- Первый harness ошибочно ожидал photo loading overlay в settings; второй
  использовал приблизительный RTC+lifetime UTC с неверной нижней границей.
  Финальный тест проверяет реальные переключатели/API и SDK timer components.
  Оба первоначальных failed report и точные исходники сохранены, не заменены pass.
- Cherry-pick H10 metadata c0fc3cb3 завершён какb1bba736; конфликт только двух
  добавленных разделов WORK_LOG разрешён сохранением обоих. Production/archive
  не менялись, live full533 повторно совпали. Controller10836 и все4H10PID живы;
  file-only prefix58cycles/31inputs, одинROM boot безpanic, пока pending.
  Полный прогон прошёл photo_controls/reinit/settings; terminal result ещё нет.

### 2026-10-18 — резервированные JPEG DHT branches, factory correction

- Непокрытый edge case найден после чтения существующего41-case JPEG gate.
  T.81 AnnexC/F.1.2.2.1/TableF.2 запрещают all-one Huffman words и AC size>10
  либо zero-size кромеEOB/ZRL. Фактический factory0x42011100/0x42011208 и старый
  C принимают121неиспользуемую malformed ветвь, поскольку entropy использует
  только DC0/EOB. Три запрещённыхDC controls уже отклонялись, четыре valid pass.
- Добавлены jpeg_dht_oracle.py (128cases) и общий jpeg_dht_contract.py.
  Полный panel guard и discard validation; native должен отказать до jd_decomp.
  Все шесть test/helper SHA и128fixture SHA before/after совпали. Original dump,
  ELF и CPU instructions не патчились; synthetic bytes подаются наSDK read boundary.
- В tjpgd.c/create_huffman_tbl поменяны две проверки, FIXED_FACTORY comment
  объясняет стандарт. Native before0x4201320c bltu заменён candidate0x4201320a
  bgeu;0x420132aa добавляет AC size/EOB/ZRL. Три точных disassembly сохранены.
- Успешная SDK6.1 build архивирована:0592b510/ELFaea10675/sourceD338a294,
 1169936bytes (+32), free366064, DEBUGoff.59production inputs, delta только1file.
  Bootloader359de03d после новой сборки не объявляется алгоритмическим изменением.
- Candidate:128DHT + прежние41inputs,107public JPEG/35errors/7placements,
 5531host C и6artifact checks pass. Семь evidence rejection controls pass;
  новый child gate обязателен в machine_jpeg_inputs, обоих publication tools.
- HTTP before/after выполнен с одним exact harness/QEMU20B. Все три362-byte
  reserved-table upload раньше200/exists, теперь400/absent. Candidate22checks
  pass, including valid files/retries/download/несколько холодных запусков и
  восстановление после interrupted replacement. В before false только новый
  reserved_dht_rejected; raw failure не переписан. JPEG proof +12gzip сохранены.
- Root/active full533 и H10BC68 не редактировались/не останавливались, все пять
  process identities перепроверены. Полное соответствие0592, его full/H10 и
  физическая приёмка ещё не доказаны. Следующий шаг — изолированный полный прогон.

## 2026-10-18 — восстановлена надёжность Windows-супервизора H10

- Работа выполнена в новой `codex/small-tv-runtime-supervision` от `cf131575`.
  Исторические деревья, 539 входов полного прогона и 31+11 входов прерванного
  H10 не редактировались. Полный 0592/20B завершён: 19 групп, публикация и шесть
  проверок артефактов приняты. H10 BC68/20B после 336 циклов остаётся непринятым;
  сопутствующий ENOSPC не объявляется доказанной причиной исчезновения хоста.
- Установлен дефект finally: ошибка WriteAllText первого child log прерывала
  очистку guard/VM. Очистка вынесена в `runtime_cleanup.psm1`: все свои children
  останавливаются через удерживаемые handles, helper своей VM выполняется до
  открытия его лога, stdout/stderr сохраняются независимо. Потеря диагностики
  сохраняет failed state; если диск недоступен, JSON footer передаётся в stderr.
- Атомарное состояние вынесено в `runtime_state_io.psm1`. Windows rename иногда
  возвращает ACCESS_DENIED при читателе без FILE_SHARE_DELETE. Немутационная
  DELETE-access probe отличает sharing conflict от реального запрета; heartbeat
  откладывается до существующего следующего такта, без добавления пауз. Финальная
  ошибка, read-only и ошибки самого WriteAllText не откладываются и не дают pass.
  Python children запускаются с UTF-8/-B; fallback JSON экранирует не-ASCII.
- Окончательный `runtime_supervisor_test.py`: десять реальных OS/process/file
  сценариев pass, источники неизменны, canary сохранён. Старый 8c91874b… source
  проходит только normal/footer/guard: семь случаев отклонены; в четырёх
  зафиксированы оставшиеся VM и/или guard до очистки самим тестом. Тестовые
  stdout-файлы заменили ожидание pipe EOF, чтобы измерять настоящий Process exit.
- Реальная пара app0592/ELF aea10675/QEMU d64f3013: окончательный обычный
  preflight завершил четыре цикла, два outage, HTTP/photo/weather и память;
  supervisor/workload/guard успешны, источники неизменны. Отдельный окончательный
  fault test испортил только host paths после готовности guard: supervisor
  корректно вернул 1, workload/guard/VM закрыты, VM helper exit 0, structured
  failed footer сохранён, дополнительная очистка тестом не понадобилась.
- Предварительные провалы стенда (локальная cp1252 при чтении UTF-8 state и
  ожидание pipe EOF) сохранены отдельно и не являются подтверждением работы.
  Тесты не заполняют диск; directory/read-only fault не объявляется точным
  воспроизведением ENOSPC. См. tests/RUNTIME_SUPERVISION.md и новый proof в
  Small_TV/qemu/parity. Полный новый H10, полный набор на новом QEMU и CYD
  PHY/cache расследование остаются обязательными следующими шагами.

## 2026-10-18 — независимые проверки сети и дисплея после reset

- Старый полный 0592/D64 завершился с failed QEMU: 18 других групп pass,
  network/DHCP/SNTP после reset pass, два ROM-баннера, но единственный
  after-reset кадр полностью чёрный. Все 553 frozen inputs совпали.
  Сырой failure и live H10 checkpoint сохранены коммитом bc9aff58.
- В отдельной ВМ с прежним неизменным helper воспроизведён partial frame
  624 -> 11629 RGB-байтов за 0.034633 гостевой секунды. Это гонка host capture
  с очисткой/отрисовкой, а не доказанный отказ SNTP или перезагрузки.
- По требованию пользователя результаты разделены на boot/network/display/
  source_integrity. Дисплей вынесен в small_tv_display.py, наблюдает только
  240x240 PPM и bounded clocks. Сеть использует прежний SDK/NTP observer.
  Network timeout не пропускает display; display error не стирает network.
  Метки FIXED_TEST объясняют исправление; production app/ELF/source не менялись.
- Пройдены независимые 9 panel +3 isolation, прежние 19 ELF/SNTP,
  8 consumer tests и 38 реальных report rejection controls. Отдельный native
  прогон original + три reconstructed завершён успешно на неизменном D64;
  это короткая проверка, а не полный suite или H10 acceptance.
- Новая ветка codex/small-tv-reset-display создана от bc9aff58. Live H10
  остаётся в small-tv-runtime-supervision с прежним frozen helper; новых
  QMP/RSP клиентов к нему нет. Полный новый прогон и CYD ещё не приняты.

## 2026-10-18 — строгие JPEG DRI/SOS/DQT headers и component IDs

- В новой sparse рабочей копии codex/small-tv-jpeg-headers подтверждены ошибки
  factory header parser. 22 начальных RV32 пробы показали 15 принятых
  повреждённых вариантов. Расширенный неизменный before/after harness: 133
  случая, 14 корректных, 119 повреждённых; app0592 принимает 115 повреждённых.
- T.81 Annex B задаёт DRI/SOS lengths, baseline scan fields, component identity
  и ненулевые quantizers. create_qt_tbl/jd_prepare получили FIXED_FACTORY
  comments с исходными адресами. Добавлен component_id[3] в хвост JDEC;
  DWARF реальных ELF подтвердил прежние offsets, RV32 size 120 ->124.
  IDCT/цвет/вывод не переписаны; изменены только два production source files.
- Успешная production сборка сохранена в firmware/development: app F1ADA8B4,
  ELF91E26EB2, source F849F5BF, DEBUG off/WARN. App1170032 bytes (+96),
  свободно365968 в app partition. Автоматическая прошивка платы не запускалась.
- Новый native gate: все 119 malformed reject до jd_decomp без рисования,
  все14 valid совпадают с factory по всему panel, включая arbitrary IDs0/17/255.
  Семь consumer rejection controls pass. Прежний JPEG inputs gate (41 +128DHT),
  новый133, public107 +35errors +7placements, host5531 и artifact6 pass.
- Один и тот же photo HTTP harness на том же D64: before0592 принимает пять
  из шести новых invalid header inputs (короткий DRI уже получает400),
  afterF1 возвращает400/absent для всех шести; custom RGB IDs
 0/17/255, byte-exact download, retries, cold boot и interrupted replacement pass.
  В before false только header_fields_rejected; failed evidence сохраняется.
- Gate включён в jpeg_inputs_oracle и оба publication consumers. Metadata
  UPSTREAM.json и CORRECTION_MARKERS обновлены. Это targeted acceptance,
  а не полный прогон новойF1, H10, CYD или физическая приёмка.
- Исторический полный561 app0592/D64 и H10 остаются живы в своих frozen
  деревьях; новыеQMP/RSP к H10 не добавлялись. После адресной валидации
  требуется отдельный полный набор и длительный workload на точной новой паре.

## 2026-10-18 — desktop/mobile настройки и холодное сохранение F1

- В отдельной sparse рабочей копии `codex/small-tv-browser-controls-verify`
  добавлены browser_controls_qemu.py и browser_controls_flow.mjs. Production C,
  HTML/JS устройства и archived firmware не менялись: F1/ELF91E2/sourceF849/D64.
  Собственный Chrome155.0.8059.80 получает настоящие страницы и API из отдельной
  writable QEMU; внешние browser origins запрещены, все данные синтетические.
- Пройден281UI check (236mutate/45cold),96настоящих UI POST и5storage/source
  checks. Обе ширины1280×900/390×844, все4темы/5GIF/3даты, три флага,0/100/37%
  day brightness,3RGB565 colors, night on/off/start18/23/stop12/5/brightness2/99,
  фото interval3/60 и masks0/1/17/31. Город с trim и ключ проверены в raw ABI;
  NTP со спецсимволами пережил submit/reload, после restore сохранён pool.ntp.org.
- После настоящих reload DOM совпадает с отдельными GET API. Cold stage работает
  в новом процессе ВМ/Chrome и не отправляет POST; все настройки сохраняются.
  Dirty flag настоящего matching ELF проверяется до и после raw read, чтобы не
  останавливать ВМ посреди записи. За пределами NVS/raw sector flash, включая
  photo banks, побайтно прежняя. Все25наблюдаемых inputs совпали. По одному ROM
  boot на каждый процесс, panic/console warnings/errors/page exceptions нет.
- Снимки desktop и mobile просмотрены: поля читаемы, горизонтального выхода нет.
  Новый тест описан в tests/BROWSER_CONTROLS.md; это отдельная частьH03/H04,
  не замена network/SNTP, display pixels/PWM, crop/upload, physical или H10 gates.
  В frozen full566/H10 F1 новый harness задним числом не добавляется.
- Новый H10 F1 работает в small-tv-jpeg-headers. Прежний0592 H10 намеренно
  остановлен после committed prefix/intent;182complete journal cycles и16pending
  events сохранены, last periodic report181 не переписан. Полные0592/full561 и
  F1/full566 продолжаются независимо; все их inputs сохраняются неизменными.

## 2026-10-18 — независимые cold LCD и network-without-LCD gates

- Новый display_boot_observer.py сравнивает весь RGB с реальным factory setup
  frame, не использует HTTP/SDK role flags/UART для готовности изображения.
  12unit cases отвергают black/white/wrong-color/partial/stale/truncated кадры,
  stalled clock и readiness на deadline; source hashes включены в unit report.
- Эталон из actual immutable factory5321/D64 AP services subtest, visually checked,
  RGB SHAACC588AB; compressed PPM2207bytes и provenance сохранены в fixtures/display.
  Весь parent full этим не принимался. Preliminary1+1cold VM pass, затем тот же
  harness выполнил20+20процессов: все40boot/display/source results pass,62inputs
  неизменны. Network явно not_run; host HTTP forwarding отключён.
- Network_without_display_qemu.py создаёт собственный профиль devices=[] с той
  же сетью и не меняет обычный профиль. Обе неизменённые прошивки прошли настоящий
  GET и новый SNTP до/после reset при полном отсутствии LCD. QOM подтверждает
  отсутствие устройства; screenshots/PNG/PPM отсутствуют. NTP1→2,4HTTP200,
  SDK UTC/wire maxdelta0.191694s; native connected/DHCP10.0.2.15/time_synced и
  AP false получены из matching ELF. По2ROM boot, no panic,59inputs совпали.
- Boot/display/network/source integrity остаются отдельными результатами.
  Это новые самостоятельные software gates частиH01/H02, не physical power,
  RF/WPA/PWM, доступность Internet, all-theme LCD или24h/H10 acceptance.
  Production/firmware и входы live full/H10 не менялись; новые тесты не внесены
  задним числом в frozen run. Сценарии и ограничения описаны отдельными MD.

## 2026-10-18 — повторные F1 browser photo и первоначальная настройка сети

- На той же F1/ELF91E2/D64 завершены два самостоятельных browser gates.
  Photo:23UI+6storage/source checks,27inputs неизменны; desktop/mobile crop,
  resize240×240, удаление синтетических metadata через Canvas,12multipart chunks,
  byte-exact HTTP/raw readback и новый cold process. Оба снимка кадрирования
  просмотрены; console errors/JavaScript exceptions отсутствуют.
- Wi-Fi:93UI+18role/storage checks,26inputs неизменны; discovered/literal-manual/
  manual-entry сценарии, отказ короткого пароля без изменения raw/AP/boot,
  настоящий DHCP/SNTP и cold persistence. В preflight каждой ветки сохранены
  ровно две ожидаемые console errors об HTTP400; исключений и прочих ошибок нет.
  Первоначальная слишком строгая archival-проверка ожидала пустой console и
  остановилась; после проверки фактических отрицательных сценариев правило
  исправлено на точное сопоставление этих двух записей. Гостевые тесты не менялись.
- Все восемь точных VM identities отсутствуют: один PID занят другим процессом,
  который не останавливался. OS cleanup proof,22photo и45Wi-Fi gzip artifacts
  сохранены отдельно; hashes оригинальных/распакованных/архивных bytes проверены.
  Full flash images в публикацию не включены, прежние BC68 proofs не заменены.
- Результаты проверяют browser/network/storage и не подтверждают LCD pixels,
  физический RF/WPA/PWM, полный набор или24h/H10. Production/source archive и
  все frozen full/H10 inputs остались прежними; новых клиентов к H10 нет.

## 2026-10-18 — JPEG DC/AC selectors по каждому компоненту

- В новой sparse рабочей копии `codex/small-tv-jpeg-selectors` от409f4333
  подтверждена ошибка factory иF1. Factory SOS0x42011eae..0x42011efa разрешает
  лишь00/11, mcu_load0x42011a9a выводит table ID из component class через snez.
  T.81 B.2.3/Table B.3 задают независимые DC/AC selectors0/1; mixed/shared/swapped
  таблицы допустимы. Восстановленный C повторял заводскую ошибку.
- Новый неизменный before/after RV32 harness:136valid и32invalid. Все136valid
  fixtures независимо декодированы Pillow12.3.0, каждый RGB pixel128/128/128;
  три отдельных240×240upload fixtures также проверены Pillow. Before F1 прошла
  только34/168:4valid и30invalid; два отсутствующих table1 доходили до entropy
  и очистки LCD. After B50D проходит168/168, validation не рисует, все guards
  вне8×8 сохранены;8negative evidence controls отвергаются.
- В jd_prepare/mcu_load стоят FIXED_FACTORY comments с адресами и спецификацией.
  Packed selectors занимают3tail bytes JDEC,124→128bytes по actual DWARF,
  offset123 использует бывший padding; все прежние member offsets сохранены.
  Native mcu_load встроен в jd_decomp: сохранён настоящий before/after листинг;
  пустая попытка standalone objdump отмечена как отсутствие symbol.
- Production сборка B50D15A1/ELF85FCCF00/sourceFC337C9B сохранена в development.
  App1170048bytes (+16), free365952, DEBUGoff/WARN. Из59compiled inputs изменены
  только tjpgd.c/.h; IDCT/color/output прежние. После уточнения комментария
  source manifest обновлён повторной incremental сборкой до запуска final gates;
  первоначальный manifest сохранён отдельно, stale archive не принимался.
- Прежние107public JPEG/35errors/7placements,41additional inputs/128DHT/133headers,
  host5531 и6artifact checks pass. Selector child обязателен в parent JPEG inputs,
  publisher и verifier. В строгом photo schema этих двух consumers также учтены
  прежние header_fields_rejected/custom_component_ids_published: старый список
  требовал22ключа, хотя header gate уже выдавал24. Теперь требуются26 с selectors.
- Один HTTP harness/helpers/D64: F1 отвергает три допустимых selector JPEG400,
  B50D публикует их200 с точным скачиванием и отвергает оба missing tables400.
  Все26after checks, cold/immediate-finish/interrupted persistence pass;
  пять отрицательных мутаций HTTP evidence отвергаются. Before позднее получил
  отдельный cold-stage start_upload timeout с WSAEventSelect warning QEMU:
  failure сохранён, причинная связь с JPEG не заявляется.
- Proof jpeg-selector-correction-20261018.json +42raw gzip, exact synthetic fixture
  bytes, исходники и logs сохранены. Все собственные HTTP ВМ завершены по OS
  run paths/identities. Старые F1 full/H10 пять exact identities живы17:59:39UTC;
  их inputs не менялись, новыхQMP/RSP кH10 нет. Новый полныйB50D и24h/H10
  ещё обязательны; physical RF/LCD/PWM, CYD и общая приёмка не объявляются pass.

## 2026-10-19 — terminal F1 full и прерванный H10 перед B50D

- Full F1 завершён18октября18:10:03UTC сexit0:19automatic groups pass,
  hardware_browser_soak not_run. Все566входов повторно совпали. Выполнен
  неизменённый publisher той же F1: он отвергает24успешных photo checks по
  старому требованию22. Сохранены failure/exit1, runtime success отдельно;
  эта ошибка schema уже исправлена в56010f00, новой публикации F1 не заявляем.
- H10 остановился без terminal footer: supervisor/VM исходные PID отсутствуют,
  workload/guard PID переиспользованы чужими процессами. По точным creation
  timestamps подтверждено отсутствие всех четырёх original identities;
  чужие процессы не остановлены, новыхQMP/RSP клиентов не создавалось.
- File-only analyzer проверил32inputs и canonical start record:640complete
  journal cycles,4pending events,10855.929945guest seconds; periodic report639.
  Start matches, но24h/terminal guard/steady windows не подтверждены. Отсутствие
  trend flags при insufficient data не означает отсутствия утечки. Причина
  прерывания неизвестна; stale running JSON сохранены как были.
- Сохранены72raw gzip, full/subreports/UART/QEMU logs, событийный journal,
  original freezes/launch/supervisor/guard и отдельные analysis/OS proof.
  Предыдущий goal turn дал новые доказательства, определяющие следующий шаг:
  запускать exact последнюю B50D сборку, а не считать старые прогоны её приёмкой.

## 2026-10-19 — область новой JPEG библиотеки и план следующих форматов

- Пользователь уточнил: сейчас требуется наиболее полная подходящая свободная
  библиотека для обычных `.jpg/.jpeg`, включая progressive/CMYK/разрядности.
  Исследуются поддерживаемые режимы, лицензия и реальные flash/RAM/stack limits
  C2. Выбор готовой библиотеки не объявляется автоматическим покрытием T.81.
- JPEG-LS, JPEG2000, JPEGXL и WebP по прямому запросу сохранены как отложенный
  план улучшений в WORKING_NOTES. Для каждого нужны version/license review,
  измерения ресурсов, codec module, independent fixtures/reference pixels,
  privacy/error handling, HTTP/storage и отдельный display test. WebP alpha и
  animation имеют отдельные критерии. В текущую реализацию они не добавляются.

## 2026-10-19 — квалификация памяти новой JPEG библиотеки

- В отдельной ветке `codex/small-tv-jpeg-library` от7f26262e подготовлен
  воспроизводимый host-стенд для libjpeg-turbo3.2.0/c85e6b90. Upstream tree
  остаётся неизменным; build.py экспортирует точный commit и применяет отдельный
  patch к копии. Сохранены исходные LICENSE.md/README.ijg, SHA и происхождение.
- Найдены две устранимые затраты: range-limit table не используется в прямом
  lossless без quantization/buffered mode; progressive резервирует пять iMCU
  строк даже при явно отключённом smoothing. Патч оставляет прежний путь для
  quantized/buffered клиентов. В test allocator используются минимальные
  virtual windows и hard cap фактических allocations; 5% headroom сам по себе
  проблему пяти строк не исправил.
- Итоговый MSVC/Release стенд использует общий static CRT `/MT` для probe и
  library, поскольку между ними передаются FILE pointers. Сборка не запускает
  upstream regression. Сохранены и не объявляются успехом промежуточные ошибки:
  PDB/compiler configuration, недопустимый restart13 для lossless row31 и
  недостаточный Pillow encoder MAXBLOCK. Исправлены Release try-compile,
  MCU-row restart62 и host encoder buffer1MiB соответственно.
- Итоговые25resource cases,924lossless cases (2–16bits,7predictors,point
  transforms),16truncated inputs,4optional controls и18budget cases прошли.
  Все successful bytes совпали с upstream; lossless — также с независимой
  integer sample formula. Ещё18non-flat baseline/progressive RGB/L/CMYK JPEG
  совпали по каждому byte с Pillow12.3.0/libjpeg-turbo3.1.4.1. Cleanup проверен
  и на четырёх budget failures после открытия1/3backing files.
- RGB16 lossless pool755907→29980bytes; color progressive8 укладывается в64KiB
  pools с host backing. Worst CMYK capacity460800bytes, logical writes2764800,
  поэтому обычная перезапись tempfile не моделирует NOR erase/wear. 12-bit
  lossy176345/347927bytes ещё требует адаптации. Общий RAM/stack/RV32 flash,
  RGB565/factory pixel parity, NOR backend, I/O faults/reuse и production
  HTTP/display/full/H10 остаются открытыми; текущая прошивка не заменена.
- Proof `jpeg-library-host-qualification-20261019.json`:13raw artifacts и
  983fixtures, build/source/executable hashes и полные результаты. Production
  B50D/85FC, его ресурсы и frozen full/H10 inputs не менялись. На14:33UTC
  исходные full controller38780 и H10 supervisor22868/workload29172/VM30196/
  guard40272 подтверждены через ОС; H10 на67циклах, acceptance ещё нет.

## 2026-10-19 — размер и стек JPEG-кандидата на настоящем RV32 toolchain

- Добавлен отдельный link-only стенд `rv32_footprint.py`/`footprint.c`.
  Экспортируется точный libjpeg-turbo3.2.0/c85e6b90 и bounded patch из b7bfb69c,
  SDK/production/frozen baseline не меняются. Compiler GCC15.2.0_20251204,
  RV32IMC/ilp32/soft-float/esp-base/Os, picolibc headers, SIMDoff.
- После static build и relocatable section GC:144626bytes executable sections,
  9680allocated read-only,0data/0bss. Независимый binutils size подтверждает
  сумму154306. Оставлены8/12/16 scanline APIs, arithmetic, progressive и lossless
  roots, header/start/finish/error paths; jpeg_CreateCompress отсутствует.
  Список unresolved libc/libgcc symbols сохранён без fake stubs. Это не
  production firmware size/heap acceptance и не bootable binary.
- Исправлена атрибуция `.su`: статические одноимённые функции сопоставляются
  по паре object/function в retained linker map. Quantizer12 fill_inverse_cmap
  имеет24928byte frame; jpeg_make_d_derived_tbl1376, IDCT16×16 656. Палитровый
  вывод не нужен RGB565 adapter, но compile profile/call chain/runtime stack
  пока не проверены; большой linked frame не объявляется реальным переполнением.
- Подтверждены источники расхода12-bit lossy RAM: range-limit45056bytes,
  YCC conversion tables65536bytes +pool overhead. Следующий вариант — точные
  immutable flash lookup tables либо эквивалентные вычисления; оценка должна
  учитывать полный firmware link и не исключать12-bit из пользовательской задачи.
- Исходный запуск GCC внутри sandbox получил DLL relocation error; установленный
  toolchain нормально работает вне этого ограничения. Повторение измерения
  оправдано уточнением stack attribution и добавлением независимой size-сверки;
  оба результата/логи сохраняются. Production/frozen full/H10 не перезапускались.
  На14:49UTC H10 supervisor сообщает112циклов без cleanup errors; это всё ещё
  running, не24h pass. Полный regression продолжает HTTP-сценарии.

## 2026-10-20 — 12-bit JPEG tables в read-only storage и завершение host-проверки

- Возобновлены изменения после прерывания с855e55507; они сохранены. Добавлены
  deterministic flash-table generator и отдельные patches:45056range +65536
  color bytes в static const, IMAGE spare chunks4096/1024 вместо16000/5000.
  Объекты/alignment/lifetimes/IDCT/color arithmetic не меняются. Реальный private
  table dump из pinned upstream C подтвердил все38912значения побайтово.
- Исправлен build helper: mixed patch внутри sparse worktree пропускал new
  headers; Git discovery теперь останавливается у parent export, enclosing repo
  отвергается и оба headers обязательны. Неудачные сборки не считаются pass.
- Прежний reserve оставлял richYCCK12progressive без памяти при cap64KiB;
  compact pools устранили это. Все48rich images и12truncated cases проходят;
  максимальный pool64869bytes, cleanup pool/backing завершён. Ещё25resource,
  924lossless,16negative,4optional,18budget и18independent Pillow cases прошли.
- Найдено излишне сильное требование теста: optional unlimited smoothingTRUE
  progressive420 может получить больше small-pool headers. Exact output сохранён,
  но205325 против204180bytes (+1145). Эта разница записана в raw metrics;
  FIXED_TEST ограничивает такой control behavior/cleanup, реальные hard cap cases
  остаются строгими. Два lossless quantization controls отвергнуты обеими libs.
- RV32 full decoder144394text+120272read-only=264666bytes; пять tables имеют
  r/R symbols и размер110592bytes, data/bss0. Это не firmware fit: adapter,
  libc/libgcc/final link, общий heap/task/interrupt stack и NOR scratch ещё нужны.
  Документированы scope/оставшиеся cases в tests/JPEG_FLASH_TABLES.md.
- Отдельно проверены прежние B50D full/H10:20Oct все5original identities
  отсутствуют, host не перезагружался с14Oct. Terminal full/H10 evidence нет,
  causeunknown. Canonical analyzer проверил32inputs,179complete journal cycles,
  5pending events и3034.241151guestsec; report178. Никакие stale running flags
  не объявлены pass. Сохранение baseline proofs выполняется в её собственной ветке.

- После сохранения86raw артефактов в baseline bf3618f2 новый supervised preflight
  завершил8cycles/4outages,32inputs unchanged, workload/guard exit0, cleanup[]
  (09:25:55UTC20Oct). Full581input freeze2996eea2 и H10prelaunch08e3366 сохранены
  до старта. Full controller29928 и H10supervisor22184/workload32636/VM32580/
  guard18268 подтверждены черезОС09:29UTC, launchers outside callerJob. VM
  SmallTV-131b35021705. Launch/checkpoint c8e56f932 в baseline branch. Старые
  каталоги19Oct не переименованы; новые20Oct покаrunning, не acceptance.

## 2026-10-20 — JPEG allocation/I/O failures и reuse после fatal error

- Добавлены отдельные host modules probe_faults и probe_reuse. В7точках считаются
  настоящие вызовы: allocation, temporary open/read/write/seek, input и output.
  Short transfers действительно выполняют частичную операцию до fatal error.
  Heap session сохраняет cleanup state через longjmp. После create failure —
  destroy/recreate, после остальных errors —abort и повторное использование
  того же объекта, как требует pinned upstream API.
- Прошли1227инъекций:346allocation,22open,169read,169write,317seek,40input,
  164output; ещё36truncated recoveries и12format transitions. Recovery pixels
  exact upstream.63разовых allocation failures восстановлены pool manager;
  не требовать ошибку там, где allocator retry штатно успешен.36create failures
  требуют нового объекта. После abort backing closed; final pool0, cap64KiB.
  Peak61421/session4096 — отдельные host measurement, не общий heap C2.
- На новых точных upstream/candidate builds повторены25resource/924lossless/
  16negative/4optional/18budget и48rich12-bit/12truncated/38912table entries:
  проходят. Прежние binary proofs не переименовываются. Начальная сборка
  закончилась до последнего изменения runner C; для acceptance созданы новые
  v2directories с текущими hashes. Новый gate и raw evidence сохранены отдельно.
- Production app B50D, frozen ELF/resources/SDK/full/H10 не менялись. На10:05UTC
  H10 supervisor сообщает100cycles, cleanup[]; terminal acceptance ещё нет.
  NOR backing/износ, RGB565, final app link и hardware gates остаются открытыми.

## 2026-10-20 — отдельный модуль цветов и RGB5652–16-bit qualification

- RGB888↔RGB565 helpers перенесены из settings.c в app/media/color_convert.c,
  общий header подключён через settings.h без изменения callers. Pure row API
  gray/RGB/CMYK2…16бит использует caller buffers, явную CMYK polarity, native
  samples и display-owned SPI byte order. Проверяются range/size/address wrap/
  overlap до output writes; нет heap/float/I/O. Gray и8-bit path сокращают работу,
  black component читается один раз наpixel. CMYK generic, не ICC transform.
- Literal factory helpers сверены по manifest bytes:65536expand/3304pack,
  без LCD/format adapters.61host rows/549676samples и141actual RV32 rows exact;
  65host+68RV32negative cases не меняют buffers, включая32-bit address wrap.
  66realJPEG,18independent Pillow RGB565 cases pass. RV32 standalone540code+
  4read-only bytes, frame96, no unresolved stubs. Row API ещё не вызывается app.
- Полная DEBUGoff сборка C8FD1170032bytes, app partition1536000; ELF368AB7B5,
  sourceE34BEBEB. Saved development app/bootloader/manifest. СтарыйTJpgd остаётся,
  новая libjpeg не включена.5531native checks повторены на окончательных sources.
- Scoped display gate2factory+2native cold processes: full setup pixels exact,
  62inputs unchanged, network not_run. Отдельный network withoutLCD gate:
  original/native HTTP и freshSNTP до/послеreset,59inputs unchanged, display
  not_run. Все свои scoped ВМ закрыты. Первый sandbox display запуск получил
  QMP startup timeout; original PID9856 отсутствует, failed report сохранён.
  Retry вне sandbox —новый directory и pass. Причина timeout не установлена.
- Proof color-conversion-validation-20261020.json сохраняет reports/raw frames,
  synthetic fixtures и matchingELF. Full/H10 B50D в другом tree не изменены;
  C8FD не объявляется full/24h/physical accepted. Следующие работы: codec adapter,
  NOR temporary backing иwear policy, общий heap/stack, privacy/HTTP/LCD/full/soak.
- Read-only OS checkpoint10:23:31UTC подтверждает все5original B50D full/H10
  process identities; H10running149cycles/cleanup[], full безterminal footer.
  Собственных scoped display/network ВМ больше нет. Это checkpoint, не24h pass.

## 2026-10-20 — read-only JPEG scratch/cache layout на4MiB

- Проверены настоящие lengths пяти native animation containers и полные
  protected upload/weather/status slots. Свободные erase-aligned области:
  121сектор между app/assets,112в animation tails и29после icon banks. Всего262.
  Measured backing113+metadata2+пять RGB565 caches145=260, spare2сектора8KiB.
  Это позволяет проектировать decoding при upload/invalidation, без повторных
  scratch writes накаждом slideshow pass. Runtime такого cache ещё не написан.
- Добавлен отдельный read-only planner и contract: manifest/payload hashes,
  partition ownership, header/frame bounds, FF tails после установления ownership,
  sparse nonoverlapping allocation. Все1024сектора распределены protected/free.
 30unsafe cases/4controls pass, images unchanged. Удлинение animation0на2сектора
  пересчитывается ивлезает,3сектора —refusal. CLI не заменяет output и не создаёт
  его при unsafe layout. Первый positive padding test сам пересёк границуphoto;
  payload guard отказал корректно, FIXED_TEST делает mutation однобайтной.
- Plan4508149b...51ad9ca6 и raw reports/logs сохранены. Допуск460800относится
  к measured matrix, не всемуT.81. Нужны NOR backend/RMW/fault/cold recovery,
  atomic metadata, source/codec/layout keys, immutable resource guards и физические
  erase counts. C8FD source/firmware, shared SDK и frozen B50D не менялись.


## 2026-10-20 — двусторонняя сверка переноса

Просмотрены все16 reference modules и26 app C modules. Явная карта
reference/correspondence.json:176 factory (120app/56SDK),168native app,
13TJpgd+116cJSON,11assembly-only codec entries.198direct factory callees
вне выбранного экспорта перечислены, а не объявлены автоматически перенесёнными.
Найдены HTTP-404 (Host/root/absolute redirect), CITY-REINIT (updateCity снимает
factory theme-init latch), HTTP lifetime multi-peer test gap, RESET/DC pulls
и устаревшая coarse navigation. Подробности reference/BIDIRECTIONAL_AUDIT.md.
Checker+10tests проверяют пропуски в обоих направлениях/опечатки/stale inputs,
не доказывают semantic equivalence. В native run добавлен обязательный gate.
Firmware C8FD пока не менялась. Frozen B50D full завершился exit0 в10:56UTC;
H10 всё ещё running, никаких новых QMP/RSP к нему не подключали.


## 2026-10-20 — terminal B50D full suite

Полный regression B50D/ELF85FCCF/sourceFC337C завершён:19automatic groups
passed, hardware_browser_soak not_run, controller exit0/terminal_passed
2026-10-20T10:56:30.2074153Z. Исходный report4.5MB иfooter сохранены без
изменения байтов (gzip) вqemu/parity/raw/b50d-full-20261020; certificate
qemu/parity/b50d-full-terminal-20261020.json. Это результат B50D, неC8FD/54F4
и не24h H10. Frozen tree/snapshot не редактировались. H10 supervisor11:56UTC
всё ещё running,396cycles,cleanup_errors[]; наблюдение только через его файлы.


## 2026-10-20 — исправлен найденный HTTP-404

Factory0x4200d4be: AP Host/нетHost ->root200, foreignHost ->absoluteAP302.
Наш unconditional relative redirect исправлен; factory substring bug с именем
192.168.43.1.example.invalid подтверждён в реальной factory VM и исправлен.
STA сохраняет local redirect, поскольку setup AP там не активна. Два старых
теста закрепляли неверное поведение, исправлены с FIXED_TEST. Новый тест
до изменения кода падает; после —5608native checks и10audit controls pass.
Новый network-only captive_qemu.py:factoryAP/nativeAP/nativeSTA,15HTTP cases,
59inputs unchanged, noLCD/noRSP, all3owned VMs stopped. Proof+before/failure/
after logs+matchingELF: qemu/parity/captive-portal-validation-20261020.json.
Production archive:app54f441af...,1170240bytes/free365760; ELF83ed2a7a...,
source9c16c56a...; DEBUGoff, oldTJpgd, libjpeg notlinked. Physical board,
full suite и24h новой54F4 не запускались. B50D full/H10 ей не приписывать.
Карта refreshed только для повторно просмотренного server.c; source-only
coverage не превращается вsemantic proof. Далее CITY-REINIT, AP multi-peer
HTTP lifetime и RESET/DC pulls; остальные оговорки вBIDIRECTIONAL_AUDIT.md.

Archive integrity:6tests pass; image checksums/partition MD5/current compiled sources/media/34routes/original dump unchanged. Report preserved with captive proof.


## 2026-10-20 — интеграция завершённых worktree

Объединены jpeg-library B3FC и боковые selector/header/H10/reset/flash-full
records; код54F4/source9C16 не меняется.277review inputs exact,5608native,
10inventory controls и6artifact checks pass в отдельнойintegration-worktree.
Единственный конфликт WORK_LOG разрешён сохранением актуального текста:
входящие непустые строки уже есть. Подробности Small_TV/WORKTREE_INTEGRATION_20261020.md.
Удаление7завершённыхworktree —после verified local archives иpush main;
active selector H10/CYD инезакоммиченные C3/ESP8266 сохраняются.

## 2026-10-20 — очистка после опубликованной интеграции

В main опубликован 678f6ac37 с проверенной интеграцией Small TV. Удалены семь
завершённых рабочих копий и временная integration-worktree; все ветки сохранены.
Полные локальные архивы семи копий проверены до удаления и повторно по SHA-256
после него: .build/worktree-retention/integration-20261020/. Shared SDK сохранён.
В реестре остаются основной checkout и семь активных/незавершённых worktree;
H10/CYD не прерывались. Пользовательские изменения root совпадают с начальным
inventory. Код и firmware не менялись; тесты повторно не запускались.
Подробности: Small_TV/WORKTREE_INTEGRATION_20261020.md и машинный отчёт.

## 2026-10-20 — план следующего этапа

По запросу пользователя сохранён IMPROVEMENT_PLAN.md с порядком и критериями:
CITY-REINIT → JPEG/NOR integration → AP lifecycle → hardware → full-image audit
→ приёмка окончательной версии. Работа в отдельной small-tv-improvement-plan;
активный H10 B50D/source/SDK/snapshot не меняются. Первое исправление — город
и команда переинициализации темы, согласованно опубликованные под mutex.

## 2026-10-20 — CITY-REINIT исправлен

Ассемблер0x4200f3cc очищает theme-init latch0x3fcc39e9. Новый settings_update_city
публикует только city/country и transient theme revision под одним mutex, не
откатывая более свежие theme/brightness/photo settings из раннего HTTP snapshot.
Одинаковые команды перерисовывают тему без лишних flash commits. Общий helper
debounce заменяет повторяющиеся generation/dirty/deadline операции без изменения
правил остальных настроек. Маркеры FIXED_RECONSTRUCTION и комментарии добавлены.

На pre-fix51cd native city assertion падает. После исправления 5806native,
10correspondence controls, 6artifact checks pass. Четыре реальные QEMU темы:
8city commands, init/complete output pass. Отдельные photo-city и прежняя
photo-theme: original blank bug наблюдён; native full frame57600pixels exact,
0different. Network-only:15HTTP cases/AP/STA, безLCD. Cold LCD-only:2factory+
2native processes, exact setup frame, без сетевого readiness criterion.
Все15финальных VM завершены owners; failed harness attempts также сохранены
и очищены отдельно. Inputs unchanged. Старый H10/SDK/snapshot не менялись.

App3e030c1c...,1170432bytes/free365568, ELF54293e97..., DEBUGoff/TJpgd;
архив в firmware/development/small-tv-esp32c2-reconstructed. Proof94raw:
qemu/parity/city-reinit-validation-20261020.json. Полный suite/24h/physical для
этой app не выполнялись. Подробности tests/CITY_REINIT.md; план обновлён.
Следующий этап — NOR-aware JPEG scratch/cache и безопасная metadata publication.

## 2026-10-20 — базовый NOR слой для JPEG

Активная цель: выполнить весь IMPROVEMENT_PLAN, не ограничивая её одним JPEG
стендом. Завершён следующий самостоятельный checkpoint, не весь пункт2:
storage/jpeg_nor.c/.h — reusable portable core с trusted extent allowlist,
overflow/alias/bounds checks, одним sector cache4096, sparse logical I/O, RMW,
erase/program verification, explicit sync/abort и poisoned failure state.
Данные не считаются атомарными: следующий metadata слой должен invalidate cache
до записи и publish только после полного успешного flush/hash verification.

MSVC /W4 /WX:3000random operations при128/256page geometry,83partial I/O/silent
erase/program failures с reopen и сверкой protected bytes всего4MiB,7реальных
layout stores pass.6скомпилированных mutants runtime-rejected. Первый allowlist
mutant escaped: corpus не проверял final allowed boundary. FIXED_TEST добавил
эту границу/полностью чужой final range; прежний report/exe/source сохранены.
Текущий core уже правильно отвергал этот случай, production bug не объявлялся.

Настоящий GCC15.2 RV32IMC/ilp32: code1848,static writable0,handle4352 включая
cache4096; max single stack frame304. Первичный запуск compiler в sandbox
не прошёл Windows loader; тот же tool вне sandbox собрался без source changes.
Это object/ABI compile measurement, не execution/whole firmware memory proof.
Proof78raw: qemu/parity/jpeg-nor-core-validation-20261020.json.6artifact checks
подтвердили unchanged app3E03; physical flash/SDK/H10/QEMU не менялись.
Далее ownership guard, atomic metadata/cold recovery, ESP-IDF transport/budgets,
shared scratch subfiles и реальная libjpeg integration. Остальные пункты плана
и full/24h/hardware acceptance остаются открытыми.

## 2026-10-20 — portable ownership guard для JPEG flash

После status-only turn план/чистая рабочая копия revalidated; выполнен следующий
самостоятельный checkpoint, не вся production integration. Новый readonly
storage/jpeg_guard проверяет точную ALL-partition map/geometry, classified
sector ownership и streaming SHA27immutable payloads. Новая crypto implementation
не добавляется: provider API, host BCrypt, future ESP-IDF mbedTLS adapter.

При review найден недостаток payload-only identity: прежние hashes могут
сохраниться при новом использовании свободных хвостов. Поэтому tools/
jpeg_guard_layout создаёт matching const descriptors и отдельный stamped native
assets copy. Canonical ownership ID включает resources/map/allocation. Stamp64
на0x28f720 находится внутри уже protected final-sector padding анимации; spare
8KiB не расходуется, все photo/resource payloads сохранены. Legacy/unmarked или
чужой stamp запрещает authorization. Pipeline никогда не перезаписывает занятое
padding/исходные images. Runtime guard не модифицирует flash и не принимает
whole-assets hash после user uploads. Это mismatch guard, не authentication.

MSVC /W4 /WX:49invalid layout,84resource/stamp corruptions,3050read faults
(2954partial callback ordinals+96silent corruptions),3010SHA callback failures
pass; cleanup/readonly invariants проверены. Generator12rejects/12controls,
включая changed layout со старыми27payloads.10compiled mutants runtime-rejected.
Ранний generator test ошибочно считал icon hashes уникальными; FIXED_TEST
проверяет кратность, прежние failed log/source сохранены. Guard bug не было.

GCC15.2 RV32IMC/ilp32:core1150code/static writable0,generated const1448,
maxsingleframe320+caller96 (не whole call-chain stack); успешная проверка
752121bytes/2954read calls. Только ET_REL/ABI compile, не RV32 execution.
Proof85raw: qemu/parity/jpeg-ownership-guard-validation-20261020.json.
6artifact checks:app3E03/TJpgd и archive неизменны.6oldH10 original process
identities подтверждены readonlyCIM; SDK/QMP/RSP/snapshots/physical flash не
менялись, новыхVM нет. Working log/plan/audit обновлены.

Далее atomic metadata invalidation/publication/cold recovery, затем полный
ESP-IDF partition enumeration/SHA/authorization adapter, matching stamped
assets build с сохранением user photos/settings, budgets/shared subfiles и
libjpeg bridge. Guard/NOR пока не включены в CMake, production capabilities
не выдаются. Полная цель и остальные network/hardware/audit/final gates открыты.

## 2026-10-20 — atomic JPEG cache journal и cold recovery

Previous goal turn — progress:78e817f21; текущие branch/чистота/план перепроверены.
Новый portable storage/jpeg_journal.c/.h: два4096byte banks snapshot всех5entries,
explicit LE/CRC/commit page, layout/codec/source/frame identities. Durable invalid
до in-place frame/source writes; publish вызывает mandatory flush/physical SHA
до первого metadata erase. Другой bank сохраняет last confirmed head. При I/O/
read-back failure handle poisoned; abort/cancel без записи. Повторный begin для
durably invalid entry не стирает flash ещё раз.

Cold open выбирает newest structural snapshot даже при foreign IDs и не
возвращает старый matching cache. Equal sequences fail closed; MAX counter не
wrap. Отдельно закрыт опасный fallback: повреждённый newest invalid record после
частичной перезаписи frame может вернуть older ready metadata. Поэтому каждый
lookup требует full physical frame SHA; lookup error не очищает только RAM flag
и не позволяет следующему begin пропустить durable invalidation.

MSVC /O2 /W4 /WX: actual NOR core и реальная planner mapping, synthetic full
frames5×115200bytes.4270/2410callbacks на update при128/256pages;5fault modes
на каждый ordinal =33400cases. Partial error, silent partial/corrupt read и
hard cuts до/в середине/после операции. СвежаяRAM после каждого cut; ready всегда
равен целому old/newframe, остальные4frames и protected flash не меняются.
769metadata corruptions(512body/256footer bytes+explicit dangerous fallback),
6boot-read failures,14state/argument/foreign/sequence rejects pass.12compiled
mutants runtime-rejected в quick state/corruption mode; full fault gate отдельный.
Independent Python struct/zlib/hashlib parser проверил4реальных snapshots и все
source/pixel hashes.3.17billion internal assertions не являются coverage claim.

При RV32 compile оптимизирован open: удалить expected footer copy256bytes,
проверить fields/padding непосредственно. Open frame704→448; тот же full33400
gate и12mutants заново pass. GCC15.2 RV32IMC/ilp32 ET_REL:code2976,const24,
writable0,handle1032(включаетbody512),maxsingleframe448. Caller/callback/NOR/
IRQ/task stack и physical timing не измерены. Precompact source SHA связан с
старым report; outputs/ABI/source pins сохранены в118raw proof:
qemu/parity/jpeg-cache-journal-validation-20261020.json.

App3E03/TJpgd archive unchanged,6artifact checks pass;6original oldH10 owners
readonly-confirmed. Physical flash/QEMU/SDK/snapshot не менялись; новыхVM нет.
Journal пока не в CMake и не связан с upload. Он не решает atomic source JPEG
replacement сам по себе. Следом authorized ESP-IDF/SHA transport и budgets,
shared scratch subfiles, actual source/cache workflow и matching stamped assets
build, затем real codec/final tests. Полная цель IMPROVEMENT_PLAN остаётся открыта.

## 2026-10-20 — guarded ESP-IDF transport и исполнение target probe

Previous goal turn — progress:93ac71929; чистая branch/активная цель/план сверены.
Новые storage/jpeg_transport.c/.h и jpeg_espidf.c/.h: shared physical calls/bytes/
erase/time budgets для всех ports, preflight ranges/readonly/alias/overflow,
epochs/revocation после ошибок и authorization attempt. Перед/после synchronous
I/O deadline; отдельный check для RAM/codec rows. Нельзя отменить уже выполняемый
SPI callback; owner abort/reopen cached NOR/journal после fail и drop borrowers
перед reuse port memory. Создание нового port не обнуляет общий budget.

Проверены реальные pinned SDK APIs, а не придуманный shim. get_physical_size
отличается от image get_size; обе ёмкости сверены. SDK iterator теряет unknown
raw flags, поэтому discovery читает whole3KiB raw table, SDK MD5/canonical tail,
полные flags +ALL SDK partitions/chip/known flags/erase size. Discovery read/call/
time вычтены из startup limits. SHA public PSA setup/update/finish/abort, timer
monotonic esp_timer, без software delays. SDK tracked tree clean, mbedTLSce3f348…
при SDK9a97f6…; core/backend код не меняет SDK/H10.

31host cases MSVC /O2 /W4 /WX: реальные resource hashes BCrypt, fake clock и
independent raw counters. Quota sharing даже при создании второго port после
I/O; readonly writes внутри valid scope; pre/post/final-hash deadlines, I/O
faults, epochs, revoke, ranges/alias/clock bounds.14compiled mutants runtime-
rejected. Host counters не объявляются coverage percentage/hardware endurance.

Standalone ESP-IDF probe впервые связывает и исполняет NOR/guard/transport/PSA
на RV32 QEMU. Final app6cb29771…,135504bytes/ELF pinned, archive в firmware/
development/small-tv-storage-probe. Build captures19source/generated hashes
BEFORE compilation, verifies after, deterministic source JSON; прежняя successful
probe494ac7…/ELF сохранена в raw. Первая CMake include попытка имела Windows
escape error; FIXED_TEST нормализует path. Две harness pre-launch ошибки
(network=none, missing firmware argument) исправлены/сохранены с original scripts.
Они не дошли до создания VM и не являются firmware failures.

Final target gate:4variants/5actual processes. Matching writes cross-sector and
0→1RMW:157callbacks/53314read/1024program bytes/1erase, exact4MiB comparison
only35expected changed bytes. Process quit/disk flush +fresh emulator reads
persistent bytes,0program/erase. Unmarked, valid-MD5 unknownflags0x80 и extra
partition в scratch отвергнуты без изменения flash. Каждый owner завершён по
своим QMP name/process handle; earlier10successful processes также stopped.
Frozen47files checked unchanged; no RSP/guest memory/PC patches, network/LCD
criteria отсутствуют. OldH10 six original process identities readonly-confirmed.

Exact target flag replay:transport2324code/frame240, ESPbinding1448/frame416,
writable0; executed globals storage536, ports152, NORhandles4352. Это не whole
heap/task stack или flash delta полной UI+libjpeg.155raw proof:
qemu/parity/jpeg-transport-validation-20261020.json. Main app3E03/TJpgd unchanged,
6artifact checks pass. Plan/notes/audit updated; весь IMPROVEMENT_PLAN активен.
Далее shared scratch subfiles без4KiB rounding per-array, actual libjpeg NOR
matrix/traffic/bounds, actual upload/source/journal/build integration и final gates.

## 2026-10-20 — shared scratch и actual libjpeg/NOR qualification

Продолжен пункт2 IMPROVEMENT_PLAN, вся цель остаётся активной. Предыдущий turn
ответил на вопрос о плане без нового implementation checkpoint; продолжение
прочитало текущие build.json/logs и перешло к проверке готовых reference-v2 и
nor-v2, не перезапуская сборки из-за утраченного observation/session output.

Добавлен storage/jpeg_scratch.c/.h:16byte-granular subfiles над ONE NOR/cache,
без padding каждого файла. Four115200arrays fit exactly460800. First-fit/whole
request bounds, initialized prefix, no writable gaps/unwritten reads, monotonically
increasing by-value tokens over close/abort/reopen; overflow fails closed.
Mandatory checkpoint даже при dirty RAM hit; ошибка poison всего job,
cleanup/abort без I/O и flush временных данных. Heap/global writable0.
Pinned actual jmemmgr first_undef_row contract проверен настоящими codec traces.

Тронутый host probe разделён по назначению: общий capped pool allocator,
независимый stdio backing oracle, NOR bridge и strict physical model.
Модель проверяет page/1→0/erase, whole outside-scratch canaries, не откатывает
partial writes и сохраняет physical bytes между двумя decode на одном object.
Её8MiB host arrays не объявляются памятью ESP32-C2. Library patches/production
UI app3E03/TJpgd, existing targetprobe6cb29771… и SDK не менялись.

Native final16432assertions/5000random operations(128/256page),134partial
error/silent cases, fragmentation/stale tokens/deadline and exhausted ID space;
13compiled unsafe mutants runtime-rejected. FIXED_TEST: ID exhaustion terminal,
поэтому тест выполняется последним; original failed source/log сохранены.
First NOR build failed missing common hook include; CMake own include добавлен,
failed original CMake/log и финальные успешные source-pinned builds сохранены.

Actual libjpeg/NOR:25resources/924lossless/16invalid/4optional/18budget;
38912table entries,48non-flat12-bit/12truncated;18Pillow independent pixels pass.
1227logical fault recoveries,36truncated и12format transitions pass.
Pillow отсутствовал в SDK Python: использован готовый bundled Python/Pillow,
SDK packages не менялись. Ошибка первого запуска сохранена. Artifact script
сначала вызван без required --output; correct invocation6checks pass, отдельные
correspondence10controls pass. Ошибочные CLI не являются failed firmware runs.

2238real partial physical errors с I/O return error: all2010small callbacks,
4full-size fixtures по57sampled calls. First abort closes everyfile, recovery
sameJPEGobject/retained permanent pools/partial physical NOR имеет exactpixels,
final library pool0. Arbitrary silent read corruption без per-block hash не
обещается detect. Separate NOR tests verify silent program/erase readback.
Rich240×240CMYK12:460800scratch,16850432read/3780608program bytes/923erase calls.
Это конкретная модель, не universal limits/timing/hardware endurance. Integration
должна сохранять RGB565 cache и не повторять такой decode при каждом показе.

RV32IMC/ILP32 object1240code,576handle/24token/32region, maxindividualframe48;
не target execution/final link/whole heap/stack. Raw proof и exact hashes:
qemu/parity/jpeg-scratch-validation-20261020.json. SDK tracked clean; six oldH10
original process identities readonly-confirmed. Их ВМ/QMP/RSP/source не трогались.
Следом expanded sampling/capacity (460800 всё ещё only fixtures), production
budgets, actual source/upload journal+hash/cache workflow и matching assets
deployment, затем native codec link/HTTP/LCD/full/24h/hardware acceptance.

Во время checkpoint пользователь уточнил политику невозможных входов: отказ с
правильной причиной или preflight rejection до decode. Сохранено в плане/notes:
unsupported, invalid/truncated, RAM/scratch limit и I/O не смешивать; required/
available для resource limit, без публикации partial cache. Это следующий
контракт интеграции; текущий checkpoint не объявляет его уже реализованным в UI.

## 2026-10-20 — сокращение JPEG NOR traffic без потери коэффициентов

Предыдущий goal turn — progress: focused commit1261d1444. Продолжение прочитало
clean worktree и native/параметры jmemmgr. Планировался error/resource preflight;
пользователь спросил, можно ли уменьшить объём записей. Выполнена эта оптимизация,
preflight остаётся следующим шагом, весь IMPROVEMENT_PLAN активен.

Новый отдельный codec/jpeg_coefficients converter: DC complement two's-complement,
AC complement sign/magnitude, INT16_MIN через reserved negative-zero. All65536values
обратимы, включая invalid intermediate data. Correct successive DC/AC refinements
программируют1→0; DC нельзя трактовать как AC.256byte conversion buffer, прежние
4KiB cache и scratch capacity. Selected pinned direct progressive non-quantized
JBLOCK path; другие backings raw. Host environment0/1 для same-executable A/B.

Initial pack-only prototype улучшил richCMYK12 program3780608→3041536/erase923→225.
Найдены лишние первые RMW при восстановлении uninitialized old bytes. Final
15byte bitmap готовит каждый113sector лишь раз/job с logicalFF через тот же
cache/buffer; соседние valid bytes потом не очищаются. Reset bitmap после abort,
physical flash сохраняется. Checkpoints/I/O failures распространяются; actual
short transfers затрагивают partial data. Final program2582784(-31.68%), erase113
(-87.76%), read16850432→13532672/calls61729→49114; pool42275/scratch460800 те же.
Flat tradeoff честно измерен: CMYK program460800→2048, erase0→113. Это не universal
wear/timing improvement, whole RAM или включение нового codec в UI.

Native19726488assertions/4194304value-position cases/983040independent refinement
steps pass;7pure mutants+4compiled integration mutants caught by exact pixels or
repeated erase in first/reused job.18traffic cases(14rich/4flat), 25resources/
924lossless/16invalid/4optional/18budget,38912tables/48rich12bit/12truncated и
18Pillow independent images pass.1227logical errors/36damaged recoveries/12format
transitions;1573physical partial errors(all1345small,4full-size по57sampled) pass,
same object/partial flash/exact recovery pixels, no leaked stores/pool. Silent
arbitrary read corruption не заявляется. RV32converter234code/static0/frame0,
не target runtime или full app link. Intermediate versions сохранены отдельно.

6artifact/10map controls pass. Main3E03/TJpgd/probe6cb unchanged. SDK tracked clean,
frozen47files и6oldH10 original owners readonly-verified, no QMP/RSP/device actions.
Proof qemu/parity/jpeg-coefficients-validation-20261020.json. Далее precise
unsupported/invalid/resource/I/O errors и preflight с required/available, expanded
sampling/capacity, actual native upload/source/journal/cache/codec integration
и target link/heap/stack/time/HTTP/LCD/full/24h/hardware. Не объявлять цель закрытой.

## 2026-10-20 — portable decoder API, resource preflight и точные отказы

Предыдущий turn — progress, focused commit44f106cb5. Clean worktree проверен;
продолжена полная цель IMPROVEMENT_PLAN. Вместо дальнейшего изменения CLI
probe перенесён настоящий decoder binding в codec/jpeg_decoder.c/.h и jpeg_memory.c,
private header отдельно. Input/read/check и provisional RGB565 row callbacks,
per-instance capped allocator/backing; без network/LCD/ESP-IDF I/O. Existing
RGB565 converter переиспользуется. Никаких mutable globals в binding.

Actual virtual-array requests wrapped: padded rows/columns, sample precision и
JBLOCK size. Min-window policy такая же, как qualified jmemsys. Whole sum проверяется
в realize до любого backing open. При460799 вместо460800 точные required/available,
opened/read/write/rows0. Legal noninterleaved4x4 CMYK на самом деле требует524288;
при460800 отказ до backing. Positive rare-sampling oracle повышал host limits до
262144pool/1MiBbacking; это не native fit и не исключение форматов ради зелёных тестов.

Раздельные unsupported/invalid/truncated/dimensions/pool/allocation/backing/input/
output/cancel/time/quota reasons; cause library enum/detail/value и callback code
сохраняются отдельно. Allocation retry может успешно восстановиться; final fatal
классифицируется по последнему отказу, pool cap не выдаётся за неизвестный free heap.
Огромный declared dimension не помечается corrupt из-за internalIJG limit65500;
height0/DNL отличается от invalid width0. Неприменимый msg_parm не становится
параметром ошибки. Provisional rows нельзя publish до OK; настоящий HTTP/journal
workflow здесь ещё не интегрирован, это остаётся отдельной обязательной работой.

Mutable setjmp state/rows/source и16backing handles в owner context. Abort/reuse
сохраняет успешно созданный JPEG object; recreate только после failed creation.
Pre/post callback checkpoints. Post-open deadline может прервать библиотеку до
b_s_open=true; после её abort loop explicit cleanup закрывает orphan без обращения
к освобождённому owner/flush. Ошибка close тоже не превращает decode в успех.

Final host contract:63positive RGB565 cases/7limits/10negative/1197callback failures
и12format transitions. Все2–16lossless precisions, gray/RGB/CMYK/YCCK8/12,
arithmetic8, fullCMYK12,411/440/410/4x4. Exact upstream samples +independent Python
RGB565 arithmetic. Actual partial stdio transfers, same-object recovery после
creation, no open handles/final requested heap0.6compiled unsafe mutants runtime-
rejected, в том числе пропуск complete preflight, неверный размер, ложные bad-JPEG
причины, stale job и post-open orphan leak. Compiler/loader errors/crashes не
засчитываются как caught mutants.

Generator first compile обнаружил J12SAMPROW signedness; исправлен настоящий
J12SAMPLE, original source/log сохранены. Strict C11/RV32 first build обнаружил
ненужный private jinclude/setenv dependency и misleading indentation. Подключены
только нужные standard/private ABI headers, formatting исправлен без suppressions.
Host build freeze включает private/generated JPEG headers ДО compilation.
Финальные source hashes отдельно от всех промежуточных успешных/failed stages.

Host context5232, fullCMYK12pool42275:47507requested allocator bytes, не actual
malloc metadata/stdio/whole RAM. RV32 context4984, decoder2384code+311rodata,
memory1870code/color586code; binding writable static0. Largest individual binding
frame144/color96, не complete library/task stack. Real relocatable RV32 link
148672code+120581rodata, JPEG symbols resolved; libc/libgcc/SDK/startup ещё external.
Это не bootable firmware/target execution/final UI app delta или memory/time fit.

Proof qemu/parity/jpeg-decoder-validation-20261020.json.6artifact/10map controls
pass. Main app3E03/TJpgd и transport probe6cb не менялись. SDK tracked clean,
frozen47files и6oldH10 original owners readonly checked; no QMP/RSP/physical board.
Далее portable actual NOR/packed backend для нового API, target probe/runtime,
source/upload/journal/physical hash/RGB565 cache/matching assets/native UI workflow,
total heap/task stack/time/HTTP/LCD/network/full/24h/hardware. Вся цель активна.

## 2026-10-20 — actual NOR backing нового API и C2 target execution

Продолжена цель IMPROVEMENT_PLAN послеccb29b1db. Добавлен отдельный
codec/jpeg_backing: соединение portable decoder с existing scratch/NOR и
coefficient converter, без повторения storage core или знания LCD/network.
Caller-owned bitmap подготавливает каждый temporary logical sector один раз;
сохраняются initialized соседние files и physical padding. Raw byte sample files
не конвертируются; homogeneous mode обязателен. Prefix/bounds/alignment/alias/wrap
проверяются до first-use clearing. Monotonic handles и constant borrowed capacity
переживают job reuse. Close/abort не flush и не зависят от expired budget.

Обнаружено при связи с transport: неуспешный callback может означать глобальный
time/quota stop. Добавлен общий decoder helper: сохранить callback code, опросить
owner, затем лишь при отсутствии более точной причины вернуть generic I/O.
Inactive transport.check возвращает STATE, поэтому target owner сохраняет
первопричину из transport.last_error. После cleanup decoder diagnostic сохраняется;
last_error адаптера отражает последнюю операцию, включая successful close.

Final native unit15273assertions/134partial+silent physical faults. Четыре полных
arrays/refinement и interleaved boundary paths, raw bytes, stale IDs, stopped RAM
и stopped first-use sector, invalid descriptors до I/O.6compiled mutants runtime
rejected. First RAM-checkpoint mutant survived because underlying scratch also
checked already-cached reads; добавлен действительно отсутствовавший first-use
dirty-sector cancellation test. Exact earlier unit source/log сохранены.

Новый API реально связан с adapter/NOR в host driver:61exact RGB565 positives,
7resource refusals,10negative,12format transitions,827physical failures/recoveries
и48time/quota/cancel stops. Every small-image physical operation faulted; full
image boundary/middle/last cases separately. Physical partial bytes сохраняются,
тот же decoder object восстанавливается; все handles closed/final requested heap0,
outside-scratch canaries всей4MiB не меняются. Global stop model сначала проверял
logical вызовы, а не каждую physical callback; стенд исправлен на реальные pre/post
checks, теперь calls не превышают ordinal. Это исправление тестового transport.

Уточнены реальные отказы4x4:8bit524288/460800backing,12bit70760/65536pool раньше
backing preflight. При повышении только host pool оба дают524288backing requirement.
Никаких opens/physical calls во всех refusals. Первые ошибочные test expectations
сохранены, library errors не замаскированы ради зелёного результата. Existing stdio
contract63positive/7limits/10negative/1197faults/12transitions pass после cause fix.

Standalone ESP-IDF C2 probe связан полностью, retained libjpeg+actual decoder,
scratch/NOR/guard/transport/espidf/PSA/RGB565. Probe app0f637039a537b0eca0f2bb5761c6e939d190489bc91823fee9c4c7e09aa45ad8,
506784bytes; ELF040300f81e15639d4c17abfa53bfff5969833522d5bb57ed83665746013863a5,
source15ab27cd82bf74f3b4281b8ce2d9da20809c0639338272f8ec49ddcda4573306.
Matching stamped assets/bootloader/partitions/config/manifest/licences сохранены
в firmware/development/small-tv-jpeg-decoder-probe. Старый storage probe6CB2 и
UI3E03/TJpgd неизменны. Fixture source — linked const synthetic JPEG; backing —
actual esp_flash SDK APIs. Это не native upload/cache/UI/network/LCD test.

Two-process target gate: small/fullCMYK12,lossless16,gray,17-call quota refusal,
same-object recovery и capacity460799 до любых writes. Whole4MiB comparison разрешает
изменения лишь scratch extents. Первые два процесса завершили7firmware cases, но
observer требовал changed bytes даже при идентичном replay. FIXED_TEST разрешает
идентичные final bytes на повторе, сохраняя positive actual SDK traffic и полное
сравнение protected bytes. Финальный новый two-process gate сохраняет каждый
уникальный полный before/after image и UART/session до assertions; история не удалена.

RV32adapter600bytes +bitmap15 +NOR4352, largest adapter frame368 включая256byte
conversion buffer. Target fullCMYK12 pools40592 +context4984 =45576requested bytes;
minimum8bit free heap149576, minimum stack free1988/4096. No UI/framebuffer/Wi-Fi:
это не whole-app fit. First final full decode39137736guest microseconds, с probe-only
idle yield каждые64checks; не hardware/CPU benchmark или universal production budget.
Host rich full traffic2582784program/113erases остаётся как44f106cb5; capacity460800
и compressed source44402 не меняются. Native source inventory не расширяется до
production UI integration.6artifact/10correspondence checks pass.

Proof qemu/parity/jpeg-backing-validation-20261020.json. Далее durable cache workflow
(один validation+cache decode), bounded source/hash/journal/ownership/asset deployment,
privacy/error HTTP +shared UI RAM/stack/time, reset/power-loss, независимые LCD/network/
full/24h/hardware и остальные factory/network/electrical audit. Цель остаётся активной.

Финальный observer two-process run terminal exit0: оба85checks/7cases, full-image
hashes/positive issued writes/protected4MiB bytes проверены. Первый before image
и identical replay сохранены по content hash без копирования одинаковых images.
Первый full39137736us/2erases, повторный45058612us/113erases; оба2580736program bytes.
Все4new QEMU owners31824/2476/38320/39016 stopped/reaped, исходные6oldH10 owners
по original creation timestamps живы, SDK tracked clean, frozen47files exact.
No old QMP/RSP/native board/other repository writes. Фактические outputs/history
и current source snapshot включены в proof; base artifact/API inventory прежние.

## 2026-10-20 — verified persistent source/RGB565 cache pipeline

Previous69f138125 classified progress. Goal IMPROVEMENT_PLAN active; worktree
проверена clean до продолжения. Добавлены storage/jpeg_cache.c/.h и build generator
tools/jpeg_cache_layout.py. Новая категория storage owner, не изменение factory
renderer или network. Borrowed scoped source/frame/metadata devices одного job,
durable invalidation до first frame write/source upload, exact LE RGB565 rows,
source/hash identity, physical full-frame flush/reopen/hash, journal publication
последней. Abort не flush, не publish, не требует оставшегося бюджета.

Cache hit заново хеширует actual persistent source и full physical frame, затем
читает строки без decoder/program/erase. All slots/maps/aliases проверяются до
metadata reads, unknown/failed state не разрешает drawing. Большой source — отдельный
SOURCE_LIMIT с точными required/available. Это не damaged/unsupported JPEG.
Code ID включает archiveSHA/3patches/codec+converter+storage sources/geometry;
ownership resources не меняются при смене codec identity. Actual archive mismatch
отвергается до создания output. Matching assets deployment не производится этим tool.

В первом synthetic layout тесте ошибочно считался invalid сдвиг последнего readonly
source на1byte, хотя он не пересекал следующий slot. Тест исправлен на реальное
пересечение предпоследнего/последнего; argument gates не ослаблены. Начальные
resource expectations также учитывают реальную102400byte source capacity: rich
4x4 и некоторые lossless сначала не помещаются в slot. Flat4x4 сохраняет такую
же padded geometry и проверяет backing524288/460800 или pool70760/65536, когда
compressed source действительно помещается. Старый generatorargc5 output8/12
побайтово совпадает; добавлен отдельный optional flat mode без смены geometry.

Найдена и воспроизведена существенная ошибка нового cache protocol: silent physical
read378 менял валидные decoder input bytes, pre/post source SHA оставались прежними,
неверный RGB565 публиковался как READY и выдавался cold hit. Before source/header/
model/driver snapshots сверены с BEFORE-compilation hashes, фактические wrong pixels
и отчёт сохранены. FIXED_RECONSTRUCTION в jpeg_cache_read_source сверяет каждый
полученный input block с fresh bounded256byte physical readbacks перед codec.
Новая heap не нужна; дополнительные44402read bytes на full fixture. Исходная UI
не использовала этот модуль и не затронута. Два хеша source не выдаются за защиту
от transient decoder reads; tested single-callback fault scope указан явно.

Final synthetic cache:12120fault/cut cases (2424callbacks×5modes),946SHAfaults,
2424stops. Source/hash/row/invalidation/commit/cold recovery, all5slots, dangerous
old-ready fallback и весь protected4MiB проверены. Independent observer считает
physical frame reads внутри SHA, поэтому пропуск reopen/старый NOR RAM cache
не проходит как physical verification.9compiled unsafe variants rejected runtime
assertions/independent pixel oracle; crashes/compiler/loader failures не counted.
Internal1.26billion CHECKs не являются числом независимых cases.

Actual libjpeg/cache integration:59full240JPEG8/12lossy,2–16lossless predictor4,
baseline/progressive/gray/RGB/CMYK/YCCK/arithmetic8;5source capacity refusals,
6negative/resource cases,268fault recoveries (43physical/7SHA/218silent source
reads+readbacks),18global time/quota/cancel stops. Persistent source реально
читается через bounded role callbacks. Cold job сохраняет physical bytes, не
повторяет decoder; failures могут rebuild только после invalidation/reopen.
Final decoder requested heap0; independent upstream samples/Python RGB565 exact.

FullCMYK12:52775calls/14471482reads/2703104program/144erases при1decode; cold
lookup+display1135calls/276338reads/0program/0erase/0decode, BE98FC78…E4C8CF46.
Первая запись:2582784scratch +118784frame/padding +1536metadata. Model starts
nonFF; это issued traffic, не chip endurance/hardware timing. Decoder host heap
peak47507 отдельно от cache/OS/model. Source44402bytes unchanged.

Strict RV32 compile сначала указал misleading indentation — formatting исправлен,
warning не подавлялся. Первый measurement ошибочно применял final picolibc linker
script к ET_REL, исправлен driver на bare ld. Финальный all9roots cache+NOR+journal
9016code/16rodata/static0, cache5600bytes (journal1032+frameNOR4352), layout156/
devices72; maxcacheframe336/readsource304, maxjournal448. Unresolved только
memcmp/memcpy/memset. Это не final SDK/UI link, runtime, whole heap/call-chain stack.

10generator rejects/identity/resource-separation и6artifact/10inventory controls
pass. Main3E03/TJpgd и storage6CB2/decoder0F63 target probes неизменны. Новые
production firmware не собирались, новых VM/physical-device действий не было.
SDK tracked clean, frozen47files/original6H10 owners readonly, no QMP/RSP.
Proof qemu/parity/jpeg-cache-pipeline-validation-20261020.json.

Далее production media owner/worker, actual RV32 cache runtime, build/vendor and
matching deployment, privacy/HTTP typed errors и settings publication. Текущий
photo_upload_finish удерживает общий media_mutex на всём validation: подставить
туда slow decode напрямую нельзя, это заблокирует UI/media clients. Затем общий
heap/stack/time и reset/power-loss, независимые network/LCD/full/24h/hardware;
остальные factory/network/electrical audit пункты остаются. Goal не закрыт.
# 2026-10-20 — offline JPEG dependency in the main build

Продолжена прежняя цель IMPROVEMENT_PLAN. Предыдущий ответ об объёме записей был
read-only status, без нового implementation progress. Текущий checkpoint меняет
реальную production build path: больше не нужен отдельный upstream checkout и
тестовый build script для libjpeg. Сохранён deterministic upstream archive2520264
bytes (исходный tar9932800), три ранее проверенных patch bytes и licenses.
Production helper проверяет pins, exports/patches в build dir, вызывает pinned
RV32/CMake/Ninja и проверяет reuse по actual archive/source/private headers.
13dependency controls pass, включая повреждения gzip/tar/patch/license/headers/
archive/report и прерванную сборку.10cache-layout rejects pass.

App CMake компилирует11codec/storage sources; early component expansion ESP-IDF
не получает custom JPEG path, поэтому проверка dependency availability выполняется
только на полном configure pass. Первоначальная ошибка сохранена в raw evidence.
Новый explicit reverse inventory459functions/170app,12omission controls pass.
Native result **5806checks**,107JPEG/98animation/18BMP, pass.
Никакой новый decoder/cache ещё не вызван из UI/upload: это проверено по finalELF.

Уточнение про flags: CMakeCache старого probe показывалO3, но actual Ninja commands
использовалиOs. Теперь Release задан явно и проверяются реальные FLAGS. Новая
libjpeg.a побайтно совпала с qualified D690BDF3; configured headers тоже одинаковы.
Это не новое уменьшение размера или новая target runtime qualification.

Main development build сохранён: app676C5EDF/ELF CB84E536,1170432bytes,
365568bytes free; source2D1FB659. AssetsBB4469E3 не менялись, stamp/cache deployment
ещё не активированы. DEBUGoff, SDK9a97f6c5.6artifact checks pass. Во время build
отключена Python bytecode generation, pins rechecked после link. Shared SDK clean;
шесть старых H10 owners сохранены, новых VM/прошивки платы не было.

Далее — source privacy parser и media owner/worker, один decode→verified cache,
invalidation-before-upload, typed HTTP errors и штатный async request lifecycle.
Не держать общий media_mutex весь decode. Затем общий RAM/stack/time, safe matching
assets deployment с сохранением фото/settings, независимые LCD/network/full/24h/
hardware gates. Цель не завершена. Подробности tests/JPEG_DEPENDENCY_BUILD.md и
qemu/parity/jpeg-dependency-build-validation-20261020.json.


## 2026-10-20 — metadata gate in the actual photo upload

REQUESTED_CHANGE: baseline-only privacy scanner replaced by codec/jpeg_privacy;
actual upload finish calls it before its existing full TJpgd decode. Gate handles
multi-scan marker grammar, FF00/restart/TEM/fill, DNL continuation, fixed JFIF and
canonical Adobe. APP/COM/private thumbnails/trailing data refuse with separate
metadata/truncation/I/O/stop diagnostics. No heap/global mutable state. Decoder
support and privacy are no longer the same scanner; HTTP format support still
baseline until native worker/newcodec is integrated. JS crop/resize/privacy unchanged.

63actual codec-qualified JPEGs pass;5late private/trailing files refuse. Direct
3727assertions cover45metadata locations/353truncations/2physical read failures/
343stops and255/256buffer boundary.7unsafe mutations compile and fail assertions.
Direct controls now included in ordinary native runner;5806old checks and12reverse
inventory controls pass, inventory469/172app.10cache generator rejects pass; policy
source/header now bind cache identity. RV32maxframe368;1224code/180rodata/0data+bss,
not whole HTTP chain. Main compile/link+6artifact checks pass. App733C006A/ELF
C1F1D94B/source4C8C3878,1171136bytes/364864free, DEBUGoff, assetsBB4469E3 unchanged.
No new VM or hardware flash; shared SDK and oldH10 only observed read-only.

Next owner/worker+async HTTP, one decode into durablecache, source invalidation/
publish ordering and typed network errors. Combined heap/stack/time/deployment/
independent network/LCD/full/24h/hardware remain pending; goal active. Proof:
qemu/parity/jpeg-privacy-validation-20261020.json; tests/JPEG_PRIVACY.md.

## 2026-10-23 — actual photo owner and whole-app resource admission

Продолжен IMPROVEMENT_PLAN в той же worktree. Реальные UI/upload теперь используют
photo_codec/photo_worker и durable RGB565 cache; TJpgd strip producer сохраняет
factory baseline pixels, расширенные JPEG идут через bounded libjpeg. Source
invalidation durable до erase; publish length только после full privacy/decode/
physical verify/journal. SDK async begin/complete освобождает HTTP task, общий
media_mutex не удерживается во время decode, clocks/immutable media продолжаются.
Matching ownership stamp/cache headers/assets генерируются обычной offline build.

Failing native regressions выявили stale queued source length и permanent-failure
cache после transient privacy read. Исправлены повторная проверка length/ownership
и публикация результатов под codec owner; retryable I/O/allocation/stop причины
не блокируют неизменённое фото навсегда. Queue-full/async-begin/disconnected-send
проверяют single completion и освобождение source/request ownership.

FullCMYK12 в main действительно декодировался, но HTTP timeouts и1392sum heap
minima не позволили принять результат. Переход observer на keep-alive сам проблему
не устранил. Allocation-only16KiB reserve тоже недостаточен: другие задачи могут
выделять RAM позже. Final allocator + cooperative service floor отвергают вход с
точным required/available, освобождают pools и не публикуют partial frame. Это
resource admission, не доказательство неисправного JPEG или полноты support на C2.

6001native +direct privacy,12inventory controls и6artifact checks pass; inventory
176factory/212app/514total. Final QEMU:5HTTP workflows,46concurrent GET probes без
ошибок (max0.657host seconds), source exact после второго cold process, protected
flash/другие photos unchanged.3allocation refusals +1late reserve abort, gray
progressive accepted. Separate HTTP-only control160GET pass, max0.640seconds.
Четыре собственных VM остановлены/reaped. Не LCD/RF/weather/power-cut/full/24h gate.

App4B7530CB/ELF6B233C4F/sourceC6B9D1AD,1464560bytes/71440partitionfree, DEBUGoff.
Saved firmware/development/small-tv-esp32c2-reconstructed, matching assets1032119B.
Подробности tests/JPEG_MAIN_INTEGRATION.md; raw failures сохраняются отдельно от
final proof qemu/parity/jpeg-main-integration-validation-20261023.json.

Далее safe migration старого unstamped assets без потери photos/settings, полный
target memory/stack/fault/format matrix, independent LCD/clock continuity, actual
upload/decode power-cut, network lifecycle/churn, whole image audit/full/24h/hardware.
Old frozen QEMU/SDK не менять; на физической плате действий не было. Goal active.

## 2026-10-23 — безопасное принятие matching legacy assets

Добавлен отдельный startup bootstrap jpeg_provision; обычный guard остался
read-only. Raw/SDK partition map/MD5/flags/geometry, 27 immutable payloads,
compiled stamp digest, все candidate bytes (включая spare sectors, fresh double
read) проверяются до записи. Один общий count/byte/time budget, старые порты
отозваны; выдача новых — только после последнего physical guard/deadline.
Photo/settings/protected capabilities не выдаются bootstrap. Erase отсутствует.

Новый negative test выявил ошибку первоначального незакоммиченного прототипа:
полный чужой header с неправильным, но монотонно совместимым ID принимался как
недописанная запись. Исправлен протокол: ID32 + exact readback первым, header8 +
readback последним; tail24 FF не записывается. Partial header требует полного ID.
Обычный complete stamp сохраняет существующий cache без scan/reinitialization.
Неизвестные write orderings/чужие или занятые области отклоняются без erase.

23409 host scenarios, 452 torn recoveries, 786 occupied, 524 hidden-read,
14599 read faults, 6325 hash faults и quota/revocation checks pass. Все 8 новых
и 14 transport compiled mutants падают на assertions; 31 transport cases,
5995 native + direct privacy, 12 inventory controls и 6 artifact checks pass.
Inventory: 176 factory /212 app /527 total, не proof полной эквивалентности.

Actual main: 12 owned/reaped cold QEMU processes. Erased/torn ID — 40 SDK program
bytes, complete ID/torn header — 8, следующий persistent boot — 0. Foreign/header,
occupied last byte, corrupt payload и unknown raw flags — 0, access revoked.
Valid nonempty owned cache и application update поверх реального retained
old-main NVS/photos/cache — 0 writes. Полное сравнение flash вне NVS/stamp;
в persistent cold/upgrade также NVS exact. Preboot dial/mask fixture объявлен,
guest RAM/PC/code не изменялись. Отдельный storage gate, не LCD/network/RF приёмка.

App034287C7 /ELFBB7FD7A1 /source1D1F52CE, 1466576 bytes /69424 free, DEBUG off.
Production archive сохранён; assets1032119B и layout/codec IDs прежние.
RV32 core1331 text/readonly,0 data/bss; largest individual frame464 (не whole-stack).
Подробности tests/JPEG_LEGACY_PROVISION.md; proof/raw в
qemu/parity/jpeg-legacy-provision-validation-20261023.json. Полные flash images
хранятся losslessly как common base + deduplicated sector deltas, с full SHA.

Далее: independent LCD/clock continuity текущей app, полный target RAM/stack/
format/fault matrix, actual upload/decode/journal reset/power-cut, network lifecycle/
churn, whole-image audit/full/24h/hardware. На физическом устройстве действий нет;
SDK/frozen QEMU не менялись. Цель остаётся активной; push отдельно не выполнялся.

## 2026-10-23 — independent cache-backed LCD, startup timing gap

Старый photo_frames observer падает до VM: ждёт два vTaskDelay calls, в текущем
clock_task один final yield. Новый photo_cache_frames_qemu наблюдает real cache
readiness, blocked calls не меняют state; не подменяет guest RAM/PC/time. Literal
factory PhotoMachine исполняет JPEG/footer/selection/fade instructions. Известное
исправление restoration отдельно учитывает actual backlight_update calendar.

Текущая неизменённая app034287C7: 54 whole frames /3110400 pixels exact, 28 all-photo,
22 masked-night с4cycles (2unsynced +actual synchronized restore),4empty-dark.
13 report mutation controls pass;3main owned VM stopped/reaped. Boot/application/
photos/immutable/protected сохраняются, candidate scratch/cache writes разрешены.
Это LCD gate, не HTTP/RF или clock continuity других тем при foreground decode.

Дополнительная literal-stock owned VM с тем же профилем измерила первый полный
кадр20.565822guest sec; current main23.389901 (предыдущий repeat23.559866).
Timing gap не скрыт pixel success. Ready samples показывают slot0 примерно5.3sec,
но renderer ждёт все5jobs до23sec. Оптимизация initial/preload scheduling — NEXT:
без новых software sleeps, пропусков valid slots, застревания на damaged slot,
регрессии fade/cancel/retry. Добавить timing/partial readiness/cold0writes tests.

Production firmware/SDK/frozen QEMU не менялись; на плате действий нет. Подробности
tests/PHOTO_CACHE_FRAMES.md, proof qemu/parity/photo-cache-frames-validation-20261023.json.
Полный target JPEG memory/stack/format/fault, clock continuity, actual power-cut,
network lifecycle/churn, whole-image audit/full/24h/hardware остаются открытыми.

## 2026-10-23 — следующий кеш без задержки первого фото

Исправлена измеренная задержка23.389901guest sec: раньше worker готовил все5slots,
renderer ждал всю очередь. Теперь display/factory_photo_prefetch выбирает только
следующий eligible source; photo_prepare_next запрашивает его при fade0/2.
В фазах1/3/4/5 новая обработка не начинается. После последней фазы готовим
следующий снимок в паузе до timer event. Валидный pending target не пропускается
ради готового более позднего; invalid/empty источники можно пропустить. Worker
публикует stable failure только для current length, transient read/memory/cancel
остаются retryable. Same-length upload инвалидирует readiness/failure как прежде.
Новых sleeps/software delays нет. Общий selector сохранён в display module.

6077native +privacy/12inventory controls pass; real worker damaged/current-length/
read-retry/cancel-no-writes/retry cases.6compiled unsafe policies падают на assertions,
normal control проходит.13440literal factory/current RV32 transitions совпали по
outputs/state/duty/completion across32masks/6phases/5slots.6artifact pass.217app/
532total inventory не доказывает full-image equivalence.

Actual current main:5owned/reaped cold processes,104wholeframes/5990400pixels exact.
All-photo first5.560901sec (pilot5.619954), presentmask1 — другие cache ещё не готовы.
Stock reference20.565822; old timing отдельно падает на новом критерии. Mask10
включает настоящий unsynced→night sync; source0 с испорченным SOI пропускается,
slots1..4 сохраняют порядок.17negative report controls pass.

Durable cold process получает EXACT flash после warm process без reseed/NVS reset.
First2.251859sec; hardware breakpoints на уникальных actual JPEG flash_program/
flash_erase не сработали,0attempts. Все candidate bytes и весь4MiB unchanged.
Во всех warm случаях source photos/boot/immutable/protected сохранены. Это
LCD/storage/timing gate, не HTTP/RF/physical или clock continuity остальных тем.

AppABF14143 /ELF896558F5 /source64EDEEF9,1466800bytes/69200free,DEBUGoff. Production
archive сохранён; assets1032119B/layout44268211/codecB33BC0A1/libraryD690 прежние.
tests/PHOTO_PREFETCH.md; qemu/parity/photo-prefetch-validation-20261023.json.
Independent verifier восстанавливает104RGB surfaces и10physical images, проверяет
hashes/protected/cold identity. Около0.8MB новых compressed данных,184payloads reuse.

Далее current classic/simple/dial continuity при foreground decode, полный target
JPEG memory/stack/format/fault, HTTP resource/lifecycle/churn, actual publication
power cuts, whole-image/full/24h/hardware. Старые HTTP результаты на новую app
не переносить. Physical/SDK/frozen QEMU действий нет; цель остаётся активной.

## 2026-10-23 — часы при foreground JPEG, HTTP и interrupted recovery

AppABF14143/ELF896558F5/source64EDEEF9 без production изменений. Classic/simple/dial
сверены с clean native +corrected literal factory RV32 во время настоящего gray8
progressive decode:13frames, maxgap1.069112/1.101215/1.116249guest s. Отдельный
start/chunk-only control:47frames. Все3456000pixels точны, real minute rollover,
active foreground/source4, no RAM/PC/time writes.16+12report negatives. Только
isolated native renderer reference пропускает RTOS owner startup; actual main
выполняется целиком. Полные clean surfaces без masks/actual-panel copying.

HTTP fixture исправлен на persistent WeatherFixture. Старый240host s timeout
CMYK12 сохранён; passive counters показывают progress, mutex deadlock не найден.
Explicit900host s повтор:CMYK12 200OK за305s, richRGBprogressive146.438s, gray37.25s;
sampling44-8 backing-capacity524288/460800, sampling44-12 heap-headroom15379/6692.
862GET/0errors/max0.875s; отдельный no-upload160GET/0errors/max0.5s. GET10s,
firmware180guest s/200k calls/64MiB read/16MiB program не ослаблялись. Host time
под icount не является скоростью физического C2. Cold source readback точен.

Independent canonical journal reader проверяет CRC/footer/newest identity и
physical source/frame SHA. Upstream gray samples57600×128 →RGB565 frameA3EC07B0
совпал послеLCD/HTTP/cold/recovery.3offline damage controls — не powercuts.
Actual stopped pre-publication CMYK image(slot5size0/notready) загружен в новуюVM;
ordinary gray replacement OK, journal1→2, protected bytes unchanged. Это restart
до publication, не brownout внутри page/erase. Все11accepted owned VM reaped.

Сохранены test helpers, отдельные gates, raw proof/sector deltas и independent
verifier:tests/JPEG_CLOCK_CONTINUITY.md, qemu/parity/jpeg-clock-continuity-validation-
20261023.json. FactoryELF/ROM archival checks отдельно от runtime pins. Старые
coefficient optimization и persistent cache включены: не повторять scratch decode
при показе. Их прежние traffic/cold0write результаты не подменяются новыми tests.

NEXT: current target format/RAM/stack/fault, LCD под CMYK12/richRGB, publication
powercuts, lifecycle/churn, whole-image/full/24h/hardware. Shared SDK/frozen QEMU
не менялись, физических действий и push нет. Цель всего плана остаётся активной.

## 2026-10-23 — настраиваемый суммарный лимит записи JPEG

По уточнению пользователя default200KiB относится к cumulative program traffic
одной обработки: коэффициенты, RGB565, journal. Исходный upload отдельно.
Photos UI/API принимают0..uint32 KiB, отдельный NVS key сохраняется без изменения
legacy ABI.0запрещает program и erase JPEG/cache. Уже готовые фото читаются.
Расход invalidation переносится в finish, live снижение не сбрасывает счётчик,
background failure не вызывает бесконечные новые записи. Повышение разрешает
следующую попытку. Отказ сообщает flash-write-limit/flash-writes-disabled и
следующую cumulative потребность; partial ready frame не публикуется.

6298native +privacy3727,13inventory controls,348557transport/34cases,18unsafe
transport +6integrated policy mutants,16DOM/HTTP contracts и6artifact pass.
На текущем C2: CMYK12 отказ ровно204800bytes, следующий запрос205056 не выполнен;
gray progressive после отказа успешен за115968bytes. Сохранённый0: hot request
без записи/стирания, cold EXACT stopped flash без reseed — настоящий draw из
cache успешен, callbacks с reset0, весь4MiB unchanged. Physical journal/source/
frame SHA проверены отдельным reader.

Дополнительный legacy startup выявил40-byte обход нуля в первой appF94C00B8:
bootstrap писал32+8bytes stamp. Failing trace/images сохранены. Исправлен readonly
startup в photo_storage.c: при0 legacy без stamp не принимается, никаких writes/
erases, остальные часы/HTTP работают; matching complete cache доступен. Если
stamp отсутствует, повышение лимита требует обычного restart для adoption.

App9C1A83BD/ELF76B5CE37/source7D95988C,1476432bytes/59568free,DEBUGoff, archive
firmware/development сохранён. Separate LCD:15wholeframes/864000pixels exact
classic/simple/dial при реальном gray decode и minute rollover,16negative controls.
Worker untouched5012/8192, pool14099/context4984 observed. Raw RAM и точный ELF
layout позволяют отдельно пересчитать stack/heaps; pool pointer не сохранён.
Все6текущих VM остановлены/закрыты. Timing icount не является скоростью платы.

tests/JPEG_WRITE_BUDGET.md и jpeg-write-budget-validation-20261023.json:15physical
images (13current+2failingbefore), PNG/RAM/trace/mutants и independent offline
verifier. Legacy factory dump не добавлялся. SDK/frozen QEMU не менялись, physical
flash/UART/reset и push не выполнялись. Полная новая target matrix, publication
cuts, network lifecycle/churn, whole-image/full/24h/hardware остаются в плане.

## 2026-10-24 — текущая JPEG format/resource проверка

Production app9C1A83BD не менялась. Новый runner читает committed70-vector corpus
с SHA checks и выполняет реальную HTTP загрузку, полный physical cache hash и
канонический journal. Для baseline8 эталон — буквальные factoryRV32 instructions,
для extended — закреплённый upstream samples+PythonRGB565. After refusal следующий
gray progressive реально обрабатывается. Entry/exit RAM и адрес diagnostic дают
независимую offline проверку nested fields/task stack/heaps. Отдельные network и
LCD gates этой проверкой не заменяются.

Pilot6primary/9workflows terminal pass: CMYK12progressive/lossless-gray16/baseline8
точные; richprogressive12 write-limit205056/204800, oversizedsource admission и
SOF5 unsupported, после каждого recoveryOK.6accepted/2finishrefused/1sourcefail,
worker untouched5012/8192, heap minima sum lowerbound10548. Это не измерение
одновременного whole-app peak. Pilot VM stopped/reaped; saved-byte checker pass.

Полные70primary запущены4disjoint parts18/18/17/17, handles/paths в WORKING_NOTES.
На момент checkpoint они живы, полного matrix pass пока нет. Application/SDK/
frozen QEMU не менялись, физической платы/push нет. Full fault/publication,
network lifecycle/churn, whole-image/full/24h/hardware остаются в плане.

Сохранён pilot proof jpeg-format-pilot-validation-20261024.json:19physical images
и16RAM snapshots в lossless/deduplicated gzip, около1.3MBновых compressed bytes.
Offline verifier повторно проверил source/frame/journal, целый diagnostic из RAM,
heap/task fields и factory baseline oracle. Full4parts в этот accepted proof не
включены: они пока работают; окончательные результаты сохранять после terminal.

## 2026-10-24 — исправлены ссылки на разделённые модули

74из176symbol-map module summaries указывали старые файлы. Теперь точные
native_targets берутся из reviewed correspondence; file summary выводится из
них.16reference headers направляют к per-function mapping. Organizer умеет
--refresh-navigation без регенерации псевдокода и не придумывает файл для новых
непроверенных адресов. Audit отвергает старую навигацию и pins обоих tools.

До исправления реальный audit падает на0x4200826a/native_module. После — pass,
повторный refresh idempotent;13existing controls pass. Тела/имена/calls176reference
функций побайтно/по SHA сохранены; длина header может сдвинуть line numbers.
Inventory176/219/535, production app9C1A83BD и ELF76B5CE37 прежние. Запущенные
JPEG ВМ продолжают свои неизменённые workloads. Полнота factory image, indirect
callbacks, flags и остальные проверки плана этим не закрываются.
Before/after, SHA/call tables, original rejection и13-test log сохранены в
reference-navigation-validation-20261024.json с compressed raw metadata.

## 2026-10-24 — завершён полный70-vector current JPEG corpus

Все4exec terminal0, четыре owned VM stopped/reaped. Independent aggregate
проверил exact union70 без duplicates на одном app9C1A83BD/ELF76B5CE37/source7D95.
92workflows:48primary accepted,17finish refusals,5source refusals,22successful
immediate gray recoveries. Причины primary refusals:8write budget,5heap,
1backing,1unsupportedSOF5,1truncated,1invalid и5source capacity. Program limit200KiB
не ослаблен; source upload отдельно. Exact physical pixels/source/journal и
nested diagnostic из RAM проверены независимо от HTTP status flags.

Worker untouched5012/8192; observed pool max47983 +context4984отдельно. Сумма
individual heap minima15468 — lowerbound, не simultaneous whole-app peak.
192physical images и174RAM snapshots/raw logs/layouts сохраняются как
jpeg-format-matrix-validation-20261024.json. Parent-image deltas уменьшают
повторение неизменённого кода без потери какого-либо physical byte/SHA.

Это приёмка корпуса, не всех возможных JPEG. LosslessRGB6/CMYK6 оказались больше
source slot; для исполнения этих путей нужны меньшие дополнительные fixtures.
Current actual I/O/allocation fault injection/publication cuts, network lifecycle/
churn, whole-image/full/24h/hardware остаются открытыми. SDK/frozen QEMU/production
firmware неизменны, physical/push нет. Цель всего плана остаётся активной.
Schema2/3574sector references сохраняют full hashes и запрещают cycles/forward
bases; новые compressed payloads около12.3MB. Числа primary outcomes и recoveries
verifier заново считает из raw reports, не доверяя summary полям.

## 2026-10-24 — проверены оставшиеся lossless RGB6/CMYK6 paths

Не повышая limits, созданы27754/36999-byte240×240gradient JPEG,predictor4, source
formula(x+2*y+3*c)&63 со всеми64значениями каждого канала. Encoder — unmodified
upstream; decoder восстановил original samples exactly; RGB565 — independent
Python arithmetic. Shared generator recipe воспроизвёл exact compressed bytes.
Первый predictor1/rich опыт остался слишком большим141194/188235 и не засчитан.

На неизменённой9C1A83BD оба приняты actual HTTP owner: full physical source/frame/
journal и saved RAM processSOF3/precision6/components3/4/240rows совпали. Не cache
hit и не baseline fallback.116736programbytes каждый, default200KiB сохраняется.
Worker untouched5320/8192,pools12901/15198/context4984 отдельно; heap-minima lower
bound41044 не whole-app peak. VM27340 stopped/reaped,exec80350=0. Дополнение
jpeg-lossless6-validation-20261024.json +base70 на тех же app/ELF/source закрывает
45lossless precision/color pairs. Все possible streams/faults это не покрывает.

QEMU читался без изменений: frozen D64 имеет operation-timing; reference79badcba
прямо ограничивает модель functional contents/WIP timing, не electrical power
failure. В отдельной branch0860e568d4 есть newer shared NOR/cache fixes. Actual
target faults/publication cuts и остальные пункты плана остаются открытыми.
Supplement verifier повторно проверил весьbase70 archive и historical source
pins из Git05da без reset рабочей копии; неверныйE5D (24pin differences) отклонён.
Exact45lossless pairs выведены изactual successful SOF3 RAM diagnostics, не списка
генерируемых файлов. Producer inputs/current app identity сохраняются отдельно.

## 2026-10-24 — cold recovery на8границах публикации фото

Новый отдельный storage harness прерывает реальные HTTP/cache/settings операции
неизменённой production9C1A83BD после completed SDK call/HTTP chunk. Сохраняет
paused/stopped actual flash; новый process получает EXACT bytes без reseed.
8cuts: invalidationbody/footer, sourceerase, firstchunk, firstframepage,
publicationbody/footer, completefinish. Старый CMYK6 видим только в первых2,
новый RGB6 только после complete; промежуточные5состояний невидимы. Full committed
cache footer до settings commit также не публикует photo_size0.

Оба4-case exec88011/66603 terminal0;16owned VMs stopped/reaped.8cold boots и
8normal gray recovery uploads successful. Independent saved-byte checker повторил
source/frame/journal/protected identities;10unsafe report/image controls rejected.
Initial images до первого CPUcontinue, all callback traces/return status и actual
instruction prefix сохранены; offline verifier связывает их с exact ELF symbols.
Proof photo-publication-validation-20261024.json. DOM policy16cases также pass.
Archive57full physical images/78raw items,60416new gzip bytes плюс JSON metadata;
все4MiB identities восстанавливаются побайтно, прежние sector payloads reused.

Два failed pilots — ошибки observer: numeric response parsing доcut; затем30s
host recovery timeout. Они не засчитаны. Final900s host observer не меняет firmware
guest time/write policies. No app/SDK/frozenQEMU/physical/push changes. Проверены
selected completed-operation boundaries; actual in-page electrical cuts, SDK I/O/
allocation/NVS-internal faults и остальные требования плана остаются открытыми.


## 2026-10-24 — два AP-клиента и исправления QEMU

В отдельной QEMU branch codex/small-tv-ap-clients сохранены fdb97bef73
(Windows trace paths),6324e5e152 (independent virtual AP peers),d49be39d77
(безопасный DHCP и ожидание ACK). Full targets build успешен; protocol349cases,
905guard-page truncations/10000bad inputs, C3 default/modular60s boot pass.
Xtensa binary identical baseline, известный CYD PHY gap этим не закрыт.

Actual factory/native SDK events1→2→1→0→1 прошли на двух QEMU binaries.
Наша прошивка1start/0stop; factory3starts/2stop wrappers, первый handle потерян
при повторном listen112, listener остаётся живым. Это уточнение прежней гипотезы
про остановку сервера на каждом уходе. 16HTTP200 всего в4принятых runs.
Offline proof network-peer-validation-20261024.json повторно сверяет ABIobject,
точные ELF/SDK event bytes/handles и24negativecontrols. Новый архив не копирует
полную заводскую flash/RAM/UART. Все8C2 и2C3 VMs остановлены/reaped, живых нет.
Два observer pilots не засчитаны. Production app/SDK/frozenQEMU unchanged.

HTTP-LIFETIME всё ещё открыт: уход первого/маршрутизация через второго,
per-client endpoints/scan/upload/weather/theme/reconnect/churn. Общая цель
активна, physical actions/push не выполнялись. Детали tests/NETWORK_CLIENTS.md.


## 2026-10-24 — исправлены уход первого AP-клиента и L2-маршрутизация QEMU

На прежнем QEMU128D native реально терял HTTP при маске2, хотя второй peer
был associated/DHCPbound, а HTTP handle оставался рабочим. Выбор другого peer
сам по себе не помог (v3): ARP гостя сохранял MAC первого. v4 отправляет обычный
ARP через radio/DMA перед IPv4 при смене relay. Отдельный factory reconnect
завис в managementstate3; run исключён/остановлен/reaped. v5 повторяет незаконченный
probe/auth/association после1virtualsec без задержки приложения.

QEMU7a9764712b/CCE6B471: native/factory × уход первого/второго —4runs pass,
16HTTP200, zero→survivor recovery. FinalC3default/modular60sboot pass, Xtensa
побайтно baseline. Все19C2+6C3 процессов этой серии остановлены. App unchanged.
Новый offline contract проверяет обе departure пары и before controls; AID
правильно отслеживается в пределах ассоциации, с повторным использованием после
ухода (FIXED_TEST). Proof network-relay-validation-20261024.json повторно использует
неизменённые gzip payloads; factory fullflash/RAM/UART в новый архив не копируются.
Полный HTTP-LIFETIME/traffic/churn/APSTA/RF и остальной план остаются открытыми.


## 2026-10-24 — scan/photo/theme в ходе реальных AP peer transitions

Новый network_activity_qemu.py проверяет native на9C1A83BD/76B5CE37/QEMUCCE6B471.
При реальном входе в SDK/photo/settings function ещё pending HTTP меняет mask
внешних клиентов; затем исполняются штатные callbacks/return/HTTP. Двацикла:
scan3→2, start2→3, chunk3→1, finish1→3, theme3→2, reselect2→3.
12основных HTTP200,14SDKpeer events,6nestedcallbacks, две побайтные проверки
508-byte JPEG и сохранённой темы, одинстарт/нольостановокHTTP. Scan видит все3APs.

Pilot1cycle и final2cycles terminal0; обеownedVMs остановлены/reaped. Olderpilot
producer сохранён по егоhash, финальная приёмка не смешивает разныеисходники.
Offlinecontract сверил actualABI/ELF/MAC/AID/returnordering и отверг8unsafecontrols.
Proof network-activity-validation-20261024.json:29raw/29payloads,25531newgzipbytes,
старыеpayloads reused, полнаяVMflash/RAM/UART не копируются. No app/SDK/QEMUchange,
physicalactions/push нет. Network gate отдельный отLCD; STAweather/reconnect,
prolongedchurn/loss/полныйплан остаются открытыми. См.tests/NETWORK_ACTIVITY.md.


## 2026-10-24 — погода при реальном STA disconnect/GOT_IP

Новый station_weather_qemu.py на неизменённом9C1A83BD/76B5CE37/CCE6B471:
локальныйfixture удерживает ответпогоды, реальнаяAP выключается, SDKcallback
восстанавливаеттолько externalAP, native сампереподключается/получаетDHCP.
2outages/3GOTIP, retries1→0, адресretained,2freshHTTPпубликации(humidity78/79),
старыйrawcache сохранён,1serverstart0stop/1ROMboot. ОбаHTTPweather запроса
завершилиськакобрывтранспорта доосвобожденияfixture; этотscope не доказывает
полныйполученный503. Holding1.563/1.610hostсек, гостевыетаймауты неизменены.

Pilot/final2cases каждыйterminal0,обеVMs stopped/reaped. ELF/DWARF выводитSDK
IDs2/5/0,IPevent20bytes/offset4 безперекомпиляции. Offlinecontract декодируетrawcache,
проверяетnativeflags/SDKIPbytes/HTTPfreshbodySHAs и отвергает9unsafecontrols.
Proof station-weather-validation-20261024.json:32raw/32payloads,30274newgzipbytes,
старыеpayloads reused,fullVMflash/RAM/UART не копируются. Production/SDK/QEMU
source/physicalнеизменны,pushнет. SelectedSTAweather/recovery теперьпроверен;
prolongedchurn/loss/полныйnetwork/fullsuite/24h/hardware иостальнойплан ещёоткрыты.


## 2026-10-24 — точечные потери и исправление DHCP-повторов QEMU

В QEMU добавлен отключаемый one-shot fault mask для7protocol stages каждого
peer (287d95e1b1), без payload logs или изменений guest RAM/SDK callbacks.
Контрольная потеря DHCP Discover/Request/Offer/ACK показала зависание state6/7
на12guest s при живом соседе/HTTP. b85483c98d добавляет acquisition retry deadlines,
backoff/jitter и отдельные свежие XID, сохранённые при повторах. RFC2131§4.1
проверен по первичному источнику; lease renewal/rebinding не заявляются.

14live runs:7before (4expectedfailcontrols) и7after recoveries, плюс factory
primary-departure regression; все15C2 процессов остановлены/reaped. C3default/
modular60sboot checks тоже pass и reaped; Xtensa unchanged821D. Native app и SDK
не изменялись, physical/push нет. PureC351cases/905guard prefixes/10000non-DHCP/
14007jitter combinations pass. Offline14reports +112negative controls pass.
Proof network-loss-validation-20261024.json:61raw/54payloads,116266newgzipbytes,
старыеpayloads reused, полныеVMflash/RAM/UART не добавлены. Детали NETWORK_LOSS.md.
Следующие проверки: liveness моста при stalled primaryDHCP (пока code hypothesis),
combined/repeated loss и prolonged churn/soak. Общий план остаётся активным.

## 2026-10-24 — исправление AP bridge QEMU и совмещённые потери

Повторная потеря Discover у первого peer воспроизвела настоящую ошибку модели:
HTTP pending при готовом втором peer. До исправления run завершился AssertionError;
после снятия потерь DHCP и HTTP восстановились. Задержка второго peer не ломала
HTTP. QEMU21a8d6dd8c распространяет выученный guest AP address на все AP peers,
сохраняя отдельные leases; функция и отдельная политика отмечены FIXED_EMULATION.
После исправления оба stalled-peer runs обслуживают HTTP во время задержки.

Добавлены --all-stages и два запуска с семью потерями подряд, для каждого peer.
В обоих 7 потерь/4 DHCP retries цели/0 у соседа, HTTP доступен до и после recovery.
Factory regression и C3 default/modular60s boot checks pass, Xtensa unchanged821D.
Все7C2+2C3 VM остановлены/reaped; production app/SDK/frozen tools неизменны.

Offline proof network-stalled-peer-validation-20261024.json:57raw/44payloads,
100050newgzipbytes, exact ABI/ELF/Git blobs и 44 negative controls pass. Реальный
before failure сохранён как passed=false. Full flash/RAM/UART не копируются.
См. tests/NETWORK_STALLED_PEER.md. Общий план, длительный churn/soak, full network,
fullsuite/24h/hardware и остальные пункты остаются открытыми. Push не выполнялся.
