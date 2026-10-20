# План улучшения восстановленной Small TV

Обновлено: 2026-10-20. База: `main` / `51cd114f9`.

Цель — восстановить полезное поведение заводской прошивки ESP32-C2, исправляя
её подтверждённые ошибки. Сопоставлять ассемблер, декомпиляцию и наш C-код в обе
стороны; различать расхождение, пробел тестирования и намеренное улучшение.

## Исходное состояние

В `main` сохранены подготовка libjpeg-turbo 3.2.0, патчи ограниченной памяти,
read-only таблицы, RGB565 converter, host/RV32 проверки и план flash layout.
Рабочая app `54f441af…` пока использует исправленный TJpgd. Объединённая версия
прошла 5608 native checks, 10 controls карты и 6 artifact checks. Это не полная
аппаратная или суточная приёмка. Full regression прежней B50D завершён; идущий
H10 относится к B50D. Его frozen source/SDK/snapshot и владельцев QMP/RSP не
менять. Новые исправления выполнять в отдельной рабочей копии.

## 1. Переинициализация темы при смене города

Статус: **выполнено и проверено в native/QEMU; не full/24h/hardware приёмка**.
Сборка `3e030c1c…`, [проверки](tests/CITY_REINIT.md). Основание: `CITY-REINIT` в
[двустороннем аудите](reference/BIDIRECTIONAL_AUDIT.md).

Заводская `/updateCity` (`0x4200f2c0`) очищает latch инициализации темы даже при
повторной отправке того же города. До исправления у нас команда была только
у `/setclocktype`; теперь она также публикуется при каждом valid `/updateCity`.

- [x] Сверить порядок обновления города/страны, weather trigger и theme latch
  с декомпиляцией и адресным ассемблером.
- [x] Добавить падающие тесты: четыре темы, новый и тот же город, некорректный
  запрос без побочных эффектов, отсутствие лишней flash-записи.
- [x] Публиковать настройки и команду под одним mutex, без выбора устаревшей
  темы; сохранить обычную настройку города, страны и обновление погоды.
- [x] Проверить настоящий renderer всех тем, отдельно город во время photo fade.
  Сохранить исправление заводского blank-frame/fade бага.
- [x] Обновить карту/журнал; сохранить новую app и выполнить подходящие native,
  artifact и независимые network/display gates.

## 2. Новый JPEG в рабочей прошивке

Статус: **подготовительные стенды готовы; production integration не выполнена**.

Checkpoint 2026-10-20: реализован portable NOR core с 4 KiB cache, sparse mapping,
sector RMW и read-back verification. 3000 random operations, 83 injected partial
failures, 7 реальных layout stores и 6 compiled mutation controls прошли.
RV32 object1848bytes/handle4352/frame304 измерены; это ещё не production link
или hardware execution. [Результаты](tests/JPEG_NOR_STORAGE.md).
Следующий checkpoint: portable immutable-resource/layout guard готов отдельно.
27payloads + ownership stamp в уже protected padding;49layout/84corruption,
3050read/3010hash faults,12generator rejects/12controls и10compiled mutants pass.
Native UI capabilities/build integration пока не подключены. RV32 core1150 и
const descriptors1448bytes измерены. [Результаты](tests/JPEG_OWNERSHIP_GUARD.md).
Следующий checkpoint: portable two-bank cache journal готов отдельно. Durable
invalidation до data writes, verified publication и каждый physical cache hit;
33400NOR/power-cut cases,769metadata corruptions,6boot failures,12mutants и
independent wire gate pass. RV32 code2976/const24/handle1032/maxframe448;
не production link. [Результаты](tests/JPEG_CACHE_JOURNAL.md).
Следующий checkpoint: shared budget/port transport и ESP-IDF flash/PSA binding
реализованы и исполнены в standalone C2 probe.31host cases/14mutants,4target
variants/5fresh owned processes, actual writes/RMW/cold process persistence и
readonly rejection чужого map/stamp/flags pass. Probe6cb29771… сохранена отдельно;
main app3E03/TJpgd не менялась. [Результаты](tests/JPEG_TRANSPORT.md).
Следующий checkpoint: byte-bounded shared scratch реализован, один NOR cache
обслуживает все files без per-file sector padding. Actual libjpeg/NOR matrix,
18independent Pillow images,1227logical и2238physical error recoveries прошли;
16432native assertions/13mutants и RV32 object1240/handle576/frame48 измерены.
Трафик richCMYK12 —3780608program bytes/923erases на один tested240×240decode;
это не production limits или endurance. [Результаты](tests/JPEG_SHARED_SCRATCH.md).
Далее — расширить sampling/capacity bounds, выбрать budgets; invalidation/source
hash в upload/cache workflow, matching assets build/deployment с сохранением photos/settings.
Полный HTTP/power-loss workflow и native UI decoder integration ещё открыты.

1. Зафиксировать матрицу входов/лимитов: baseline/progressive, gray/RGB/CMYK/YCCK,
   8/12-bit lossy и 2–16-bit Huffman lossless. Не обещать весь T.81: библиотека
   не поддерживает hierarchical, DNL, fractional subsampling и lossless arithmetic.
   По уточнению пользователя: вход, который устройство не может декодировать,
   отклонять с точной причиной. Различать unsupported mode, damaged JPEG и
   resource limit; для последнего указывать required/available. По возможности
   проверять до decode/backing writes. Не называть JPEG повреждённым из-за
   недостатка RAM/scratch и не публиковать частичный результат как готовый cache.
2. Реализовать отдельный NOR-aware storage module: sparse extents, ограниченный
   RAM sector cache, read/modify/erase/program, измерение износа. Проверенный
   layout planner сам не выполняет flash I/O; отдельные core/transport уже
   проверены в model и target probe. Запас плана — лишь 8 KiB;
   460800 bytes backing — максимум fixtures, не предел любого JPEG.
3. Реализовать atomic metadata/invalidation и cold recovery при прерванных
   upload/decode/erase/write. Перед записью проверять ownership immutable resources
   matching build; сохранять все photo slots и settings.
4. Подключить codec через bounded input/output API и RGB565 converter; сеть/LCD
   не должны знать внутренности libjpeg. Сохранить browser metadata removal/crop
   и серверную privacy validation. Запрет progressive менять после готовности codec.
5. Проверить полный RV32 link, размер app partition, общий peak heap/task stack,
   время decode и abort/reuse после реальных I/O/allocation faults. 64 KiB library
   pools не считать всей RAM приложения. Учесть output policy и большой quantizer stack.
6. Выполнить HTTP/upload/reset persistence и независимый полный LCD кадр, затем
   full regression/soak точного app/ELF. Только после этого объявлять decoder
   включённым и публиковать подтверждённый список поддерживаемых режимов.

Материалы: [host qualification](tests/jpeg_library_probe/README.md),
[fault recovery](tests/JPEG_FAULT_RECOVERY.md),
[flash layout](tests/JPEG_STORAGE_LAYOUT.md), [RGB565](tests/COLOR_CONVERSION.md).

## 3. Сетевой жизненный цикл

Статус: **не проверено полностью** (`HTTP-LIFETIME`). Проверить два AP-клиента:
отключение одного не убирает HTTP для другого; zero→one reconnect не создаёт
второй сервер и не теряет сервис. Проверить scan/upload/weather/смену темы во
время reconnect. Заводскую остановку сервера при уходе одного клиента не копировать.
Сетевой gate — без LCD, display gate — без сетевого критерия. QEMU TCP clients
не выдавать за реальную RF/WPA association; ограничения модели указывать явно.

## 4. Электрические и аппаратные различия

Статус: **аппаратная приёмка не выполнена**. Исследовать RESET/DC pull-ups:
factory включает, native выключает; проверить схему/startup/reset до изменения.
Выполнить H01–H09 из [матрицы](tests/README.md): настоящее питание, дисплей,
GPIO18/LEDC, Wi-Fi, настройки/фото после потери питания и Internet weather.
Для испытаний потери питания — отдельный тестовый образ/backup. Подключённую
плату сначала идентифицировать; посторонние устройства не прошивать. QEMU
кадры не подтверждают электрические состояния GPIO и RF.

## 5. Аудит всего заводского образа

Статус: **176 выбранных функций учтены; полнота всего образа не доказана**.
Проверить indirect calls/callback tables, tasks/timers и handlers вне экспорта.
Найти full-image xrefs NETWORK/SLOW flags, `browser_time`, `clickCount` и JPEG
flash-output branch. Не придумывать функционал по неиспользуемому полю и не
объявлять ветку мёртвой по отсутствию caller в выбранном экспорте.
Исправить устаревшую навигацию symbol-map/reference/organizer. Расширять полные
кадры на цвета/яркость, длинные поля и переходы тем; известные factory corrections
документировать, не скрывать несовпадения масками.

## 6. Приёмка окончательной версии и правила работы

Для завершённого исправления — focused commit, failing test и проверка исправления,
метки FIXED_RECONSTRUCTION/FIXED_FACTORY по принятым правилам, комментарии функций
и сложных мест. Затронутый код разделять по назначению; converters — свои модули.
После интеграции — native/artifact/browser/flash, отдельные network/display gates,
full suite и 24h H10 с heap/stack. Связывать отчёты с точными app/ELF/source/QEMU
hashes; успех старой сборки или короткого прогона не переносить на новую.
Production builds для тестирования сохранять в
`firmware/development/small-tv-esp32c2-reconstructed/`; releases не перезаписывать.
При изменении QEMU сохранять CYD/C3 OLED и выполнять их отдельную regression.

JPEG-LS, JPEG 2000, JPEG XL и WebP — отложенные улучшения. OTA не добавлять по
текущему запросу пользователя; звук и SD не входят в заводской функционал Small TV.
