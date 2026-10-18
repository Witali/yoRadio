# Перенос timezone, SNTP и состояния часов на CYD

Дата: 2026-10-18. Этап **CYD-C3-09**. Общий SNTP backend и отдельные
CYD settings/service реализованы и проверены на host; интеграция startup/Wi-Fi,
C3 adapter, SDK builds/lint и аппаратная квалификация ведутся отдельно.
Документ дополняет [общий план](ESP32_CYD_C3_TRANSFER_PLAN.md#L114).
Существующие audio/display core bindings, OLED, deep sleep и RTC не меняются.

## Проверенные входы и различия до time batch

| Область | Текущий исходник | Вывод для переноса |
| --- | --- | --- |
| C3 SNTP worker / callback | [time_service.c:30](../idf/esp32c3-oled-native/main/time_service.c#L30), [apply:64](../idf/esp32c3-oled-native/main/time_service.c#L64), [header](../idf/esp32c3-oled-native/main/time_service.h) | Полезны постоянные буферы имён и короткое уведомление из lwIP; управление выполняется worker с priority 1. |
| C3 сохранённые настройки | [runtime_settings.h:22](../idf/esp32c3-oled-native/main/runtime_settings.h#L22), [load:164](../idf/esp32c3-oled-native/main/runtime_settings.c#L164), [setters:284](../idf/esp32c3-oled-native/main/runtime_settings.c#L284) | NVS namespace `runtime`, ключи `tzh`, `tzm`, `sntp1`, `sntp2`, `timeint`. Строки ёмкостью 35 байт, интервал 15–1440 минут. Весь runtime_settings переносить не требуется. |
| C3 подключение и запуск | [GOT_IP:161](../idf/esp32c3-oled-native/main/network_service.c#L161), [startup:913](../idf/esp32c3-oled-native/main/app_main.c#L913) | Повторное подключение уведомляет worker; начальный GOT_IP предшествует apply. В CYD нужен явный контракт для первого подключения и disconnect. |
| C3 невалидные часы | [порог:51](../idf/esp32c3-oled-native/main/app_main.c#L51), [clock:546](../idf/esp32c3-oled-native/main/app_main.c#L546) | Порог `1704067200` — 2024-01-01 UTC; не показывать epoch 1970 как верное время. OLED/deep-sleep функции не переносить. |
| CYD Wi-Fi события | [event_handler:68](../idf/esp32-cyd2usb-native/main/network_service.c#L68), [TCP/IP init:121](../idf/esp32-cyd2usb-native/main/network_service.c#L121) | Сейчас нет time hook. Disconnect не очищает `native_state.network_mode/ipv4`; этот snapshot не является достоверным признаком наличия сети для SNTP. |
| CYD state | [native_state.h:24](../idf/esp32-cyd2usb-native/main/native_state.h#L24), [snapshot:33](../idf/esp32-cyd2usb-native/main/native_state.c#L33) | Полей времени нет. Snapshot берёт mutex и при timeout возвращает нулевые данные без результата; новому time snapshot нужен проверяемый результат. |
| CYD display | [display_task:53](../idf/esp32-cyd2usb-native/main/app_main.c#L53), [cyd_display.c](../idf/esp32-cyd2usb-native/main/cyd_display.c) | Сейчас task рисует цветные полосы состояния сети; cyd_display — SPI/DMA driver, готового TFT clock renderer нет. Перенос сервиса не означает готовый виджет часов. |
| CYD задачи | [app_main.c:115](../idf/esp32-cyd2usb-native/main/app_main.c#L115), [board_config.h](../idf/esp32-cyd2usb-native/main/board_config.h) | Сохранить существующие core bindings. Новый worker priority 1 можно создавать unpinned; 2048 байт донора — начальный бюджет, требующий target stack qualification. |

До time batch в native CYD не было `TZ`, timezone или настроенного приложением SNTP. Поэтому
не следует приписывать ему C3/Arduino defaults. Текущий CYD SDK профиль:
`CONFIG_LWIP_SNTP_MAX_SERVERS=1`, `CONFIG_LWIP_SNTP_UPDATE_DELAY=3600000`,
startup jitter включён, максимум 5000 ms. Без `TZ` libc использует UTC.
У C3 [sdkconfig.defaults:131](../idf/esp32c3-oled-native/sdkconfig.defaults#L131)
явно включает два сервера; C3 defaults — UTC, `pool.ntp.org`, `time.nist.gov`,
60 минут. Отдельный legacy Arduino
[Config::setDefaults](../yoRadio/src/core/config.cpp#L612) задаёт UTC+3 и
`1.ru.pool.ntp.org`; это не defaults текущей native CYD прошивки.

Для CYD сохраняются UTC и интервал 60 минут. В будущем time batch явно поднять
`CONFIG_LWIP_SNTP_MAX_SERVERS=2` и перенести оба сервера, как у C3:
`pool.ntp.org` / `time.nist.gov`. Это выбранные defaults **нового** сервиса,
а не обнаруженные исторические настройки CYD. Сначала квалифицировать сервис
и отказы при доступной ёмкости 1/2, затем включить ёмкость 2 в обоих CYD audio
профилях и проверить ресурсы. Полный этап 09 требует двух серверов; текущий
SDK default 1 не является основанием оставить feature отложенной. До изменения
конфигурации попытка установить index 1 при лимите 1 запрещена.
SDK upgrade, DHCP NTP, country/DST database и внешнее RTC сюда не входят.

## Подтверждённая lifetime проблема донора

На обоих закреплённых SDK public `esp_sntp_stop()` лишь вызывает
`tcpip_callback(do_stop, NULL)`: возврат функции не подтверждает остановку.
Public `esp_sntp_setservername()` выполняет TCP/IP API call, но сам lwIP
`sntp_setservername()` сохраняет указатель (`sntp_servers[idx].name = server`),
не копию строки. Исторический C3 apply (frozen source hash ниже, lines 80–84)
ставит stop в очередь и сразу перезаписывает эти строки. TCP/IP worker ещё
может читать старое имя в момент записи. Пожизненный static buffer защищает
от освобождения памяти, но не от этой конкурентной перезаписи.

Проверено по локальным pinned источникам в `<repository-root>/.idf/`:

- `v6.0.2/components/lwip/apps/sntp/sntp.c:187–189` и
  `v6.1-9a97f6c54ec6/components/lwip/apps/sntp/sntp.c:187–189`: async stop.
  SHA-256 обоих файлов:
  `d783936fdc879b2200bf03ffae45da4c928847791da95bcdac65d0ca6c72b5a0`.
- `v6.0.2/components/lwip/lwip/src/apps/sntp/sntp.c:921–925`:
  сохранение указателя имени. `sntp_stop():712` снимает таймеры и UDP PCB.
- `v6.0.2/components/esp_netif/include/esp_netif_sntp.h:99–112`:
  public checked init/start и deinit.
- `v6.0.2/components/esp_netif/lwip/esp_netif_sntp.c`: init выполняет
  `esp_netif_tcpip_exec(sntp_init_api, ...)`; deinit —
  `esp_netif_tcpip_exec(sntp_stop_api, ...)`; start синхронно выполняет
  stop/init внутри такого же вызова. SHA-256:
  `240f0f4e2254be3f66e7dce831e80d8267a9c9da93d14dd4070de74e36a77746`.
- `v6.0.2/components/esp_netif/include/esp_netif.h:1086–1096`:
  public API выполнения callback в TCP/IP context и возврата его результата.
  Его backend `esp_netif_lwip.c:239–252,789–796` использует
  `tcpip_send_msg_wait_sem`, возвращает `msg->ret` либо выполняет callback
  непосредственно, если уже находится в TCP/IP context. Это подтверждает
  отличие managed stop от постановки raw stop в очередь.

Реализованный общий путь — [native_time](../idf/components/native_time/CMakeLists.txt),
[public API](../idf/components/native_time/include/native_time_sntp.h),
[lifecycle controller](../idf/components/native_time/native_time_sntp.c) и
[TCP/IP callbacks](../idf/components/native_time/native_time_sntp_context.c).
Controller создаёт checked mutex без обращения к TCP/IP; atomic ever-GOT_IP
latch разрешает сетевые операции только после подтверждённой готовности стека.
Offline/startup failure не вызывает IPC в неинициализированный TCP/IP. Текущая
доступность сети хранится отдельно от этого пожизненного readiness latch.

Managed `esp_netif_sntp_init` вызывается **один раз** с нулём начальных серверов,
`start=false`, `wait_for_sync=false`, `renew_servers_after_new_IP=false`.
Оба pinned SDK допускают `num_of_servers=0`: init проверяет только верхнюю
границу, устанавливает callback/mode, не создаёт UDP PCB и не выдаёт указатели
банков. Это разделяет failure ownership managed allocation и публикации имён.
После успешного init managed storage/callback/context остаются до reboot;
runtime deinit/reinit отсутствует. Нет sync semaphore, strdup серверов или
повторной регистрации IP handlers со стороны managed клиента.

Каждый apply/restart выполняет raw **public** lwIP операции исключительно
внутри checked `esp_netif_tcpip_exec` callback. Controller TU включает
public managed/ESP headers; отдельный context TU — только raw lwIP header.
Это исключает конфликт legacy inline wrappers без SDK-private component macros.
Отложенные `esp_sntp_init/stop/restart` не используются. Mutex wait ограничен
100 ms; сам public TCP/IP executor синхронный и не предоставляет bounded deadline.

Кандидат проверяется до сетевых изменений. Два пожизненных банка выбираются
по фактическим slot pointers **всех** `SNTP_MAX_SERVERS`, включая неактивный
slot после 2→1 и третий apply. Проверка отсутствия ссылок, заполнение выбранного
банка и смена привязок происходят в одном TCP/IP callback; DNS callback между
этими шагами не исполняется. Если оба банка ещё используются, apply возвращает
ошибку без перезаписи. Неограниченного retention поколений нет.

После stop callback проверяет disabled state, очищает **все** slots через
`sntp_setserver(i, NULL)`, устанавливает interval/mode, привязывает новые имена
и запускает клиента. `sntp_setservername(i,NULL)` недостаточен: он оставляет
старый resolved IP, который `sntp_try_next_server` считает доступным сервером.
`setserver(NULL)` в обоих pins обнуляет и имя, и адрес. Равная работающая
конфигурация — no-op, поэтому смена только timezone не сбрасывает backoff.
После binding банк считается заимствованным даже при неуспешном start.

SDK `sntp_init` возвращает void. Проверка `sntp_enabled()` обнаруживает отказ
UDP allocation только в no-assert профиле. Текущие C3/CYD конфигурации включают
`CONFIG_LWIP_ESP_LWIP_ASSERT=1` и compiler assertions: `sntp_init():688`
при отсутствии PCB вызывает assertion/abort **до** этой проверки. Actual SDK
child test подтверждает abort; recoverable target OOM здесь не обещается.
Managed `.start=false` устраняет эту allocation только на стадии managed init.

Для данных pinned SDK отдельно установлено: `dns_enqueue():1632–1633` копирует
hostname во внутреннюю DNS entry; `sntp_dns_found():602` игнорирует hostname/arg
и использует глобальные `sntp_current_server`/PCB. Поэтому поздний resolver
callback не удерживает старый service name buffer после завершения enqueue,
но **может** подставить старый результат DNS в новый SNTP singleton, послать
запрос через новый PCB или запланировать retry. Pointer-race и stale-result
поведение — разные задачи. Managed deinit/reinit не предоставляет generation
cancellation, и этот проект её не обещает. Sync snapshot означает наблюдение
SNTP sync, а не доказательство, что ответ получен именно от сервера последней
config revision. Нужна явная проверка второго/третьего apply с очень поздним
DNS callback; если понадобится строгая отмена старых результатов, это отдельная
SDK-supported возможность/изменение, которое сначала надо доказать, а не
заменять бесконечным retention. Пока это documented limitation этапа.

Для C3 это отдельный узкий commit: сохранить namespace/ключи/defaults,
UI hour/minute contract, приоритет и stack worker; сериализовать apply и
reconnect control одним владельцем/lock; заменить весь набор управляющих
вызовов согласованным managed backend. Забрать проверенную копию всех time
settings **до** stop; timeout строкового getter не должен заменять рабочий
сервер пустой строкой. Не менять OLED, deep sleep или RTC fast path. Текущий
C3 time source до исправления имеет SHA-256
`bba95c0224185c4e93b3ca49a48f3827788bd27ccd53e832ae6ebc96f45bc8cb`.

## Минимальный сервис и API

Реализованы [time_settings.c/.h](../idf/esp32-cyd2usb-native/main/time_settings.h),
[time_service.c/.h](../idf/esp32-cyd2usb-native/main/time_service.h) и отдельные
host suites. Public interface:

```c
typedef struct {
    int16_t utc_offset_minutes;
    uint16_t sync_interval_minutes;
    uint8_t server_count;
    char servers[2][35];
} time_settings_t;

esp_err_t time_service_start(void);
esp_err_t time_service_get_settings(time_settings_t *out);
esp_err_t time_service_save_settings(const time_settings_t *desired);
void time_service_notify_network(bool has_station_ip);
bool time_service_snapshot(time_snapshot_t *out);
```

Timezone хранить одним signed количеством минут: диапазон −720…+840,
шаг 15 минут, включая −00:30 и +05:45. Это предотвращает смешивание двух
независимых hour/minute значений и ошибку знака у отрицательного нулевого часа.
Донор проверяет hour/minute отдельно: там возможны +14:45/−12:45, и −00:30
непредставим. Новый CYD формат не требует менять существующие C3 настройки.

NVS: отдельный namespace `native_time`, один 82-byte versioned bounded record `cfg`.
Кодировать поля явно, без raw C struct padding; при чтении проверять точную
длину, version, reserved, числовые диапазоны, количество серверов и завершение
строк. Хосты 1–34 байта, без whitespace/control/NUL внутри, URL/порта и
разделителей; допустимые DNS labels/IPv4 валидировать полностью. Интервал
15–1440 минут. Invalid/missing record использует defaults без erase NVS;
ошибки чтения отличать от отсутствия ключа. Wrong NVS type использует defaults;
прочие IO errors возвращаются без публикации и перезаписи NVS.

`save_settings` проверяет весь кандидат и сериализует запись. Ошибка NVS
не публикует новый active snapshot. Успех означает **сохранён desired config**;
worker применяет его отдельно. Snapshot содержит desired/applied revision и
`last_apply_error`, поэтому ошибка managed init/start после commit видна
потребителю. Не обещать атомарность flash commit и изменения сетевого сервиса.

Для нового CYD сервиса часы системы остаются UTC. Местное время snapshot
вычисляется через checked `gmtime_r(epoch + offset_minutes * 60)`: достаточно
для fixed-offset contract и не требует глобального `setenv/tzset`, гонок
timezone environment или DST. До сложения проверять диапазон. Если позднее
понадобится глобальный POSIX TZ, его изменение и все localtime consumers
потребуют отдельного согласованного контракта; знак POSIX offset обратный.

## Сеть, invalid clock и блокировки

1. После NVS init создать checked mutex/worker **до Wi-Fi событий**. Worker
   не вызывает TCP/IP/SNTP до первого station GOT_IP, когда TCP/IP уже готов.
   Уведомление хранит текущее network state даже до полной готовности worker.
   Альтернатива для позднего старта требует явной первоначальной проверки
   station link/IP; старый native_state snapshot для этого недостаточен.
2. GOT_IP и disconnect/lost-IP только записывают актуальное состояние и
   уведомляют worker; никаких DNS, NVS, SNTP control, libc formatting или
   display operations внутри Wi-Fi/lwIP callback. AP-only не запускает SNTP.
3. Worker использует общий init-once backend с `wait_for_sync=false`,
   immediate sync, checked start по сети и permanent server storage.
   Не блокирует startup через sync_wait и не начинает второй singleton SNTP.
4. Повторный GOT_IP без изменения состояния не перезапускает клиент.
   На disconnect отметить отсутствие сети, сохранить backend/backoff, ход
   wall clock и историю синхронизации; не уничтожать клиент на каждом flap.
   Новые принудительные restart во время offline не ставить. SDK может
   завершать DNS/retry; этот контракт не обещает их мгновенную отмену.
   Flap/reconfigure restart ограничить monotonic
   cooldown, чтобы не обнулять backoff непрерывно. Обычные retry/DNS/UDP
   timeout оставить lwIP: receive timeout 15 s, single-server retry
   экспоненциально ограничен 150 s; при двух серверах SDK переключает сервер
   и сбрасывает per-server retry interval. Hourly polling — после успеха.
   Источник: pinned `lwip/apps/sntp_opts.h:163–201`, `sntp.c:371–395`.
5. SNTP sync callback только уведомляет worker. Не использовать
   `sntp_get_sync_status()` как постоянный флаг: чтение COMPLETED сбрасывает
   его. Worker хранит собственные `synchronized_this_boot`, last observed
   sync epoch и monotonic timestamp. Все deadlines/age считаются monotonic,
   независимо от скачков wall clock вперёд или назад.
6. Snapshot: `available`, `network_ready`, `clock_valid`,
   `synchronized_this_boot`, UTC epoch, local `struct tm`, last sync/age,
   revisions/error. `clock_valid` требует epoch не раньше 2024-01-01 и
   успешной конвертации; plausible clock и SNTP этого boot — разные признаки.
   После disconnect валидное время не обнуляется. Cold boot без времени
   отдаёт `clock_valid=false`, чтобы UI показывал placeholder, а не 1970.
7. Settings snapshot копируется в короткой portMUX critical section, service
   snapshot — под checked mutex. Копирование без NVS, SNTP,
   логирования или libc formatting под snapshot lock. Записи настроек имеют
   отдельную сериализацию; их успешная публикация после commit не требует
   новой allocation. Не вкладывать native_state/audio/display locks в time
   locks. Callback вообще не берёт эти locks. Timeout snapshot возвращает
   false; потребитель не интерпретирует нули как достоверные данные.

TFT integration позднее читает собственный time snapshot отдельно от audio
state. Добавление полей в общий native_state и новый renderer не обязательны
для изолированного service commit. Текущие display/network core-0 bindings и
аудиопотоки не изменяются. Никаких OLED fonts, display-off clock, RTC-specific
retention, wakeup, погоды или deep-sleep hooks.

## Проверки перед переносом

- Actual validation/codec tests: все границы offset/interval/server count,
  ±00:30, +05:45, endpoints −12/+14, malformed NVS record/unterminated names,
  слишком длинные/пустые/URL/whitespace hosts, NVS open/set/commit failures.
  Проверять actual save/load и неизменность active config при отказе, а не
  только копию валидатора в тесте.
- Actual service tests с fake monotonic/wall clock и RTOS/TCPIP scheduler:
  alloc/task failure, первые GOT_IP до/после startup, AP-only, duplicate IP,
  disconnect, rapid flaps, delayed sync, DNS/NTP недоступны, success после
  retry; отдельно clock jumps, time conversion overflow и snapshot timeout.
- Отдельный C3 regression: удержать отложенный `do_stop`, показать, что старый
  apply меняет уже выданный lwIP name buffer до stop ACK. Новый путь должен
  сохранить старые bytes до подтверждения остановки; delayed DNS/callback
  и одновременный reconnect/reconfigure не получают освобождённые либо
  перезаписываемые строки. Historical implementation — negative control.
- Второй/третий apply, смена двух серверов на один, partial rebind, failed init
  и очень поздний DNS callback: проверять все slot pointers перед reuse банка.
  Отдельно фиксировать stale DNS result через новый PCB; не засчитывать
  отсутствие pointer-race как доказательство generation cancellation.
- Проверить pinned public wrapper/managed backend semantics настоящими
  выбранными SDK функциями с очередью TCP/IP seam; не подменять async stop
  немедленным действием. Проверить ошибки init/start, постоянство адресов
  имён и отсутствие второго SNTP singleton/дублированных workers.
- ASan/UBSan и meaningful negative controls: выключенная проверка NVS,
  ранняя перезапись SNTP имени, неправильный знак offset, restart на каждом
  duplicate GOT_IP, clock reset при disconnect должны обнаруживаться.
- Actual pinned SDK build и focused clang-tidy новых units на CYD и C3 fix.
  На устройстве позже проверить оба CYD audio профиля, недоступный NTP,
  reconnect, stack high-water/heap и отображение invalid/valid clock.
  Host mocks не доказывают реальную SNTP сеть, время ответа или target RAM.

## Выполненная host квалификация

- Shared backend commit `d1c33cd4`, [runner](../tests/run-native-time.py):
  `.build/native-time-qualified-01/report.json`, **76 positive groups и 12
  semantic mutants** (оба SDK × capacity 1/2), ASan/UBSan clean. Компилируются
  actual pinned full SNTP core, managed lifecycle, ESP sync/status/interval
  functions и точный `dns_enqueue` с его entry/request structures. RTOS,
  TCP/IP executor scheduling, UDP/pbuf/timers, DNS network completion и wall
  clock — явные seams. Проверены borrowed lifetime, третий apply, all-slot
  references, очистка IP+name при 2→1, equal-config backoff, managed alloc/IPC
  failures, реальный SNTP packet→clock/callback/hourly timer. Assertion-enabled
  PCB OOM подтверждён отдельным child abort; no-assert OOM/error + поздний DNS
  фиксируются отдельно. Cancelled DNS и physical network/RAM не заявлены.
- CYD commit `cd3bb69b`, [runner](../tests/run-cyd-time.py):
  `.build/cyd-time-qualified-02/report.json`, **24 actual cases и 7 semantic
  mutants**, ASan/UBSan clean. Actual settings codec/save/load и worker/state
  проверены с NVS/RTOS/SNTP seams: границы, canonical record/hidden tail/type,
  open/get/set/commit errors, concurrent saves + snapshot во время commit,
  startup allocation/task/backend failures, early/duplicate IP, coalesced
  flaps/cooldown, offline desired config, save-during-apply, persisted/apply
  failure, sync notice retry, monotonic age, timezone signs/overflow и timeout.
  Эти seams не доказывают физических flash transactions или target stack.

Дополнительно выполнены:

- C3 commits `642ee17f`/`7fd417a6`: coherent time snapshot и сериализация пяти
  setters с commit-before-publication; actual time worker и managed backend.
  Host campaigns: 69 settings checks +3 mutants; 14 service groups +6 mutants;
  historical queued-stop reproducer обнаруживает перезапись borrowed имени
  старым production кодом, текущий backend сохраняет bytes до SDK ACK.
- [CYD startup/events](../tests/run-cyd-time-events.py): actual `app_main`,
  `network_service_start`, `station_lost_ip` и `event_handler` выполняются с
  SDK seams. Финальные 32 groups +9 semantic controls включают сохранение
  прежних core-0 display/network bindings, AP-only startup, delayed GOT_IP,
  disconnect/LOST_IP, обнуление старого адреса, RAM storage и отсутствие
  подключения retained profile при пустом CSV на CYD/C3. CYD defaults теперь
  задаёт `CONFIG_LWIP_SNTP_MAX_SERVERS=2`; старые build sdkconfig требуют
  явного применения этой настройки при новой квалификации.
- [CYD HTTP handlers](../idf/esp32-cyd2usb-native/main/web_time.c): GET
  показывает desired/applied revisions и valid/invalid clock отдельно от
  сохранённых настроек. POST принимает ровно четыре query fields, валидирует
  всё до NVS commit и сообщает pending apply. Нежелательный request body
  закрывается без HTTPD purge. 69 checks/7 groups +5 semantic controls проходят
  с ASan/UBSan; три actual response body разобраны JSON parser.

Далее: завершение compact WebUI integration и общего evidence archive,
actual SDK build + полный lint после заморозки исходников, физическая
проверка ресурсов/сети. TFT clock widget, OLED/deep-sleep/RTC features
в этот сервис не входят.
