# Контекст работы над восстановленной Small TV

Актуальные решения и рекомендации для продолжения сравнения заводской прошивки
ESP32-C2 с собираемым C-проектом в `Small_TV/src`. История действий и результатов
сохраняется отдельно в [рабочем журнале](WORK_LOG.md). Обновлять этот контекст после
завершённых исправлений; при продолжении читать оба файла и проверять Git-статус.

## Цель и принятые решения

Добиться функционального соответствия заводской прошивке. Подтверждённые ошибки
оригинала исправлять, как попросил пользователь. Намеренные исправления учитывать
отдельно от ошибок нашего переноса; полное совпадение пока не установлено.

- Сопоставлять оригинальные инструкции с реально скомпилированным C ELF, а не
  только с псевдокодом Ghidra. Не менять исходный `Small_TV/full-flash.bin`.
- Если обнаружен интересный случай или пограничное состояние, добавлять тест:
  повторные вызовы, смена настроек/темы, ошибки SDK, незавершённые операции и
  сохранение состояния между шагами. По возможности показать сбой до исправления.
- Рефакторинг допустим в текущем участке работы: выделять повторяющийся алгоритм
  в общую функцию и проверять, что состояние и последовательность вызовов сохранены.
- По уточнению пользователя ненужные программные паузы (`delay`, `vTaskDelay`,
  циклы ожидания) убирать, включая заводские:
  устанавливать их причину и влияние, устранять лишнее блокирование и отмечать
  намеренное исправление отдельно от parity. Проверять отзывчивость и работу
  таймеров после изменения; периоды часов и debounce не считать лишними без анализа.
- Выбирать осмысленные имена; объяснять назначение каждой функции и сложные места.
  Комментарии в C писать на английском. Исправленные функции маркировать по
  [CORRECTION_MARKERS.md](CORRECTION_MARKERS.md).
- OTA пока не добавлять. Обработка фотографий сохраняет удаление метаданных,
  изменяемую рамку кадрирования и масштабирование выбранного фрагмента до 240×240.
- Поля текста очищать и ограничивать собственными границами. Длинные город,
  описание и название погоды прокручивать туда и обратно с паузами; короткие
  оставлять неподвижными. Смена текста/темы сбрасывает фазу, обновление статуса
  сохраняет её. Прокрутка — запрошенное расширение, а не поведение оригинала.
- Сохранять сборки в `firmware/development/small-tv-esp32c2-reconstructed/`.
  Коммитить завершённые изменения отдельно, не включать посторонние правки,
  временные ВМ и журналы с пользовательскими данными.

## В работе: календарные переходы через SNTP

2026-10-16: новый `tests/calendar_qemu.py` готовит natural-transition matrix:
14 границ (Sunday/year/month/leap/noon, GB/US/AU DST, NP fractional offset,
post-2038), каждая в classic/simple/dial. Три date formats и оба hour modes
чередуются по случаям: все шесть сочетаний встречаются в каждой теме. Это
42 transitions / 84 completed frames на прошивку, не полный декартов продукт
всех параметров. Между before/after не разрешается новый NTP reply; ход часов
не подменяется. Наблюдаются реальные args/flags/calendar и все 57 600 пикселей.

Native календарь обязан совпасть с pinned IANA TZif; literal factory Newlib
исполняется отдельно и сохраняет implicit-DST ошибки. Чистый pixel reference
исполняет реальные factory renderers с ранее объявленными коррекциями; буквальный
factory replay сохраняет фактические flags/cache и entry background в отдельной
модели. Рабочая QEMU-прошивка не получает записей RAM/PC/регистров/инструкций.

Пробный Sunday прошёл во всех трёх темах отдельно для factory и native. Literal
factory replay даёт 0, native clean corrected reference даёт 0. В native один
POST занял 5.75 guest / 8.14 host seconds; H09/network latency этим не закрыт.
Новый helper измеряет обе длительности, не повторяет failed requests, ограничивает
ответ шестью гостевыми секундами и внешним wall guard 20 s. Old five-host-second
timeouts сохранены, не выданы за успехи или окончательно объяснённые product bugs.

Неверный NTP-log path и повторный breakpoint на прежнем PC исправлены в harness.
Native integer-Celsius field хранится как double: теперь проверяется точная
целочисленность и канонический Inputs использует int, как factory ABI. Поздний
city-triggered ответ не должен считаться ADV restart; перед ADV ждём реальные
initialized/sync flags. Stable factory наблюдение подтвердило saved host,
initialized client и отсутствие новой синхронизации в течение 3.01 guest seconds.

Full `calendar-final-20261016`, shell `97647`, завершился exit 1. Все 42 factory
перехода и первые пять reconstructed/classic прошли. Следующий `/SetTimeModeValue`
вернул 200 за 6.128 guest / 8.718 host s, превысив новый шестисекундный предел.
Это failed run, не общий passing checkpoint; native matrix не завершена.
Output `.build/small-tv-functional/calendar-final-20261016`; log
`.build/small-tv-calendar-full.log`. Новый полный результат не опубликован.
Приложение остаётся 9e4f856a, ELF 7e34a29b. Не повышать тайм-аут без изучения
транспорта; причина задержки пока не установлена.

Независимая ветка `codex/small-tv-offline-clock` в `.worktree/small-tv-offline-clock`
содержит исправление зависания активных часов/фото-fade без STA и подмены IP
адресом AP. App 072135ee / source e10dd9f6 / ELF eec972f2 собран и сохранён в
firmware ветки; 33 platform cases прошли. Новые реальные RV32 network traces
дают expected fail прежней сборки и pass кандидата: DHCP .15→.21, четыре retry,
сброс счётчика, сохранение IP; 16 factory main dispatch states продолжают темы
offline. Кандидат не прошёл полный QEMU и natural link-loss test, не в main.
Его scoped reports/ассемблер/описание находятся в worktree, не выдавать прежние
опубликованные общие результаты за подтверждение нового app.
Исправление/тесты/сборка сохранены и отправлены как `6f10bc46`; exact staged
50 production inputs, network/adapter bytes, 24 platform test/stub files,
LFS app и paired ELF сверены. Platform: 33 cases / 1,181,610 checks.

PCAP diagnostic `.build/small-tv-parity/http-latency-pcap-20261016-03` воспроизвёл
три медленных POST из 60: первый SYN не дал ответа, повтор через 5.82–5.94 guest s,
после прихода HTTP headers ответ через 42–49 ms. Это локализует фазу задержки,
но не доказывает RX DMA/SLIRP/SDK причину. Обезличенная сводка —
`../qemu/parity/http-latency-observation.json`; raw PCAP не публикуется.
Failed calendar summary — `calendar-transport-observation.json`.
Тестовая diagnostic VM закрыта. Создан отдельный QEMU worktree
`C:/Work/QEMU-ESP32/.worktree/small-tv-wifi-link`, ветка `codex/small-tv-wifi-link`,
от 1c7e4c0512. Diagnostics завершены: dedicated RX trace подтвердил no-descriptor
loss. Commits `6f3fa56a48` (trace), `9d4da15732` (C2 queue) отправлены в отдельную
ветку; remote SHA сверён. Candidate QEMU SHA e8122fe2, canonical по-прежнему
c970591d. C2 теперь удерживает head frame в существующей bounded queue до записи
RX_BASE_DESC, без poll/retry delay; C3 legacy path сохранён. Новый packet test
показывает fail только C2 на старом canonical и pass всех семи на candidate;
проверяет starvation 5 s, FIFO, queue limit и no duplicates. SPI/I2C/SD и
CYD/C3 legacy/modular boot прошли. 120 реальных HTTP POST: max .165376 guest s,
раньше trace-only QEMU давал 5.74/5.76 s. Scoped evidence
`../qemu/parity/rx-queue-candidate.json`. Это не полный firmware suite.

Сейчас жив native-only calendar process shell 32961, output
`.build/small-tv-functional/calendar-native-complete-20261016`, log
`.build/small-tv-calendar-native-complete.log`. ROOT production/test inputs и
canonical QEMU c970591d заморожены до terminal result. Не заменять binary и не
перезапускать только из-за observer timeout. После завершения: обновить QEMU
canonical только из проверенной ветки с regressions, затем новый полный suite.
Для offline app 072135ee ещё нужна natural station disconnect/reconnect проверка.

Новый участок для последующего анализа: `settings.c` сохраняет через 1 s покоя;
factory dirty countdown начинает с 50 и сохраняет на 51-м eligible loop pass;
в loop передаётся delay 10 ticks. Реальный factory QEMU/GDB sample теперь
подтвердил около 100 ms для десяти ticks (98.5–109.5 ms, десять samples);
`../qemu/parity/factory-loop-delay-observation.json`. Эта задержка измерена,
а время body/render/weather в расчёт 51-pass модели отдельно не включено.
Игнорируемый persistence_probe использует явную модель 100 ms/eligible pass;
получает single 5.1 s против native 1 s, burst один save против трёх. Это
model timestamps, не измеренные RF/RTOS задержки. Счётчик
останавливается на blocking weather и не выполняется в setup branch. Адреса
`0x420090e2..0x420090f8`, save call `0x4200916a`, loop delay `0x42008fd2`;
bounded assembly в `.build/small-tv-save-delay-assembly`. Это установленная
разница алгоритмов, требующая отдельного теста/coalescing analysis, не закрыта
текущим календарным gate. Возможная связь с HTTP latency пока только гипотеза.

## Последний проверенный участок: завершённые кадры и яркость цифровой темы

2026-10-16: добавлен строгий gate полного кадра: реальные QEMU renderer entry/return
наблюдаются аппаратными GDB breakpoints без записи guest RAM/регистров/кода.
В отдельном Unicorn исполняются реальные RV32 renderers и JPEG/BMP. Все 57 600
пикселей сравниваются; поздний кадр после 40 virtual seconds строится с чистого
фона. Пройдены classic без/с погодой и dial, обе прошивки, по четыре кадра (24),
плюс 40 полных сцен с одинаковыми входами. См.
`../qemu/parity/completed-scene-checks.md`.

На прежнем app 446a5c3c первый цифровой кадр имел стартовую яркость 901/1000
при выбранной 1000. Read-only LEDC/GPIO observation отделил эту ошибку от
отрисовки: при фактической яркости отличалось 0 пикселей. Factory 0x42008e08
применяет backlight перед последующим digital render; наш объединённый init/render
передавал первый кадр раньше. В `clock_task` восстановлен этот порядок для
classic/simple. Новый платформенный тест проверяет duty во время передачи
цветных пикселей обеих тем, а не только после завершения кадра.

Новая сборка: app `9e4f856a45fb3526eb2032f08f948c1354e8ba80065d1b4b32242f2d0c94f03c`,
source `6ab9c80f0d245a4fdd977b6028a453d95a6156de6172ee959ced5284159db51b`,
ELF `7e34a29babbb85c1d9f8f5eac8f01ce48e7748952ed6d5c4dcb0e31bc91a7170`.
App 1,176,112 bytes, свободно 359,888; DIRAM 80,706. Full `scene-final-20261016`
прошёл из одного неизменяемого набора тестов: native 3,884, platform 29 /
1,180,724 checks, все RV32/QEMU groups и пять обычных scene pairs. Все 24
завершённых кадра совпали с replay. В 33 canonical classic scenes literal
factory/native difference равен 0; семь dial scenes совпали с явно исправленной
геометрией, буквальные отличия сохранены. Все 54 test inputs, 50 production
inputs, 106 TZif, font, LFS app и ELF проверены по staged bytes.

Код/тесты/сборка — `caad5d3c`. Current positive reports опубликованы для этого
app, включая `../qemu/completed-scenes-validation.json`; scoped negative
`../qemu/parity/first-digital-brightness-before.json` сохраняет старые app/ELF
и фактический duty 819. Запуск preflight с изменившимися test bytes не принят.
QEMU executable/source и физическая плата не изменены, созданные ВМ закрыты.
Полное соответствие всех путей не установлено: calendar/DST transport matrix,
дополнительные JPEG и concurrency/browser/physical/long-run остаются ниже.

## Предыдущий проверенный участок: региональные ключи и NVS v2

2026-10-16: восстановлены все 20 байт country slot, HTTP, raw import/export,
time/weather buffers и cache. NVS v2 = 364 bytes; v1 = 344 bytes мигрируется
по прежнему ABI с сохранением всех полей. Raw sector имеет прежние смещения
и приоритет. Нулевой legacy mode нормализуется только для v1; v2 mode 0
сохраняется. Неизвестный корректный ключ продолжает использовать GB fallback;
город не определяет часовой пояс. Details: `../qemu/parity/regional-settings-checks.md`.

Host проводит все 109 ключей через API/codec/persistence. Actual QEMU проверяет
все 15 regional keys (US/CA/AU/PT-AZ), clock/date pixels, weather cache, max
64-byte city + 19-byte region + full-width comma, rejected inputs и cold boot.
Настоящий SDK NVS fixture проверил все поля v1 migration и загрузку только из
NVS v2 после стирания raw sector в остановленной disposable VM.

`regional-final-20261016` полностью прошёл host/RV32/QEMU, все пять scene pairs:
native 3,884, platform 28 /
1,145,676 checks, timezones 109 / 36,404 comparisons,
JPEG 107, UTF-8 и transport gates. Сходство полных кадров не является критерием
parity; аппаратная плата, браузер и soak не проверены. Дамп не менялся.

App `446a5c3c5484c43a9f1645fd4e4487e62cf8443ccc4e76637c266ae4745d0bfb`; source `031eec92fad917e25cf7250e2427edb24524a7b29ae13cd90131101b0c766619`;
ELF `bde762ed5653506d3aadb65cb30c135dabef65f0b5da62cfa42b67375ac68da5`. App 1,176,096 bytes,
free 359,904; DIRAM 80,706.
Runtime heap/stack не измерены. Entry comments 157,
correction markers 50. Code/build commit `f27401af`.
QEMU main `1c7e4c0512`, compiled source `5e136b6eab`, executable c970591d unchanged.
Новые эмуляторные изменения и физическая прошивка не выполнялись.

Отрицательный `regional-before.json` относится к прежнему native app 2acdf34f:
AU-W обрезался до AU и показывал на три часа больше. `regional-factory-delay.json`
побитно подтверждает старую дату Jan 1 при обновлённом календаре Dec 31.
Оригинальная simple theme проверяется после штатного dial→simple re-entry,
наша — без него. AU-C/AU-E сохраняют объявленную factory implicit-DST разницу;
native обязан совпадать с IANA. Отрицательные результаты не переименованы в green.

Это предыдущий checkpoint; его app/source/ELF не переименовываются в новую
сборку. Перечень остающихся проверок расположен ниже.

## Предыдущий проверенный участок: новый сетевой профиль QEMU

Repo-owned `Small_TV/qemu/profiles/small-tv-c2.json` хранит schema 1 hardware,
factory SPI2/ST7789 wiring, network URLs/NTP hosts/SSID. `qemu/run.ps1` передаёт
его shared QEMU launcher; default state — `.build/small-tv-vm/<network>-<variant>`.
Standalone/full/comparator paths используют один профиль, weather/fields/text
fixture использует generic `service_port`. NTP/URL names остались factory;
profile не меняет compiled firmware endpoints и не содержит private keys.

QEMU kernel built from `5e136b6eab95345fa6889463dc5b0e3125d792ef`, source/helper main
`1c7e4c0512c68efd6e6d11276bfe7a13c070b7bd`, RISC-V executable
`c970591d626c7500cccd00121ba52667998ebeb091388acd2af46c22cc10bea6`. Установлен в canonical QEMU bin; прежний BF98..
и marker сохранены в `.cache/small-tv-profile-runtime-before`. Xtensa F6A.. прежний.
Own frozen worktree `C:/Work/QEMU-ESP32/.worktree/small-tv-service-profile`
(codex/small-tv-service-profile) оставить для следующих parity checks.

`service-profile-verified-20261014` объединяет реальные passing stages третьего
full attempt с fresh profile gate + пятью scene pairs после исправления seeder
signature. Успешные stages сохраняют точные unchanged input bytes. Все automatic
gates прошли на прежнем
app/source/ELF: host/native/platform/JS/integrity/timezone-source; RV32 renderer,
control/classic/weather/calendar/JPEG/timezones/time-state/text; profile 4;
реальный QEMU boot/reset/AP→STA/persistence/weather/fields/UDP SNTP/UTF-8 и пять
сцен. Source app не переписывалась. `qemu_profile` и publisher/verifier связывают
profile/launcher/comparator/compiler bytes; runtime guard проверяет стабильность.
Точные staged hashes проверяются перед коммитом. Source/app остаются ниже в
UTF-8 checkpoint; full functionality / physical RF/browser/soak ещё не доказаны.

Дополнительные evidence: packet DNS/NTP 6, shared helper 11, modular SPI/I2C/SD/CS
и CYD MMIO; legacy CYD + C3 legacy/modular boots. CYD boot LCD blank baseline,
LCD проверен отдельным MMIO; C3 OLED nonempty и legacy/modular hashes совпали.
Штатный wrapper/main runtime offline и clock boot/reset/SNTP passed. Public summary:
`../qemu/profile-compatibility-validation.json`; raw logs/flash не публиковались.

Неуспешные service-profile full runs сохранены: test-only old
weather-services property, затем service=weather trace. Generic service-hosts /
service=http expectations исправлены; target weather preflight прошёл обе apps.
Третий attempt дошёл до всех HTTP/time/UTF-8 passes, затем остановился на новом
optional SSID argument seeder. Исправлен comparator; scenes и profile gate
повторены отдельно и проверены точным unmodified validator из qemu_suite.py.
QEMU helper 1c7e4c исправляет ложное animation ожидание для static offline/setup;
clock animation остаётся обязательной. Main QEMU fix pushed; private user/source
images и physical devices не менялись. Owned VM/listeners закрыты после тестов.

## Последний проверенный участок: UTF-8 и поля текста

Строгий `app/text/text.c` decoder принимает Unicode scalars, а не произвольные
high-byte pairs. Известные A1E6/A848 и Unicode ℃/℉/°C/°F сохраняют factory
bitmaps. Неизвестный scalar без глифа -> '?'; malformed byte не поглощает ASCII.
452 bundled non-ASCII Spleen glyphs подготовлены в 16/24/32 cells, factory ASCII
сохранён. UTF-8 copy сохраняет прежний 15-byte бюджет погоды и полную границу
символа. Ширина/центрирование/прокрутка используют общий token decoder.
Новый URL escape явно ASCII-only, не зависит от locale.

`utf8-verified-20261014` объединяет прошедшие host/RV groups исходного full run
и полный повтор QEMU на pinned dependencies с теми же test/app/source bytes:
native 3,069, platform 26 /
1,145,647; JS/integrity, timezone_sources 9,
прежние renderer/control/classic/weather/calendar/JPEG/timezone/time-state.
Новый text RV32: 1,644 glyph comparisons,
195 full-panel cases, 219 scalar и
240 prefix/guard checks. Новый real HTTP gate прошёл
пять synthetic Unicode случаев, fragmented response, точные cache bytes,
все native field/guard pixels и полный scroll cycle. QEMU AP→STA/persistence,
weather/fields/actual SNTP и пять сцен тоже прошли. Сходство whole-frame остаётся
наблюдением; полного соответствия, physical/RF/browser/soak результата нет.

Factory UTF-8 `/updateCity` воспроизвёл NULL-client Load access fault в отдельной
VM: MEPC 4203e8f0, RA 4201098c, address c. `42010864` вставляет raw city bytes,
`42010988` вызывает perform без init guard. Native URL encoding/NULL-check
защищают этот путь; normal original flows использовали ASCII locations, чтобы
отдельно проверить Unicode JSON/cache. Source dump и физические платы не менялись.

Сборка: app 1,175,584, free 360,416,
DIRAM 80,650; app SHA
`2acdf34f68edccdfa9fd4753a22909598391ee23a6bc2e40e91737061a80f826`;
source `72ad106b1276f430f7f26b5e1a7fc6660f0174919f009d3591a70d660b64e1b5`;
ELF `570d62ad0547ae49a4bbe42b7deee586d319553f5565599d35635eaf5da6d2c5`.
Entry comments 155, markers
44. Public evidence:
`../qemu/parity/text-validation.json`, `../qemu/text-http-validation.json` и
`tests/functional-validation.json`. Старый negative text observation сохраняет
прежние app/ELF hashes. Native text/time-sync excerpts обновлены на точный ELF;
bounded factory temperature helper добавлен в existing assembly manifest.

Первый `utf8-final-20261014` дошёл до всех сцен, но runtime guard отклонил QEMU:
параллельное слияние изменило canonical HTTP-helper. Этот failed report сохранён.
Все QEMU checks повторены без overlay в собственном
`C:/Work/QEMU-ESP32/.worktree/small-tv-utf8-validation` на ветке
`codex/small-tv-utf8-validation`, pinned commit `5520fbb787` (parent b90e2131b8).
Использованы те же BF98.. executable и production app; fresh executable/profile/
helpers сохранились за повтор. Фактический client SHA
`222c3b17f3cf9fc4aed123fda4939678f7366076cd8f86373d3e59b630b22c94` записан в report.
Только реально прошедшая новая QEMU-группа заменяет rejected attempt; остальные
группы сохраняют исходные результаты и точные unchanged test hashes.
Чужие branches/worktrees не переключались. Worktree оставить для следующих
parity checks, пока параллельный main продолжает меняться; binaries в нём ignored.

## Завершённый участок: время и часовые пояса

`timezones.c`, `time_sync.c`, `clock_ui.c`, `timezone_oracle.py`. Настоящий
заводской `tzset`/`localtime_r` исполняется по адресам `0x420aa9c8`/`0x420aa5ce`;
новый C, Gregorian-переходы и `gmtime_r` исполняются из нашего ELF. Библиотеки
с прежними строками TZ совпадали, но дали 116 календарных отличий от IANA в
12 месячных выборках 2026 года для каждого из 109 ключей.

Добавлены закреплённые TZif IANA 2026e из wheel tzdata 2026.5, SHA и происхождение
в `resources/timezones/manifest.json`. Сохранён выбор по стране, fallback GB и
двухбуквенный интерфейс; длинные исходные ключи не добавляют выбор региона.
Генератор проверяет хеши/ключи, сохраняет полную историю и явные будущие правила,
дедуплицирует таблицы; TZif отмечены в Git как binary. Дисплей рассчитывает
календарь по текущему snapshot независимо от глобальной TZ; worker обновляет
фиксированное смещение libc при переходах, включая offline.

По запросу об открытом источнике добавлен `tools/update_timezones.py`:
`--check-latest` читает официальный IANA `tzdb/version`; download воспроизводит
закреплённый wheel tzdata либо требует все три новых version/SHA pins. Данные
пакета не устанавливаются и не исполняются. Кандидат сначала проверяется целиком;
`prepare_timezones.py --source ...` позволяет проверить его без замены текущей
базы. Обычная сборка остаётся офлайн. Проверены настоящая HTTPS-загрузка,
побайтовое воспроизведение 106 TZif/109 country keys и идентичный generated header,
девять офлайн-регрессий. IANA на 2026-10-14: 2026e, пакет 2026.5. В full suite
добавлен обязательный `timezone_sources`; старые опубликованные отчёты не
содержат эту группу и не являются доказательством нового полного прогона.

Текущий SNTP участок остаётся отдельным от обновлятора: atomic validity после
настоящего callback, pre-2025 и validity-change при том же epoch; пять literal /
восемь native RV32 случаев и две real clock-task темы. `time-network-ninth`
прошёл обе целые прошивки: отказ NTP 1/2 -> 3, reconfigure -> 2, 2024/2026,
backward leap day, post-2038 и reset/recovery. `0x42017ea0` вызывает restart,
enabled query находится в `0x4201bec6`, stop/init callback — `0x42017d34`.
Restart может прерывать 15-секундное ожидание следующего сервера. SDK сохраняет
server index при stop/init; тест не должен предполагать возврат на 0.
После reset использовать настоящие SYSTIMER ticks*5/52, RTC/HRT offset и system
correction; QEMU lifetime counter не равен SDK time-since-boot. Только QMP read /
stop/cont и внешние NTP packets; нельзя подменять guest clock/RAM/callback.

QEMU main `b90e2131b8` отправлен: service controls и документация; свежие CYD/C3/
модульные SPI/I2C/SD и пять network cases прошли. RISC-V SHA `bf98de89...33d44c`,
Xtensa `f6a5f293...3abc35`. Финальный app 1,115,104, SHA
`2a60eefcc480f96eced3e6318f91995f89b38475f93ce3551da1847c135f672c`, source
`9402fd83c7cef65222685deff3fbe6a98ad9cb197413da3d6af2b90536ace019`;
ELF `ee74d566d3d13a33c5d2ce767d8b7570efc853b6446d390b9d6646dc7793a394`.
Полный `sntp-final-20261014` прошёл и опубликован: native 3,021, 26 platform /
742,437, JS/integrity, timezone_sources 9, прежние machine/control/classic/
weather/calendar/JPEG, 36,404 timezone, 5+8 time-state и полный QEMU. В реальном
SNTP шесть UTC observations, максимум около 33 ms; все reset/date stages прошли.
151 production entry comments, 36 marker functions, DIRAM 80,650; 47 test inputs.
Код/сборка/тестовые инструменты — `6b7a52d3`; 48 production и 106 TZif совпали
с Git bytes. Результаты/журнал фиксируются отдельным коммитом.
Текущие отчёты связаны с этим архивом. Нижеследующий timezone baseline сохранён
как история; не переписывать старые negative/board identities. См.
`../qemu/parity/time-sync-checks.md`. Полное соответствие ещё не установлено.

Машинный gate прошёл 36,404 проверки: 109 ключей, все записанные переходы ±1 s,
будущие границы 2026/2038/2100/2400, дробные смещения, отрицательный DST,
fallback и пять ошибочных параметров. Ошибочный epoch сохраняет выходной календарь.
Прежний ABI-прототип ошибочно выравнивал named 64-bit argument; исправлен по
скомпилированным инструкциям: utc занимает a1/a2, output — a3.
Платформа прошла 24 случая, включая реальные worker и обе темы при изменении
страны/epoch с прежними секундами. Colon зависит от исходного timer event;
не подменять его фазу ожиданием нового полного кадра.

Сборка сохранена: app 1,115,008 байт, SHA
`4778377602bd3c596aba9640202fd40fb9420fb7a10b3da29c949a936a72585c`;
source `b1acb29646c238edda0018deac4e07042d5ff1187106bd4e9836fcdb4ffc875c`.
Полный `timezone-final` прошёл и опубликован: все host/machine/QEMU gates,
native 3,021; платформа 24 / 742,006; 36,404 timezone и прежние renderer/media
группы. В реальном HTTP field-потоке принято 110 native кадров прокрутки.
Архив и отчёты повторно проверены по хешам. App-раздел: свободно 420,992;
DIRAM 80,650; 148 entry comments, 34 функции с метками. Описание проверки —
`../qemu/parity/timezone-checks.md`. Порог валидности 2025, успешный SNTP callback,
transport retry/fallback и same-second gate оригинала — следующий отдельный
участок, этим исправлением не объявлены завершёнными. QEMU/платы не изменяются.
Текущие отчёты: `tests/functional-validation.json`, `validation.json`,
`../qemu/parity/timezone-validation.json`; scoped negative — `timezone-before.json`.
Исторические negative JPEG и CYD/C3 отчёты сохранены с прежними хешами.
Созданные для текущего прогона ВМ закрыты.
Код, тесты и сборка — `1e9fac91`; 48 production source files и 106 TZif
сверены с байтами Git index перед коммитом. В полном отчёте 44 test inputs.

Для следующего участка уже выполнен настоящий `0x42010b70` с синтетическими
epoch и SDK time/enabled/log boundaries. При 2025-01-01 18:14:07 публикуется
2025; скачок к 2026 с теми же h/m/s оставляет 2025. Настоящий callback
`0x420109de` выставляет sync flag, но корректное время 2024 всё равно игнорируется.
На 21-м обновлении сбрасывается retry counter; если SNTP stopped, очищается
initialized flag. Наблюдение — `../qemu/parity/time-cache-observation.json`,
это не passing gate и не транспортная проверка. Прототип пока в игнорируемом
`.build/small-tv-parity/time_state_probe.py`; перенести в воспроизводимый тест
вместе с будущим исправлением успешной SNTP-validity.

## Предыдущий проверенный участок: JPEG

`assets.c`, `tjpgdcnf.h`, `jpeg_oracle.py`. Исполняются настоящие RV32-декодеры,
callback и LCD blitter; подменяются только SDK flash/malloc/mutex и транспорт LCD.
Оригинал `0x42011624..0x420116c6` ограничивает IDCT-компоненты байтом до YCbCr.
Прежний `JD_FASTDECODE=1` давал отличия в четырёх status JPEG: 3/33/3/3 пикселя;
все 98 анимационных кадров и пять фото совпадали. `JD_FASTDECODE=0` восстанавливает
цвета. Код декодера third_party не переписан.

При ошибке после входа в `jd_decomp` известная область изображения очищается;
подготовка, недостаток malloc и discard-validation не изменяют экран. Старый
C сохранял смешанные полосы; оригинальный callback `0x4200c33e` вообще игнорирует
SDK-ошибку чтения. Метки и отдельный JPEG-документ объясняют причины.

Новый gate включает 107 изображений, 35 ошибок/повторов/валидаций и семь размещений,
включая отрицательные координаты и очистку при обрезанном выводе. Смещения кадров
native нужно читать из санитизированного GIF-контейнера; исходные смещения следующих
кадров отличаются. Ранний отрицательный midpoint подготовки с неверным ожиданием
очистки исключён: strengthened harness наблюдает реальный `jd_decomp` entry.

Текущая сборка: app SHA-256
`997769839e8a016cb1c86845410297cea4097b47580b820fe0a77492267e2ded`;
source `a754f79707a9f140c381c171101d5837ac9a7a62f9e6c8813c9a65491868434d`.
App 1,022,496 байт; свободно 513,504 в app-разделе. DIRAM 80,650;
runtime-память платы не измерялась. Entry comments у 142 функций, метки у 31.
Полный `jpeg-idct-final` прошёл: все host/machine/QEMU gates, 107 JPEG / 35 ошибок /
семь размещений. В реальном field HTTP-потоке принято 106 кадров прокрутки.
Отчёты опубликованы и проверены по хешам; все 46 production inputs совпадают с
байтами в Git. Код/сборка — `04f6438e`; JPEG-отчёты находятся в
`../qemu/parity/jpeg-validation.json`, `jpeg-before.json`. ВМ закрыты, QEMU и
физические платы не изменялись. Полное соответствие всех путей не установлено.

## Предыдущий проверенный участок

Дата и реальные HTTP-обновления: `ui_renderer.c`, `calendar_oracle.py`,
`field_qemu.py`. Оригинальные инструкции `0x4200b850`, `0x4200b0b2`,
`0x4200bd8c` проверены по сохранённому адресному ассемблеру.

Подтверждены два сбоя прежнего C: сравнение только `tm_yday` не замечало смену
года или календаря с теми же h/m/s и номером дня; простая тема оставляла края
длинной даты при выводе короткой. Отрицательный машинный тест — 48 сбоев из 96,
до 411 лишних пикселей; `../qemu/parity/calendar-before.json` и две картинки
относятся к прежнему app `d89542e62f823c0862c6e4d15b618ecc5e416ea5d87a9d21b7ae7d00cc591bd5`.

Общая `calendar_changed` сравнивает year/month/day/yday. Дата простой темы
очищается в x=0…239, y=180…203, не затрагивая weekday/IP. Новые 96 RV32
сценариев и два теста реального clock_task прошли. Исходная исправленная модель
объявляет только clock/minute event, Sunday и очистку даты; оригинальная ветвь
и её отличия сохранены. SNTP-транспорт при скачке epoch этим тестом не проверяется.

`field_qemu.py` проверяет настоящий `/updateCity` и ответы локального сервиса.
Город/название/иконка сравниваются с независимыми исходными bitmap и соседними
полосами. Прокрутка достигает обеих сторон и пауз; задержанный ответ удерживает
кадр/фазу. После нового поколения погоды нужно дождаться подтверждения рендерера
и сохранить фазу. Смена темы сбрасывает её. Проверены короткая строка, ошибка
сервиса, восстановление и неизвестная иконка. QMP только кратко останавливает
наблюдение и возобновляет ВМ; RAM/регистры/код не подменяются.

В реальном заводском HTTP-потоке короткие подписи могут очищаться полной
переинициализацией экрана: остатки текста в прямых incremental-вызовах не приписывать
каждому `/updateCity`. При неуспешной погоде старая иконка с ненулевым указателем
всё же остаётся — это подтверждено. Неизвестная иконка в отдельном HTTP-переходе
может дать пустую область; не обобщать этот результат на все пути декодера.

Код даты/сборка — `a3b35c8c`, network/общие проверки — `0c961908`.
Полный `.build/small-tv-functional/calendar-http-fields-final/report.json`
прошёл: native 3 021, платформа 21 сценарий / 741,961, JS, целостность,
машинные renderer/control/backlight/classic/weather/calendar и QEMU обеих
прошивок. В сетевой прокрутке наблюдались 107 корректных кадров,
новое weather generation подтверждено рендерером до проверки сохранения фазы.

App SHA-256 `5e12da8c5b20740316f17da954b7ce8bc250e06b04e2f1e4f1095ccf484acc44`;
source SHA-256 `fdaf71adcda5d52aa288989fa7872115c53c328c3219818272e36e4dc301246d`. App 1,022,416 байт,
свободно 513,584 в app-разделе. DIRAM 80,650;
runtime-память платы не измерялась. Entry comments у 142 функций, метки у 30.
Актуальные отчёты: `tests/functional-validation.json`,
`../qemu/parity/calendar-validation.json`, `../qemu/field-http-validation.json`.
Перед повторным использованием после новых правок проверять app/source/test
хеши. Полное соответствие всех путей остаётся неустановленным.

## Следующие участки для исследования

Остаются явно не проверенные или не восстановленные пути:

1. Расширить реальные UDP-проверки midnight/Sunday/country/DST/всех тем/форматов.
   SNTP validity/retries/same-second cache/reset уже проходят обязательные gates,
   IANA helper исполняет libc, но весь transport/locale путь ими не покрыт.
   Unicode gate охватывает bundled 452 scalars и '?' для остальных; это не все
   письменности, shaping/bidi/NFC или полный fuzz всех HTTP input strings.
2. JPEG: новый gate охватывает все публичные ресурсы и ограниченные ошибки/обрезку.
   Произвольные пользовательские JPEG, разные subsampling и malformed Huffman/
   restart marker требуют дополнительных фикстур. Старый classic oracle сохраняет
   media-вызовы как границу; новый complete-scene gate исполняет renderers и
   JPEG/BMP вместе, дополняя отдельные decoder gates.
3. Проверить более длительные сетевые/загрузочные сценарии и расход памяти во
   время работы. Аппаратные и браузерные сценарии описаны в `tests/README.md`;
   их нельзя объявлять выполненными по результату других тестов.

4. Расширить полные кадры на другие настройки, цвета/яркости, длинные поля и
   переходы тем. Canonical classic/dial и 24 actual completed frames уже проходят
   строгий gate без масок, но не исчерпывают все состояния. Известные factory
   corrections и разная фаза кадра не должны скрывать ещё не восстановленный
   путь. Scene similarity percentage остаётся наблюдением, не критерием parity.

## Проверки и репозитории

`tests/run-all.ps1` запускает C, платформенные/JS/артефактные проверки, машинные
сравнения и QEMU. После успешного полного запуска `tests/publish-report.py`
публикует компактный отчёт, а `tools/verify_artifacts.py` обновляет размеры и
счётчики в `validation.json`. Проверять соответствие отчётов текущему архиву.
Количество проверок и сходство снимков не являются процентом покрытия или
доказательством полной идентичности. Синтетическая погода не проверяет живой сервис.

QEMU находится в `C:\Work\QEMU-ESP32`; изменения ESP32-C2, модульных SPI/I2C и
виртуальной сети объединены и отправлены в `main` до `1c7e4c0512` (kernel built from `5e136b6eab`). Сохранять
совместимость CYD и ESP32-C3 OLED. При изменении эмулятора выполнять их регрессии.
Закрывать созданные для проверки ненужные ВМ. Физические платы в текущих
проверках не прошиваются.

Отдельные незавершённые черновики, например `tools/assist_c_port.py`, не считать
готовыми инструментами. Чужие файлы `.karadio-*.patch`, `tmp/` и другие
посторонние изменения не относятся к этой задаче.
