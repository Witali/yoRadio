# Проект переноса OTA на ESP32 CYD

Дата: 2026-10-18. Этап: **CYD-C3-08**, статус: **проект, реализация не начата**.
Документ дополняет [общий план](ESP32_CYD_C3_TRANSFER_PLAN.md), не меняя его
статусы. Текущий Web/RFC batch, production-код, firmware и evidence этим
документом не изменяются. Реализацию начинать после архивации этого batch.

## Результат этапа

CYD принимает только application `app.bin` через существующий нативный сервер:
проверяет платформу и проект, переводит аудио в подтверждённое maintenance
состояние, записывает неактивный OTA-раздел и проверяет весь образ. Только
после этого выбирает новый boot-раздел и планирует reboot. Ошибка до активации
сохраняет работающий образ, NVS и SPIFFS, освобождает OTA handle и возвращает
радио из maintenance по явно проверенному сценарию.

HTTP и HTTPS используют один и тот же обработчик. WebUI показывает реальный
размер слота, выбранный backend, ход загрузки, отказ и возможность повторить
попытку. HTTP 200 без проверки нового ELF identity и running partition после
перезагрузки не является успешной установкой.

## Платформа и границы совместимости

| Область | Донор ESP32-C3 | Цель CYD и решение |
| --- | --- | --- |
| SDK / CPU | Закреплённый IDF 6.1, RISC-V, одно ядро | IDF 6.0.2, ESP32 Xtensa LX6, два ядра; пересобрать и проверить публичные API |
| Chip ID | `ESP_CHIP_ID_ESP32C3`, значение5 | `ESP_CHIP_ID_ESP32`, значение0; использовать SDK enum, не числовую копию |
| Project | `yoradio_esp32c3_oled_native` | `yoradio_cyd2usb_native`, [CMakeLists.txt:20](../idf/esp32-cyd2usb-native/CMakeLists.txt#L20) |
| Application slot | `0x1D0000` | **`0x1B0000` = 1 769 472 байта**, размер проверять также по выбранному разделу |
| Partition layout | app0/app1, SPIFFS и coredump C3 | Сохранить CYD [partitions.csv](../idf/esp32-cyd2usb-native/partitions.csv): app0 `0x10000`, app1 `0x1C0000`, SPIFFS `0x370000` |
| Audio | C3 PDM и собственный lifecycle | Сохранить CYD PDM, continuous DAC и legacy DAC, mono GPIO26, clocking и DMA |
| Scheduling | Single-core policy C3 | stream/core0/priority3, decoder/core1/priority5, output/core1/priority6 сохраняются |
| Activity | Deep-sleep/display leases C3 | Не переносить C3 deep-sleep, USB, BOOT, дисплей, 160 МГц и pinning hooks |

PDM, continuous DAC и legacy DAC сейчас имеют одинаковые chip/project поля.
Эти две проверки **не различают аудиоварианты**. Первая приёмка проводится для
каждого опубликованного варианта с соответствующим ему образом; UI/manifest
должны явно показывать backend. Нельзя объявлять автоматический отказ от
неподходящего DAC/PDM-образа без отдельного машинно проверяемого признака в
образе. Если такой фильтр входит в реализацию, сначала определить его формат,
совместимость с уже выпущенными образами и negative test; одного имени файла
или заявления браузера недостаточно. Переименование project не должно
незаметно оборвать совместимость OTA.

## Входы существующего кода

| Назначение | Вход и что сохранить / изменить |
| --- | --- |
| Потоковый OTA sink | C3 [ota_upload.c:18](../idf/esp32c3-oled-native/main/ota_upload.c#L18), [ota_upload.h](../idf/esp32c3-oled-native/main/ota_upload.h): буфер4096, проверка заголовка, отдельные finish/activate/abort |
| HTTP lifecycle | C3 [web_ota.c:60](../idf/esp32c3-oled-native/main/web_ota.c#L60): адаптировать под CYD maintenance/reboot и убрать аппаратные C3 hooks |
| Multipart | Общий [web_multipart.h:260](../idf/components/native_storage/include/web_multipart.h#L260): использовать `mp_form_data_boundary`, общий parser и `mp_parameter`; не переносить старый ad-hoc `boundary_from_request` |
| Существующие upload endpoints | CYD [web_upload.c:130](../idf/esp32-cyd2usb-native/main/web_upload.c#L130): переиспользовать контракт bounded receive; OTA пишет в flash sink, не в staging SPIFFS |
| Audio cancellation | CYD [audio_service.c:1104](../idf/esp32-cyd2usb-native/main/audio_service.c#L1104), [audio_service.h](../idf/esp32-cyd2usb-native/main/audio_service.h): Stop сейчас асинхронен, подтверждённого maintenance API нет |
| Владельцы ресурсов | CYD [stream:425](../idf/esp32-cyd2usb-native/main/audio_service.c#L425), [decoder:623](../idf/esp32-cyd2usb-native/main/audio_service.c#L623), [output:882](../idf/esp32-cyd2usb-native/main/audio_service.c#L882): добавить подтверждения завершения именно в owning tasks |
| Output backend | [native_audio_output.h:25](../idf/esp32-cyd2usb-native/main/native_audio_output.h#L25), [native_audio_output.c](../idf/esp32-cyd2usb-native/main/native_audio_output.c): flush/reset не равен ожиданию DMA; backend операции выполняет только output task |
| Persistent radio state | Общий [radio_control_impl.h](../idf/components/native_storage/include/radio_control_impl.h): `radio_control_stop` сохраняет SmartStart «stopped», поэтому не использовать его как внутреннюю maintenance-остановку |
| Preallocated reboot | CYD [web_reboot.c:33](../idf/esp32-cyd2usb-native/main/web_reboot.c#L33), [web_reboot.h](../idf/esp32-cyd2usb-native/main/web_reboot.h): выделен при старте, запрос не требует allocation |
| Routes и capabilities | CYD [web_service.c:316](../idf/esp32-cyd2usb-native/main/web_service.c#L316), [startup:331](../idf/esp32-cyd2usb-native/main/web_service.c#L331): пока `ota:false`; новые routes до wildcard, проверить вместимость таблицы и startup rollback |
| Native UI | CYD [web_pages.cpp](../idf/esp32-cyd2usb-native/main/web_pages.cpp), [page tests](../tests/cyd-native-page.test.js): добавить родной app-only OTA flow без SPIFFS/bootloader выбора |
| Plain/TLS I/O | [native_web_transport.h](../idf/components/native_web_transport/include/native_web_transport.h): сохранять HTTPD session ownership, TLS WANT direction и конечные deadlines |
| Первичный boot | CYD [app_main.c:75](../idf/esp32-cyd2usb-native/main/app_main.c#L75): NVS/SPIFFS/audio/web startup; сейчас нет подтверждения pending OTA image |

Донорские [host sink tests](../tests/native/esp32c3_ota_test.c),
[HTTP tests](../tests/native/esp32c3_ota_http_test.c) и
[runner](../tests/run-esp32c3-ota.py) дают начальную матрицу. Они не проверяют
CYD audio acknowledgement, его DMA, размер слота или аппаратный rollback.
Runner сейчас собирает с host mocks без ASan/UBSan; новая матрица должна
добавить санитайзеры, snapshots/hashes и executable negative controls.

## Предлагаемый контракт реализации

Имена ниже — проект новых API, **сейчас их в production нет**.

```c
esp_err_t audio_service_maintenance_begin(audio_maintenance_token_t *token,
                                        uint32_t timeout_ms);
esp_err_t audio_service_maintenance_end(audio_maintenance_token_t *token,
                                      bool resume_previous);
```

Token ограниченного размера принадлежит запросу; содержит epoch/валидность и
снимок предыдущего URL/codec/состояния без private SDK handles. Вход выполняется
под существующим control ownership: запрещает новый Play, фиксирует намерение
восстановления и отменяет старую generation. Ждать acknowledgements под
state mutex либо внешне удалять task/client запрещено.

Для разрешения записи нужны три подтверждения одной maintenance epoch:

1. Stream task завершил прежнюю операцию, закрыл HTTP/TLS client и вернул
   producer leases. Учесть connect/open timeout, idle owner и отменённую
   команду, которая ещё лежит в очереди.
2. Decoder task уничтожил decoder и PCM workspace, вернул текущие и старые
   encoded leases. Текущий `s_decoder_released_generation` публикуется раньше
   полного осушения очереди и сам по себе не является таким подтверждением.
3. Output task вернул PCM leases, отбросил старый software tail/history и
   подтвердил тихое состояние конкретного backend/DMA. Не вызывать его
   private operations из HTTP task. `audio_running=false` и
   `native_audio_output_flush_pcm()` не доказывают этот пункт.

Установить один конечный deadline maintenance. Его величину выбрать с учётом
текущего stream startup timeout10s и максимальных backend writes; проверить
реальные границы на плате. Превышение deadline не считается освобождением
ресурсов: запрещает `esp_ota_begin/write`, возвращает ошибку, сохраняет
однозначное владение token и запускает проверенный cleanup/retry сценарий.
Нельзя просто очистить флаг и объявить старые ресурсы свободными.

На ошибке восстанавливать только действительно работавший/подключавшийся
поток. Ранее остановленное радио остаётся остановленным. Восстановление не
должно менять last station, SmartStart, playlist index или audio settings.
Token старой epoch не возобновляет поток поверх нового намерения пользователя.
Политику конкурентных команд зафиксировать в коде и тестах: возвращать busy
до выхода из maintenance; явно поддержанная отмена должна инвалидировать
resume token. Ошибка восстановления показывается отдельно, а не превращает
неуспешную OTA в успешную.

## Порядок HTTP-запроса и flash lifecycle

1. Проверить готовность заранее созданного reboot service, отсутствие другого
   upload/reboot, Content-Type/boundary и ограниченный Content-Length.
   Выделить один фиксированный workspace и token до остановки аудио.
2. Общий parser принимает один `updatetarget` перед одним `update`.
   Допустимы только `fw`/`firmware`. Не принимать дополнительные файлы,
   неожиданные поля, дубликаты, неполную форму и посторонний epilogue.
3. Накопить только image/app prefix в bounded workspace. До flash begin
   проверить magic, `ESP_CHIP_ID_ESP32`, app-desc magic и полный ожидаемый
   project field. Только после валидного prefix запросить maintenance.
   Для этого shared sink нужен явный before-flash hook/state transition;
   donor `check_header` сейчас немедленно вызывает `esp_ota_begin`.
4. Проверить неактивный APP/OTA-раздел, отличный от running address; разрешённый
   диапазон и размер — текущая CYD partition table. Не разрешать bootloader,
   partition table, factory relocation, SPIFFS и arbitrary flash offsets.
5. После всех audio acknowledgements вызвать
   `esp_ota_begin(..., OTA_WITH_SEQUENTIAL_WRITES, ...)`. Писать фиксированными
   блоками до4096, контролируя `received <= partition->size` до арифметики.
   Полный образ и его копию в SPIFFS не хранить.
6. Сохранить donor-кандидаты deadline180s на запрос и10s без данных, проверяя
   время до и после каждого receive. Положительное чтение не продлевает общий
   срок. Проверять `0 < received <= requested <= remaining`; retries должны
   уступать scheduler. Выбрать HTTPD timeout так, чтобы внутренний read не
   делал эти пределы фиктивными.
7. Завершить multipart и `esp_ota_end`. В IDF6.0.2 эта функция потребляет handle
   также при ошибке; после неё нельзя повторно вызывать abort того же handle.
   Проверить `esp_image_get_metadata` и точное равенство image length числу
   принятых image bytes: это отсекает merged/trailing bytes и старый flash tail.
8. Повторно проверить readiness reboot service, выбрать проверенный раздел
   через `esp_ota_set_boot_partition`, зафиксировать состояние committed.
   После этого не выполнять fallible allocation для организации reboot.
9. Отправить ответ и запросить заранее созданный `web_reboot` с короткой
   задержкой. Потеря клиента/ошибка ответа после commit не отменяет reboot.
   Maintenance остаётся удержанным до restart.
10. До commit при любой ошибке abort только живого handle, освободить workspace,
    завершить транспорт и выполнить проверенный maintenance exit. Не менять
    active application, NVS, SPIFFS, bootloader и partition table.

Request-envelope limit проверять отдельно от image cap. Донор допускает
`partition->size + 2048` для multipart overhead; сохранить эту величину лишь
с проверкой переполнения и матрицей максимальных допустимых headers/boundary.
Не объявлять envelope size максимальным размером `app.bin` в UI.

Общие байты/grammar parser можно вынести в shared OTA core с явной target
policy, оставив тонкие adapters C3/CYD. Изменение донора требует его regression
tests; C3 hardware hooks не должны становиться зависимостями CYD.

## HTTPS и завершение отклонённой загрузки

Donor `finish_rejection` делает raw `recv` после `shutdown(SHUT_WR)`. Этот код
нельзя копировать в HTTPS как plaintext reader. Ответ, drain и закрытие должны
сохранять owned TLS context и направление WANT_READ/WANT_WRITE. Выбрать
конечный алгоритм завершения отказа через transport API и проверить, что
браузер получает ошибку, а не ложный `OK` или бесконечное ожидание.

Не добавлять второй listener для OTA. Сохраняются текущие лимиты HTTPD и secure
mode. Пока синхронный handler занят загрузкой, HTTPD не обслуживает обычные WS
команды: UI должен явно показывать maintenance и корректно reconnect после
отказа/reboot, не трактуя паузу статуса как разрешение второй загрузки.

## Сохранение данных и rollback

OTA пишет только spare app и штатную OTA metadata; не форматирует SPIFFS,
не стирает NVS и не заменяет bootloader/partition table. Проверять сохранность
Wi-Fi, playlist/index, SmartStart, audio settings и TLS NVS bundle. Проверки
не должны публиковать содержимое ключей/паролей или их hashes. Физическое
сравнение приватных snapshots проводится вне evidence/source/firmware archive.

**Автоматического rollback сейчас нет.** В проверенной CYD конфигурации
`CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE` выключен; в `app_main` нет обработки
`ESP_OTA_IMG_PENDING_VERIFY` и mark-valid. Наличие двух слотов и сохранение
старой программы не является автоматическим восстановлением после bad boot.

Для отдельного rollback-enabled профиля потребуются:

* согласованный bootloader baseline и проверка его фактической установки;
  application OTA не заменяет уже установленный bootloader;
* `esp_ota_get_state_partition` и подтверждение через
  `esp_ota_mark_app_valid_cancel_rollback` после определённых startup checks;
* контролируемый отказ/неподтверждённый restart и проверка возврата к прежнему
  image/partition, а также отсутствие дальнейшей OTA из неподтверждённого app;
* критерии здоровья NVS/SPIFFS, backend/pipeline и web startup без обязательной
  доступности внешней радиостанции или интернета;
* доказательство сохранности настроек и поведения при отключении питания.

IDF6.0.2 при включённом rollback может инвалидировать неактивную OTA metadata
уже в `esp_ota_begin`. Поэтому нельзя требовать byte-exact неизменности всей
`otadata` на каждом отказе; нужно доказывать корректность running/boot selection
и восстановление. Secure Boot, eFuse anti-rollback и необратимые записи не
требуются для этого переноса и автоматически не включаются.

## Последовательность реализации и обязательные проверки

Каждая строка — кандидат отдельного focused commit после текущего batch.
Статус OTA в capabilities включать лишь после реализации его обязательных
зависимостей, не по факту добавления формы.

| Шаг | Изменение | Проверка перед переходом |
| --- | --- | --- |
| 08.1 | Shared sink/target policy и CYD prefix/partition validation | Actual production tests: chip/project/magic, APP-only, cap/cap+1, отсутствующий/активный slot, allocation/flash/API failures; C3 regression |
| 08.2 | Maintenance epoch, три owner acknowledgements, backend pause/resume | Stop не считается ack; connect/read cancellation, queued commands, leased/full queues, decoder release, DMA write, timeout до первого erase, stale/duplicate token, fail/resume и SmartStart preservation |
| 08.3 | HTTP/HTTPS handler, bounded receive, transport-safe rejection, preallocated reboot | Один upload, idle/overall deadlines, partial/oversized receive, disconnect/slow sender, retry, response failure после commit и единственный reboot |
| 08.4 | Routes/capabilities и native UI app-only/recovery flow | Actual handler tests плюс Node DOM/XHR/fetch tests: размер, backend, progress/cancel/error/retry, busy controls, схема/host/port origin, reconnect; startup rollback каждой новой route |
| 08.5 | SDK/host verification и firmware export | Оба pinned SDK, C3 и все intended CYD backends; lint/warnings review, map/size/stack review, source/image/ELF/config hashes и manifest |
| 08.6 | Физическая OTA/данные/rollback при соответствующем bootloader | Только реальные выполненные сценарии; явные pending/failed gates вместо вывода из mocks |

Host tests должны исполнять production core/handlers, а SDK/flash/backend seams
обозначать отдельно. Минимальная расширенная матрица:

* все split позиции multipart boundary, headers и image/app prefix; ложные
  boundary внутри бинарных данных; duplicate/misordered parts и malformed
  Content-Type/Content-Disposition;
* zero/truncated image, wrong chip/project, bootloader/SPIFFS/merged image,
  corrupted payload/checksum/hash, trailing bytes, stale flash tail,
  переполнение длины и предел ровно `0x1B0000` / плюс1;
* OOM workspace/SDK begin, ошибки write/end/metadata/set-boot; handle
  освобождается ровно раз, ранняя ошибка не выбирает образ;
* абсолютный/idle timeout, HTTPD timeout, positive short reads, invalid receive
  count, EOF и disconnect на разных стадиях, повторная попытка после отказа;
* paused/connecting/playing/stopped snapshots, delayed/missing owner ack,
  generation wrap, конкурентный Play/Stop, полный ring/leases и ошибки resume;
* preallocated reboot readiness и ошибка отправки ответа после commit;
* HTTP и настоящий TLS с валидирующим клиентом, buffered plaintext/WANT paths,
  корректная ошибка отказа и отсутствие raw application I/O в secure mode.

Обязательны ASan/UBSan и negative controls, которые тесты реально ловят:
отключённые chip/project/cap проверки, ранняя активация, запись до owner ack,
двойной abort после end, продление общего deadline каждым chunk и потеря
reboot при неуспешном ответе после commit. Не считать compile failure
успешным semantic negative control.

## Физическая квалификация и критерий закрытия

Успешные host-тесты не доказывают SPIFFS/flash behavior, IRQ/DMA continuity,
межъядерные задержки или достаточную RAM. На каждом intended CYD backend:

1. Сохранить текущие идентичности и приватный snapshot данных; загрузить
   соответствующий app-only image и подтвердить переход app0↔app1, полный ELF
   identity, settings и нормальную работу после reboot.
2. Проверить загрузку из состояния stopped, connecting и активного HTTP/HTTPS
   playback, отмену/обрыв/медленный клиент и повторную попытку. Аудио должно
   действительно остановиться до flash write; failure resume оценивается
   отдельно от успешности OTA.
3. Измерить internal heap minimum/largest block, DMA reserve, HTTPD и трёх audio
   stack high-water marks, CPU/watchdog, освобождение decoder/TLS и возврат
   ресурсов после отказа. C3 measurements и полная SRAM ESP32 не заменяют это.
4. Контролируемо прервать питание при begin/erase/write/end/otadata и проверить
   старый рабочий образ, данные и возможность восстановления. Действия с
   питанием/bootloader не выполнять автоматически вместе с host-проверками.
5. Если используется rollback-enabled baseline, проверить bad boot до mark-valid
   и healthy boot после mark-valid; отдельно подтвердить сам bootloader.

Каждую успешную production-сборку для испытаний сохранить под
`firmware/development/<variant>/app.bin` с manifest/config/logs; versioned
releases не перезаписывать. Отчёт связывает source hashes, SDK, backend,
bootloader baseline, partition table и фактически выполненные сценарии.

Этап нельзя закрывать формулировкой «OTA с rollback готова», пока отсутствуют
физические подтверждения соответствующих режимов. Допустим раздельный статус:
программная часть проверена, физическая приёмка и automatic rollback pending.

## Проверенные pinned SDK входы

В локальном IDF6.0.2 (`.idf/v6.0.2/components/`) проверены:

| Файл / API | Существенное поведение |
| --- | --- |
| `app_update/esp_ota_ops.c:143`, `esp_ota_begin` | Проверяет APP/OTA partition, running conflict и pending-verify при enabled rollback; поддерживает sequential erase |
| Тот же файл:566, `esp_ota_end` | Проверяет образ и потребляет handle также при ошибке |
| Тот же файл:763, `esp_ota_set_boot_partition` | Проверяет образ перед изменением boot selection |
| `bootloader_support/src/esp_image_format.c:365`, `esp_image_get_metadata` | Публичный источник image length после SDK validation |
| `bootloader_support/include/esp_app_format.h:20` | `ESP_CHIP_ID_ESP32 = 0`, C3 имеет отдельный ID |
| `app_update/include/esp_ota_ops.h` | Публичные state/mark-valid/rollback API; наличие функций не означает enabled rollback в установленном bootloader |

SHA256 inspected SDK units: `esp_ota_ops.c`
`afe45475f68c5952bfaea73e8dc200e963df4b9036e67ec17418cc4ea2986290`,
`esp_image_format.c`
`193717dffff9a13063e88b30d100dc8d82a4eaab089f1271b389df43056a730d`.
Это fingerprints аудита, не доказательство SDK integration новой OTA:
production-реализации CYD на момент составления документа ещё нет.
