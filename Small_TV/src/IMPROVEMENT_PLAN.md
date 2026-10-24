# План улучшения восстановленной Small TV

Обновлено: 2026-10-24. База: `main` / `51cd114f9`.

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

Статус: **codec/cache/worker включены в development app; полная приёмка не завершена**.

Уточнение пользователя 2026-10-23: не отключать все progressive JPEG по названию
режима. Ограничивать **суммарный program traffic** одной обработки, включая
коэффициенты, RGB565 cache и его journal. Default200KiB (204800bytes), значение
настраивается от0;0запрещает program **и erase** decoder/cache. Исходный upload
считается отдельно. Cache invalidation до source upload переносит свой расход
в finish, чтобы два этапа не получали по полному бюджету. Это не лимит размера
scratch и не обещание заранее знать суммарный трафик любого JPEG. Операция,
которая превысила бы бюджет, не должна попасть в physical callback; partial
результат не публикуется. Нужны persisted UI/API setting, отказ с точной причиной,
reuse после отказа, zero hot/cold readonly, live reduction без reset/underflow,
отсутствие periodic retry writes и разрешение retry после увеличения лимита.
Это заменяет прежний безусловный acceptance тяжёлых JPEG по умолчанию; полезное
поведение заводской прошивки, остальные форматы и весь план остаются в scope.

Настраиваемый лимит **реализован и проверен** в app9C1A83BD/ELF76B5CE37/
source7D95988C, DEBUGoff;1476432bytes/59568free. Отдельный NVS key, UI/API0..uint32
KiB, единый allowance invalidation+decode, live tightening и background retry
policy. Zero включает startup: legacy без stamp не размечается; complete cache
читается без program/erase. Требование0 относится к обработке JPEG, исходный
upload/обычные settings отдельно.6298native +privacy,13inventory controls,
18transport +6integrated unsafe mutants,16DOM contracts,6artifact checks pass.
Actual C2 trace: CMYK12 остановлен ровно на204800bytes, gray progressive после
него успешен за115968; zero hot/cold и legacy startup0callbacks, whole flash
unchanged. Отдельный current LCD:15wholeframes/864000pixels exact для3тем,
real decode overlap/minute rollover.6текущих VM закрыты. Старый40-byte startup
bug сохранён как failing before control. Подробности и независимый offline
verifier: [JPEG_WRITE_BUDGET.md](tests/JPEG_WRITE_BUDGET.md).
Полная target format/fault/RAM/stack матрица под новой политикой ещё открыта;
прежние unlimited JPEG результаты не подменяют приёмку current default policy.

2026-10-24: [production format matrix](tests/JPEG_FORMAT_MATRIX.md) начат на
неизменённой9C1A83BD с200KiB. Pilot6vectors/9workflows проверил точные baseline8,
CMYK12progressive/lossless-gray16, write-limit/source-slot/SOF5 refusals и3реальных
успешных recovery. Saved-byte checker пересчитывает physical source/frame/journal,
полный diagnostic из RAM и task/heap measurements; observed worker margin5012.
Полный корпус70 завершён4independent parts18/18/17/17: всеexec0/VMreaped,
union70/92workflows independently verified.48primary pixels exact,17finishrefusals,
5sourceadmissionrefusals и22successful immediate recoveries.192physical images/
174RAM snapshots подтверждают source/frame/journal и returneddiagnostic/task/heaps.
Worker untouched5012/8192; pool47983max observed/context4984, heap-minima sum
lowerbound15468 не является simultaneous whole-app peak. Два losslessRGB6/CMYK6
вектора превышают source slot; дополнительные27754/36999-byte gradient fixtures
на том же app/ELF/source прошли настоящий decode и exact physical pixel/RAM gate.
Теперь исполнены все45precision/color pairs2..16×gray/RGB/CMYK; это не все
возможные JPEG streams. Current actual I/O/allocation faults, exhaustive publication
cuts, lifecycle/churn, whole-image/full/24h/hardware остаются открытыми.
Выбранные8границ между completed SDK operations проверены отдельно:
[PHOTO_PUBLICATION.md](tests/PHOTO_PUBLICATION.md).16fresh owned processes,
8exact cold backings и8успешных recovery uploads; весь physical flash/authority
проверен offline,10negative controls отвергнуты. Partial cache никогда не видим;
committed cache до settings commit тоже не публикуется. Это abrupt process cuts,
не in-page electrical power loss, injected SDK I/O/allocation или NVS-internal faults.

Checkpoint 2026-10-23: реальные upload/UI используют общего владельца codec и
проверенный RGB565 cache. Фоновая очередь и SDK async HTTP освобождают HTTP task;
общий media mutex не удерживается во время decode. Для заводского baseline
оставлен TJpgd strip producer с прежними пикселями, расширенные режимы идут через
bounded libjpeg. В обычной сборке генерируются matching stamp/cache headers/assets.
6001 native checks,12 inventory controls и6 artifact checks pass; исправлены
устаревшие queued source lengths и подавление повторной обработки после временного
read fault. Реальный C2 workflow выявил нехватку общей RAM: одного malloc limit
недостаточно. Добавлены16KiB service reserve при allocation и cooperative decode
checkpoints; точные required/available в HTTP. Проверки текущего target workflow
и дальнейшие ограничения — [JPEG_MAIN_INTEGRATION.md](tests/JPEG_MAIN_INTEGRATION.md).
Это не приёмка всех JPEG на target: host support не означает, что конкретный
файл помещается в рабочую C2 с Wi-Fi/UI. Полный RAM/stack/time/abort matrix,
отдельный LCD, power-cut/full/24h/hardware остаются открытыми. Safe migration
matching native assets проверена следующим checkpoint. Предыдущие checkpoint
ниже — история, не текущий статус UI.

Следующий checkpoint 2026-10-23: matching unstamped native assets теперь принимаются
отдельным erase-free bootstrap. Raw/SDK partitions, 27 physical payloads, каждый
candidate byte (fresh double-read), допустимое состояние stamp и final physical
guard обязательны. ID32 записывается и проверяется первым, commit header8 — последним;
FF tail24 не записывается. Это исправляет найденное ошибочное принятие чужого
заголовка с недописанным ID. Без erase/photo/settings writes; один startup budget
и отзыв всех старых портов. 23409 host scenarios/8 new +14 old compiled mutants,
31 transport cases, 5995 native/direct privacy, 6 artifact и 12 owned main C2 processes pass.
Проверен app update поверх реального сохранённого old-main образа с его NVS/photos/
cache; layout/codec IDs не меняются. Чужие/занятые области не стираются. Подробности
[JPEG_LEGACY_PROVISION.md](tests/JPEG_LEGACY_PROVISION.md). Это закрывает matching
legacy migration в host/QEMU, не аппаратную или произвольную factory-layout миграцию.
Target memory/stack/fault/format matrix, отдельный LCD, upload/decode power-cut,
network lifecycle/full/24h/hardware по-прежнему открыты.

Следующий checkpoint: [cache-backed photo LCD](tests/PHOTO_CACHE_FRAMES.md) текущей
app034287C7 прошёл отдельно от network gate. 54 полных кадра /3110400 pixels
совпадают с literal factory instructions: все пять фото, mask10, empty mask,
все fade phases, configured day/night restoration с настоящей SNTP синхронизацией.
13 negative report controls, 3 owned/reaped native VM; protected source photos/
immutable flash сохранены. Это не clock continuity других тем во время upload.
Найдено открытое расхождение времени старта: первое native фото23.389901guest sec
против factory20.565822 в том же профиле (отдельная owned VM). Slot0 готов уже
около5.3sec, но worker держит slideshow заблокированным до подготовки всех пяти.
Следующее действие: оптимизировать initial/preload scheduling без искусственных
задержек, пропуска валидных фото, зависания на damaged slot или изменения fade;
добавить failing timing/partial-readiness/cancellation/cold0writes проверки.
Pixel gate pass не закрывает этот timing gap, полный JPEG target matrix,
clock continuity, power-cut/network lifecycle/whole-image/full/24h/hardware.

Следующий checkpoint: [next-photo prefetch](tests/PHOTO_PREFETCH.md) закрывает
измеренный startup gap. Первый native кадр теперь5.560901guest sec (pilot5.619954)
вместо23.389901; готовится только следующий eligible source между fades, damaged
source пропускается, transient I/O/cancel/memory retry сохраняется.6077native/
privacy,12inventory controls,6compiled unsafe policies,13440executed RV32 selector/
fade transitions и6artifact pass. Actual appABF14143:5owned/reaped processes,
104полныхкадра/5990400pixels exact, включая damaged-first и настоящий cold cache.
Cold first2.251859sec, ни одной попытки JPEG program/erase, весь4MiB unchanged.
App/ELF/source/runs привязаны к новому proof. Это photo LCD/storage/timing gate;
другие clock themes during foreground decode, полный target RAM/stack/format/
fault matrix, HTTP/network lifecycle/churn, power cuts, whole-image/full/24h/
hardware остаются открытыми. Старые HTTP/decoder проверки не переносить на новую app.

Следующий checkpoint: [clock continuity](tests/JPEG_CLOCK_CONTINUITY.md) той же
appABF14143 проверена отдельно от HTTP. Classic/simple/dial продолжают показывать
точные целые кадры при foreground progressive gray8:13workload+47control,
3456000actual pixels, native/factory references, minute rollover,16+12negative
controls. HTTP requalification: fullCMYK12/richRGBprogressive/gray приняты, два
sampling44 refusals с required/available;862GET/0errors(max0.875host s), отдельно
160controlGET/0errors(max0.5). Прежней host границы240s не хватило на CMYK12;
explicit900s наблюдение завершилось за305host s при прежних guest budgets/GET10s.
Actual stopped pre-publication VM восстановлена обычным boot/upload:journal1→2,
source/frame SHA exact. Это не physical brownout. Все11accepted processes reaped.
Открыты CURRENT target format/RAM/stack/fault, LCD под CMYK12/richRGB, publication
powercuts, lifecycle/churn/whole-image/full/24h/hardware. Progressive coefficient
write optimization и cache сохраняются; повторный показ не повторяет decode.

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
По запросу уменьшить трафик добавлен reversible coefficient converter и first-use
sector initialization. На same-executable raw/packed richCMYK12 program3780608→
2582784(-31.68%), erase923→113(-87.76%); capacity/pool peak прежние. Flat tradeoff
учтён.19726488native assertions/11compiled mutants, actual codec/fault gates pass;
это пока host, не native UI. [Результаты](tests/JPEG_COEFFICIENTS.md).
Следующий checkpoint: самостоятельный portable decoder API с bounded input/
RGB565 output, per-instance pools/backing, exact whole-array preflight и typed
errors реализован.63positive/7resource/10negative/1197callback failures/12format
transitions и6compiled mutants pass. Legal4x4 требует524288; при460800 refusal
до backing I/O. RV32 binding связан, context4984, но не исполнен на target.
[Результаты](tests/JPEG_DECODER.md). Native UI3E03/TJpgd пока без изменений.
Следующий checkpoint: API связан с production NOR/packed adapter и исполнен в
standalone C2 QEMU с real ESP-IDF flash calls.61host positives/827physical faults/
48global stops,15273unit assertions/6mutants и два fresh target processes pass.
Target fullCMYK12 requested allocator peak45576, stack free1988/4096; это без
UI/Wi-Fi и не whole-app fit. [Результаты](tests/JPEG_BACKING.md).
Следующий checkpoint: persistent source/SHA/row cache/journal owner реализован
и связан с реальным decoder на host.59images/5source limits/6negative,268fault
recoveries/18stops;12120physical cuts/946SHA faults/2424stops и9mutants pass.
Cold hit не вызывает decoder и не пишет flash. Исправлен подтверждённый silent
source read bug, проверены все218input/readback points. RV32cache handle5600,
полный cache/storage ET_REL9016code/16rodata; нового target cache runtime ещё нет.
[Результаты](tests/JPEG_CACHE_PIPELINE.md).
Далее — расширить sampling/capacity bounds, выбрать budgets; invalidation/source
hash в upload/cache workflow, matching assets build/deployment с сохранением photos/settings.
Полный HTTP/power-loss workflow и native UI decoder integration ещё открыты.
Следующий checkpoint: обычная production-сборка сама готовит offline JPEG из
закреплённого source bundle, компилирует codec/storage adapters и сохраняет
точный dependency report. Архив RV32 побайтно совпал с ранее проверенным D690;
само это изменение ещё не переключает UI/upload с TJpgd. Расширен явный reverse
inventory до459functions при прежних170app, добавлены omission controls для
codec/storage. [Сборка и границы проверки](tests/JPEG_DEPENDENCY_BUILD.md).
Следующий checkpoint: metadata-only multi-scan gate подключён к реальному
upload finish,63validJPEG/5private-or-trailing refusals,7compiled unsafe variants
отвергаются.3727direct controls включены в обычный native runner вместе с5806
прежними checks. Source inventory469/172app. TJpgd пока остаётся decoder для
upload/UI; разрешение progressive в HTTP ещё не включено. Новый gate не смешивает
privacy и codec support. [Проверки](tests/JPEG_PRIVACY.md).

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
   Объединить validation и заполнение RGB565 cache в один decode; готовые кадры
   читать из cache без повторного multi-scan decode/записи coefficient scratch.
   При native integration не держать общий media mutex на всём slow decode:
   owner/worker должен сохранять source serialization и отзывчивость UI/HTTP.
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

2026-10-24: проверены реальные SDK events двух виртуальных AP peers для обеих
прошивок: 1→2→1→0→1, четыре HTTP-запроса на каждый run. Native — один start,
ноль stop; factory — повторный start затирает handle при listen(112), и stop
после этого не достигает оставшегося сервера. QEMU DHCP исправлен: bounded
parser/identity/server selection/ACK-before-ready, отдельные protocol tests.
См. [NETWORK_CLIENTS.md](tests/NETWORK_CLIENTS.md) и сохранённый offline proof.
Остаются уход **первого** при подключённом втором, корректная Ethernet
маршрутизация/endpoint selection, scan/upload/weather/theme/reconnect/churn.
Этот checkpoint не закрывает весь `HTTP-LIFETIME`.

Следующий checkpoint того же дня: QEMU `7a9764712b` исправляет выбор оставшегося
peer, ARP-соседа и повтор незавершённой management association. Обе прошивки
прошли уход **любого** из двух клиентов и zero→survivor return (4 runs/16 HTTP).
Before controls воспроизводят потерю HTTP на старой модели; один stalled factory
reconnect сохранён отдельно. Proof `network-relay-validation-20261024.json`.
Эти selected сценарии закрыты; scan/upload/weather/theme, reconnect/churn,
deterministic loss и full APSTA/RF gate остаются открытыми. Отдельные host
endpoints каждого Wi-Fi peer — возможное улучшение QEMU, не условие текущей
проверки: AP/STA endpoints уже разделены, HTTP здесь проходит через оставшегося peer.

2026-10-24 AP activity checkpoint: native `9C1A83BD` на том же QEMU `7a9764712b`
прошёл scan/start/chunk/finish/theme/reselect во время alternating peer changes.
Два полных цикла: 12 основных HTTP 200, 14 SDK peer events, две точные проверки
байтов JPEG и темы, один start/ноль stop сервера. Presence меняется на реальном
входе функции при ещё pending HTTP; 6 callbacks вложены в исполняемые вызовы.
Offline proof `network-activity-validation-20261024.json`, 8 negative controls.
См. [NETWORK_ACTIVITY.md](tests/NETWORK_ACTIVITY.md). AP scan/upload/theme на
этих selected переходах проверены; STA weather/reconnect, prolonged churn/soak,
deterministic loss и аппаратная RF/WPA приёмка остаются открытыми.

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
Навигация symbol-map/reference/organizer исправлена2026-10-24:176явных function
links,74исправленных module summaries, original pseudocode bodies сохранены,
13existing inventory controls и reject-before/idempotent-after проверки pass.
Это не закрывает полноту образа или неизвестные indirect calls. Расширять полные
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
