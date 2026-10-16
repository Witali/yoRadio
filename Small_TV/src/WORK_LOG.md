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
