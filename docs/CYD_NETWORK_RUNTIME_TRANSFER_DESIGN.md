# Runtime Wi-Fi: перенос профилей, reconnect, RSSI и power policy на CYD

Обновлено: 2026-10-19. Остаток этапа **CYD-C3-09** из
[общего плана](ESP32_CYD_C3_TRANSFER_PLAN.md#L72). Блоки N0–N4 реализованы
и программно проверены. Для N5 готово checked хранилище; подключение
hostname/AP timeout к runtime/WebUI остаётся открытым. Приватный редактор desired credentials и
[time service](CYD_TIME_TRANSFER_DESIGN.md) выполняются отдельно.

## Реализованный runtime и входы

Постоянный [network_runtime.c](../idf/esp32-cyd2usb-native/main/network_runtime.c)
сериализует driver operations, попытки профилей и RSSI. Новая задача имеет
priority 2, core 0 и stack 4096; существующие audio/display/bootstrap bindings
не изменены. [Facade](../idf/esp32-cyd2usb-native/main/network_service.c)
выполняет checked startup/rollback; [profiles](../idf/esp32-cyd2usb-native/main/network_profiles.c)
атомарно загружает первые пять valid rows; [netif wrapper](../idf/esp32-cyd2usb-native/main/network_netif.c)
проверяет attach/handler setup без assert factories SDK.

Активная таблица неизменна до reboot. Первичное и ручное подключение идут
с первого профиля; после позднего обрыва цикл начинается с последнего
успешного и проходит таблицу с wrap. Максимум три попытки на профиль,
20 s на попытку и 300 s на весь цикл; общий deadline может сократить число
попыток. Через 20 s startup доступен AP, owner продолжает работу. APSTA
сохраняется при ручном retry. Ещё один ручной цикл отклоняется как busy
до завершения принятого цикла, включая pending mailbox.

[Snapshot API](../idf/esp32-cyd2usb-native/main/network_status.h) не содержит
SSID/password, отдельно описывает STA online, AP enabled, RSSI validity/age,
phase и budgets. Pending SDK events маскируют устаревший IP/RSSI.
[HTTP](../idf/esp32-cyd2usb-native/main/web_service.c) публикует
`GET /api/native/network`; reconnect подтверждает только admission.
[WS](../idf/esp32-cyd2usb-native/main/websocket_service.c) и
[страница](../idf/esp32-cyd2usb-native/main/web_pages.cpp) используют validity;
поздний REST ответ не перезаписывает более новое WS уведомление.

[Frozen qualification](../tests/results/cyd-network-runtime-20261019/README.md)
содержит 44 полных owner-loop сценария и четыре semantic controls,
loader/netif/rollback/API/WS/UI проверки с ASan/UBSan. TSAN недоступен:
его независимый контроль падает при старте runtime. Xtensa GCC component
compile проходит; полные production exports, RF, heap/stack и физическая
SMP/audio приёмка остаются открыты. Таблицы ниже сохраняют исходные точки
сравнения до замены runtime; source-level дефекты относятся к historical baseline.

### N4: generation-aware power реализован

[Общий компонент](../idf/components/native_network_power/native_network_power.c)
принимает `accept(generation, active)` только из сериализованного audio control.
`receive(generation)` и `finish(generation)` меняют intent лишь при равенстве
поколения. C3 [audio integration](../idf/esp32c3-oled-native/main/audio_service.c)
исправлена вместе с [CYD](../idf/esp32-cyd2usb-native/main/audio_service.c):
Play принимает active intent до публикации queue, Stop/maintenance задают новое
idle поколение, resume устанавливает active до снятия maintenance. Backoff
завершает receive intent, следующая попытка того же поколения включает его
снова. EOF заканчивает network receive, buffered PCM может ещё проигрываться.

`esp_wifi_set_ps` вызывается только сетевым owner: на CYD — существующим
runtime, на C3 — прежней RSSI task. Её stack/priority сохранены; policy tick
100 ms, RSSI cadence 2 s. Короткая critical section защищает intent, SDK call
выполняется вне неё. Новая команда во время SDK call сохраняется, следующий
poll согласует latest desired mode. На одну revision — максимум три попытки
с 250 ms между неудачами. Ошибка не отклоняет Play. Поле `power` ответа
`GET /api/native/network` показывает desired и последнюю успешно подтверждённую SDK policy, validity,
revisions, attempts/error; это не измерение физического энергопотребления.

[N4 qualification](../tests/results/network-power-transfer-20261019/README.md)
воспроизводит обе гонки на старом C3 коде и проверяет shared policy, actual
C3/CYD audio owners, retry/maintenance, CYD network owner и HTTP/WS. Полный
clang-tidy: CYD 50/C3 65 units, 0 новых warnings, 0 errors; GCC component
compiles обеих платформ проходят. Production exports и hardware gates
учитываются отдельно.

### N5: только persisted precursor

[network_settings.c](../idf/esp32-cyd2usb-native/main/network_settings.c) хранит
маленькую versioned NVS record, публикует coherent desired snapshot/revision
после commit. Defaults: `yoradio`, timeout 0. Новый CYD hostname contract —
одна ASCII label 1–23 bytes с внутренними hyphens; C3 legacy validation шире.
[12 случаев и 7 controls](../tests/results/network-power-transfer-20261019/settings-precursor/report.json)
проверяют полный source с NVS/RTOS seams. Этот модуль пока не подключён к
CMake/runtime/routes: сохранение/AP timer/hostname application через UI ещё
не реализованы и не считаются завершёнными.

## Входы и переносимые возможности

| Возможность | Донор C3 | Текущий CYD / решение |
| --- | --- | --- |
| Пять упорядоченных профилей | [read_credentials:143](../idf/esp32c3-oled-native/main/network_service.c#L143), [select_credential:180](../idf/esp32c3-oled-native/main/network_service.c#L180) | [CYD reader:105](../idf/esp32-cyd2usb-native/main/network_service.c#L105) выбирает первый valid row. Перенести до пяти активных профилей, порядок CSV и два повторных подключения на профиль. |
| Переход к следующему профилю | [DISCONNECTED:198](../idf/esp32c3-oled-native/main/network_service.c#L198) | [CYD:148](../idf/esp32-cyd2usb-native/main/network_service.c#L148) повторяет единственную config восемь раз. Нужен постоянный runtime owner, обслуживающий и позднюю потерю сети. |
| AP и ручной retry | [AP:250](../idf/esp32c3-oled-native/main/network_service.c#L250), [retry:373](../idf/esp32c3-oled-native/main/network_service.c#L373) | [AP:171](../idf/esp32-cyd2usb-native/main/network_service.c#L171), [retry:245](../idf/esp32-cyd2usb-native/main/network_service.c#L245), [HTTP:158](../idf/esp32-cyd2usb-native/main/web_service.c#L158). Сохранить существующий endpoint, заменить прямое изменение driver state на admission запроса. |
| RSSI каждые 2 s | [rssi_task:122](../idf/esp32c3-oled-native/main/network_service.c#L122), [state setter:25](../idf/esp32c3-oled-native/main/native_state.c#L25) | Поле [wifi_rssi](../idf/esp32-cyd2usb-native/main/native_state.h#L32) и [WS status](../idf/esp32-cyd2usb-native/main/websocket_service.c#L318) уже есть, producer отсутствует. Добавить valid/age и очистку при потере STA. |
| Modem sleep / активное аудио | [set_streaming:360](../idf/esp32c3-oled-native/main/network_service.c#L360), [Play:2308](../idf/esp32c3-oled-native/main/audio_service.c#L2308), [stream finish:1186](../idf/esp32c3-oled-native/main/audio_service.c#L1186) | Переносим `NONE` при принятом активном аудио и `MIN_MODEM` при idle; bool last-writer интерфейс сначала исправить на generation-aware intent. SDK failure остаётся best effort, Play не отклоняется. |
| Hostname | [startup:309](../idf/esp32c3-oled-native/main/network_service.c#L309), [runtime defaults](../idf/esp32c3-oled-native/main/runtime_settings.h#L17) | Отдельная bounded network setting с default `yoradio`, применяемая до start/reconnect. Это DHCP hostname; сам вызов не создаёт mDNS responder. |
| Optional AP timeout reboot | [timer:244](../idf/esp32c3-oled-native/main/network_service.c#L244), [setting:291](../idf/esp32c3-oled-native/main/runtime_settings.c#L291) | Переносимый option 0–30 min, default **0 / disabled**. Нужны отмена при выходе из fallback и согласование с существующим reboot/OTA lease, а не прямой `esp_restart()` из timer callback. |
| Desired credentials | [shared store API](../idf/components/native_wifi_store/include/native_wifi_store.h), [privacy design](CYD_WIFI_PRIVACY_TRANSFER_DESIGN.md) | Уже до пяти редактируемых профилей. Commit меняет desired CSV/revision; active runtime cache остаётся неизменным до reboot. Reconnect использует active cache, а не перечитывает newly saved CSV. |

Действующие byte limits сохраняются: SSID 1–31, password 0–63, максимум пять
профилей; SDK массивы 32/64 не повод незаметно расширять wire/storage contract.
Malformed строки legacy boot loader пропускает, весь IO failure не должен
превращаться в частично прочитанный набор. Пустой committed CSV означает
отсутствие профилей и не восстанавливает старый backup. Имена/пароли не попадают
в status, диагностические snapshots или новые логи.

## Проверенная аппаратная и SDK граница

Сверены первичные [ESP32 datasheet](https://documentation.espressif.com/esp32_datasheet_en.html)
и [ESP32-C3 datasheet](https://documentation.espressif.com/esp32-c3_datasheet_en.html).
Обе платформы поддерживают 2.4 GHz 802.11 b/g/n; CPU, память и периферия различны.
Выбранный C3 profile — одно RISC-V ядро, 160 MHz; CYD — два Xtensa LX6, 240 MHz.
400/520 KiB SRAM из datasheet не являются свободным heap прошивки.

| Ресурс | Проверенный профиль / правило |
| --- | --- |
| Pins SDK | CYD `v6.0.2`, commit `7101770dc6db2667b3c477cc31365dd1acd6db4e`; C3 `v6.1-9a97f6c54ec6`, commit `9a97f6c54ec638111ce55cd36581b3c192f15207`. Обновление SDK не требуется. |
| Existing application tasks | [CYD audio task table](../idf/esp32-cyd2usb-native/main/audio_service.c#L1194): stream priority 3/core 0, decode 5/core 1, output 6/core 1. [Display/bootstrap](../idf/esp32-cyd2usb-native/main/app_main.c#L120): display 1/core 0, network bootstrap 3/core 0. Все привязки сохранить; bootstrap после запуска сервисов завершается. |
| SDK tasks | В CYD config Wi-Fi core 0; default `sys_evt` создаётся на core 0 (`components/esp_event/default_event_loop.c:98`), TCPIP имеет no affinity. Не менять affinity этих задач. Event handler не должен ждать owner/settings/audio locks. |
| Wi-Fi buffers | [C3 overrides](../idf/esp32c3-oled-native/sdkconfig.defaults#L122): static RX 6, dynamic RX 16, dynamic TX 16. Текущий CYD generated config: 10/32/32. Не копировать уменьшение вместе с runtime: оно требует отдельного RF/audio/heap измерения. |
| Stack/память | [CYD stack budgets](../idf/esp32-cyd2usb-native/main/board_config.h#L24) сохраняются. Новый owner — отдельная проверяемая затрата, не переиспользование уже завершённого bootstrap stack. Для профилей достаточно 480 байт строк плюс metadata; текущий C3 хранит пять полных `wifi_config_t`. Реальные `sizeof`, static map и peak stack измерять обоими SDK. |
| RF/APSTA | Один физический канал: при STA подключении SoftAP следует каналу станции. Сохранение APSTA не гарантирует непрерывный TCP клиент портала при смене канала. Не переносить Bluetooth, OLED, C3 USB, RTC или deep sleep hooks. |

Публичные контракты проверены в обоих локальных SDK; ссылки ниже фиксируют
исходники CYD pin, эквивалентные объявления сверены с C3 pin:

- [esp_wifi.h:452](https://github.com/espressif/esp-idf/blob/7101770dc6db2667b3c477cc31365dd1acd6db4e/components/esp_wifi/include/esp_wifi.h#L452):
  `esp_wifi_connect()` инициирует одну попытку; повторениями управляет приложение.
  Дополнительный `failure_retry_cnt` не включать поверх application budget.
- [esp_wifi.h:1008](https://github.com/espressif/esp-idf/blob/7101770dc6db2667b3c477cc31365dd1acd6db4e/components/esp_wifi/include/esp_wifi.h#L1008):
  интерфейс должен быть enabled; `set_config` во время connecting может вернуть
  `ESP_ERR_WIFI_STATE`. Там же описано ограничение одного APSTA канала.
- [esp_wifi.h:1088](https://github.com/espressif/esp-idf/blob/7101770dc6db2667b3c477cc31365dd1acd6db4e/components/esp_wifi/include/esp_wifi.h#L1088):
  storage по умолчанию FLASH. RAM selection не обещает очистку config,
  загруженной при init. Checked RAM storage и `s_have_credentials` guard перед
  STA_START connect уже добавлены отдельным startup prerequisite на обеих платах.
- [station scenario:89](https://github.com/espressif/esp-idf/blob/7101770dc6db2667b3c477cc31365dd1acd6db4e/docs/en/api-guides/wifi-driver/station-scenarios.rst#L89),
  [default STA_START handler:76](https://github.com/espressif/esp-idf/blob/7101770dc6db2667b3c477cc31365dd1acd6db4e/components/esp_wifi/src/wifi_default.c#L76):
  start/netif setup и application connect — отдельные действия. Наблюдаемый риск
  пустого файла создавал наш безусловный connect; скрытый autoconnect закрытого
  бинарного драйвера этим аудитом не установлен. NVS erase не нужен.
- [esp_netif.h:390](https://github.com/espressif/esp-idf/blob/7101770dc6db2667b3c477cc31365dd1acd6db4e/components/esp_netif/include/esp_netif.h#L390):
  `get_ip_info` при down возвращает cached IP. Для reconciliation нужны
  `is_netif_up`, текущее association и phase, а не один ненулевой IP.
- [IP-lost timer:1541](https://github.com/espressif/esp-idf/blob/7101770dc6db2667b3c477cc31365dd1acd6db4e/components/esp_netif/lwip/esp_netif_lwip.c#L1541):
  timer проверяет текущий zero IP перед post; delay в обоих текущих configs —
  120 s. Немедленную invalidation делать на DISCONNECTED, не ждать LOST_IP.
- [disconnect payload:1180](https://github.com/espressif/esp-idf/blob/7101770dc6db2667b3c477cc31365dd1acd6db4e/components/esp_wifi/include/esp_wifi_types_generic.h#L1180)
  содержит SSID/BSSID/reason/RSSI, но не application generation. Наш epoch не
  отменяет уже поставленные/поздние SDK events.
- [RSSI / power APIs:653](https://github.com/espressif/esp-idf/blob/7101770dc6db2667b3c477cc31365dd1acd6db4e/components/esp_wifi/include/esp_wifi.h#L653):
  AP query может вернуть NOT_CONNECT, default power save — MIN_MODEM.
  Модемный sleep не равен CPU light/deep sleep и не требует переноса C3 sleep flow.

## Подтверждённые source-level проблемы, которые нельзя копировать

Это воспроизводимые расписания из текущих function bodies, не измерения платы.
Новый executable runtime suite должен закрепить их до исправлений.

1. **Поздний отказ не включает AP.** Единственный consumer FAILED bit —
   startup wait ([C3:353](../idf/esp32c3-oled-native/main/network_service.c#L353),
   [CYD:237](../idf/esp32-cyd2usb-native/main/network_service.c#L237)).
   После первого GOT_IP/start return последовательность DISCONNECTED сверх
   retry budget лишь устанавливает bit. `start_access_point` больше никто
   не вызывает. У C3 при соединении с последним профилем поздняя потеря также
   не возвращает попытки к более ранним профилям.
2. **HTTP/event concurrency.** HTTP reconnect вызывает retry_client прямо в
   HTTPD task. Одновременно default event task меняет plain `s_retries`, а у C3
   ещё index/config. Driver API thread safety не сериализует этот набор шагов.
   Например, HTTP reset index=0 пересекается с event increment/select; итоговый
   index и реально установленная config могут не соответствовать друг другу.
   C3 select публикует cache/index **до** результата `esp_wifi_set_config`;
   ошибка оставляет software selection, которую driver не принял.
3. **Старый status.** C3 DISCONNECTED не очищает CLIENT/IP/RSSI, а RSSI task
   при query failure вообще не публикует invalid state. CYD time hook уже
   [очищает IP](../idf/esp32-cyd2usb-native/main/network_service.c#L131), но
   одному enum всё ещё не хватает независимого признака AP active: поздний
   GOT_IP после startup fallback ставит CLIENT, хотя физически APSTA сохранён.
4. **Старое audio false побеждает новый Play.** Старый stream проходит
   generation check на C3:1186 и прерывается. Новый Play:2312 задаёт NONE.
   Старый stream:1190 затем задаёт MIN_MODEM, в том числе после generation
   advance нового Play. Проверка перед driver call не является транзакцией.
   Существующие maintenance tests подменяют set_streaming seam; они не
   доказывают отсутствие этой гонки.
5. **AP teardown до HTTP ответа.** retry_client делает `set_mode(STA)` до
   возврата в HTTP handler. Запрос через SoftAP может лишиться соединения до
   ответа. Сохранение APSTA устраняет этот явный teardown, но RF channel change
   всё равно может оборвать клиента. Успех HTTP означает admission, не GOT_IP.
6. **Неконтролируемый AP timer.** C3 timer после fallback не отменяется при
   GOT_IP/manual retry, callback вызывает restart без OTA lease. Это не
   подходящий готовый implementation для CYD; option переносится отдельным
   lifecycle блоком с default disabled.

Также проверять immediate ошибки connect/mode/config: текущие event handlers
игнорируют результат connect и могут ждать событие, которое не придёт.
Поведение LOST_IP нельзя описывать как гарантированно stale: SDK timer
проверяет actual IP перед post. Тест нужен именно на уже queued event и
reconciliation после новой association.

## Минимальная реализация и ownership

Предлагаются новые `main/network_runtime.c/.h` на CYD и отдельные actual-loop
tests. Сначала один target adapter, без переноса всего C3 runtime_settings и
без нового общего framework. Существующий network_service остаётся facade
для startup, desired-store API и runtime requests. Выделение общего policy
core для обоих targets имеет смысл после qualification тех же semantics.

- Один постоянный owner: candidate **priority 2 / core 0**. Он единственный
  вызывает runtime set_mode/config/connect/disconnect/set_ps и меняет
  active index/retry/AP/link state. RSSI period 2000 ms обслуживается там же,
  отдельный C3 `wifi_rssi` task не копируется. Новый stack budget определить
  target map/HWM, а не объявлять безопасным по host результату.
- Bootstrap загружает complete bounded active table до wifi_start и передаёт
  владение owner. Строки хранятся в private table; один `wifi_config_t`
  создаётся/переиспользуется owner. SDK default initializer и auth/PMF policy
  донора сохраняются; compact table не меняет выбранные SDK поля.
- Event callbacks копируют только bounded event data в заранее созданную
  очередь, делают nonblocking wakeup и возвращаются. Никаких FS/NVS,
  ожидания mutex, driver reconnect chains или форматирования password.
- Отдельный fixed request mailbox, максимум один ожидающий manual retry;
  повтор возвращает BUSY. Event queue capacity первоначально 16 записей:
  overflow выставляет atomic resync flag, owner инвалидирует online/RSSI и
  делает bounded reconcile. Нельзя просто терять terminal disconnect.
  Latest power intent coalesces отдельно и не вытесняет lifecycle events.
- Существующие `network_service_retry_client()` / HTTP URI сохраняются.
  ESP_OK означает запрос принят; NOT_FOUND — нет active profiles,
  INVALID_STATE — owner не готов, TIMEOUT/BUSY — admission не состоялся.
  Вызов не ждёт association и не выделяет память. HTTP mapping различает
  unavailable/busy/no profiles; failure не выдаётся за reconnect success.
- Новый checked `network_service_snapshot(out, timeout_ms)` возвращает
  coherent phase, operation epoch, active index/count, STA up/IP, AP enabled,
  last SDK error/reason, RSSI valid/value/age, desired/applied power revision.
  Выход не меняется при failure. В snapshot нет password. Это authoritative
  network view; native_state остаётся bounded projection для старого UI.
- Все allocations/регистрации проверяются до publication ready. При failure
  undo только собственных registrations/tasks/netifs; не deinit общий TCPIP
  и не удалять объект, который ещё читает callback/owner на другом ядре.
  Повторный start не создаёт второй owner. После startup queue/task storage
  и retry/RSSI work не требуют per-request allocations.

Lock order: HTTP не держит desired-store/storage lock при runtime admission;
event callback не берёт owner lock. Owner не держит snapshot/native_state lock
во время SDK calls или ожидания event. Snapshot publication короткая и
проверяемая; UI не принимает нулевой struct после timeout за валидную сеть.
Audio control передаёт intent без ожидания network owner/SDK, чтобы не
ввести обратную зависимость между audio locks и networking.

## Reconnect и deadlines

Состояния owner: `WAIT_START → CONFIGURE → CONNECTING → ONLINE`; отказ ведёт
через `WAIT_DISCONNECT` к следующей попытке; исчерпание — `AP_IDLE`.
`AP enabled` — отдельный флаг, а не взаимоисключающая фаза.

Startup UI budget остаётся **20 s**: если STA ещё не готова, owner включает
существующий APSTA portal и разрешает остальным сервисам стартовать. Owner
после этого продолжает конечный profile cycle; startup wait не отвечает за
поздний fallback. No-profile boot сразу запускает AP и ни разу не connect.

Manual retry начинает с profile 0; после потери ONLINE начать с последнего
успешного профиля, затем пройти остальные с однократным wrap. Initial attempt
и максимум два reattempt на профиль — максимум 15 connect calls на цикл.
Предлагаемый верхний attempt budget — 20 s, whole-cycle budget — 300 s
включая disconnect/reconcile; это **новая bounded policy**, а не обнаруженный
donor timeout. При общем deadline оставшиеся попытки отменяются. Значения
квалифицировать на slow scan/DHCP до production включения. Portal доступен
уже после первых 20 s, ждать весь цикл HTTP/startup не должен.

При exhaustion owner включает AP один раз и остаётся AP_IDLE до manual retry
или реального действительного GOT_IP; бесконечный tight retry не добавляется.
Immediate SDK error получает тот же конечный failure path и snapshot error.
Два повторных подключения остаются конечными, с nonblocking pause между
ошибками; конкретный retry delay фиксируется вместе с executable tests.
Все deadlines absolute/monotonic, wrap проверяется, socket/HTTP работу owner
не выполняет. Внешняя ассоциация/DHCP не имеет обещания завершиться успешно
за этот срок.

Profile/config публикуется как applied только после успешного SDK set_config.
Перед сменой connecting profile требуется checked disconnect/reconcile,
а не слепой set_config. Старые event data не получают вымышленный новый epoch:
сверяются phase, текущая association/SSID/BSSID, netif up и IP. Неоднозначное
событие запускает reconcile, а не увеличивает retry counter нового профиля.
Одинаковые SSID в разных строках особенно важны: SSID comparison сама по себе
не доказывает принадлежность события попытке. Application epoch отменяет
только наши отложенные requests/timers; SDK generation cancellation не заявляется.

## RSSI, power и дополнительные settings

RSSI публикуется только для подтверждённого текущего STA link. На DISCONNECTED,
LOST_IP или NOT_CONNECT value становится invalid; поздний AP query не может
вернуть valid RSSI после смены operation/link epoch. Сохраняются separate age и
validity; для старого wire `rssi` можно отдавать 0 при invalid и добавить
`rssi_valid`, UI скрывает недостоверное значение. Проверить фактические WS
ключи/heartbeat после этого изменения, не только source regex.

Power input разделяется на **accept(generation, active)** от audio control и
**finish(generation)** от stream owner. Только accept устанавливает новую
current generation; finish очищает intent лишь при точном совпадении. Старый
stream start/finish не может заменить новый command intent. Stop, maintenance,
accepted resume и retry/backoff получают явные правила в audio integration.
Семантику EOF донора сохранить: после конца network receive MIN_MODEM
допустим, даже если decoder ещё допроигрывает buffered PCM.

Единственный network owner сериализует set_ps и сводит current desired/applied
revision. Если новый intent приходит во время SDK call, следующий шаг
восстанавливает актуальную policy; мгновенное аппаратное переключение вместе
с Play не обещается. SDK error записывается, имеет конечный retry budget и не
блокирует аудио. Не переносить старую bool last-writer гонку в новую очередь.

Hostname и AP timeout оформляются отдельным маленьким `network_settings`
record с checked coherent snapshot/persist-before-publish, не копией всего
C3 runtime_settings. Hostname bounded по donor capacity 24, ASCII hostname
validation; default `yoradio`. `esp_netif_set_hostname` после соединения
отражается только после reconnect (public esp_netif.h:350); runtime edit не
обещает немедленную смену DHCP имени. AP timeout 0–30 min/default 0, проверка
epoch/состояния перед request reboot. Timer callback только уведомляет owner;
lease [web_reboot.h](../idf/esp32-cyd2usb-native/main/web_reboot.h) защищает OTA.
Не добавлять автоматический reboot при обычном late disconnect.

## Последовательность блоков и проверка

| Блок | Узкие owned paths после отдельного назначения | Обязательная проверка |
| --- | --- | --- |
| N0: зафиксировать исходные дефекты | NEW `tests/native/*network_runtime*`, runner | Actual unchanged handler/start/retry/RSSI/power functions с deterministic SDK/RTOS seams; late disconnect после успешного startup, retry/event interleaving, stale power false. Known-bad baseline — executable negative, не постоянный падающий positive test. |
| N1: profiles + постоянный CYD owner | NEW CYD `network_runtime.c/.h`; integration owner — `network_service.c/.h`, CMake | Actual owner loop и profile reader; 0/1/5/6 rows, malformed/CR/NUL/IO/close failures, no secret output, immutable active cache после desired edit; SDK startup rollback. |
| N2: late reconnect/AP + bounded HTTP | Network integration + `web_service.c`, checked snapshot/state projection | Initial success → later outage → all budgets → AP; 20 s startup vs late GOT_IP; APSTA сохраняется при retry; duplicate/queue full/SDK error/deadline/event overflow; old/ambiguous SDK events и одинаковые SSID. |
| N3: RSSI + UI state | Owner, narrow `native_state`, WS/status/UI | Actual poll/publish paths, NOT_CONNECT, late result, invalid/age, snapshot timeout, status retry/heartbeat/JSON; existing UI/status executable suites сохраняются. |
| N4: power + narrow donor repair | Network owner + coordinated audio integration обеих плат | Barrier между old generation check/new Play/old false; Stop/retry/EOF/maintenance/resume; desired/applied errors/retry; Play остаётся best effort. Сначала подтвердить old-code negative. |
| N5: hostname/AP timeout | NEW small settings + owner/web wiring | NVS failure/validation/coherent snapshot; hostname deferred apply; AP timer cancel/rearm/epoch; pending OTA lease и failure не вызывают restart. |

У каждого завершённого блока — focused commit, raw frozen source hashes,
ASan/UBSan, semantic mutants по конкретным инвариантам. Concurrent tests
действительно запускают owner/callback/request publishers; ACK/phase нельзя
выставлять тестом вместо actual owner work. Driver/RF и RTOS scheduler seams
явно перечисляются. TSAN запускать, если runtime поддерживается; отсутствие
TSAN не заменять заявлением о доказанной SMP безопасности.

Existing executable coverage переиспользовать, но не расширять её claims:
[C3 persistence](../tests/run-c3-wifi-persistence.py) и
[CYD storage](../tests/run-cyd-wifi-storage.py) проверяют реальные store/loader
functions, не runtime reconnect/power. [CYD startup/time events](../tests/run-cyd-time-events.py)
проверяют реальные startup/event bodies, RAM selection и no-profile START
guard с SDK seams. [C3 maintenance](../tests/run-c3-maintenance.py) проверяет
audio owners, но network power там является seam.
[Node architecture checks](../tests/esp32c3-native-idf.test.js) не заменяют
ни одного interleaving test.

Перед приёмкой нужны оба реальных pinned SDK builds/lint и production maps,
затем CYD DAC/PDM hardware: RF outage/recovery со всеми профилями, AP channel
change с открытым UI, scan/DHCP delays, длительный stream при NONE/MIN_MODEM,
RSSI validity, heap/stack/task/core evidence. Работу двух ядер, экономию энергии,
throughput или отсутствие audio underrun host harness не доказывает.
Ресурсные измерения C3 на CYD не переносятся.
