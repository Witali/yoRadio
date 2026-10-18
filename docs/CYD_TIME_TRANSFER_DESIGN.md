# Перенос timezone, SNTP и состояния часов на CYD

Дата: 2026-10-18. Этап **CYD-C3-09**. Статус: проект, реализации и
аппаратной проверки ещё нет. Документ дополняет
[общий план](ESP32_CYD_C3_TRANSFER_PLAN.md#L114). OTA source/SDK batch завершается
независимо; этот документ не меняет time sources, CMake, audio, сеть или WebUI.

## Проверенные входы и различия

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

В native CYD нет `TZ`, timezone или настроенного приложением SNTP. Поэтому
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
не копию строки. C3 [apply:80–84](../idf/esp32c3-oled-native/main/time_service.c#L80)
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

Безопасный путь для CYD и отдельного C3 исправления: один владелец SNTP
управляет жизненным циклом через **managed public esp_netif SNTP API**.
Не смешивать этот путь с отложенными raw `esp_sntp_restart/init/stop`.
Сначала подготовить и проверить новую конфигурацию, затем подтвердить stop
старого экземпляра через managed deinit и только после завершения TCP/IP
операции менять привязки. Использовать два service-owned static банка имён:
новый кандидат заполняется в неактивном банке; банк, на который сейчас
ссылается lwIP, не перезаписывается. После checked TCP/IP переключения pointers
старый банк становится неактивным. DNS enqueue копирует hostname во внутреннее
хранилище (`lwip/src/core/dns.c`, `dns_enqueue`); память текущего указателя
должна быть неизменной на протяжении всего синхронного DNS enqueue. Static
банки не освобождаются. Init/start ошибки учитываются; успешное сохранение
настроек не выдаётся за успешное применение SNTP.
Public deinit возвращает void; перед переключением привязок controller
дополнительно проверяет disabled state внутри checked `esp_netif_tcpip_exec`. При отказе
барьера/проверки старые buffers остаются неизменными и публикуется ошибка.
Stop снимает SNTP timers/PCB, но не доказывает отмену уже отправленного DNS:
`sntp_dns_found():602` может прийти позднее. Поэтому нельзя считать stop
универсальным cancellation ACK либо освобождать DNS-related state. Минимальный
disconnect contract ниже сохраняет backend и его retry state; отдельный
delayed-DNS тест обязателен при reconfigure/deinit и отказе последующего init.

Для C3 это отдельный узкий commit: сохранить namespace/ключи/defaults,
UI hour/minute contract, приоритет и stack worker; сериализовать apply и
reconnect control одним владельцем/lock; заменить весь набор управляющих
вызовов согласованным managed backend. Забрать проверенную копию всех time
settings **до** stop; timeout строкового getter не должен заменять рабочий
сервер пустой строкой. Не менять OLED, deep sleep или RTC fast path. Текущий
C3 time source до исправления имеет SHA-256
`bba95c0224185c4e93b3ca49a48f3827788bd27ccd53e832ae6ebc96f45bc8cb`.

## Минимальный сервис и API

Предлагаемые новые CYD файлы: `time_service.c/.h`, `time_settings.c/.h` и
собственные host tests/runners. Это предложение интерфейса, ещё не frozen API:

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

NVS: отдельный namespace `native_time`, один versioned bounded record `cfg`.
Кодировать поля явно, без raw C struct padding; при чтении проверять точную
длину, version, reserved, числовые диапазоны, количество серверов и завершение
строк. Хосты 1–34 байта, без whitespace/control/NUL внутри, URL/порта и
разделителей; допустимые DNS labels/IPv4 валидировать полностью. Интервал
15–1440 минут. Invalid/missing record использует defaults без erase NVS;
ошибки чтения отличать от отсутствия ключа.

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
3. Worker использует `esp_netif_sntp_init` с `wait_for_sync=false`,
   `smooth_sync=false`, managed start по сети и permanent server storage.
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
7. Копирование config/state — короткая защищённая операция, без NVS, SNTP,
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

Последовательность реализации после OTA export: изолированные settings/core
и tests → CYD worker/backend и tests → узкий C3 lifetime fix/regression →
parent-owned Wi-Fi/startup wiring → отдельные UI/snapshot integration и
target checks. До назначения ownership новых файлов этот документ остаётся
планом; существующие time sources здесь не менялись.
