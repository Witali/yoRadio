# План переноса улучшений ESP32 C3 на CYD

Обновлено: 2026-10-28. Ветка: `codex/esp32-cyd-c3-review`.
Worktree: `.worktree/esp32-cyd-c3-review`, исходная база `42bc7bd4`.
Цель: общие программные улучшения нативного `idf/esp32-cyd2usb-native`
для ESP32-2432S028 CYD2USB. Аппаратно-зависимые функции C3 исключены.
Arduino CYD и `esp32-cyd2usb-minimal` остаются отдельными профилями.

Наиболее полезный перенос начинается с жизненного цикла аудиопотока,
распознавания кадров, управления памятью и полноценного WebUI. Оптимизации
внутренностей AAC и Vorbis требуют отдельной проверки Xtensa-библиотек.
Результаты C3 не являются измерениями скорости, RAM или звука CYD.

Этот план дополняет [сентябрьский план CYD](ESP32_CYD_ESP8266_IMPROVEMENTS_PLAN.md)
изменениями C3 вплоть до [приёмки 15 октября](ESP32C3_PRODUCTION_ACCEPTANCE_20261015.md).
Пункты выполняются отдельными коммитами; статус меняется после проверки.

## Что в CYD уже есть

| Возможность | Место в CYD | Решение |
| --- | --- | --- |
| Три задачи, сеть на core 0, decode/output на core 1 | [audio_service.c](../idf/esp32-cyd2usb-native/main/audio_service.c) | Сохранить разделение. Output уже имеет приоритет 6 против decode 5. |
| 16 КиБ encoded и 8 КиБ PCM, запись через ring acquire/complete | [audio_service.c](../idf/esp32-cyd2usb-native/main/audio_service.c) | Не переносить второй раз отсутствие malloc на каждый пакет. README ошибочно говорит про 8 КиБ encoded. |
| QIO 80 МГц, 240 МГц CPU, tick 1000 Гц, performance compiler | [sdkconfig.defaults](../idf/esp32-cyd2usb-native/sdkconfig.defaults) | Уже включено. C3 QIO overlay и изменение tick не нужны. |
| PDM 48 кГц и 6.144 МГц, отдельные continuous/legacy DAC | [native_audio_output.c](../idf/esp32-cyd2usb-native/main/native_audio_output.c) | Сохранить аппаратные backends и mono GPIO26. |
| Espressif MP3/AAC, optional Helix/minimp3, Ogg Opus/Vorbis | [CMakeLists.txt](../idf/esp32-cyd2usb-native/main/CMakeLists.txt), [sdkconfig.defaults](../idf/esp32-cyd2usb-native/sdkconfig.defaults) | Сначала измерить штатные реализации. |
| Q15 volume/balance и NVS audio settings | [native_audio_output.c](../idf/esp32-cyd2usb-native/main/native_audio_output.c), [native_audio_settings](../idf/components/native_audio_settings) | Сохранить существующие значения и миграцию. |
| Нативный ST7789 SPI DMA | [cyd_display.c](../idf/esp32-cyd2usb-native/main/cyd_display.c) | Использовать этот драйвер для нового интерфейса. |

## Совместимость аппаратных платформ

Перед каждым переносом сверять ограничения SoC, схему конкретной платы и
реальный build profile. Спецификация SoC не определяет свободный heap платы.
Первичные источники: [ESP32 Series Datasheet](https://documentation.espressif.com/esp32_datasheet_en.html)
и [ESP32-C3 Datasheet](https://documentation.espressif.com/esp32-c3_datasheet_en.html),
сверены 2026-10-18. Распиновка и выбранные режимы ниже относятся к профилям
репозитория, а не ко всем платам с этими SoC.

| Область | Донор C3 | Цель CYD | Следствие для переноса |
| --- | --- | --- | --- |
| CPU/ABI | Одно ядро RISC-V, профиль 160 МГц | Два ядра Xtensa LX6, профиль 240 МГц | C/C++ алгоритмы пересобираются; assembler, private offsets, archive patches и результаты производительности требуют собственной проверки. |
| Синхронизация | Single-core FreeRTOS | SMP FreeRTOS, stream на core 0, decode/output на core 1 | Локальное IRQ masking не защищает от второго ядра; ownership и snapshots проверяются с межъядерной синхронизацией. |
| Память | 400 КиБ SRAM, часть используется cache | 520 КиБ SRAM с собственной раскладкой IRAM/DRAM | Это полные ресурсы SoC, не свободная RAM. Heap, DMA-capable largest block, TLS reserve и stacks выбираются по CYD измерениям с TFT и сетью. |
| Аудио платы | Два PDM data GPIO10/GPIO3 | Mono GPIO26, PDM либо continuous/legacy DAC | Переносить DSP с сохранением CYD downmix, clocking, DMA и всех трёх backend; C3 stereo wiring/FIR/timing не копировать. ESP32 имеет два 8-bit DAC, C3 встроенного DAC не имеет. |
| Дисплей/пины | OLED I2C GPIO5/6, BOOT GPIO9 | TFT SPI с DMA, BOOT GPIO0 | Эти аппаратные функции исключены из переноса; CYD pin map и display driver сохраняются. |
| USB/reset | Native USB Serial/JTAG | Адаптер CH340 | C3 USB/reset/deep-sleep hooks не переносить. |
| SDK/библиотеки | Закреплённый IDF 6.1, RISC-V archives | Закреплённый IDF 6.0.2, Xtensa archives | Публичный API проверять компиляцией CYD; private codec ABI — отдельный этап 14. |

Конкретные настройки: [CYD board](../idf/esp32-cyd2usb-native/main/board_config.h),
[C3 board](../idf/esp32c3-oled-native/main/board_config.h),
[CYD SDK defaults](../idf/esp32-cyd2usb-native/sdkconfig.defaults),
[C3 SDK defaults](../idf/esp32c3-oled-native/sdkconfig.defaults).
Численное ускорение и экономию памяти отмечать только после измерения на CYD.

## Очередь реализации

Все строки со статусом «Открыт» — предстоящая работа. Размер буфера, порядок
allocation и численные настройки C3 являются кандидатами для CYD A/B,
а не готовыми параметрами нового профиля.

| Этап | Статус | Результат и критерий завершения |
| --- | --- | --- |
| CYD-C3-00 | Программная база готова | План, исходная сборка IDF 6.0.2 и исправные host-проверки донора. Первоначальный полный clang-tidy прогон CYD и C3 сохранён. Аппаратный baseline отдельно. |
| CYD-C3-01 | Программная часть выполнена | Generation, decoder/PCM lifetime, ordered completion и output flush/reset проверены host-тестами. Финальные PDM/continuous/legacy images коммита `2df73834` собраны и сохранены; физическая приёмка отдельно. |
| CYD-C3-02 | Программная часть выполнена | Общие probe/ID3/ICY/JSON helpers подключены к CYD, HTTP startup ограничен общим deadline и числом redirects; fatal TLS/partial bytes и raw EOF проверены на реальном HTTP-парсере обоих SDK. Host/санитайзеры проходят; физическая сеть отдельно. |
| CYD-C3-03 | Программная часть выполнена | CYD подключён к continuous MP3/ADTS confirmation, ID3 stripping/recovery и ordered codec drain. 34 corpus cases обеих целей, byte-exact переходы и шесть lifecycle вариантов проходят. PDM/continuous/legacy CYD и C3 source `8bf1d73a` собраны и сохранены. Физическая приёмка отдельно. |
| CYD-C3-04 | Программная часть выполнена | Общая SMP-очередь leases/control/tail, бюджет 8 slots, минимум 4 и независимый control node подключены. Default-off bounded prefill проверен host-тестами и GCC/clang-tidy профилем 250 ms; image source `112c871f` сохранён. Физическая приёмка и выбор ёмкости/TLS reclaim — отдельно, этап 13. |
| CYD-C3-05 | Программная часть выполнена | SMP-safe health подключён к pipeline и `/api/native/health`: heap/internal/DMA, input occupancy, ошибки, optional CPU/stack по двум ядрам. Host core/HTTP/lifecycle, SDK quiet/diagnostic и полный lint проходят; images `b7362172` сохранены. [Backend telemetry](CYD_OUTPUT_TELEMETRY_DESIGN.md) подключена ко всем трём выходам и HTTP: SMP-счётчики16/7, backend22/8 и bounded JSON2000/2304 проходят; quiet без timer calls, целевые IRAM/DRAM helper objects проверены. Физические CPU/heap/stack/IRQ/DMA измерения отдельно. |
| CYD-C3-06 | Программная часть выполнена | Общий radio controller, index recovery, last station/SmartStart, Next/Prev/Toggle и HTTP API подключены к CYD. Pending-state, boot/NVS failure, stale cache и concurrency проверены. Возобновлённый format/bitrate и audio settings [программно квалифицированы](../tests/results/cyd-c3-format-dsp-20261018/README.md): 51 stream/80 settings запросов, обе startup/format цели, SDK и полный lint проходят. Дальнейшие WebUI/runtime settings относятся к этапам 07/09; физическая приёмка отдельно. |
| CYD-C3-07 | Программная часть выполнена | Native UI, snapshots/events, два async static workers, bounded multipart uploads, восстановление файлов, публикация CSV/index парой и Wi-Fi save/reboot реализованы. [Host-проверки](../tests/results/native-web-transfer-20261018/HOST.md), [матрица RFC 6455](WEBSOCKET_RFC6455_AUDIT.md) и [TLS/WSS](WEBSOCKET_TLS_PLAN.md): полный host TCP pipeline — по164 сценария, combined WSS — по14. [Четыре GCC images](../tests/results/native-web-transfer-20261018/SDK.md) сохранены из чистого `6db5651a`. Полное соответствие на плате, ресурсы TLS/audio, две вкладки и медленный клиент требуют физической квалификации. |
| CYD-C3-08 | Программная часть выполнена | [Общий image sink](../idf/components/native_ota/include/native_ota_sink.h), остановка трёх audio owners, атомарная reboot reservation и capability-gated UI реализованы. [Host-квалификация](../tests/results/native-ota-transfer-20261018/HOST.md): CYD83/C3148 concurrent scenarios, реальный HTTP/HTTPS pipeline44 и целевые semantic mutants проходят с ASan/UBSan. [Четыре GCC images](../tests/results/native-ota-transfer-20261018/SDK.md) сохранены из чистого `ab1e4c6e` с прежними SDK настройками и core bindings. [Проект и входы кода](CYD_OTA_TRANSFER_DESIGN.md) описывает target/slot и timeout/cleanup. Физическая OTA/data/power-loss приёмка отдельно; автоматический rollback требует отдельного bootloader baseline. |
| CYD-C3-09 | Программная часть выполнена | Общий checked SNTP backend, coherent C3 time settings, CYD timezone/SNTP service и private Wi-Fi desired store реализованы. [Host-квалификация](../tests/results/native-runtime-transfer-20261018/HOST.md): время46 и Wi-Fi124 реальных HTTP/TLS сценария, полный clang-tidy CYD46/C364 units без tool errors. CYD startup/IP hooks сохраняют affinity; пустой файл не подключает старый профиль драйвера. HTTP/UI keep/set/revision и три legacy imports используют bounded I/O; публичное скачивание паролей закрыто. [Проект времени](CYD_TIME_TRANSFER_DESIGN.md) и [Wi-Fi](CYD_WIFI_PRIVACY_TRANSFER_DESIGN.md) перечисляют входы. [Четыре GCC images](../tests/results/native-runtime-transfer-20261018/SDK.md) сохранены из чистого `8bcacfe9`: core bindings прежние, единственная CYD SDK разница — два SNTP servers, C3 config неизменна. [Runtime N0–N3](CYD_NETWORK_RUNTIME_TRANSFER_DESIGN.md) реализован: immutable boot cache до пяти профилей, постоянный owner, late reconnect/wrap/APSTA, checked snapshot и RSSI validity/age. [Квалификация](../tests/results/cyd-network-runtime-20261019/README.md): owner44 + четыре controls, loader/netif/rollback/HTTP/WS/UI и Xtensa component compile проходят. [N4 power](../tests/results/network-power-transfer-20261019/README.md) подключён к обеим платформам: generation intent, bounded owner-only set_ps, actual audio/maintenance/retry и полный clang-tidy CYD50/C365 проходят без новых предупреждений. [Пять полных GCC exports](../tests/results/network-power-transfer-20261019/SDK.md) из чистого `489c9f819` сохранены, включая CYD custom FLAC PDM; target/OTA/configuration/affinity проверены. [N5 hostname/AP timeout](../tests/results/cyd-network-settings-20261020/README.md) подключён к runtime, HTTP и WebUI: 82 owner случая/12 controls, HTTP80/7, UI48/14, actual NVS/reboot и полный Clang52/86warnings/0errors проходят. Настройки сохраняются без разрыва online соединения; optional AP timeout default0 использует checked immediate reboot lease без durable pending запроса. [Шесть полных CYD exports](../tests/results/cyd-network-settings-20261020/SDK.md) из чистого `195cd3b0e` проверены для vendor/custom FLAC и всех трёх backend; конфигурации и core bindings сохранены. Физическая AP/client/DHCP/reboot проверка остаётся. |
| CYD-C3-10 | Программная часть выполнена | Gain рассчитывается один раз на packet; [общий normalizer](../tests/results/cyd-normalizer-20261018/README.md) подключён ко всем трём backend через owner-only DSP без изменения input PCM. [Итоговая квалификация](../tests/results/cyd-c3-format-dsp-20261018/README.md): HTTP controls, golden PCM, reset/layout/EOF и полный lint проходят. [PCM 8/16/24/32 и resampler](../tests/results/cyd-startup-pcm-web-20261018/HOST.md) квалифицированы: до 1359 сценариев/backend, исправлены PDM rate-tail и DAC priming/short writes. [Новые SDK images](../tests/results/native-warning-fixes-20261018/SDK.md) сохранены; PDM DSP/layout symbols — 555 B DRAM, soft-limit LUT — 1170 B flash (без linker padding). Физическая приёмка остаётся. |
| CYD-C3-11 | Исключён | Перенос дисплея, рендеринга, физических controls и других аппаратных функций C3 не входит в задачу по уточнению пользователя. |
| CYD-C3-12 | В работе | [Optional custom FLAC runtime](CYD_FLAC_TRANSFER_DESIGN.md) подключён к actual CYD decoder task; vendor остаётся default. [Квалификация](../tests/results/cyd-flac-runtime-20261019/README.md): 520 exact PCM сравнений, 4304 metadata-prefix случая, 24 allocation failure/reopen и lifecycle/maintenance controls, actual Xtensa custom/vendor component compile. Source depth и PCM16 разделены; workspace освобождается до maintenance ACK. [Полный custom PDM app export](../tests/results/network-power-transfer-20261019/SDK.md) проверен по ELF/image/configuration; текущий host rerun повторяет 520 точных PCM сравнений. [Все три custom backend exports](../tests/results/cyd-network-settings-20261020/SDK.md) собраны и проверены; [QEMU adapter/core](../tests/results/cyd-flac-qemu-20261020/README.md) проходит 520 byte-exact PCM случаев и 48 guards на SDK6.0.2/Xtensa/core0+1; [Actual CYD task QEMU](../tests/results/cyd-flac-task-qemu-20261020/README.md) проходит три public-API случая: ordered EOF/exact PCM, Stop/reopen и three-owner maintenance/resume; пять реальных decoder/client cleanup, исходные cores/priorities/stacks. OOM/backpressure/target semantic controls, production watchdog/ресурсы и физический vendor/custom A/B остаются. |
| CYD-C3-13 | В работе | [Освобождение GET TX-буфера](CYD_MEMORY_TRANSFER_DESIGN.md) подключено через проверяемый build-local overlay SDK6.0.2. Host SDK17/8, actual open_stream62/6, CMake9 и whole Xtensa compile проходят. Число 4096 — configured capacity, не измеренная экономия heap. [Освобождение IDLE slots при отказе TLS allocation](CYD_INPUT_RECLAIM_DESIGN.md) реализовано отдельной default-off опцией: binding после READY, SMP pin/retirement и фиксированный бюджет повторов. Host21/17, startup12/4, CMake8 и полный Clang54/86warnings/0errors проходят без новых предупреждений. [Actual SDK/QEMU](../tests/results/cyd-input-reclaim-qemu-20261020/README.md) проходит пять сценариев и четыре exact controls: реальный calloc NULL/recovery, health hook, оба ядра, retirement/refill и timer ISR. [Семь production exports](../tests/results/cyd-input-reclaim-20261020/SDK.md) из чистого `a1b9d5a1` проверены для vendor/custom FLAC × три выхода и disabled PDM control; ELF allocator/free, OTA и прежние task bindings подтверждены. [Аудит TLS reserve/MPI](../tests/results/cyd-tls-reserve-mpi-audit-20261020/README.md) завершён. [Ранняя MPI](CYD_EARLY_MPI_DESIGN.md) подключена default-off в `959f35486`: canonical startup, реальные SDK locks/heap, оба ядра и exact controls проходят; [архив проверок](../tests/results/cyd-early-mpi-20261020/README.md) сохранён. [Семь полных MPI exports](../tests/results/cyd-early-mpi-sdk-20261020/README.md) из чистого `1190aebce` также проверены: vendor/custom × три выхода и disabled PDM, actual first-call/allocator/free/config/OTA; минимальный запас OTA — 224912 B. [Статический TLS RX reserve](CYD_MEMORY_TRANSFER_DESIGN.md) также подключён default-off: host, 12 SDK/QEMU вариантов, [семь GCC exports и шесть Clang-профилей](../tests/results/cyd-tls-static-rx-sdk-20261020/README.md) проходят. Radio boot/board, TLS traffic, IRAM/stack и физические измерения CYD остаются. |
| CYD-C3-14 | В работе | [Постоянный public raw decoder](CYD_VORBIS_DECODER_DESIGN.md) реализует replace/measure/process/info/reset/clear. [Host и actual SDK/QEMU](../tests/results/vorbis-decoder-20261028/CHECKPOINT.md) проходят все31/434/738560 PCM-байт к обоим эталонам при bound2/all14; host/ESP32/C3 побайтно совпадают. Host закрывает1480 allocation refusals/recovery, capacity, reset, replacement, lifetime и typed numeric routes; native — полный corpus после actual 8355840-byte malloc отказа и его cleanup. Production backend не переключён. [Общие certified gain/wider численные маршруты](CYD_VORBIS_CERTIFIED_GAIN_REMAINING.md), Ogg/container metadata handoff, actual audio-task integration/resources и физическая приёмка остаются. AAC compact owners требуют собственной Xtensa ABI/PCM/OOM/lifetime адаптации; прежние отложенные scopes сохраняются. |
| CYD-C3-15 | В работе | [Production wrapper](../idf/esp32-cyd2usb-native/PRODUCTION_BUILD.md) и верифицированный экспорт реализованы; 42 host tests проходят, 1 symlink case пропущен. Изолированный sdkconfig сохраняет аппаратные настройки и обеспечивает минимум два SNTP servers. [Шесть CYD сборок после N5](../tests/results/cyd-network-settings-20261020/SDK.md) проверены: vendor/custom FLAC во всех трёх backend; [C3 N4 image](../tests/results/network-power-transfer-20261019/SDK.md) сохраняет отдельный baseline; конфигурации, image/ELF/compiler hashes, task affinity и запас OTA сохранены. Фактические DWARF размеры структур и static symbols зафиксированы без заявления об экономии heap. Единая физическая приёмка HTTP/HTTPS/кодеки/WebUI/OTA/длительное воспроизведение каждого backend ещё впереди. |

Дополнительная [проверка status keys](../tests/results/ws-status-key-20261023/README.md)
устранила зависимость публикации WebSocket от padding структуры в CYD и C3.
CYD: 59 host-групп; C3: 42 сценария/7 controls и focused GCC/Clang обеих целей проходят;
это исправление переносимости, физическая приёмка и остальные gates ниже остаются.

## Что осталось по переносу

Актуальная очередь после квалификации 28 октября:

- Vorbis: подключить [проверенный постоянный raw decoder](CYD_VORBIS_DECODER_DESIGN.md)
  к Ogg/container metadata и actual audio task CYD. Нужна явная передача granule/EOS,
  проверка трёх заголовков/конца и смены logical stream, остановки/повторного открытия,
  очередей и ресурсов полного radio/TLS приложения. HTTP EOF не является packet EOS.
  Базовое воспроизведение Ogg/Vorbis уже работает; новый путь пока не выбран production.
  [Квалификация raw owner](../tests/results/vorbis-decoder-20261028/CHECKPOINT.md)
  уже проходит все31 исходных потока/434 пакета/738560 PCM-байт на host и в actual
  SDK/QEMU ESP32/core1 и C3/core0: ошибка максимум2 к обоим эталонам при прежнем
  допуске2, все14 relations, host/native PCM побайтно равен. История/granule/EOS,
  транзакционный output/capacity, replace/reset/clear и1480 host OOM ordinal
  refusals/recovery реализованы. Эти public raw gates больше не открыты.
  Законная конфигурация255 каналов/8192 проходит host с большим аллокатором;
  на обоих MCU actual malloc корректно отказывает8355840-байтному запросу и
  освобождает candidate, после чего декодируется весь исходный корпус.
  Это не утверждение, что большой профиль помещается на MCU.
  [Certified floor0 gain и полный wider/precision путь](CYD_VORBIS_CERTIFIED_GAIN_REMAINING.md)
  через IMDCT/историю ещё нужны: обычный finite corpus не доказывает весь диапазон.
  Один допустимый finite gain требует минимум1572 бита для целой части показателя;
  замена int64 на int128 и per-bin double exponent не закрывают эту задачу.
  [Независимый directed MPFR-эталон](../tools/codec_benchmark/vorbis_floor0_mpfr_oracle.md)
  уже проверен на8202 точных наборах с сохранением всех447 packet-frame identities;
  два tiny finite случая получают совпадающие arbitrary-length integer floors
  после уточнения до4096 bits. Это host oracle для следующих правок, не реализация
  certified gain на MCU и не доказательство универсальной достаточности4096 bits.
  Для MCU добавлена [основа направленной арифметики](../idf/components/native_vorbis_bigfloat/README.md):
  точные dyadic inputs, проверяемые add/sub/mul/div/sqrt и arbitrary-length floor.
  [Host-проверка](../tests/results/vorbis-bigfloat-20261028/CHECKPOINT.md) проходит
  701 сценарий в обоих limb models и 1288 отказов памяти с восстановлением.
  [LX6/RV32 source profiles](../tests/results/vorbis-bigfloat-20261028/SOURCE_PROFILES.md)
  также проходят; это компиляция, а не выполнение новой арифметики в SDK/QEMU.
  Направленные pi/ln2/sine bounds, сам gain и его продолжение через синтез ещё нужны.
  Комментарии/порядок заголовков и транспортная семантика остаются вне raw API.
  Native resource/performance полного radio/TLS/TFT и physical также открыты.
  Все прежние отложенные пункты сохраняются; повторно они не запускались.
- AAC compact owners: собственная Xtensa ABI/PCM/OOM/lifetime адаптация;
  прежний private owner-view сохраняет пометку «отложен».
- FLAC: target OOM/backpressure/semantic controls и физическое vendor/custom A/B.
- Память: radio/TLS traffic, фактический heap/IRAM/stack и выбор default-off
  опций по измерениям. Общая физическая приёмка всех трёх выходов остаётся
  отдельной работой после подключения платы; программные проверки продолжаются.

**Уточнение после [аудита всех веток](CYD_OGG_VORBIS_BRANCH_AUDIT_20261025.md):**
базовое воспроизведение Ogg/Vorbis уже есть в `main` и CYD/C3 runtime с августа.
Его обеспечивает существующий декодер Espressif. Ниже остаются исправления
надёжности/соответствия формату и подключение дополнительного repair, а не
первичное добавление поддержки Vorbis. По принятому пользователем подходу
готовый upstream-декодер уже проверен с минимальной адаптацией:
[Xiph на ESP32](../tests/results/vorbis-xiph-20261025/CHECKPOINT.md) проходит
все исходные 31 случая, 434 пакета и 738560 PCM байт с побитным совпадением;
максимальная ошибка 0 при прежнем допуске 2, все 14 отношений проходят.
Новый алгоритм IMDCT не нужен: [широкий адаптер](CYD_VORBIS_TRANSFORM_DESIGN.md)
повторно использует неизменённые тела Xiph. [Отдельный binary64 вход](CYD_VORBIS_NORMALIZED_IMDCT_DESIGN.md)
теперь позволяет подключать другие представления спектра без искусственного
floor1 product; это ещё не floor0 gain или полный синтез. Следующие программные проверки —
общая обработка allocation/recovery, packet-sized scratch и оставшиеся format/range
границы. [Отдельный ресурсный порт](../tests/results/vorbis-xiph-resources-20261025/CHECKPOINT.md)
уже исправляет optional realloc arena и переносит book-init scratch в проверяемый
heap. ASan/UBSan и ESP32 QEMU проходят 11 arena-сценариев, 200864 book-проверки,
124754 bit-пробы и все исходные 31 случая с max0; dense4096 помещается в worker
со стеком 16 КБ. Общий OOM и стеки всех decode-путей ещё не квалифицированы;
два partition-sized массива residue0 теперь убраны в
[следующем исправлении](../tests/results/vorbis-xiph-residue-20261026/CHECKPOINT.md).
Однопроходное размещение значений сохраняет полные VQ-слова при nominal EOP
по спецификации, без новых аллокаций. ASan/UBSan и ESP32 QEMU проходят 3997
новых сценариев; partition4096/dim1 работает в том же worker16КБ, собственный
compiler frame32B static. Все прежние31 PCM остаются побитно точными.
В [разборе заголовков](../tests/results/vorbis-xiph-headers-20261026/CHECKPOINT.md)
проверены все прямые выделения памяти: ASan/UBSan и ESP32 QEMU проходят 1598
сценариев отказа, очистки, повторного открытия и классификации ошибок.
Проверены оба floor, все три residue, несколько comment strings и zero-size
book allocations; все прежние31 PCM остаются точными. Ошибка памяти возвращает
`OV_EFAULT`, ошибочный заголовок — прежний `OV_EBADHEADER`; public ABI сохранён.
[DSP init кандидат](../tests/results/vorbis-xiph-dsp-20261026/CHECKPOINT.md)
проверяет частичные MDCT/floor/residue/PCM allocations; ASan/UBSan проходят 3584
сценария и все прежние31 PCM с max0. ESP32 SDK сборка завершилась, но QEMU gate
остаётся NONPASS: длинная серия тестов вызвала watchdog на IDLE1.
[Доработка scheduling теста отложена](CYD_XIPH_DSP_TARGET_DEFERRED_20261026.md)
после автоматического отказа; повторный target/PCM gate и Clang ещё нужны.
Независимые [comment query/add API](../tests/results/vorbis-xiph-comments-20261026/CHECKPOINT.md)
теперь проверены отдельно: ASan/UBSan и metadata-only ESP32 QEMU проходят399
сценариев. Поиск тегов не выделяет память, добавление сохраняет прежнее состояние
при отказе любой из трёх аллокаций; указатели существующих значений и binary
metadata сохранены. DSP/декодер в этом target не исполняются; отложенный DSP gate
не возобновлялся и его NONPASS остаётся.
[Packet allocation/recovery](../tests/results/vorbis-xiph-packets-20261026/CHECKPOINT.md)
теперь проходит отдельные host ASan/UBSan проверки: 41086 сценариев, включая
27875 исходного корпуса, 13188 synthetic/no-work и 23 arena. Все прежние31 PCM
сохраняют max0 и все14 relations; возврат только прежнего кода выделения PCM
воспроизводит UBSan NULL store. Arena growth сохраняет прежние owners и данные
при отказе node/buffer, floor/residue передают required OOM до synthesis как
явное расширение OV_EFAULT; nominal EOP остаётся успешным. 48 прямых no-work
controls проверяют отсутствие scratch allocation attempts и сохранение armed
refusal. Clang всех25 library/fixture units: 308 предупреждений/0 ошибок,
диагностики сохранены. [Подготовка отдельного packet target отложена](CYD_XIPH_PACKET_TARGET_DEFERRED_20261026.md):
инструмент вернул «aborted before dispatch» без причины; проект не создан,
SDK/QEMU не запускались. Это не подтверждённый отказ по кибербезопасности.
[Channel-sized scratch](../tests/results/vorbis-xiph-channels-20261026/CHECKPOINT.md)
теперь использует локальные массивы на два канала: моно/стерео не добавляет
выделений в арене, более широкие mapping/residue0/1 bundles используют checked
block storage. Host ASan/UBSan проходит 47166 сценариев, все прежние 31 PCM и
14 relations остаются точными. Source-only Xtensa GCC подтверждает static
собственные frames 128/112 B вместо dynamic; это не stack high-water задачи
или полный SDK/runtime gate. Clang 25 units проходит с 316 warnings/0 errors;
новые восемь pointer/narrowing diagnostics разобраны с bounds channels 1–255.
General stack/heap и runtime с максимальными 255 каналами остаются открытыми.
[Широкая floor0 amplitude отложена](CYD_XIPH_FLOOR0_AMPLITUDE_DEFERRED_20261026.md):
read-only аудит подтвердил gaps 31–63, но подготовка тестов остановлена
автоматической проверкой с сообщением possible cybersecurity risk; новые файлы
не созданы, implementation не менялась.
[Unsigned rate API](CYD_XIPH_RATE_DESIGN.md) теперь сохраняет положительные
значения всего uint32 диапазона: на 32-bit long поле unsigned, на LP64 прежний
long; layout сохранён, source signedness явно расширена и требует matching
headers. Два checked16 reads не смешивают 0xffffffff с EOP; zero остаётся
invalid, signed bitrate hints неизменны. Host ASan/UBSan и независимый metadata-only
ESP32 SDK/QEMU проходят по 13492 сценария; все 12 C/C++ public entry orders
проверены на обеих платформах, native ABI32/struct32/alignment4/offset8 подтверждены.
Native metadata не исполняет setup/DSP/audio и не закрывает их deferred gates.
Host packet47166 сохраняет прежние31 PCM max0/14 relations; никаких clamp,
новых format caps или изменений аппаратных rate limits нет. Full-range encoder,
convenience library, native audio/runtime integration отдельно.
Независимый [аудит диапазона VQ](CYD_XIPH_VQ_RANGE_DESIGN.md) подтверждает
унаследованное ограничение показателя степени Xiph до −63…63. Среди 14 336
упакованных значений найдены 1 682 расхождения для точно представимых binary32
чисел. Проверка ASan/UBSan и сравнение 8 225 таблиц завершились; все 271 626
результатов существующего точного VQ-слоя совпали с целочисленной моделью.
Это подтверждает его пригодность для дальнейшего подключения, но не исправляет
Xiph и не квалифицирует весь декодер. Ограничение диапазона и обычное округление
float посчитаны отдельно; счётчики пересекаются. Табличные примеры с несколькими
записями не являются полными потоками Huffman.
[Checkpoint](../tests/results/vorbis-xiph-vq-range-20261026/CHECKPOINT.md) сохраняет
первый отказ компиляции, оба успешных захвата и Clang для трёх модулей:
25 предупреждений / 0 ошибок. Следующий шаг — владение исходными книгами
и выбор полного числового пути до преобразования в float; граница floor→IMDCT
остаётся открытой.
Следующий [компонент владения точным setup](CYD_VORBIS_SETUP_OWNER_DESIGN.md)
реализован отдельно от allocation-free парсера: сохраняет исходные VQ-поля,
активные sparse indexes и коэффициенты после освобождения заголовков. Замена
атомарна относительно отказа; прежние данные сохраняются при ошибке, а успешная
замена освобождает их исходным аллокатором. Host ASan/UBSan проходят 335 случаев,
все 31 исходные пары заголовков, 399 810 ошибок разбора и 2 982 allocation
refusals; Clang шести модулей — 0 предупреждений / 0 ошибок.
[SDK/QEMU подготовка не завершена](CYD_VORBIS_SETUP_OWNER_TARGET_DEFERRED_20261026.md):
запись контроллера дважды вернула `aborted before dispatch` без причины;
native случаев нет. Семь файлов первоначального прототипа сохранены в архиве,
но его subset без prefix sweeps не закрывает полный target gate. Подключение
владельца к декодеру и полная native проверка остаются открытыми.
Поверх него реализован [общий точный разбор аудиопакета](CYD_VORBIS_PACKET_FRAME_DESIGN.md):
mode/window → floor по каналам → residue по submap → обратный coupling.
Проверены 1 311 сценариев и все 434 исходных пакета: 411 520 точных слов residue,
2 769 affine-значений и 2 224 raw Y; 3 332 отказа ёмкости с восстановлением.
Окончание внутри floor обнуляет все каналы по спецификации; окончание внутри
residue сохраняет завершённые VQ-слова. Исходные floor-флаги не меняются из-за
coupling. Host ASan/UBSan проходят; C/C++ source-only GCC для LX6 и RV32IMC
также проходят. Это граница до умножения floor/IMDCT/PCM, а не готовый raw
decoder или native runtime gate. Выбор числового пути и подключение остаются.
Следующий [точный product floor1](CYD_VORBIS_FLOOR1_PRODUCT_DESIGN.md) также
реализован: неизменённая таблица Xiph умножается на широкий residue без
предварительного float-округления. [Host-квалификация](../tests/results/vorbis-floor1-product-20261026/CHECKPOINT.md)
проверяет 619 540 произведений для всех 256 коэффициентов и ширин 1–1087,
а интеграция — 1 313 пакетов, включая все 434 исходных, 1 750 каналов floor1
и 297 056 точных слов результата. Отсутствующий floor обнуляет канал даже
после coupling; тихий индекс0 остаётся ненулевым. ASan/UBSan проходят,
новый компонент Clang без предупреждений; C/C++ GCC LX6/RV32IMC компилируется.
Само [ядро floor1 scale проверено на SDK/QEMU обеих архитектур](../tests/results/vorbis-floor1-product-native-20261026/CHECKPOINT.md):
по 2 957 вызовов, 619 564 точных отсчёта, 11 817 093 слова и 713 отказов на
ESP32 и C3. Watchdog/IDLE проверки включены; числовые результаты и независимый
replay проходят. Исходные CLI завершились1 из-за ошибки финальной печати уже
после успешных SDK/QEMU; исправлено только выражение summary, исходные ошибки
сохранены. Это generic scale gate, не native проверка owner/frame или IMDCT.
Floor0 product, window/overlap/PCM, полная native квалификация и radio
integration остаются открытыми; прежние отложенные пункты этим не закрыты.
Для IMDCT реализован [адаптер существующего алгоритма Xiph](CYD_VORBIS_TRANSFORM_DESIGN.md):
вычислительные тела скопированы без изменения, используются double и отдельная
степень двойки. [Host-проверка](../tests/results/vorbis-transform-20261026/CHECKPOINT.md)
проходит 3 084 случая, 465 958 точных входных преобразований и 881 216 временных
отсчётов при прежней нормовой границе 5e-12. Проверены все восемь размеров блока,
1 750 прежних каналов floor1 и 266 исходных пакетов с floor1; остальные 168
исходных пакетов требуют floor0. Все 434 исходные модели сохранены. Это ещё
не полный PCM или native/runtime gate. C/C++ GCC LX6/RV32IMC проходит,
оба новых C модуля Clang0/0; пять предупреждений fixture относятся к проверке
собственных byte snapshots. Window/overlap, floor0 и подключение остаются.
Дальше — незавершённые native gates, общие stack/resource проверки,
floor0 amplitude/VQ range и runtime integration с unsigned rate API.
Новый кандидат пока не подключён к радио. Старые
NONPASS относятся к прежнему repair и не переобъявлены успешными. Это также
не закрывает deferred scopes, physical acceptance или полное соответствие
стандарту за пределами измеренного корпуса.

- **Этап 13, память:** завершить radio-boot/board и сетевую приёмку
  статического CYD TLS RX reserve, завершить radio-boot/board квалификацию [ранней MPI](CYD_EARLY_MPI_DESIGN.md)
  и подобрать heap/IRAM/стеки по CYD. MPI уже подключена default-off и прошла
  проверки actual startup/SDK mutex/OOM/двух ядер, а также
  [семь полных application exports](../tests/results/cyd-early-mpi-sdk-20261020/README.md);
  physical benefit ещё открыт. Первый кандидат reserve прошёл локальные
  host/config проверки, но не подключён к firmware: ревью выявило неполный
  контракт pointer/numeric `user_data`. [Новая привязка конфигураций](CYD_MEMORY_TRANSFER_DESIGN.md)
  уже подключена к радио отдельной default-off опцией и не использует application
  userdata. [Текущие host-результаты](../tests/results/cyd-tls-static-rx-host-20261020/README.md)
  сохраняют unit, полную service-матрицу и CMake-проверки;
  [Actual SDK/QEMU](../tests/results/cyd-tls-static-rx-qemu-20261020/README.md)
  проходит полную матрицу из 12 вариантов. [Семь production exports и шесть
  Clang-профилей](../tests/results/cyd-tls-static-rx-sdk-20261020/README.md)
  также проверены; radio-boot/board, TLS traffic и физическая польза ещё впереди.
  Старый pointer prototype и первая registry target-матрица завершились nonpass;
  их target gate остаётся nonpass. Новая полная матрица прошла после исправления
  ошибочного тестового отождествления pre-handshake MFL getter и размера RX storage.
  Освобождение HTTP GET TX и lifetime-safe reclaim уже реализованы;
  семь production exports reclaim проверены, физический выигрыш ещё не измерен.
  [Запуск двух полных PDM образов в QEMU](../tests/results/cyd-production-radio-boot-20261020/README.md)
  завершился nonpass в SDK SPI flash init до `app_main`: reserve ON/OFF дают
  одинаковый QIE/QIO отказ. Ранняя MPI и radio startup этим не квалифицированы;
  исходные образы и конфигурации сохранены, аппаратная приёмка остаётся.
- **Этап 14, Vorbis/Ogg:** выбрать и подключить проверенный путь к actual audio
  task после необходимых lifecycle, allocation failure/reopen, concurrent scopes
  и format/conformance проверок. Готовый Xiph теперь основной кандидат на
  дальнейшую квалификацию; [прежний ESP32 bridge](CYD_VORBIS_TRANSFER_DESIGN.md)
  остаётся изолированной альтернативой со своими callback ABI/Ogg EOF/reset gates.
  Deferred scopes этим не возобновляются. Для прежнего repair Raw PCM
  и undersized retries проверены отдельно; [raw8192 regression](../tests/results/cyd-vorbis-format-20261020/README.md)
  снимает только одно rate/block ограничение: 340 точных пакетных сравнений,
  четыре malformed-header controls и точный old-guard отказ. Дополнительная
  [матрица размеров блоков](../tests/results/cyd-vorbis-block-matrix-20261020/README.md)
  проходит на Xtensa: 108 случаев, 5472 пакетных сравнения и 32 543 616 точных
  PCM байт; все 36 пар размеров и переходы short/long сохранены.
  [Unsigned-rate regression](../tests/results/cyd-vorbis-uint32-rate-20261020/README.md)
  исправляет signed32 отказ двух допустимых значений: 16 частот, 1088 пар пакетов,
  4 362 240 точных PCM байт; отдельный optional-cap прогон и оба восстановления
  старых guards проходят. [Независимая C3/RV32 проверка](../tests/results/c3-vorbis-uint32-rate-20261020/README.md)
  той же находки и исправления также проходит все пять отдельных кампаний.
  [Генераторы](../tests/vorbis_format_corpus/README.md) воспроизводят 17
  books/floor0/residue0 случаев и ещё 29 mono/stereo/mapping и map2-регрессий;
  [новые 149 файлов](../tests/results/vorbis-more-generators-20261020/README.md)
  совпадают с исходными побайтно. Их target PCM и независимое численное сравнение
  ещё не квалифицированы целиком. [Setup checkpoint](../tests/results/cyd-vorbis-map2-20261020/CHECKPOINT.md)
  исправляет чтение всех исходных lookup2 строк и mapped-single-entry leaves.
  Полный корпус25 проходит raw open/decode/close:350 пакетов/623360 PCM байт.
  Исходные книги8, single/twin случаи4 и контрольные floor1/residue0 случаи3
  отличаются от Xiph не более чем на1 PCM16 LSB. Широкие D16 lookup2 случаи4
  пока дают max65535 и нарушают sparse/dense PCM равенство; причина не установлена.
  Все шесть floor0 случаев также нарушают заранее выбранный проектный предел2:
  максимумы even6:40664/1649/40664; odd5:65535 во всех трёх парах блоков.
  Полный численный результат и подгруппа books16 остаются NONPASS.
  [Отдельный Xtensa unit-тест](../tests/results/cyd-vorbis-owned-book-20261023/CHECKPOINT.md)
  подтверждает публикацию16 наших книг и61 векторную пробу, включая обе
  wide sparse/dense пары, без vendor-декодера.
  [Шесть эквивалентных floor0 представлений](../tests/results/cyd-vorbis-floor0-equivalent-20261023/CHECKPOINT.md)
  с ненулевым минимумом прошли полный raw31 прогон:434 пакета/738560 PCM байт.
  Их target PCM совпадает с исходными шестью, прежние25 результатов сохранены;
  полное численное сравнение31 остаётся NONPASS с прежним пределом2.
  Отдельный расчёт публичной формулы нашёл147 положительных ideal-dB значений
  среди2688 активных bins; integer Tremor/PCM этим расчётом не проверялись.
  [Собственный floor0 unit](../tests/results/cyd-vorbis-owned-floor0-20261023/CHECKPOINT.md)
  подтвердил все12 публикаций/6 пар/32 events, точные66/74 bits и normal free.
  [Публичная integer-кривая](../tests/results/cyd-vorbis-public-floor0-curve-20261023/CHECKPOINT.md)
  проверена отдельно на Xtensa:6 случаев/84 пакета/168 вызовов/58368 bins.
  Явно помеченная PORTED копия Tremor содержит только три изменения
  переносимости C; исходник и обе прежние неудачные попытки сохранены.
  Отдельный математический расчёт2688 активных bins остаётся диагностикой;
  подтверждённой причины широкого/floor0 PCM пока нет.
  [C3/RV32 checkpoint](../tests/results/c3-vorbis-map2-20261023/CHECKPOINT.md)
  подтверждает ту же setup правку на SDK6.1/core0: все25 случаев/350 пакетов
  декодируются; исходный отказ case6 воспроизведён до исправления.
  Полное численное сравнение C3 также завершено и остаётся NONPASS:
  те же wide4/floor0×6 нарушают предел2, остальные15 имеют max1.
  [Эквивалентные wide lookup2 ширины2/9/16](../tests/results/cyd-vorbis-wide-width-20261023/CHECKPOINT.md)
  проверены отдельно:12 случаев/168 пакетов/337920 PCM байт. Все12 имеют
  max65535; все4 target width-группы и6 sparse/dense пар нарушают равенство,
  Xiph подтверждает все10 relations. Исходные4 PCM совпадают с прежним25.
  Одна лишь смена ширины эту ошибку не устраняет; общий wide формат не квалифицирован.
  [Дополнительные singleton-регрессии](../tests/results/cyd-vorbis-more-singletons-20261023/CHECKPOINT.md)
  проходят полный raw8 прогон:112 пакетов/225280 PCM байт. Sparse lookup2 D4
  sequence0/1 и D16 sequence0, dense/sparse map1 D16 sequence0 имеют max1;
  все три D16 sequence1 дают max65535. Полное численное сравнение8 — NONPASS,
  хотя обе equal triples и все4 sequence-difference пары проходят на CYD/Xiph.
  [Исходные4/preferred-zero4 на CYD](../tests/results/cyd-vorbis-singleton-zero-bit-20261023/CHECKPOINT.md)
  теперь проверены полным raw8 прогоном:112 пакетов/225280 PCM байт. Все4 target
  и4 Xiph пары совпадают побайтно. Численное сравнение12 доступных эталонов
  остаётся NONPASS: sequence0 max1, sequence1 max65535; смена кодового бита
  ошибку не устраняет. Native принимает новые4, исходные4 по-прежнему отклоняет.
  [Полный mono/stereo/mapping21 checkpoint](../tests/results/cyd-vorbis-mono-mapping-20261023/CHECKPOINT.md)
  проходит на Xtensa/core1:294 пакета/464640 PCM байт, все42 сравнения с двумя
  эталонами имеют max1 при прежнем проектном пределе2. Проверены9 mono/12 stereo
  случаев, девять частот, coupling, два submap и residue2. Это конечный корпус,
  а не полная квалификация стандарта. Остальные gaps: численная корректность
  D16 sequence1/floor0/wide и прочие форматы.
  [Проверки floor1 X-позиций](../tests/results/vorbis-floor1-positions-20261024/README.md)
  исправлены на CYD и C3. Выявленная затем численная ошибка трёх допустимых
  случаев с короткой X-границей 1/2/8 устранена отдельным
  [floor1 renderer](../tests/results/vorbis-floor1-render-20261024/README.md):
  две конечные матрицы по восемь допустимых случаев на каждой архитектуре
  дают max1 относительно Xiph при прежнем проектном пределе2.
  Возврат только старого вычисления хвоста в отдельном образе воспроизводит
  все исходные PCM и три ошибки до65535. Старый NONPASS сохранён;
  реализация внутри vendor из этого функционального контроля не выводится.
  [Public raw registry](../tests/results/vorbis-registered-raw-20261024/README.md)
  дополнительно проверяет generic open/process/get_info/close на CYD и C3:
  по14 циклов регистрации,112 пакетов/225280 PCM байт и312 повторных отказов
  малому выходному буферу. Checked open/decode выбираются через public ops;
  весь PCM имеет max1 относительно Xiph. Следующий
  [public raw reset checkpoint](../tests/results/vorbis-raw-reset-20261024/README.md)
  проверяет реальное повторное использование handle: по 72 reset, 656 обработок
  пакетов и 336 отказов малому буферу на CYD/C3. Все повторные PCM совпадают
  побайтно с baseline, независимо сравнённым с Xiph при max1.
  Полные G1/G3/G6 открыты; bridge в radio не подключён.
  [Public raw-open OOM](../tests/results/vorbis-raw-open-oom-20261024/README.md)
  исправляет потерю `MEM_LACK` в header parser на обеих архитектурах:
  по560 отказов/полных восстановлений, четыре nested пары и два task-сценария
  проходят. Полные allocation/lifetime/SMP gates остаются.
  [Полный current-source31 прогон](../tests/results/vorbis-current-format31-20261024/CHECKPOINT.md)
  теперь повторён с текущим floor1 renderer:434 пакета/738560 PCM байт,
  все31 вектора побайтно равны прежним. Численный итог остаётся NONPASS:
  15 случаев max1, wide4 и floor0×12 нарушают предел2; target12/14 relations.
  [Следующий floor0 шаг](CYD_VORBIS_FLOOR0_REMAINING.md) требует сохранения
  точности и диапазона всей цепочки, а не отдельной подгонки inverse2.
  [Точный lookup1 root](../tests/results/vorbis-quantvals-20261025/CHECKPOINT.md)
  исправляет отдельное переполнение степеней в обоих setup: host по35975
  значений под ASan/UBSan в native-long/int32 профилях; SDK/QEMU по2179
  точных граничных значений на Xtensa/core1 и RV32/core0. Весь setup и native
  ABI assertions компилируются; это не повторная квалификация PCM/G6.
  [Собственная численная основа floor0](../tests/results/vorbis-floor0-numeric-20261025/CHECKPOINT.md)
  реализована отдельным компонентом: 60541 host-операция под ASan/UBSan,
  независимый Decimal120 oracle и по327 native coefficient/gain случаев.
  [Расчёт из исходных LSP-углов](../tests/results/vorbis-floor0-angles-20261025/CHECKPOINT.md)
  также реализован: 2376 host-случаев и по200 SDK/QEMU, отдельные точные
  phase checks и независимый Decimal oracle проходят. [Широкий путь](VORBIS_WIDE_NUMERIC_DESIGN.md)
  [Quantization/VQ/LSP слой](../tests/results/vorbis-quantization-20261025/CHECKPOINT.md)
  сохраняет исходные packed fields и точные affine значения; 6572 host-случая,
  по200 native случаев и отдельное сравнение всех значений проходят.
  [Полный codebook/Huffman слой](../tests/results/vorbis-codebook-20261025/CHECKPOINT.md)
  связывает исходные setup descriptors и audio words с точными VQ/LSP:
  382 host-сценария под ASan/UBSan и 400 native сравнений проходят.
  [Полный setup и начало аудиопакета](../tests/results/vorbis-setup-20261025/CHECKPOINT.md)
  также реализованы: 300 host-сценариев, 60 API controls и 400 native сравнений,
  включая все таблицы и getters, проходят. Исходные raw headers отдельно
  проверены на host, прежние PCM этим не переквалифицированы.
  [Floor0/floor1 packets](../tests/results/vorbis-floor-packet-20261025/CHECKPOINT.md)
  и [точные residue0/1/2 с inverse coupling](../tests/results/vorbis-residue-20261025/CHECKPOINT.md)
  также реализованы и проверены как отдельные компоненты. Широкий путь требует
  сборки полного frame decoder, применения floor0, window/overlap и public raw integration; точное
  применение floor1 координатором frame квалифицировано на host. Его generic
  scale-ядро теперь проверено на SDK/QEMU ESP32 и C3; owner/frame native gate
  остаётся отдельным. Компонент
  IMDCT повторно использует тела Xiph с binary64 и прошёл host/source-profile gates;
  полная native/resource/PCM проверка пока не завершена. Компонент
  не подключён к production и не переквалифицирует прежний PCM NONPASS.
  [Public owned-book baseline](../tests/results/cyd-vorbis-public-book-consumer-baseline-20261023/CHECKPOINT.md)
  сохранён с воспроизводимой standalone проверкой:36 публикаций/365 точных
  Xtensa векторов; host331 точный вектор и34 UBSan NONPASS остаются отдельно.
  [Public consumer zero guards отложены](CYD_PUBLIC_BOOK_ZERO_GUARD_DEFERRED_20261023.md):
  автоматическая проверка остановила подготовку отдельной
  правки; ноль guarded runtime случаев квалифицировано, обход не предпринимался.
  [Ogg target-расширение отложено](CYD_VORBIS_OGG_DEFERRED_20261020.md) после
  автоматической проверки безопасности; ноль новых runtime случаев квалифицировано.
  Затем полный Clang, три backend exports и физическая приёмка.
- **Этап 14, AAC:** отдельно адаптировать compact owners под Xtensa, проверить
  ABI, OOM/lifetime и точное PCM.
  Ранее остановленный автоматической проверкой пункт
  AAC private owner-view остаётся отложенным; ограничение не обходилось.
- **Этап 12, FLAC:** дополнительные target OOM/backpressure/semantic controls
  после прошедших трёх actual-task QEMU случаев, watchdog/ресурсы и физический
  vendor/custom A/B. Сам custom decoder уже подключён и собран для трёх выходов.
  [Расширение target-тестов временно отложено](CYD_FLAC_TARGET_ERRORS_DEFERRED_20261020.md):
  саб-агента остановила автоматическая проверка безопасности; новые случаи
  не квалифицированы и непроверенные изменения в firmware не подключены.
- **Этапы 00/05/15, аппаратура:** единая проверка сети HTTP/HTTPS, WebUI/OTA,
  DMA/IRQ, CPU/heap/stack, watchdog и длительного воспроизведения каждого выхода.
  По указанию пользователя плата пока не подключена: аппаратная приёмка ожидает
  подключения, работы без физического устройства продолжаются. Эти критерии
  остаются открытыми; дополнительный запрос IP/аудиовыхода сейчас не требуется.

Дисплей, распиновка, USB/reset и другие специфичные функции C3 исключены.
Stream остаётся на core0, decode/output на core1 с прежними приоритетами и
стеками. Программная телеметрия завершена; аппаратные измерения ещё впереди.

## Карта функций и мест в коде

Замечания об отсутствующих функциях ниже описывают исходный CYD `42bc7bd4`.
Текущее состояние переноса отражено в очереди и журнале выполнения.

### Аудиопоток и память

| Фича C3 | Донор | Место подключения CYD и условия |
| --- | --- | --- |
| Generation, очистка stale packets, раннее освобождение несовместимого decoder до TLS | [audio_service.c](../idf/esp32c3-oled-native/main/audio_service.c), [decoder_resources.h](../idf/esp32c3-oled-native/main/decoder_resources.h) | [audio_service.c](../idf/esp32-cyd2usb-native/main/audio_service.c): stream/decoder/output tasks. Сейчас output не сверяет generation, Stop только повышает счётчик. |
| Причины EOF/error и ordered PCM completion | [audio_completion.h](../idf/esp32c3-oled-native/main/audio_completion.h), [native_state.c](../idf/esp32c3-oled-native/main/native_state.c) | [audio_service.c](../idf/esp32-cyd2usb-native/main/audio_service.c), [native_state.c](../idf/esp32-cyd2usb-native/main/native_state.c). Сейчас PCM terminal marker отсутствует, decoder остаётся открытым после EOF. |
| Частичные HTTP reads, EAGAIN, TLS failure и half-close | [stream_http_reader.c](../idf/esp32c3-oled-native/main/stream_http_reader.c), [tls_stream_eof.c](../idf/esp32c3-oled-native/main/tls_stream_eof.c) | CYD `stream_task`; SDK wrappers сверить с pinned IDF 6.0.2. Сохранить аутентифицированные partial bytes перед закрытием TLS. |
| ICY stripping и ограниченный UTF-8 title | [icy_title.c](../idf/esp32c3-oled-native/main/icy_title.c), [audio_service.c](../idf/esp32c3-oled-native/main/audio_service.c) | CYD `stream_task` и `native_state`; сейчас запрашивается `Icy-MetaData: 0`. |
| Fragmented signature probe без MP3 fallback | [stream_probe.h](../idf/esp32c3-oled-native/main/stream_probe.h), [stream_tags.h](../idf/esp32c3-oled-native/main/stream_tags.h) | Заменить CYD `codec_from_signature` по первому chunk; MIME использовать как hint. |
| MP3/ADTS frame walker, ID3v1/v2, подтверждение следующего кадра | [stream_frames.h](../idf/esp32c3-oled-native/main/stream_frames.h), [stream_confirm.h](../idf/esp32c3-oled-native/main/stream_confirm.h) | Перед CYD decoder; сохранить free-format MP3 и FLAC/Ogg passthrough. |
| Bounded startup replay, continuous confirmation и codec drain | [stream_start.h](../idf/esp32c3-oled-native/main/stream_start.h), [stream_staging.h](../idf/esp32c3-oled-native/main/stream_staging.h), [stream_encoded_router.h](../idf/esp32c3-oled-native/main/stream_encoded_router.h) | CYD encoded producer/consumer после queue adapters. Drain заканчивает сегмент, а не станцию. |
| Queue acquire/commit/cancel/reclaim и независимый control capacity | [adaptive_input.c](../idf/esp32c3-oled-native/main/adaptive_input.c), [adaptive_input.h](../idf/esp32c3-oled-native/main/adaptive_input.h) | CYD `s_encoded`; оставить одного producer/consumer и явно проверить SMP ownership. |
| Minimum input pool, FLAC expansion, bounded prefill | [tls_input_reserve.c](../idf/esp32c3-oled-native/main/tls_input_reserve.c), [audio_service.c](../idf/esp32c3-oled-native/main/audio_service.c) | Выбрать по объёму CYD TLS/TFT/DMA. 1000 ms ожидания не гарантирует секунду данных в RAM. |
| Дополнение частичного READY tail | [adaptive_input.c](../idf/esp32c3-oled-native/main/adaptive_input.c), [stream_encoded_router.h](../idf/esp32c3-oled-native/main/stream_encoded_router.h), [отчёт](ESP32C3_INPUT_TAIL_20261015.md) | Только после leases: не трогать READING/единственный queued/control packet; сохранять generation/codec/EOF barriers. |
| PCM workspace и frame alignment | [decoder_pcm.h](../idf/esp32c3-oled-native/main/decoder_pcm.h), [audio_service.c](../idf/esp32c3-oled-native/main/audio_service.c) | CYD `send_pcm` и realloc output; не разрезать stereo 24-bit frame границей пакета. |
| Отдельная регистрация decoder с проверкой ошибок | [decoder_registration.c](../idf/esp32c3-oled-native/main/decoder_registration.c) | CYD `decoder_task`: проверить register/open и rollback, сохранить optional codecs. |

### WebUI и управление радио

| Фича C3 | Донор | Место подключения CYD и условия |
| --- | --- | --- |
| Станции, playlist offset index, выбор/Next/Prev, последнее состояние | [radio_control.c](../idf/esp32c3-oled-native/main/radio_control.c) | Новый общий radio core поверх CYD [audio_service.h](../idf/esp32-cyd2usb-native/main/audio_service.h); без загрузки всего CSV в RAM. |
| Runtime settings и capabilities | [runtime_settings.c](../idf/esp32c3-oled-native/main/runtime_settings.c), [display_settings.c](../idf/esp32c3-oled-native/main/display_settings.c) | CYD [native_state.h](../idf/esp32-cyd2usb-native/main/native_state.h), [web_service.c](../idf/esp32-cyd2usb-native/main/web_service.c). Скрыть ещё не реализованные SD/EQ/touch поля. |
| `/ws`, initial snapshot, heartbeat, event-driven status, metadata/bitrate/buffer | [websocket_service.c](../idf/esp32c3-oled-native/main/websocket_service.c) | CYD `web_service_start`, общий snapshot и bounded JSON escaping. Совместимость `/api/native/*` сохранить. |
| Dynamic pages, recovery page и Arduino-free templates | [web_service.c](../idf/esp32c3-oled-native/main/web_service.c), [web_pages_bridge.cpp](../idf/esp32c3-oled-native/main/web_pages_bridge.cpp) | CYD [embedded native page](../idf/esp32-cyd2usb-native/main/web_pages.cpp) обслуживает также `/webboard` и `/emergency`; controls/forms включаются по capabilities. |
| Async static workers, gzip и socket budget | [web_service.c](../idf/esp32c3-oled-native/main/web_service.c), [проверки](../tests/esp32c3-web-static-workers.test.js) | CYD [web_static.c](../idf/esp32-cyd2usb-native/main/web_static.c): два workers и два queued requests. Пять HTTP clients, два WS; для HTTPS выбран отдельный бюджет три clients в одной server instance. Реальная RAM/latency ещё измеряется. |
| Streaming multipart uploads, temp/backup, playlist index rollback | [web_upload.c](../idf/esp32c3-oled-native/main/web_upload.c), [web_file_form.h](../idf/esp32c3-oled-native/main/web_file_form.h), [web_multipart.h](../idf/esp32c3-oled-native/main/web_multipart.h) | CYD новые upload routes; ограничить RAM размером chunk, сохранить Wi-Fi/CSV/assets при ошибке. |
| Firmware OTA, target/size validation, abort и maintenance | [web_ota.c](../idf/esp32c3-oled-native/main/web_ota.c), [ota_upload.c](../idf/esp32c3-oled-native/main/ota_upload.c) | Новый общий [native_ota_sink](../idf/components/native_ota/native_ota_sink.c), CYD [audio_service.h](../idf/esp32-cyd2usb-native/main/audio_service.h), [web_reboot.h](../idf/esp32-cyd2usb-native/main/web_reboot.h), [partitions.csv](../idf/esp32-cyd2usb-native/partitions.csv). ESP32 chip0 и slot0x1B0000; не менять partition table и bootloader автоматически. |
| Wi-Fi profiles, RSSI, reconnect и активное/idle power policy | [network_service.c](../idf/esp32c3-oled-native/main/network_service.c) | CYD [network_service.c](../idf/esp32-cyd2usb-native/main/network_service.c). Проверить AP fallback и подключение после поздней потери сети. |
| Timezone, SNTP retry и clock state | [time_service.c](../idf/esp32c3-oled-native/main/time_service.c) | [Проект переноса](CYD_TIME_TRANSFER_DESIGN.md): два SNTP сервера, persisted fixed offset, clock/sync state и безопасная lifetime строк; исправить выявленную donor stop/write гонку. Не зависеть от OLED/deep sleep. |

### DSP и декодеры

| Фича C3 | Донор | Место подключения CYD и условия |
| --- | --- | --- |
| Normalizer/limiter и кэш gains | [native_audio_normalizer.cpp](../idf/esp32c3-oled-native/main/native_audio_normalizer.cpp), [AudioNormalizer.cpp](../yoRadio/src/audioI2S/AudioNormalizer.cpp), [native_audio_output.c](../idf/esp32c3-oled-native/main/native_audio_output.c) | CYD [native_audio_output.c](../idf/esp32-cyd2usb-native/main/native_audio_output.c): сейчас gain вычисляется на каждый sample; обновлять параметры и DSP только через output owner. |
| PCM flush на EOF, reset на generation и rate change | [native_audio_output.c](../idf/esp32c3-oled-native/main/native_audio_output.c), [native_audio_output.h](../idf/esp32c3-oled-native/main/native_audio_output.h) | CYD PDM имеет накопленный staging tail; отдельная реализация для continuous/legacy DAC. Проверить переходы с одинаковой частотой. |
| Custom FLAC: bounded input, bit depths, stereo decorrelation, LPC/Rice hot loops | [custom_flac](../idf/esp32c3-oled-native/components/custom_flac), [flac_decoder.cpp](../yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp), [отчёт](ESP32C3_FLAC_HOTLOOPS_20261008.md) | CYD сейчас регистрирует Espressif FLAC. Portable C кандидат; ускорение RISC-V не доказывает ускорение LX6. |
| Full-rate AAC, late/resumed SBR, metadata и input framing | [native_aac_decoder.c](../idf/esp32c3-oled-native/main/native_aac_decoder.c), [aac_fill_parser.c](../idf/esp32c3-oled-native/main/aac_fill_parser.c) | Сначала публичный decoder API и ADTS framing; внутренние hooks изолировать до Xtensa аудита. |
| Compact AAC SBR owner, PC19, scoped low-QMF, smoothing/high history | [aac_compact_owner.c](../idf/esp32c3-oled-native/main/aac_compact_owner.c), [aac_sbr_abi.h](../idf/esp32c3-oled-native/main/aac_sbr_abi.h), [aac_high_history.c](../idf/esp32c3-oled-native/main/aac_high_history.c), [aac_smoothing_history.c](../idf/esp32c3-oled-native/main/aac_smoothing_history.c) | Это private RV32 ABI, не готовый ESP32 компонент. C3 owner 55128 → 32744 B; экономия 22384 B относится к C3, пока не к CYD. |
| Vorbis/Ogg initialization/teardown, OOM и output repair | [vorbis_repair](../idf/esp32c3-oled-native/main/vorbis_repair), [vorbis_repair_abi.h](../idf/esp32c3-oled-native/main/vorbis_repair_abi.h), [CMake hash guards](../idf/esp32c3-oled-native/main/CMakeLists.txt) | Та же идея fault injection применима, но C3 offsets/hashes не использовать для `lib/esp32`. Сверить обе vendor archives. |

### Измерения и воспроизводимость

| Фича C3 | Донор | Место подключения CYD и условия |
| --- | --- | --- |
| Quiet health и накопительные ошибки | [app_main.c](../idf/esp32c3-oled-native/main/app_main.c), [native_state.h](../idf/esp32c3-oled-native/main/native_state.h) | CYD status/новый health endpoint; атомарные SMP snapshots. |
| Task CPU, stack high water и heap/largest block | [cpu_profiler.c](../idf/esp32c3-oled-native/main/cpu_profiler.c) | Учесть `IDLE0`/`IDLE1`, общий runtime denominator и migration. IRQ masking на одном core не защищает данные от другого. |
| Pipeline/DMA waits, input occupancy и delivery trace | [audio_pipeline_probe.h](../idf/esp32c3-oled-native/main/audio_pipeline_probe.h), [native_i2s_generator.c](../idf/esp32c3-oled-native/main/native_i2s_generator.c), [tls_path_profile.c](../idf/esp32c3-oled-native/main/tls_path_profile.c) | Отделять steady playback от idle/Start/Stop; completion queue overflow не равен числу слышимых щелчков. |
| TLS full-record reserve, early MPI lock, release HTTP request storage | [tls_large_reserve.c](../idf/esp32c3-oled-native/main/tls_large_reserve.c), [tls_input_reserve.c](../idf/esp32c3-oled-native/main/tls_input_reserve.c), [http_request_buffer.h](../idf/esp32c3-oled-native/main/http_request_buffer.h) | Только после карты CYD heap и проверки IDF symbols; сохранить 16 КиБ TLS RX. |
| Wi-Fi IRAM, allocator placement, static/dynamic RX/TX и stack balance | [C3 defaults](../idf/esp32c3-oled-native/sdkconfig.defaults), [tested profile](../idf/esp32c3-oled-native/sdkconfig.radio-tested.defaults) | Не копировать whole sdkconfig. У CYD TFT/SPI DMA, два ядра и другие latency требования; A/B отдельными overlays. |
| Production wrapper применяет профиль и к старому sdkconfig, экспортирует app | [build-production.ps1](../idf/esp32c3-oled-native/build-production.ps1) | CYD [build.ps1](../idf/esp32-cyd2usb-native/build.ps1); `firmware/development/<variant>/app.bin`, versioned releases неизменяемы. |
| Fixtures/HTTP server, sanitizers, QEMU, qualification/OTA restore | [audio_test_server](../tools/audio_test_server), [esp32c3_tests](../tools/esp32c3_tests), [testing guide](ESP32C3_TESTING.md) | Общие media fixtures переиспользовать; endpoints, cores, image identity, backend и hardware acceptance адаптировать для CYD. |

## Что не включать автоматически

- По уточнению пользователя аппаратно-зависимые функции вообще не входят
  в перенос: другой дисплей/рендеринг, GPIO, физические controls, native USB,
  encoder/BOOT drivers, deep sleep/RTC. Общие команды и состояние радио
  остаются частью программного переноса; железо CYD сохраняется.
- RISC-V assembler, `aac_late_sbr_bridge.S`, C3 archive patch offsets,
  cycle-counter/cache/RTC TCP memory hooks — отдельные target implementations.
- Двухлинейный stereo PDM GPIO10/GPIO3, fractional clock/FIR коэффициенты C3,
  72×40 OLED и native USB — другая аппаратная схема. CYD остаётся mono GPIO26,
  TFT и CH340; DAC backends сохраняются.
- Deep sleep с OLED wake stub, внешний RTC crystal GPIO0/1 и overclock —
  отдельные аппаратные проекты, не оптимизация текущего CYD playback.
- Private decoder arena 96/100 КиБ — эксперимент, в production C3 выключен;
  [сохранены неуспешные allocation/FLAC испытания](ESP32C3_ARENA_FLAC_DMA_20261013.md).
  Сначала исправить lifetime и измерить системный heap CYD.
- Flash Auto Suspend/агрессивный IRAM profile, byte-GHASH и уменьшение TLS
  records не становятся default по результатам чужой платы.
- Диагностические счётчики и захват payload не включаются целиком в quiet build.

## Порядок проверки каждого изменения

1. Host-проверка реальных production функций: EOF, cancellation, OOM,
   byte-exact routing и PCM; ASan/UBSan и concurrency где применимо.
2. Сборка CYD на закреплённом IDF 6.0.2. Для общих модулей — регрессия C3.
   SDK upgrade отдельным изменением, чтобы не смешивать причины регрессии.
3. Сохранить успешный тестовый image в `firmware/development/<variant>/app.bin`.
   Зафиксировать hash, sdkconfig, backend, flash/RAM и исходный commit.
4. Физическая приёмка отдельно для PDM, continuous DAC и legacy DAC:
   HTTP/HTTPS, MP3/AAC-LC/HE/HEv2/FLAC/Vorbis/Opus, Next/Stop/EOF, сеть,
   WebUI/OTA, восстановление heap и аналоговое прослушивание/loopback.
   Host pass и build pass не отмечают этот пункт как выполненный.

## Журнал выполнения

- Начат OTA08: общий image-byte sink проверен на обеих pinned layouts
  (по1529 fault groups, пять обнаруженных semantic mutants); отдельная проверка
  настоящего SDK checksum/hash продолжается. Checked pause трёх CYD backends
  проходит35 host scenarios и два ownership mutants. Reboot reservation
  проверена на actual C3/CYD API с конкурентными admission/request races.
  Native UI проходит22 JS проверки, включая progress передачи, ошибки и отсутствие
  автоматического повторного flash. Это ещё не завершённый OTA: требуются реальные
  owner cascade ACK, безопасный async cleanup, C3 maintenance и сквозная интеграция.

- WebUI/RFC/TLS batch завершён программно: [production SDK qualification](../tests/results/native-web-transfer-20261018/SDK.md)
  содержит CYD PDM/continuous/legacy и C3 из чистого `6db5651a`, SHA app/ELF,
  реальные OTA margins, разрешённые config deltas и target symbol sizes.
  `s_clients` занимает CYD384/C33200 bytes; host layout не выдаётся за RAM цели.
  Прежние audio core affinity/priority и аппаратные профили сохранены. Новых GCC
  warnings нет; у legacy остаются три прежних deprecated APLL notices.
  Физическое соответствие/ресурсы остаются открыты; следующий перенос — OTA08.

- Полная GCC15 сборка C3 обнаружила `maybe-uninitialized` в общем multipart
  helper: успешный bool `found` не связывался анализатором с записанными output
  ranges. Выходы теперь инициализируются явно, результат определяется самим
  указателем. [Отдельная повторная квалификация](../tests/results/native-web-transfer-20261018/HOST_GCC.md):
  actual GCC components, ASan/UBSan parser и полные upload handlers обеих плат
  проходят; focused clang-tidy не добавил диагностик. Предупреждения не отключены.

- Дополнительный аудит донора C3: wildcard `/data/*` в
  [static_handler](../idf/esp32c3-oled-native/main/web_service.c) через
  [recoverable open](../idf/esp32c3-oled-native/main/web_upload.c) выдаёт также
  Wi-Fi CSV, `.bak` и временные имена. Текущий UI намеренно загружает этот файл:
  [script.js.gz](../yoRadio/data/www/script.js.gz), `handleWiFiData/getWiFi`
  (decompressed lines 583/595), settings/AP/export (760/801/840);
  [OTA snapshot](../tools/esp32c3_tests/ota.py) и
  [web-memory restore](../tools/esp32c3_tests/web_memory.py) тоже зависят от него.
  Этап 09 должен менять контракт целиком: SSID-only metadata, write-only password
  с явным «не изменять», отдельный приватный export/backup, затем allowlist
  публичных playlist paths и тесты литеральных/backup/temp путей. Простое удаление
  маршрута сейчас ломает эти потребители. TLS credentials хранятся в отдельном
  NVS namespace и никогда не размещаются в SPIFFS.

- Новый перенос WebUI проверяется по [зафиксированным исходникам и отчётам](../tests/results/native-web-transfer-20261018/HOST.md).
  Общий message core поддерживает фрагменты и interleaved controls, строгий
  HTTPD overlay проверяет обязательные заголовки/длины/маски и исправляет
  folded headers, пустой Content-Length и отложенное закрытие повторно
  использованной session. Общий transport через публичный ESP-TLS API проверен
  реальными закреплёнными TLS библиотеками и независимым CA/SAN validating client:
  по8 TLS сценариев и по14 combined HTTPD/application/WSS сценариев на SDK.
  Обычный GET `/ws` получает HTTP400 до создания WS context. Это пока не отметка
  полного соответствия: финальные images и аппаратные ресурсы ещё проверяются.
  Допустимые ограничения документируются по RFC: полное text message до
  96 байт на CYD и 255 на C3, сборка до пяти секунд; расширения и subprotocol
  не согласовываются, binary radio commands закрываются с 1003.

- Дополнение пользователя: WebSocket должен поддерживать базовый RFC 6455
  полностью в части обязательных требований. Опциональные расширения допускается
  не реализовывать; лимиты памяти/размера/времени должны соответствовать разрешениям
  RFC. Этап 07 не считается завершённым по одному happy-path WebUI: нужны handshake,
  framing/masking/lengths, UTF-8, фрагменты и control interleaving, Close и проверка
  некорректных последовательностей на обеих версиях SDK. Найден реальный пробел
  прежнего harness: SDK пропускает URI handler при upgrade, так что transport
  overrides могли установиться только после первого кадра/periodic work. Новая
  регрессия воспроизводит отсутствие callback на `d13706c2`; текущий host checkpoint
  проходит 41 группу, но полная протокольная квалификация ещё впереди.

- [SDK-квалификация startup/WebUI/PCM и warning fixes](../tests/results/native-warning-fixes-20261018/SDK.md)
  завершена из чистого `3b8e5d2f`: CYD PDM/continuous/legacy и C3 production
  images сохранены с manifest/config/logs; app/ELF SHA и OTA capacity проверены.
  C3 tested profile идентичен предыдущему; CYD меняет только WebUI/WS настройки.
  Прежние affinity/priority сохранены и проверены: radio_stream core 0/priority 3,
  audio_decode core 1/priority 5, audio_output core 1/priority 6.
  GCC не выдаёт предупреждений для C3/PDM/continuous; три legacy notices относятся
  к deprecated APLL API исходного драйвера IDF 5.5.4, при `use_apll=false`.
  SDK не патчился; физическая приёмка и оставшиеся этапы переноса открыты.

- По запросу пользователя разобраны наиболее опасные предупреждения обеих целей.
  [Отчёт с исходными сбоями и регрессиями](../tests/results/native-warning-fixes-20261018/HOST.md):
  исправлены деление на ноль/отрицательный сдвиг Vorbis, потеря Wi-Fi/upload
  файлов при rename failure, переполнение малого filename buffer и lifetime
  async HTTP session донора C3. Чтение полных Wi-Fi строк и обработка read error
  проверены также в CYD; signed PCM/FLAC arithmetic сделана явной. Полный lint:
  C3 50 units/77 warnings/0 errors (20 устранено, новых нет), CYD 24/8/0.
  Добавлены отрицательные контроли, ASan/UBSan и 360 exact FLAC PCM сравнений.
  AAC owner-view warning остаётся открытым: автоматическая проверка содержимого
  остановила саб-агента до завершения тестов; непроверенный diff сохранён
  [отдельно](../tests/results/native-warning-fixes-20261018/deferred/README.md)
  и не включён в firmware. Повторять после 32-bit layout/reset и PCM проверок;
  private RV32 offsets в CYD не переносить. SDK новых исправлений и физическая
  приёмка отмечаются отдельно.

- [Новый блок startup/PCM/WebUI](../tests/results/cyd-startup-pcm-web-20261018/HOST.md)
  прошёл host/ASan/UBSan: проверенная регистрация decoder, готовность/gate трёх
  задач и rollback/retry закрывают init-failure хвост этапа 01 (228 сценариев).
  PCM 8/16/24/32, rate-tail, DAC retry/short writes проверены во всех трёх backend.
  WebSocket/embedded native UI/capabilities/static workers проверены отдельно;
  bounded uploads этапа 07 ещё не реализованы. Новые web units проходят lint без
  предупреждений, полный CYD — 24 units/8 warnings/0 errors; C3 — 50/97/0.
  По новой просьбе пользователя начат приоритетный аудит опасных предупреждений
  до следующих production builds. Физическая приёмка и SDK новых правок впереди.

- Уточнения следующих переносов по read-only аудиту: этап 08 требует maintenance
  ownership и ожидания quiescence всех трёх audio tasks; асинхронный Stop донора
  этого не доказывает. CYD OTA slots имеют 0x1B0000 bytes, project
  `yoradio_cyd2usb_native`, chip ESP32; размеры/идентичность C3 не копировать.
  Portable custom FLAC этапа 12 поддерживает source 4–24 bit, mono/stereo и
  выдаёт PCM16 через единственного owner; vendor CYD поддерживает также 32-bit,
  поэтому нужна явная vendor/custom selection/fallback без потери capability.
  Отдельно проверить донор C3 WebSocket short I/O: его IDF 6.1, как и CYD 6.0.2,
  считает положительную короткую запись кадра успешной. CYD уже имеет bounded
  public session overrides, перенос аналогичной гарантии в C3 пока открыт.

- [Интегрированная квалификация format/bitrate/DSP](../tests/results/cyd-c3-format-dsp-20261018/README.md)
  завершена для программного блока: CYD PDM/continuous/legacy `e1b1539a` и C3
  `8c302697` собраны, сохранены с manifest/config и проверены полным lint.
  Нормализованные SDK профили совпадают с предыдущими. Отложенный пункт успешно
  возобновлён; историческая пометка о пропуске ниже сохранена. Платы не прошивались.
  На этом этапе дополнительный хвост раннего аудита оставался открытым: проверить CYD
  decoder registration errors и rollback/readiness при частичном startup failure;
  текущие lifecycle тесты доказывают runtime ownership, а не все init failure paths.

- Возобновлённый format/bitrate дополнен [исправлением донора C3](../tests/results/c3-bitrate-state-20261018/README.md):
  source priority и generation проверяются одним state transaction, убран общий
  readiness bool, исправлены zero-epoch windows и округление. Восемь групп и
  существующие state/command/полная format suite проходят. Параллельные независимые
  изменения перенесли normalizer/HTTP settings и production wrapper; каждое
  зафиксировано отдельно. Общая SDK/lint квалификация новых правок — следующий шаг.

- По повторной просьбе пользователя восстановлен блок format/bitrate.
  [Исполняемые регрессии](../tests/results/cyd-stream-format-20261018/README.md)
  проверяют точный PCM format, изменения layout, 51 HTTP-сценарий, bounded
  измеритель аудиобитрейта после ICY и одновременные state publications.
  SDK/lint новых правок и физическая приёмка пока не завершены.

- Ранее по просьбе пользователя незавершённое расширение format/bitrate и его
  дополнительные проверки отложены после остановки выполнения проверкой
  безопасности. Все десять изменённых файлов были сохранены в Git stash
  `a4bdcf84e2d396d860a5e676ae2f9f4cdf50b155`
  (`Deferred CYD format and bitrate work per user request`); исходная база —
  `ce1ae2e0`. Это историческая отметка о пропуске; текущий статус возобновления
  указан выше. Остальные открытые этапы сохраняются.

- [Дополнительная pending-регрессия](../tests/results/radio-pending-20261018/README.md)
  расширена до фактической stream task и выявила сброс нового флага перед
  HTTP open. Обе цели используют atomic-per-generation connecting transition
  под state mutex; old callbacks не восстанавливают подключение после PCM/Stop.
  Все шесть CYD lifecycle ветвей, HTTP, C3 commands и общий controller проходят.

- [Stale cache регрессия](../tests/results/playlist-cache-20261018/README.md)
  воспроизвела принятие старых offsets после сдвига CSV-строк. Общий bounded
  iterator теперь сверяет весь raw index с CSV при boot, сохраняя прямой seek
  при выборе станции и пропуская лишнюю flash-перезапись для верного cache.
  Проверены NUL, длинный URL без truncation, неверная граница/диапазон offsets,
  malformed index и overflow 65536 rows. Если reindex не удался после изменения
  CSV, несовпадающий каталог не используется; старые файлы сохранены для recovery.

- Начало CYD-C3-06: общий `native_storage` проверен 356 сценариями отказов /
  rollback / прерываний между файловыми операциями. Аудит исходного C3
  воспроизвёл потерю index.dat при ошибке rename и лишнюю станцию из continuation
  слишком длинной CSV-строки. [Исполняемые регрессии](../tests/results/playlist-index-20261018/README.md)
  проверяют реальные parser/index/lookup и сохранение старого файла/count
  при ошибках write/flush/close/rename. Номер станции и формат raw offset index
  сохранены; whole CSV в RAM не загружается.
- Radio core вынесен в [общую реализацию](../idf/components/native_storage/include/radio_control_impl.h),
  CYD подключён через собственные state/audio interfaces. [Host-отчёты](../tests/results/cyd-c3-radio-20261018/README.md)
  проверяют настоящий controller с обеими state implementations, boot/NVS,
  500 concurrent commands, границы index и HTTP API, а также все шесть CYD
  lifecycle ветвей и C3 Play/Stop/Resume. Новый pending-флаг позволяет Toggle
  отменять подключение до PCM. Ошибка NVS SmartStart откатывает runtime setting;
  до исправления отрицательный тест воспроизвёл несогласованное состояние.

- Дополнительная проверка донора C3 обнаружила borrowed `pcTaskName` после
  возобновления scheduler и повторное использование TaskHandle без task number.
  [Новые регрессии](../tests/results/c3-profiler-20261018/README.md) сначала
  воспроизводят UAF/неверный CPU, затем проходят с ASan/UBSan для counters 32/64.
  Имена копируются при остановленном scheduler только на single-core C3;
  SMP-стратегия CYD использует handles/numbers без borrowed имён.

- 2026-10-18: создан отдельный worktree, выполнено сравнение исходников.
  Donor host tests `run-esp32c3-stream-probe.py`,
  `run-esp32c3-stream-frames.py`, `run-stream-start.py` с tail coalescing и
  queued consumer, `run-stream-encoded-router.py` проходят с ASan/UBSan.
  Последний startup прогон без `--corpus` выполняет unit/concurrency cases,
  его `corpus: 0` не означает повторную приёмку всего media corpus.
- `run-esp32c3-eof.py` выявил устаревшее извлечение source-фрагмента
  (`substring not found`); это неисправность harness до компиляции,
  а не наблюдённый сбой EOF firmware. Harness обновлён на реальный
  `finish_stream_audio`, добавлены текущие RTOS/probe stubs и запуск WSL на
  Windows. ASan/UBSan: PASS для delayed HE-AAC PCM, ordered EOF, error,
  empty stream, stale completion, cancellation и codec drain.
- Уточнение пользователя: аппаратно-зависимые функции C3 исключены;
  CYD-C3-11 снят с очереди, драйверы и схема CYD сохраняются.
- По запросу пользователя подключены clang-tidy и Clang Static Analyzer:
  [полные отчёты C3 и CYD, процедура и очередь замечаний](NATIVE_STATIC_ANALYSIS.md).
  Повторять полный анализ после существенных правок. Первые прогоны завершены:
  CYD 11 translation units / 29 warning instances, C3 49 / 504, без parse/tool
  errors. Warning не считается подтверждённым дефектом до разбора.
- CYD-C3-01: generation защищает очередь команд, state и обе очереди данных;
  decoder закрывается без нового input, до следующего TLS open. PCM completion
  следует после отложенных frames; PDM tail flush/discard выполняет output owner.
  [Host-тест](../tests/run-cyd-lifecycle.py) проверяет Espressif/Helix/minimp3
  ветви с codec mocks, OOM/error/Stop/EOF, frame alignment, queue cancellation,
  переключение при пробуждении output и 2000 конкурентных Play/Stop с настоящими
  host mutex. Это проверка lifecycle, не PCM vendor codecs и не физический SMP/DMA.
- По уточнению пользователя непокрытые случаи дополняются исполняемыми
  регрессионными тестами. Уже добавлены отдельные конкурентные и cancellation
  случаи; существующие 57 source/WebUI/settings проверок проходят.
- Финальные images CYD-C3-01 и базовый PDM сохранены с manifest/sdkconfig:
  [результаты и ссылки на firmware](../tests/results/cyd-c3-lifecycle-20261018/README.md).
  PDM baseline и итоговый PDM имеют одинаковые нормализованные SDK настройки.
  Сборка, sanitizer tests и lint завершены; на физическую плату эти images
  в рамках этого этапа не устанавливались.
- CYD-C3-02: [probe](../idf/components/native_stream/include/stream_probe.h),
  [ID3](../idf/components/native_stream/include/stream_tags.h) и
  [ICY](../idf/components/native_stream/icy_title.c) теперь имеют одну
  переносимую реализацию. C3 wrappers сохраняют существующие пути сборки и
  host-тестов. Probe/frame corpus и 47 C3/ICY проверок проходят после извлечения.
- CYD-C3-02: CYD использует общий fragmented probe без MIME/MP3 fallback,
  удаляет ICY до decode и публикует generation-safe title. Общий JSON writer
  экранирует control bytes и заменяет повреждённый UTF-8. HTTP status/redirects
  ограничены одним 10-секундным startup deadline, body timeout — 250 ms.
  Fatal TLS закрывается после сохранения partial bytes; scoped adapter сохраняет
  отличие raw TLS EOF от close_notify, не меняя dynamic-buffer SDK wrapper.
  [42 сценария stream task](../tests/run-cyd-stream.py),
  [ICY/JSON bounds/fuzz](../tests/run-native-stream-body.py), corpus обеих целей,
  lifecycle и по 93 сценария реального SDK HTTP/TLS reader на C3/CYD проходят
  с ASan/UBSan. [Отчёты](../tests/results/cyd-c3-stream-20261018/README.md)
  сохраняют границы эмуляции. Подтверждение соседних кадров относится к этапу 03.
- Проверка исходного C3 выявила гонку ICY title: переключение после проверки
  generation, но до state mutex позволяло старому callback записать title,
  затем стереть уже новое название повторной проверкой. Проверка generation
  перенесена под mutex; отдельная очистка после Stop удалена, поскольку её
  уже выполняет `native_state_begin_stream`. Новый
  [исполняемый тест](../tests/run-c3-state-concurrency.py) сначала воспроизвёл
  дефект, затем прошёл с исправлением: принудительное вытеснение перед mutex,
  20000 конкурентных обновлений, stale clear, bounds и wrap generation.
  [Отчёт и отрицательный контроль](../tests/results/c3-state-concurrency-20261018/README.md).
- CYD-C3-03/04: общие frame/confirmation/staging/router и leased queue
  подключены к CYD. Startup удерживает максимум четыре unpublished slots и
  10 bytes lookahead; отдельный control node обеспечивает replay без пятого
  slot и ordered EOF/drain. Queue budget — восемь slots, guaranteed floor —
  четыре; C3 TLS reserve/reclaim policy на CYD пока не подключена.
  Producer отменяется и по generation, и по output/decoder failure.
  Provisional codec на CYD не означает audio_running до первого PCM.
  [Отчёты](../tests/results/cyd-c3-frames-20261018/README.md): 34 corpus cases
  каждой цели, false headers, max ADTS, 127 truncated ID3 tails, ordered
  MP3/AAC/MP3 переходы, 60000 concurrent queue packets и 20000 random staging
  operations проходят с ASan/UBSan. Lifecycle теперь проверяет шесть
  комбинаций queue/codec API и отдельный drain без промежуточного PCM flush.
- Дополнительный аудит исходного C3 воспроизвёл потерю нового Play: один
  caller повышал generation и блокировался на state mutex, второй публиковал
  новую команду, затем первый перезаписывал очередь старой. Полный transaction
  Play/Stop/Resume и benchmark fixture теперь сериализуется control mutex.
  [Регрессионный тест](../tests/run-c3-command-concurrency.py) сначала упал
  на старом коде, затем прошёл: принудительное вытеснение, 2000 конкурентных
  команд, invalid arguments, queue failure и Resume recovery.
  [Отчёты](../tests/results/c3-command-concurrency-20261018/README.md).
- CYD-C3-04: добавлен ограниченный first-input prefill, выключенный по
  умолчанию. Он учитывает все data leases, отменяется при Stop/output failure,
  не повторяется после codec drain и пропускается для startup control replay.
  [Host-проверки](../tests/results/cyd-prefill-20261018/README.md) покрывают
  deadline, coarse tick, 64-bit clock, возврат READING lease после отмены,
  control bypass и шесть queue/codec ветвей. C3 timing-профиль не скопирован;
  Дополнительный CYD профиль 250 ms собран и сохранён; полный clang-tidy
  этого профиля завершён для 14 units: 11 warnings, 0 parse/tool errors.
  Физический A/B остаётся отдельной работой.
- CYD-C3-05: [health module](../idf/esp32-cyd2usb-native/main/native_health.c)
  использует DRAM portMUX для allocation callback и согласованных fault tuples,
  а не C3 single-core IRQ masking. Diagnostic sampler учитывает оба IDLE,
  отдельный denominator и lifetime task number; имена из SDK snapshot не
  разыменовываются после возможного удаления задачи. [Host-тесты](../tests/run-cyd-health.py)
  проходят для quiet/diagnostic32/diagnostic64: по 60000 событий каждого типа,
  concurrent snapshots, wrap, handle reuse, отсутствие снимка/IPC, startup OOM,
  worst-case JSON и все capacity bounds. Pipeline/HTTP wiring и реальная
  SDK-проверка ещё впереди; это не измерение CPU физической CYD.
- Health wiring: ошибки decoder записываются до cleanup, output configure /
  write / final flush имеют отдельные counters. GET не сбрасывает faults и не
  меняет state; input payload bytes исключают packet headers и control leases.
  Internal/DMA heap views пересекаются. Optional CPU/stack остаются `null` в
  quiet build; профилирование не добавляет задачу по умолчанию.
  [Интеграционные host-отчёты](../tests/results/cyd-health-integration-20261018/README.md).

- 2026-10-19, CYD-C3-09 N0–N3: заменён однопрофильный event-handler runtime
  на постоянного owner. Initial/manual cycle начинается с первого профиля,
  late outage — с последнего успешного, затем wrap. Один admitted manual cycle
  включает pending mailbox; APSTA сохраняется. Checked getter не отдаёт старый
  IP/RSSI при pending link event; WS/UI учитывают validity и отдельный AP state.
  [Frozen source/reports](../tests/results/cyd-network-runtime-20261019/README.md)
  фиксируют historical negatives отдельно от 44 текущих owner scenarios.
  Новая задача priority 2/core 0/stack 4096; прежние audio/display/bootstrap
  affinity и аппаратные настройки сохранены. N4/N5 остаются открыты.
- 2026-10-19, CYD-C3-12: optional custom FLAC интегрирован без переключения
  vendor default. [Доказательства](../tests/results/cyd-flac-runtime-20261019/README.md)
  связывают actual decoder/PCM/lifetime с shared core, включая source depth,
  metadata EOF, persistent OOM/reopen и concurrent maintenance cleanup до ACK.
  Component compile не считается полным application export или физической
  квалификацией; эти gates остаются в плане.

- 2026-10-19, CYD-C3-09 N4: в `bde1e645` перенесена generation-aware Wi-Fi power policy и исправлены обе воспроизведённые donor гонки old finish/new Play и old receive/Stop. [Frozen квалификация](../tests/results/network-power-transfer-20261019/README.md) связывает shared policy, actual C3/CYD audio, network owner, maintenance и API. Core/priority/stack привязки сохранены. N5 persisted precursor `6b2bbe1d` проверен отдельно (12 случаев, 7 controls); runtime/WebUI ещё не подключены.
- 2026-10-19, CYD-C3-09/12/15: [пять production images](../tests/results/network-power-transfer-20261019/SDK.md) сохранены из чистого `489c9f819`. Проверены полные app links, обе OTA slots, Xtensa/RISC-V image identity, конфигурации, compiler/ELF/evidence hashes и реальные DWARF размеры. Custom FLAC выбран только в отдельном PDM image; его текущий host rerun проходит 520 exact PCM сравнений. N5 wiring, остальные custom backend exports, QEMU и физические gates остаются открыты.

- 2026-10-20, CYD-C3-09 N5: `de1fa7a3a` добавил reserved immediate restart, `a7012415d` подключил hostname/AP timeout, persistence и WebUI. [Frozen квалификация](../tests/results/cyd-network-settings-20261020/README.md) сохраняет 82/12 owner, HTTP80/7, UI48/14, actual NVS и reboot arbitration обеих плат. Независимая проверка воспроизвела и закрыла stale timer-label после save/GET failure. Полный Clang52 прошёл с 86 warnings/0errors: пять новых low-risk diagnostics разобраны без suppression. N0–N5 программно реализованы; SDK новых настроек, физические gates и остальные этапы плана открыты.

- 2026-10-20, CYD-C3-09/12/15: [шесть чистых SDK exports](../tests/results/cyd-network-settings-20261020/SDK.md) из `195cd3b0e` закрывают build/export matrix vendor/custom FLAC × PDM/continuous/legacy. Проверены image/ELF/compiler/config/evidence hashes, обе OTA slots и прежние core/priority/stack. Actual DWARF owner936/snapshot160/settings25/runtime80 зафиксированы без заявления о свободном heap/HWM. Custom-path QEMU и физическая приёмка остаются открыты.
- 2026-10-20, проверка донора C3: `9cc619778` и `0f484bbc8` устраняют прямой AP timer restart, обходивший OTA reservation и игнорировавший late GOT_IP/сохранённый timeout0. [Квалификация исправления](../tests/results/c3-ap-timeout-20261020/README.md): 42 actual owner/settings случая, 8 semantic controls, три воспроизведённых дефекта исходного `1256de595`; reboot832/8 и существующие power/time/Wi-Fi/WS/bootstrap регрессии проходят с ASan/UBSan. Checked cancellation незавершённого connect требует нового полного интервала перед restart. Полный Clang C3: 65 units, 127 прежних warnings, 0 errors, 758 frozen inputs. Новые задачи и изменения core/priority/stack не добавлены; CYD не изменён. SDK export и физическая проверка этого donor repair отдельно.
- 2026-10-20, donor SDK export: [новая production C3 сборка](../tests/results/c3-ap-timeout-20261020/SDK.md) из чистого `e78b154da` сохранена отдельным вариантом `esp32c3-oled-native-ap-timeout`: app1542256 B, каждая OTA slot1900544 B, запас358288 B. RISC-V32/chip5, checksum/ELF/config/compiler и restart symbols проверены. SDK config полностью совпадает с N4; CYD source и прежние task/audio/hardware настройки сохранены. На плате не проверялось.

- 2026-10-20, CYD-C3-12: `0c27ae422` добавил воспроизводимый [Xtensa QEMU стенд](../tests/target/cyd_flac_qemu/README.md). [Frozen SDK execution](../tests/results/cyd-flac-qemu-20261020/README.md): 130 независимых FFmpeg PCM16 fixtures × четыре feed schedules = 520 точных сравнений в реальном core1 callback, ещё 48 guards; coordinator core0, heap poisoning/canaries и terminal exit0. Production decoder/component bytes сохранены. Независимая проверка нашла и закрыла пропуск защиты output для каталогов PowerShell/custom Python; свежий полный прогон после исправления проходит. Это adapter/core gate; actual CYD audio-task pipeline, scoped OOM/target controls и физические измерения открыты.

- 2026-10-20, CYD-C3-05/12/13: подключены счётчики трёх output backend и
  completion-queue drop PDM, bounded HTTP snapshot и освобождение завершённого
  GET TX-буфера через hash-guarded IDF6.0.2 overlay. Host/ASan/UBSan и независимое
  ревью проходят; полный Clang53 сохраняет 86 warnings/0errors. Actual full-TU
  FLAC QEMU проходит три случая с реальными SDK owners и прежней affinity;
  OOM/backpressure и физическая квалификация остаются открыты.

- 2026-10-20, CYD-C3-05/13/15: [шесть новых GCC exports](../tests/results/cyd-output-telemetry-20261020/SDK.md) из чистого `0f2a37c89` сохранены для vendor/custom FLAC и всех трёх выходов. Проверены ELF/image/configuration/OTA; минимальный запас OTA — 225504 B. Final PDM callback/helper находятся в IRAM, counters/lock 64+8 B — в DRAM. Привязки задач и аппаратные настройки сохранены; единственная sdkconfig разница с соответствующим N5 image — HTTP TX release. Физические gates и остальные пункты 12/13/14 остаются открытыми.

- 2026-10-20, CYD-C3-13: [lifetime-safe reclaim](CYD_INPUT_RECLAIM_DESIGN.md)
  подключён после READY отдельной default-off опцией. Host21/17, startup12/4,
  CMake8, независимое production review и полный Clang54/86warnings/0errors
  проходят. Actual SDK/QEMU проходит пять случаев и четыре exact controls;
  independently проверены 246 текущих входов и allocator/free initializer words
  всех пяти ELF. Неуспешные подготовительные target-прогоны сохранены отдельно,
  их abort/GC/source-selection failures не засчитаны как detections. Production
  exports и физическая квалификация этого изменения остаются отдельными gates.

- 2026-10-20, CYD-C3-13/15: [семь production exports reclaim](../tests/results/cyd-input-reclaim-20261020/SDK.md)
  из чистого `a1b9d5a1` завершены: vendor/custom FLAC × PDM/continuous/legacy
  и disabled PDM control. Проверены реальные ELF allocator/free initializers,
  image/config/receipt/evidence hashes, обе OTA slots и прежние task bindings;
  независимое read-only ревью семи комплектов не нашло новых замечаний.
  Минимальный запас OTA — 225008 B, default reclaim остаётся выключенным.
  [Аудит следующих TLS reserve/MPI кандидатов](../tests/results/cyd-tls-reserve-mpi-audit-20261020/README.md)
  сохранён отдельно: static CYD RX отличается от dynamic C3; runtime MPI и
  реализация обоих кандидатов этим аудитом не проверялись. Этапы 12/13/14 и
  физическая приёмка остаются открытыми.

- 2026-10-20, CYD-C3-13: `959f35486` подключил раннюю инициализацию SDK MPI
  mutex первым вызовом `app_main`, default-off. [Архив `f05c139bc`](../tests/results/cyd-early-mpi-20261020/README.md)
  связывает canonical startup/board header, strict host sanitizers, actual SDK
  two-core execution, два omission controls и реальный void-API OOM. Независимое
  ревью закрыто. Полные radio app exports, boot и физическая польза остаются.
- 2026-10-20, CYD-C3-14: `cbb69fdad` добавил изолированный guarded Vorbis bridge
  без включения в radio runtime. [Финальные проверки](../tests/results/cyd-vorbis-bridge-20261020/README.md)
  после нормализации исходных файлов проходят: 535 raw packets, 2,112,000 bytes
  точного PCM, 1602 rejected retries, exact preflight control и 21 CMake profile.
  Полные G1–G8 ещё не закрыты: Ogg/OOM/SMP/format/callback/integration и ресурсы
  остаются. Это не полная поддержка стандарта и не измеренная экономия памяти.
- 2026-10-20, CYD-C3-12: дополнительная target error/backpressure квалификация
  [отложена после автоматической проверки безопасности](CYD_FLAC_TARGET_ERRORS_DEFERRED_20261020.md).
  Ноль новых сценариев квалифицировано; текущий custom FLAC и прежние успешные
  тесты сохраняются. Ограничение не обходилось.
- 2026-10-20, CYD-C3-13/15: [семь полных MPI application exports](../tests/results/cyd-early-mpi-sdk-20261020/README.md)
  из чистого `1190aebce` проверены для vendor/custom FLAC × три выхода и disabled
  PDM control. Actual ELF first-call/public MPI pair, allocator/free/reclaim,
  HTTP overlay, board/task settings, image/configuration/receipt hashes и OTA
  проверены; минимальный запас OTA — 224912 B. Firmware сохранены отдельным
  коммитом `43407ba0a`, immutable SDK archive — `f522067ed`. Offline verifier
  и staged-byte/LFS проверки проходят. Default MPI остаётся off; radio-boot,
  физическая польза, TLS reserve и остальные открытые этапы остаются.
- 2026-10-20, CYD-C3-14: [Ogg target-расширение отложено](CYD_VORBIS_OGG_DEFERRED_20261020.md)
  после автоматической проверки безопасности. Уже запущенный attempt завершил
  SDK compile и остановился на observer-selection до QEMU; ноль новых runtime
  случаев/controls квалифицировано. Raw bridge и прежние успешные проверки
  сохранены, неподтверждённые drafts в radio не подключены. Ограничение не обходилось.
- 2026-10-20, предупреждения сборки: `12b4be262` исправил зависимость
  `native_ota` от заголовков `native_stream`: PRIVATE target link используется,
  когда компонент уже включён; иначе сохраняется прежний private include.
  Состав компонентов и C/H исходники C3 не изменены. [Четыре SDK проверки](../tests/results/cyd-ota-component-dependency-20261020/README.md)
  проходят: 12 actual OTA translation units, точная private/header связь,
  zero common config delta и zero new source warnings. Полная CYD конфигурация
  совпадает с baseline; C3 проверен изолированным компонентным проектом, без
  full application/link/image утверждений. Исторические ошибки стенда и
  существующие SDK diagnostics сохранены отдельно; offline и staged-byte
  проверки архива проходят.
- 2026-10-20, CYD-C3-13: первый TLS RX prototype остаётся неинтегрированным.
  Independent review подтвердил ограничение публичного getter после numeric
  userdata setter; новая реализация должна хранить binding отдельно и учитывать
  actual ESP-TLS config-free-before-ssl-free. Старый SDK/QEMU runner завершён
  с exit1: шесть принятых вариантов, седьмой control дал named failure и затем
  panic при создании timekeeping lock внутри controlled restart под OOM;
  три option-варианта не запускались. Это не полный target PASS. Старые данные
  сохраняются, корректируется тестовое завершение без ослабления panic oracle.
- 2026-10-20, CYD-C3-13: replacement registry candidate прошёл семь host-групп,
  девять exact semantic controls и 14 compile rejections с ASan/UBSan, затем
  повтор всех семи положительных групп. Проверены pointer/numeric userdata,
  init/free revocation, config-free-before-ssl-free, повторное использование
  адреса и переполнение реестра. Host layout/crypto/RTOS остаются явными seams;
  это не actual SDK/QEMU или radio integration PASS. Следующая самостоятельная
  ревизия будет хранить integer address identities и требует отдельных проверок.
- 2026-10-20, CYD-C3-13: [исторический архив первого TLS RX prototype](../tests/results/cyd-tls-rx-pointer-prototype-20261020/README.md)
  сохранён отдельно: шесть принятых результатов, один отвергнутый panic и три
  незапущенных варианта. Raw report, SDK source/config/tool identities и точная
  цепочка panic сохранены; автономный verifier подтверждает целостность архива,
  сохраняя target status nonpass. Новый registry в этот архив не включён.
- 2026-10-20, CYD-C3-13: default-off [static RX reserve](CYD_MEMORY_TRANSFER_DESIGN.md)
  подключён через отдельный integer-identity registry и точные SDK init/free hooks.
  [Самодостаточные canonical tests](../tests/native/cyd_tls_static_rx/README.md)
  проходят на текущих исходниках: unit8/9controls/14compile rejections и8restored,
  service536 сценариев/12вариантов/2controls, CMake45 с19SDK guard mutations.
  Проверены оба вида userdata, config-free-before-ssl-free, новая radio config по
  старому адресу при живом старом RX loan, overflow/fallback, cleanup и SMP host
  seams. Source/snapshot/log/tool identities перепроверены после terminal0 всех
  трёх runners. Это не actual target ISR/SMP/OOM, SDK/QEMU или physical PASS;
  целевая матрица и production qualification остаются открытыми.
- 2026-10-20, CYD-C3-13: [canonical host-архив TLS RX](../tests/results/cyd-tls-static-rx-host-20261020/README.md)
  сохраняет исходные unit8/9controls/14compile rejections/8restored, service536
  и CMake45. Самостоятельный verifier и независимый запуск из другого каталога
  проходят: raw sources/logs/config, точное воспроизведение SDK overlay и host
  predicates, 34 applied/preparation равенства и явные binary/tool omissions.
  Исходники зафиксированы в `affa3caf1` после выполнения тестов; чистота Git
  на момент тестов не заявляется. Actual SDK/QEMU, application и physical gates
  остаются отдельными проверками; старый nonpass prototype не переименован.

- 2026-10-20, CYD-C3-13: первая registry SDK/QEMU матрица `rxt01` завершилась
  с exit1: десять принятых вариантов, одиннадцатый reserve-off/reclaim-on отвергнут
  по `disabled_original_full_record_payload`, двенадцатый не запускался.
  Причина — ошибка теста: pinned SDK до handshake возвращает через MFL getter
  `min(RX, TX)=4096`, что не является размером выделенного RX-буфера.
  Исправлена только проверка: полная RX content capacity 16384 и реальный heap
  allocation проверяются отдельно от getter на всех 32 setup. Production module,
  SDK, record sizes и привязки задач сохранены. В новом полном прогоне `rxt02`
  оба reserve-off профиля прошли: storage16717, minimum allocation17396,
  getter4096. Остальные варианты выполняются; общий PASS ещё не заявлен.

- 2026-10-20, CYD-C3-15: добавлен отдельный [контроллер приёмки CYD](../tools/cyd_tests/run.py)
  и [инструкция](CYD_TESTING.md). Проверяются identity сохранённого образа,
  native health обоих ядер, HTTP/HTTPS/EOF, переходы, Stop/switch, нагрузка,
  длительное воспроизведение и WebSocket. Existing vendor Vorbis/Opus проверяются
  через public dispatch; private bridge этим не квалифицируется. Прошли 28 новых
  CYD и 44 существующих C3 проверки инструментов, всего 72. Прерывания и ошибки
  cleanup сохраняют FAIL; установка firmware и перезагрузка не выполняются.
  Это host/fake/loopback квалификация контроллера; физическая приёмка открыта.

- 2026-10-20, CYD-C3-08/15: добавлен отдельный [контроллер OTA-приёмки CYD](../tools/cyd_tests/ota.py).
  Negative-only и явно выбранный same-image upload проверяют HTTP, image/backend,
  boot/uptime/slot и неизменность settings/Wi-Fi metadata/playlist. Прошли 52
  synthetic/fake теста, включая прерывания и primary/cleanup failures; независимое
  ревью завершено. Обеим платам сохранены прежние image rejection policy.
  Реальная сеть, flash/reboot, OTA во время playback и power-loss ещё не проверены.

- 2026-10-20, CYD-C3-13: [полная registry SDK/QEMU матрица](../tests/results/cyd-tls-static-rx-qemu-20261020/README.md)
  завершилась с exit0: 12 вариантов, 200 успешных команд, все 45 исходных файлов
  и 11 инструментов совпадают по raw SHA. Сохранены реальные two-core/ISR,
  lifecycle/loan/erase, heap exhaustion/reclaim, восемь exact semantic controls
  и оба reserve-off профиля. Архив хранит 1847 файлов и 19368 hash bindings;
  старый `rxt01` остаётся nonpass. Production application/lint, TLS traffic и
  физический выигрыш памяти открыты; reserve по умолчанию выключен.

- 2026-10-20, CYD-C3-13/15: [production SDK/Clang матрица TLS RX](../tests/results/cyd-tls-static-rx-sdk-20261020/README.md)
  закрыта из чистого `3a563324a`: семь GCC exports (vendor/custom FLAC × три
  выхода и reserve-off PDM), шесть полных Clang-профилей и отдельные TLS SDK
  frontend/consumed-header проверки. 338 translation units, ноль parser errors;
  предупреждения 86/84/85 по PDM/continuous/legacy, одинаковые у двух семейств
  декодеров, разобраны без suppression и без новых опасных замечаний.
  Первоначальная Clang-квалификация остаётся nonpass: ошибочное сравнение с GCC
  исправлено отдельным квалификатором, который проверяет ровно 14 typed/presence
  изменений toolchain/libc/feature. Для GCC по-прежнему допустима только новая
  reserve bool. Прошивки сохранены и запушены в `4d3773086`; минимальный запас
  OTA — 224192 B. Сравнение PDM ON/OFF на одном коммите: app +672 B, static DRAM
  +16768 B, IRAM без увеличения. Это цена постоянного резерва; физическая польза,
  radio boot, heap/stack и TLS/audio/WebUI/OTA нагрузка ещё требуют приёмки.
  Архив SDK/Clang проверен автономно из другого каталога, включая все ссылки
  на firmware; manifest SHA256 —
  `8a120ba9329a190d7baf6f3b813bc61224a391101bcbf170b4c1f6dba96a1db1`.

- 2026-10-20, CYD-C3-13/15: [два actual production PDM boot attempts](../tests/results/cyd-production-radio-boot-20261020/README.md)
  сохранены как nonpass: reserve ON и OFF, controller exit1 при QEMU exit0
  после guest panic/reboot. Оба доходят до SDK multicore startup/heap и одинаково
  падают в `init_flash:654` до `app_main` после QIE readback failure. Вывод о
  несовместимости модели flash/профиля — обоснованная гипотеза; конкретная
  неудавшаяся transaction не установлена. Ранняя MPI, дисплей, pipeline, сеть и
  static RX loan не квалифицированы. Input/tool/source и scratch image hashes
  сохранены; firmware/SDK/model не менялись, физические операции не выполнялись.
  Manifest SHA256: `7ecef77c3b660efac39241f1a556271f9dbb60c4d08829efbe52e3048d69d5b9`.

- 2026-10-20, CYD-C3-14 G6: [raw8192 format regression](../tests/results/cyd-vorbis-format-20261020/README.md)
  подтверждён на SDK6.0.2/Xtensa. Исходный код отвергал допустимые блоки8192
  при48/63 999Гц. Удалены только две строки default-ограничения; optional cap
  и остальные header checks сохранены. Штатный кодек обрабатывает 68 пакетов;
  исправленный bridge даёт 340 сравнений пакетов и 4 631 808 точных PCM байт
  при четырёх частотах и обычном режиме с блоком 2048. Четыре некорректных заголовка
  отклоняются; восстановление старых байтов приводит к точному ожидаемому отказу.
  Десять host tests проходят. Первые metadata/runner попытки остаются nonpass,
  ручное завершение baseline сохранено отдельно. Bridge ещё не подключён к радио;
  остальные G1–G8 и физическая приёмка остаются. Отдельная C3/RISC-V проверка
  завершена следующим checkpoint.

- 2026-10-20, CYD-C3-14 G6, донор C3: [независимый SDK6.1/RISC-V прогон](../tests/results/c3-vorbis-format-20261020/README.md)
  воспроизводит исходный отказ и проверяет то же удаление двух строк в C3.
  Исправление даёт 340 попакетных сравнений и 4 631 808 точных PCM байт;
  четыре повреждённых заголовка отклоняются. Контроль с полностью восстановленным
  setup.c доходит до точного `legal_candidate_open_required` после всех
  vendor/ordinary/high-rate prerequisites. Core0, RV32 flags, ELF243 и C3 offset0
  проверены отдельно; восемь host tests проходят. Исходник C3 исправлен, явная
  ограниченная конфигурация и остальные проверки сохранены. Полное приложение C3,
  Ogg/EOF/reset/OOM и физическая приёмка этим прогоном не квалифицированы;
  отложенные AAC/application hooks не запускались. Все этапы 12–15 остаются
  открыты в прежнем объёме.

- 2026-10-20, CYD-C3-14 G6: [полная raw-матрица пар размеров блоков](../tests/results/cyd-vorbis-block-matrix-20261020/README.md)
  проверена на SDK 6.0.2/Xtensa/core1: 108 случаев, 5472 сравненных пакета,
  360 групп переходов, 32 543 616 точных PCM байт и terminal QEMU exit0.
  Все 36 допустимых пар 64–8192 проверены на трёх корпусах без пропусков.
  Host Xiph принимает все 108; исходный dual-reference прогон остаётся nonpass:
  native FFmpeg принимает 78 и отклоняет 30 из-за дополнительной floor1 границы.
  Для minimal отдельно проверены все 36 rate-only вариантов 192000 Гц.
  [Генераторы](../tests/vorbis_block_matrix/README.md) воспроизводят все 144
  reference/rebind варианта побайтно; восемь canonical protocol tests проходят.
  Это изолированный public raw API, исходные setup/output не менялись.
  C3 matrix, остальное G6, Ogg/EOF/reset/OOM, callback ABI, SMP/audio-task
  интеграция и физическая приёмка остаются. Отложенные пункты не возобновлялись.
  Финальный архив проверен автономно из другого каталога; ранние ошибки
  архивного валидатора сохранены отдельно от SDK/runtime результатов.
  Manifest SHA256:
  `97262bd2eda0a23595b322cdd91055214d919800ee3347143742137f256b0333`.
- 2026-10-20, CYD-C3-14 G6: `11d0fee4c` сохраняет
  [генераторы books/floor0/residue0](../tests/vorbis_format_corpus/README.md).
  Actual canonical generation воспроизводит 17 случаев и все 100 nonmanifest
  файлов побайтно; различаются только source/provenance поля двух manifest.
  Все восемь construction tests проходят. Это воспроизводимость исходных
  reference fixtures; новый target результат этим не заявляется.
- 2026-10-20, CYD-C3-14 G6: [unsigned-rate checkpoint](../tests/results/cyd-vorbis-uint32-rate-20261020/README.md)
  воспроизводит signed32 отказ в baseline и исправляет две проверки без изменения
  vendor ABI. Acceptance на SDK6.0.2/Xtensa/core1 проходит все 16 выбранных частот,
  1088 пар пакетов и 4 362 240 точных PCM байт; нулевая частота отвергается.
  Отдельный optional-cap вариант пропускает 11 и отвергает пять частот ≥64000.
  Оба независимых signed-guard controls достигают точных ожидаемых отказов.
  Все пять кампаний завершились с exit0; 19 canonical protocol tests проходят.
  C3 unsigned-rate regression, target расширенного 17-case корпуса, остальное
  G6/G1–G8 и radio/physical gates остаются. Аппаратные частоты выхода и
  прежние core/priority/stack этим исправлением не меняются.
  Архив пяти кампаний и 45 owned command receipts сохранён в 714 файлах;
  автономная проверка конечного каталога из другого cwd завершилась с exit0.
  Manifest SHA256:
  `6b5e4119829d87a30211bc97c0c22a0808df69b7dcb01c3d740d675669a37b80`.
- 2026-10-20, CYD-C3-14 G6, донор C3: [независимый unsigned-rate checkpoint](../tests/results/c3-vorbis-uint32-rate-20261020/README.md)
  воспроизводит отказ на SDK6.1/RV32 и исправляет две проверки без изменения ABI.
  Acceptance проходит16 частот,1088 пар пакетов и4 362 240 точных PCM байт.
  Optional-cap отдельно пропускает11 и отвергает5; оба signed-guard controls
  дают точные ожидаемые отказы. Все пять кампаний/45 owned commands завершены
  с exit0;19 canonical protocol tests и23 prep host methods проходят.
  Реальные core0/core0,160MHz/unicore, ELF243 и bootloader0 подтверждены отдельно
  от CYD. Архив705 файлов автономно проверен из другого cwd с exit0; manifest
  SHA256 `ce5bb45115eba8710b51a4d85ae376a77bb7b99e4b1e87bcb0065027a0b8cbde`.
  Полное C3 приложение и отложенные AAC hooks не запускались. Остальное G6,
  G1–G8, production exports и физическая приёмка остаются открытыми.
- 2026-10-20, CYD-C3-14 G6: [два дополнительных генератора](../tests/vorbis_format_corpus/README.md)
  сохраняют 21 случай mono/stereo на девяти частотах, coupling/submaps/residue2
  и восемь lookup2 sparse-wide/single-entry случаев. Actual generation и
  [сравнение](../tests/results/vorbis-more-generators-20261020/README.md) проходят:
  29 случаев/406 пакетов, все 149 файлов данных, включая 145 бинарных,
  побайтно равны исходным. Изменены только четыре provenance файла;
  14 construction rejection controls проходят. Это воспроизводимые fixtures,
  новый target/PCM результат этим не заявляется. Manifest SHA256:
  `c66cefeb56522cdb0b4b466c9823ca02c85d9c9772ed8679aa8944f611cf95ba`.
- 2026-10-20, CYD-C3-14 G6: [lookup2/single-entry setup checkpoint](../tests/results/cyd-vorbis-map2-20261020/CHECKPOINT.md)
  читает все исходные multiplicand строки, сохраняет только активные wide строки
  в порядке used-entry и публикует исходный mapped leaf одиночной книги для
  обоих однобитовых значений. ABI, synthesis/MDCT/PCM backend не менялись.
  Actual SDK6.0.2/Xtensa/core1 open/decode/close проходит17 и25 случаев:
  соответственно238/398080 и350/623360 пакетов/PCM байт. Все9 owned commands
  каждой кампании завершены с exit0. Три независимых возврата прежней ветки
  воспроизводят точный open отказ: packed case6 после84 пакетов, wide case8
  после112 и singleton case12 после168; полные предшествующие protocol/PCM
  префиксы равны fixed capture, panic нет. Самим control campaigns сохранён NONPASS.
  Численное сравнение25 завершено на всех случаях: исходные книги8, single/twin4
  и floor1 controls3 имеют max1; wideD16×4 и floor0×6 не проходят предел2.
  Полный25 и подгруппа books16 остаются NONPASS, допуск не повышался.
  Обе исходные независимые host dual-reference кампании также сохранены как
  NONPASS с отдельными Xiph-qualified результатами. Исходный vendor open panic,
  неиспользуемый symbol gate, ошибка C capacity17 для25 descriptors и ошибка
  framemd5 layout проверки сохранены отдельно от последующих реальных прогонов.
  Дальнейшая работа: unit-тест публикации наших book/floor0 полей, публичный
  Tremor decode_map/кривая и эквивалентные LSP представления; затем C3/RV32,
  оставшиеся single/wide-width cases и остальные G1–G8. В radio bridge пока не
  подключён, физическая приёмка не выполнялась.
  Архив4183 файлов/22126714 байт сохраняет4221 исходную identity запись,
  включая41 hash-only omission целевых бинарников. Manifest SHA256:
  `c3e1fa16adb85d25f90339a9d4c74b6c0cbc9feac3d4097624bbe1d6553bd11c`.
  [Автономная проверка](../tests/results/cyd-vorbis-map2-verification-20261020/README.md)
  конечного canonical каталога из другого cwd завершена с exit0; она подтверждает
  целостность свидетельств, сохраняя полный численный NONPASS.
- 2026-10-23, CYD-C3-14 G6, донор C3: [lookup2/single-entry checkpoint](../tests/results/c3-vorbis-map2-20261023/CHECKPOINT.md)
  переносит те же две setup ветки с сохранением CRLF и всех остальных исходных
  байтов. Actual SDK6.1/RV32/ELF243/160MHz/unicore/core0 baseline воспроизводит
  open отказ case6 после6 случаев/84 пакетов; все7 owned commands завершены0,
  panic нет. После правки полный25 capture даёт350 пакетов/623360 PCM байт,
  778 native events и9 actual terminal0 commands. Предшествующие188 native
  events/168960 PCM байт совпадают до и после правки.
  Независимое измерение всех25 случаев выполнено с прежним пределом2:
  исходные books8, single/twin4 и floor1 controls3 имеют max1; wideD16×4
  имеют max65535 и нарушают обе sparse/dense PCM пары; floor0 even6 имеет
  max40664/1649/40664, odd5 — max65535 во всех трёх парах блоков.
  Полный25 и books16 остаются NONPASS. При прямом сравнении actual C3/CYD
  PCM совпадает21 случай; различаются ровно четыре wideD16 случая. Это
  наблюдение не устанавливает причину расхождения и не квалифицирует формат.
  Полное C3 приложение/AAC hooks не конфигурировались. Production task affinity,
  ABI, synthesis/MDCT/output и CYD stream core0/decoder core1 не менялись.
  Архив1247 файлов/6507191 байт сохраняет1621 исходную identity запись,
  включая367 точных ссылок на общий committed CYD reference-архив и10
  hash-only omissions целевых бинарников. Manifest SHA256:
  `005c3e29ae2392c20f872656baba13e5ea2e7ad361e2b57efcdf717579182066`.
  [Повторная автономная проверка](../tests/results/c3-vorbis-map2-verification-20261023/README.md)
  staged и окончательного canonical каталога из другого cwd завершена0;
  baseline и полный численный NONPASS сохранены.
- 2026-10-23, CYD-C3-14 G6: [owned-book unit](../tests/results/cyd-vorbis-owned-book-20261023/CHECKPOINT.md)
  исполняет точный production setup parser с контролируемым public bit-reader
  и отдельным ограниченным public vector consumer. Actual SDK6.0.2/Xtensa/
  ILP32/240MHz/двухъядерный ESP32/main core0 подтверждены macro/include
  зависимостями; ELF94, nm, map и реальные link commands подтверждают отсутствие
  vendor codec/decode/register/wrapper linkage. Все16 книг/59 active codewords/
  61 probes/2 wide-пары/97 native events проходят, после clear live allocations0.
  Все14 owned commands завершены0. Настоящие QMP greeting/capabilities/quit
  acknowledgements, host-qmp-quit SHUTDOWN и terminal0 сохранены; EOF проверен
  точным captured helper, отдельное EOF поле в исходный receipt не добавлялось.
  Первый запуск сохранил NONPASS до build/QEMU из-за ошибочного требования
  уникальности109 GCC dependency строк: пять SDK headers законно повторяются.
  Successor сохраняет все109 строк/104 paths и повторно сравнивает raw macros
  и dependencies после build. Исправление outer/child log-name collision
  отдельно сохранено как source-only история до runtime.
  Это квалификация нашей публикации и данного public consumer при point0,
  не vendor backend/PCM/floor0/G6. Production source, ABI и task affinity
  этим unit-тестом не менялись; wide PCM и все остальные gates остаются.

- 2026-10-23, CYD-C3-14/G6: [floor0 equivalent checkpoint](../tests/results/cyd-vorbis-floor0-equivalent-20261023/CHECKPOINT.md)
  сохраняет шесть новых представлений lookup2 с минимумом1/16 и уменьшенными
  multiplicands. Независимый raw/Fraction/CRC witness и Xiph12 подтверждают
  прежние LSP/PCM; native12 lookup2 отказы и host exit1 сохранены.
  Actual SDK6.0.2/Xtensa/core1 raw31 завершён:434 пакета/738560 PCM байт/964 events,
  все9 команд0. Прежние25 PCM и775 case events совпадают побайтно; все6 новых
  target PCM совпадают с исходными floor0. Maxima новых even6:40664/1649/40664,
  odd5:65535×3; полное31 и проекция25 остаются NONPASS с пределом2 S16 LSB.
  Отдельная own binary64 формула6/84/168/2688 и5 algebra controls завершена:
  147 bins требуют положительный ideal dB; это не integer Tremor/PCM и не
  установленная причина backend ошибки. Историческая README опечатка734464
  сохранена; actual model/materializer/target требуют738560. [Архив и canonical
  offline replay](../tests/results/cyd-vorbis-floor0-equivalent-verification-20261023/README.md)
  проверены отдельно, включая полный31 и все14 relations. Публикация floor0
  полей, публичная integer-кривая, остальные форматы/G1–G8, radio integration
  и физические gates остаются открытыми; задачи и аппаратные настройки сохранены.

- 2026-10-23, CYD-C3-14/G6: [wide width checkpoint](../tests/results/cyd-vorbis-wide-width-20261023/CHECKPOINT.md)
  сохраняет исходные4 D16 lookup2 книги и8 эквивалентных представлений qbits9/16.
  Собственный raw/Fraction/CRC witness проверяет12 cases/all declared rows и5
  construction controls. Xiph принимает12, все4 тройки PCM равны; native12
  lookup2 отказы и actual host exit1 сохранены. После отдельной recorded-reference
  квалификации actual SDK6.0.2/Xtensa/core1 декодирует12/168/337920 с375 events,
  все9 команд0 и ноль compiler warnings. Полное численное сравнение12 завершено
  без input errors: max65535 во всех случаях; target не выполняет4 width-triples
  и6 source-derived sparse/dense пар, Xiph выполняет все10. Прежние4 input/PCM
  из полного25 совпадают; supplemental сравнение с31 сохранено только как запись.
  [Canonical offline replay](../tests/results/cyd-vorbis-wide-width-verification-20261023/README.md)
  повторно проверяет весь12 scope, raw witness,24 reference children, metrics,
  relations и original25 dependency. Предел2 S16 LSB и NONPASS сохранены;
  причина backend ошибки не установлена. Production код/ABI/привязки задач
  не менялись, fullG6/radio/physical остаются открытыми.

- 2026-10-23, CYD-C3-14/G6: [owned floor0 publication unit](../tests/results/cyd-vorbis-owned-floor0-20261023/CHECKPOINT.md)
  вызывает exact production `repair_floor0_info_unpack`/normal free на собственных
  vi/ci и12 исходных/эквивалентных raw setups. До SDK независимый syntax reader
  подтверждает абсолютные66/74-bit spans, все25 semantic controls проходят.
  Первая actual сборка остановилась на двух `%u`/`uint32_t` diagnostic errors;
  QEMU не запускался. Successor исправляет только два printf casts, без suppression.
  Actual SDK6.0.2/ILP32/Xtensa/SMP/maincore0 capture02 проходит все15 команд,
  12 публикаций/6 пар/32 events,40-byte guards/unchanged vi-ci/normal free live0;
  110 dependency rows сохранены, compiler warnings0. Actual QMP greeting/caps/
  quit/host SHUTDOWN/ack/EOF/reader join/exit0 проверены до full protocol.
  [Автономный архив и canonical offline replay](../tests/results/cyd-vorbis-owned-floor0-verification-20261023/README.md)
  сохраняют failed01 и acceptance02 и не требуют PCM/reference архивов.
  Это публикация наших полей; integer-кривая/vendor/PCM/fullG6/radio/physical
  остаются открытыми. Production source, ABI и radio task affinities не менялись.
  Архив712 файлов/7689937 байт сохраняет27 hash-only binary omissions и
  фактический ELF header64. Manifest SHA256:
  `43ef7d4dac52ab244be58a851ab2fee74fe02be04d34ee14a93f7400675cdea8`.
  [Автономная проверка](../tests/results/cyd-vorbis-owned-floor0-verification-20261023/README.md)
  staged и конечного canonical каталога из другого cwd завершена0.

- 2026-10-23, CYD-C3-14/G6: [публичная floor0 integer-кривая](../tests/results/cyd-vorbis-public-floor0-curve-20261023/CHECKPOINT.md)
  прошла отдельный owned-array SDK6.0.2/Xtensa/SMP/maincore0 тест:6 случаев,
  84 пакета/168 вызовов/58368 полных bins/233472 signed32 байта и3992 events.
  Все22 команды завершены0, compiler warnings0; исходные168 входов/5208 C words
  сохранены. Actual QMP greeting/caps/COMPLETE/owner quit/host SHUTDOWN/ack/exit0
  проверены; EOF/join обеспечены exact helper, отдельных booleans в старом
  helper нет. Original collector01 и strict compile02 NONPASS сохранены.
  PORTED public C исправляет два negative-constant shifts и удаляет unused local,
  без suppression/изменения алгоритма; original87-file source/license сохранены.
  Отдельная binary64 диагностика проверяет все2688 активных точек:147 ideal-dB
  положительны, public gain в них0.9999999403953552..1.0. Это finite public-source
  наблюдение, не объяснение opaque vendor PCM и не критерий conformance.
  [Автономная проверка архива](../tests/results/cyd-vorbis-public-floor0-curve-verification-20261023/README.md)
  прошла до и после точного копирования;4078 файлов/38530693 байта,
  43 hash-only binary omissions, manifest
  `ecd3133cb37dbd42bf2e3fee4715e06a26bc8d50d7a4e026654c5de72a1406d3`.
  Публичный integer experiment для этих шести fixtures завершён; floor0/wide
  PCM NONPASS, остальные G1–G8, radio/resource/physical gates остаются.
  Production source, ABI, hardware settings и core0/core1 bindings не менялись.

- 2026-10-23, CYD-C3-14/G6: [дополнительные singleton8 и preferred-zero controls](../tests/results/cyd-vorbis-more-singletons-20261023/CHECKPOINT.md)
  проверены с сохранением всех исходных данных.31 host controls/raw witness8/112/
  136 Ogg carrier pages проходят; Xiph принимает8, native отказывает4 lookup2
  на setup и4 map1 при обработке пакета. Независимый qualifier сохраняет оба
  класса и dual NONPASS. Полный Xtensa/core1 capture проходит9 команд/251 events/
  112 пакетов/225280 байт; compiler warnings0. Численное сравнение завершается1
  без input error: maxima1/1/1/65535/1/65535/1/65535, прежний предел2 сохранён.
  Все2 equal triples и4 different pairs проходят на Xiph и target; ошибка D16
  sequence1 повторяется для lookup2/dense map1/sparse map1, причина не установлена.
  Отдельные28 host controls и witness preferred-zero сравнения подтверждают
  ровно56 заменённых bits/224 token observations с сохранением остальных bits,
  headers/setup/offsets/padding/metadata и необходимыми carrier CRC. Xiph PCM
  всех4 original/zero пар совпадает, включая прежние qualified original4.
  Native принимает новые4 zero случая с max1; исходные4 map1 отказывает как
  прежде. Исходный/совместный dual NONPASS сохранён; текст Operation not permitted
  не устанавливает OS/security причину. В рамках этого checkpoint zero target
  ещё не запускался; отдельный полный target8 результат записан ниже.
  [Offline проверка](../tests/results/cyd-vorbis-more-singletons-verification-20261023/README.md)
  прошла до/после byte-exact promotion. Архив1969 файлов/9925574 байта требует
  только явно закреплённые8 shared entries committed CYD map2; прежние25/wide/
  floor0 кампании не переигрывались. Manifest
  `020f11d42d79b45dc4c7a5f5d639b03cfa9a8a451c277389325d5caf45bca2d8`.
  Production source/ABI/hardware/task affinities не менялись; numerical gaps,
  остальные G1–G8, radio/resource/physical gates остаются.

- 2026-10-23, CYD-C3-14/G6: [mono/stereo и mapping21](../tests/results/cyd-vorbis-mono-mapping-20261023/CHECKPOINT.md)
  прошли полный raw target и независимое сравнение PCM. Исходные21 случая
  сохраняют все105 raw/header/carrier файлов и109-file inventories;42 ранее
  выполненных reference children и все WAV/framemd5/metadata перепроверены.
  SDK6.0.2/Xtensa/240MHz/SMP выполняет9 команд с terminal0, coordinator core0,
  worker core1/priority3/stack16384;294 пакета/464640 PCM байт/654 events,
  mask2097151, compiler warnings0. Mono остаётся одним каналом без дублирования.
  Все21 случая имеют max1 относительно каждого из двух эталонов, включая
  полные packet boundaries и все short/long transitions; фиксированный предел2
  выбран до измерения и не является нормативным допуском Vorbis.
  Actual30 protocol controls и39 metric/path/policy controls проходят.
  Первая numerical попытка сохранена как input rejection: Windows backslash
  key вызвал KeyError до сравнения PCM, после чтения command logs с PCM_HEX.
  Successor02 исправляет только нормализацию ключей, добавляет10 path controls
  и сохраняет точные SHA/metrics/policy. Исходные29 controls, prep01 и ошибочный
  запуск сохранены без переоценки как decoder NONPASS. Финальное полное
  measurement02 завершается0 с42 сравнениями и обеими reference bounds=true.
  [Offline проверка](../tests/results/cyd-vorbis-mono-mapping-verification-20261023/README.md)
  проходит до/после byte-exact promotion, второй раз из другого cwd. Первая
  проверка архива сохранена отдельно: она неверно отождествляла original path
  и storage key замороженной копии; successor02 сверяет исходный путь, SHA и
  все байты без fallback. Архив1775 файлов/8202645 байт требует только8 явно
  закреплённых shared entries committed CYD map2; прежние кампании не переиграны.
  Manifest `3e88fda7fab1bd42d8b40e5c9de637e06050199451e54840271eeb5b3fb4e0d0`.
  Старые floor0/wide/D16 sequence1 NONPASS и отложенные Ogg/AAC пункты остаются;
  bridge в radio не подключён, production source/ABI/core bindings не менялись.

- 2026-10-23, CYD-C3-14/G6, публичные upstream releases: официальный
  [Registry](https://components.espressif.com/components/espressif/esp_audio_codec/versions/2.6.2/versions?language=en)
  отмечает2.6.2 как Latest; текущий
  [manifest Espressif](https://raw.githubusercontent.com/espressif/esp-adf-libs/master/esp_audio_codec/idf_component.yml)
  также содержит2.6.2. В опубликованном
  [changelog](https://components.espressif.com/components/espressif/esp_audio_codec/versions/2.6.2/changelog?language=en)
  не найдено документированного исправления floor0/wide-vector/sequence численных
  расхождений. Это не доказывает отсутствие неопубликованных изменений и не
  устанавливает причину наших PCM ошибок. Публичный
  [CMake](https://raw.githubusercontent.com/espressif/esp-adf-libs/master/esp_audio_codec/CMakeLists.txt)
  выбирает prebuilt archives отдельно по IDF_TARGET; исходный патч алгоритмов
  для этих случаев не найден. Версии библиотек и точные ABI/archive guards
  сохранены; замена версии не считается готовым исправлением.

- 2026-10-23, CYD-C3-14/G6: [полный исходный4/preferred-zero4 target](../tests/results/cyd-vorbis-singleton-zero-bit-20261023/CHECKPOINT.md)
  завершил9 SDK/QEMU команд на Xtensa/core1:8 случаев/112 пакетов/225280 PCM
  байт/251 events/mask255, compiler warnings0. Все исходные raw/header/carrier
  байты и56 заменённых bits/224 token observations сохранены. Все4 target
  и4 Xiph original/zero пары совпадают побайтно. Полные12 сравнений измерены:
  Xiph maxima1/65535/1/65535/1/65535/1/65535, native новых4 —1/65535/1/65535.
  Фиксированный проектный предел2 не изменён; measurement02 завершён1 как
  complete numerical NONPASS. Смена бита не устраняет D16 sequence1; причина
  opaque backend этим не установлена. Исходные4 native packet refusals и пустые
  WAV сохранены, полного8 dual pass нет. Controls28/30/44/54 проходят отдельно.
  Первая numerical schema ошибка (`ogg_sha256` вместо `files.ogg.sha256`) сохранена
  как input rejection; immutable successor02 меняет только file-fact reader
  и добавляет10 содержательных проверок схемы, сохраняя metric/policy.
  [Offline проверка](../tests/results/cyd-vorbis-singleton-zero-bit-verification-20261023/README.md)
  проходит до/после byte-exact promotion, второй раз из другого cwd. Первая
  упаковка ошибочно требовала отсутствующий OLD construction.json; successor02
  исправил план, successor03 удалил ту же ссылку из verifier metadata tuple.
  Обе actual ошибки/исходники/журналы и stage02 manifest сохранены отдельно;
  новые source gates проверяют63 пути и реальные поля исходного manifest.
  Архив1926 файлов/13063045 байт требует только8 явно закреплённых shared
  entries committed CYD map2; прежние numerical кампании не переигрывались.
  Manifest `85ba3fc45f3a8892f22601b3b6b9adf696e47d518c432a6f41015af8234fb57e`.
  Source/ABI/stream core0 и decode/output core1 сохранены. Полные G1–G8,
  floor0/wide/sequence1 numerical gaps, radio/resource/physical gates открыты.

- 2026-10-23, CYD-C3-14/G6: [public zero-guard successor отложен](CYD_PUBLIC_BOOK_ZERO_GUARD_DEFERRED_20261023.md).
  После законченного исходного baseline (SDK36/365/439 exact, host331 exact
  и34 UBSan NONPASS) автоматическая проверка остановила подготовку отдельной
  копии с двумя zero-magnitude guards: «This content was flagged for possible
  cybersecurity risk». Конкретное основание не сообщено. Root остановил peer
  review этого шага; запрос не переформулирован и не передан другому агенту
  для обхода. Draft не подключён к firmware; guarded controls/materialization/
  host/SDK не запускались root и ноль новых guarded runtime случаев принято.
  Уже выполненные baseline отчёты сохраняются независимо, без переоценки
  host34 как ожидаемого PASS. Причина vendor PCM этим не установлена.

- 2026-10-23, CYD-C3-14/G6: [public owned-book consumer baseline](../tests/results/cyd-vorbis-public-book-consumer-baseline-20261023/CHECKPOINT.md)
  полностью сохранён.26 source controls и materialization проходят; SDK6.0.2/
  Xtensa завершил14 команд,36 canonical publications,365 точных Fraction
  векторов и439 protocol events, compiler diagnostics0. Отдельный host ASan/
  UBSan прогон выполнил365 вызовов:331 доступный вектор точен,34 завершились
  oversized-shift диагностикой в исходном публичном C. Полный host результат
  остаётся NONPASS; точность target не доказывает переносимость C или причину
  прежних vendor PCM расхождений. Исходник Tremor/лицензия/неизменённая арифметика,
  две явно выделенные unit-only zero-float пробы и все реальные отказы сохранены.
  [Offline проверка](../tests/results/cyd-vorbis-public-book-consumer-baseline-verification-20261023/README.md)
  проходит до/после create-only promotion, повторно из другого cwd. Standalone
  архив1739 файлов/9221016 байт,1738 identity rows,20 binary omissions;
  manifest `a9d1e10fea01b75c5df0f0880dfafc26c2a69f941064420ccb7f19cf782c67d4`.
  Старые numerical reports и законченный guard proposal — record-only;
  отложенный guarded draft не включён, не применён и не квалифицирован.
  Production source/ABI/stream core0/decode-output core1 сохранены; fullG6,
  radio/resource/physical gates и прежние отложенные пункты остаются открытыми.

- 2026-10-23, CYD-C3-07/00: [переносимое сравнение WS status keys](../tests/results/ws-status-key-20261023/README.md)
  исправлено в CYD и C3: явные18/11 scalar fields и по4 логические строки
  заменяют whole-struct memcmp. Padding и байты после NUL больше не вызывают
  лишних revision/publication. Типы/layout/capture/heartbeat/admission и owner
  задачи сохранены. Это P3 переносимость, а не воспроизведённый production crash.
  Старые реализации обеих целей реально отклоняют padding-only regression;
  финальный CYD before использует те же harness/runner байты, что и successful after.
  CYD: 59 fixture groups; C3: 42 status-loop cases/7 semantic controls проходят
  ASan/UBSan. Каждый scalar/видимая строка и отдельные padding/string-tail случаи
  покрыты. Focused GCC компилирует реальные ELF32 relocatable units для Xtensa94
  и RISC-V243 без diagnostics; Clang сохраняет только1/2 прежних warning,0 errors,
  новых warning0, suspicious-memory-comparison исчезает в обеих целях.
  Исходные target preflight ошибки имени compiler/Windows path parser сохранены;
  промежуточный успешный прогон с неполным input capture остаётся history.
  Финальный прогон фиксирует и перепроверяет headers/config/DB/compiler/response/
  specs/actual tidy; independent review замечаний не имеет. Полные приложения,
  новые firmware images и физическая плата в этом focused прогоне не запускались.
  Архив335 файлов/2319760 байт проверен отдельно из другого cwd;
  manifest `1930fdfbb6c1e33207e0ce74981952002f106a4e795c3998e2f606d86b3dcbab`.
  HTTPD NULL trace исключён реальным SDK caller flow; signed timezone promotion
  корректна для отрицательных значений — эти пути без доказанного дефекта не менялись.
  CYD stream core0/decode-output core1, приоритеты/стеки и C3 unicore сохранены.
  Codec deferrals и fullG6/radio/resource/physical gates остаются открытыми.

- 2026-10-24, CYD-C3-14/G6: [floor1 presence39](../tests/results/cyd-vorbis-floor-presence-20261024/CHECKPOINT.md)
  закрывает отдельный пробел floor present/absent, coupling-aware residue0/1/2
  и перекрытия окон: 9 mono/30 stereo, 546 пакетов/971520 PCM байт/1212 events.
  [Генератор](../tests/vorbis_format_corpus/generate_floor_presence.py) и
  [контрольные тесты](../tests/vorbis_floor_presence/README.md) доступны в tests;
  30 исходных и 17 canonical controls проходят. Оба эталона выполняют все78
  декодирований; Xtensa/ESP32/240MHz/two-core target сохраняет worker core1,
  priority3/stack16384 и coordinator core0. Все78 полных target/reference
  сравнений имеют max1 при прежнем проектном пределе2LSB, без коррекции PCM.
  [Автономный replay](../tests/results/cyd-vorbis-floor-presence-verification-20261024/README.md)
  проходит до/после переноса архива, второй раз из другого cwd. Архив433 файла,
  manifest `0f95d0c5451290879a088ef4648ebd89cc966622584ebdbb769f2737a08f9cfc`.
  Первый отказ упаковки сохранён; добавлены точные source aliases без изменения
  verifier/helpers/policy. Контроллер остаётся прежним nine-command fixture
  без QMP; полный dependency walk и независимая проверка пропущенных binaries
  не заявляются. Scalar dimension1 не расширяет multidimensional residue0.
  Production source/ABI/core bindings сохранены; старые wide/floor0/sequence1
  NONPASS, codec deferrals, fullG6/radio/physical gates остаются открытыми.

- 2026-10-24, CYD-C3-00/15: [проверки CYD в исправленном QEMU](../tests/results/cyd-qemu-idf6-compat-20261024/CHECKPOINT.md).
  В отдельной ветке/worktree QEMU исправлены Windows trace generation,
  хранение DPORT clock register, непрерывный SR2 и SPI dummy/read modes.
  [Основной тест](../tests/results/cyd-qemu-idf6-compat-20261024/selected-qemu-source/tools/test_esp32_idf6_compat.py)
  проходит274/274; [задержка входа](../tests/results/cyd-qemu-idf6-compat-20261024/selected-qemu-source/tools/test_esp32_spi_input_delay.py)
  проходит391/391 для0нс и391/391 для25нс. При80/40/20МГц проверяются2/1/0
  compensation clocks, PRE/EQU и запрет компенсации MOSI/DOUTDIN.
  SPI2/SPI3 LCD/SD, CS isolation и неверная GPIO routing проходят в обоих
  режимах задержки. Реальные контрольные49/187,7/200,73/274 и24/391 NONPASS
  сохранены; expectations не ослаблялись. Paused QTest использует owner
  terminate/exit1 с actual EOF/join; это не natural boot exit0.
  Default input delay0 сохранён; production observation явно выбирает25нс
  как функциональную модель при фиксированном source80МГц. Произвольные
  bit waveforms, analog timing и dynamic APB не квалифицированы.
  Исходный production PDM image3a563/SDK6.0.2/QIO80/CPU240/two-core не менялся:
  после исправлений достигает app_main/ST7789/Wi-Fi init без прежней ошибки
  SPIFFS и PHY clock assertion. Затем full RF calibration завершается
  LoadStorePIFAddrError на неподдерживаемом MMIO0x60033c00. Pipeline/radio/Web
  readiness остаются false; полного startup PASS нет. Firmware, FS, приоритеты,
  стеки, core bindings и C3 hardware setup сохранены. Новый production build,
  radio/audio/network/resource/soak/OTA/physical acceptance этим не выполнены.
  Архив432 файла, manifest `5b3295b31abd869b7a8e537f8f2161a886e3e2f08999cfdb79c68f5d303ace57`;
  [автономная проверка](../tests/results/cyd-qemu-idf6-verification-20261024/README.md)
  проходит до/после byte-exact promotion из другого cwd; устанавливает
  целостность и согласованность сохранённых
  отчётов, без повторного исполнения QEMU и без full dependency closure.
- 2026-10-24, CYD-C3-14: [floor1 X-position regression](../tests/results/vorbis-floor1-positions-20261024/README.md)
  добавляет в CYD и C3 две проверки из Vorbis I §7.2.2: максимум 65 координат
  вместе с двумя неявными границами и отсутствие повторов. Сортировка,
  корректный несортированный порядок, ABI, синтез и привязки задач сохранены.
  Восемь host-тестов проходят. На каждой архитектуре actual SDK/QEMU принимает
  8 допустимых настроек, отклоняет 6 ошибочных и сравнивает 112 пакетов /
  225280 PCM байт точно с исходным декодером. Два отдельных ESP32 controls
  подтверждают ошибочное OK/non-null принятие при снятии каждой проверки.
  Xiph подтверждает все 14 решений по заголовкам. Полное численное сравнение
  остаётся NONPASS: новые допустимые случаи с короткой X-границей 1/2/8 дают
  max65535 на CYD и C3; остальные пять имеют max1. Обе платформы дают одинаковый
  PCM, причина внутри vendor не установлена. Native FFmpeg также отклоняет
  допустимую большую границу и принимает оба превышения лимита; исходный
  NONPASS и ограничения классификатора сохранены. Новый numerical gap добавлен
  к wide/floor0/sequence1; full G6, radio integration и аппаратная приёмка
  остаются открыты. Отложенные пункты не возобновлялись.
- 2026-10-24, CYD-C3-14: [floor1 curve renderer](../tests/results/vorbis-floor1-render-20261024/README.md)
  устраняет предыдущий short-endpoint gap на CYD и C3. Публичный Tremor
  рендер адаптирован с лицензией: хвост применяет inverse-dB gain, обрезка
  длинной линии сохраняет исходный наклон, wide multiply определён без UB.
  Две SDK/QEMU матрицы по8 допустимых/6 ошибочных случаев на каждой платформе
  сравнивают весь stereo PCM16 с Xiph: max1 при прежнем проектном пределе2,
  без обработки или сдвига сигнала. Пять обычных позиционных случаев
  byte-exact к старым target images; отдельный old-tail image воспроизводит
  все8 прежних векторов, включая три ошибки до65535. Это функциональный
  контроль; внутренний код vendor из него не выводится. Host ASan/UBSan:
  1472 кривые/1501440 bins/2349 wide products/32 NULL memo, canaries и
  сохранность входов проходят. Восемь classifier-тестов, семь construction
  тестов нового корпуса и22 configure-only CMake случая проходят.
  Полный raw capacity/retry gate повторён:535 пакетов/2112000 PCM байт,
  1602 undersized retries; bypass-preflight даёт ожидаемый именованный отказ.
  Same-loader пары используют общий renderer и теперь явно обозначены как
  handle parity. Старые NONPASS и первая ошибка классификатора сохранены.
  ABI, allocations и task/core/stack/priority не менялись. Wide/floor0/
  sequence1, полное G6 и прочие интеграционные/аппаратные gates остаются;
  CYD bridge в radio не включён, отложенные работы не возобновлялись.

- 2026-10-24, CYD-C3-14/G1: [public raw registry checkpoint](../tests/results/vorbis-registered-raw-20261024/README.md)
  проверяет путь регистрации → generic open/process/get_info/close на CYD и C3.
  [Точка входа](../tests/target/vorbis_floor1_positions_qemu/main/registered.c)
  использует только публичный API и один generic handle. На каждой цели
  выполнены14 циклов регистрации/проверки ops/удаления регистрации,
  8 допустимых и6 отклонённых настроек,112 пакетов/225280 PCM байт и312
  undersized retries без потребления входа или изменения выходного буфера.
  Проверены checked open/decode и vendor reset/close pointers; reset не вызывался.
  Полное сравнение PCM с сохранённым Xiph даёт max1 при прежнем пределе2;
  пять обычных случаев побайтно совпадают со старыми target images.
  Два отдельных ESP32 controls достигают точных ранних отказов
  `registry_open_binding` и `registry_decode_binding` на case0 до open/decode,
  очищают public registry и штатно завершаются. Проходят12 protocol host-тестов
  и8 реальных CMake phase-тестов, включая воспроизведение прежнего неверного
  положения проверки. Первые configure-only отказы обеих целей сохранены;
  QEMU в них не запускался. Это частичная квалификация G1. Полные G1/G6,
  reset/Ogg/OOM/SMP, radio/resource/physical gates остаются открытыми.

- 2026-10-24, CYD-C3-14/G1/G3: [public raw reset checkpoint](../tests/results/vorbis-raw-reset-20261024/README.md)
  проходит на CYD и C3 с их собственными SDK, архивами и QEMU.
  Один generic opaque handle на допустимый случай используется последовательно:
  initial reset перед baseline, reset после полного прохода, reset после
  префиксов 7/5 пакетов, после трёх tiny retries и три повторных reset подряд.
  Выполнены 9 вызовов на случай / 72 всего: baseline 112 + replay 448 +
  prefix 96 = 656 принятых пакетов; 312 baseline + 24 reset retries.
  PCM: 225280 + 901120 + 212992 = 1339392 байта. Каждый replay/prefix
  побайтно совпадает с соответствующим baseline; полное сравнение baseline
  с Xiph даёт max1 при прежнем пределе 2. Все 14 свежих reference-команд
  штатно завершаются: 8 допустимых случаев и 6 отказов ошибочным заголовкам.
  Отдельный ESP32 skip-control после baseline/round 0/prefix 7 даёт 2304
  лишних PCM байта и точный `reset_primer_empty`, закрывает handle и очищает
  registry. Проходят
  14 reset protocol, 22 CMake phase, прежние 12 registry protocol и 8 classifier
  host-тестов. Первые SDK попытки сохранены как NONPASS до запуска compiler;
  причина WinError 623 воспроизводится в sandbox, установленный GCC исправен
  вне него. Повторные запуски завершены через обычное разрешение на исполнение.
  Production source/core/stack/priority не менялись. В fixture CYD coordinator
  core 0/worker core 1, C3 core 0; priority 3/stack 16384.
  Espressif 2.6.2 разрешает повторное использование handle после reset и
  запрещает reset одновременно с processing; сценарии последовательные.
  [Xiph restart](https://xiph.org/vorbis/doc/libvorbis/vorbis_synthesis_restart.html)
  задаёт freshly initialized synthesis state. Это частичная квалификация
  G1/G3; полные G1/G3/G6, deferred Ogg, integration/resource/physical gates
  остаются открытыми.

- 2026-10-24, CYD-C3-14/G4/G5: [checked raw-open OOM checkpoint](../tests/results/vorbis-raw-open-oom-20261024/README.md)
  воспроизводит реальную ошибку на прежних CYD/C3 исходниках: отказ четвёртого
  calloc при разборе setup превращался в `FAIL` вместо предусмотренного
  Espressif 2.6.2 `MEM_LACK`. [Исправление CYD](../idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c)
  и такое же исправление C3 сохраняют причину отказа в отдельной task-local
  области каждого open с восстановлением после вложенных вызовов и очистки.
  Новых вызовов allocator, ABI полей, изменений декодирующей арифметики или
  production core/stack/priority нет; стоимость TLS и физические ресурсы не измерены.
  [Тестовый public raw caller](../tests/target/vorbis_floor1_positions_qemu/main/open_oom.h)
  наблюдает 32/36/32/36/36/36/36/36 allocation positions. На каждой архитектуре
  проходят 560 одиночных/постоянных отказов и 560 полных восстановлений:
  7840 recovery packets / 15769600 PCM байт, пустой ledger и целые guards.
  Шесть ошибочных заголовков без OOM сохраняют `FAIL`; четыре nested пары и
  два ordered task-сценария проверяют восстановление и разделение причин
  ошибки на CYD cores 0/1 и C3 core 0. Два отдельных ESP32 control images
  достигают точных `oom_memory_error` на case 0 и `oom_task_error_isolation`
  на case 14 с обязательными префиксами, очисткой и штатным завершением.
  Полный baseline PCM сравнён с 14 свежими Xiph запусками: max1 при прежнем
  пределе2. Recovery равенство подтверждено target memcmp с этим baseline;
  отдельные recovery PCM vectors не сохранены. Проходят 18 OOM protocol,
  37 CMake phase, 12 registry protocol и 8 reference outcome host-тестов.
  Исходные bug baselines, оба corrected targets, controls и offline verification
  сохраняются в архиве.
  Это частичное закрытие raw-open G4/G5; полные G1/G4/G5/G6, остальные
  allocation/lifetime/SMP, deferred Ogg, radio/resource/physical gates остаются.

- 2026-10-24, CYD-C3-14/G6: [полная31 current-source регрессия](../tests/results/vorbis-current-format31-20261024/CHECKPOINT.md)
  сохраняет весь прежний корпус и эталоны:31 open/decode/close,434 пакета,
  738560 PCM байт,964 события. На текущих canonical setup/output/ABI/floor1
  проходят actual SDK6.0.2/Xtensa и все10 owned commands; выбранный ELF
  имеет три wrapper flags в наблюдённом Ninja recipe и linked symbols.
  Сведения о recipe не выдаются за независимое наблюдение исполнения linker.
  Полное численное измерение завершено как NONPASS без изменения предела2:
  15 max1, wide4 max65535, floor0×12 с прежними ошибками; Xiph14/14 relations,
  target12/14. Все31 текущих PCM побайтно равны сохранённым прежним векторам.
  Это подтверждает сохранность результатов и остающиеся ошибки после floor1,
  без вывода о private vendor cause. Сохранённые Xiph WAV и исходные
  dual-reference NONPASS повторно проверены; новых reference-процессов нет.
  Host8 CMake phase +8 link-recipe selection +9 numeric binding проходят.
  Первая попытка с ошибочным аргументом SDK Python сохранена до compiler/QEMU;
  с правильным SDK virtualenv та же frozen source завершилась штатно.
  Production source/task bindings не менялись, bridge не включён в radio.
  [Floor0 precision/range](CYD_VORBIS_FLOOR0_REMAINING.md) зафиксированы как
  требования следующей реализации. Полные G6/прочие gates и physical остаются.

- 2026-10-25, CYD-C3-14: [lookup1 integer root](../tests/results/vorbis-quantvals-20261025/CHECKPOINT.md)
  исправлен в обоих canonical setup. Вместо unchecked степеней используется
  точный целочисленный поиск с проверкой до умножения; размерности не урезаются.
  Host native-long/int32 дают по35975 точных значений под ASan/UBSan; старый
  helper отдельно воспроизводит signed overflow на native64/entries2/dim64.
  Обе отдельные SDK/QEMU сборки whole setup/native ABI проходят по2179
  значений и9 команд, warnings0: Xtensa/core1 и RV32/core0, coordinator0.
  Codec archive и raw decoder не подключены; production core/priority/stack
  не менялись. Двенадцать reader/protocol тестов выявили и закрыли проверку
  пропущенной запятой в C row; final reader повторно проверен на реальных
  сохранённых данных/логах, отдельно от immutable исполнявшегося controller.
  Первые host LF/CRLF и WSL-launch отказы сохранены как отдельные попытки.
  Это исправление helper, а не полная raw/PCM/G6 приёмка; прежний full31
  NONPASS не переквалифицирован. Wide/sequence1/floor0, deferred scopes,
  final Clang/exports, radio/resources и physical остаются в плане.

- 2026-10-25, CYD-C3-14: [owned scaled floor0 core](../tests/results/vorbis-floor0-numeric-20261025/CHECKPOINT.md)
  добавлен по [проекту широкого пути](VORBIS_WIDE_NUMERIC_DESIGN.md), отдельно
  от vendor ABI и production registration. Host60541 операций/60471 численное
  сравнение/49 metadata controls проходят ASan/UBSan; Decimal120 проверяет
  прямые произведения/sqrt, а cosine1145/Bark25542 проверяются отдельно.
  Все168 прежних unit-входов/58368 bins сохранены. Новые SDK/QEMU каждой
  архитектуры захватывают327 случаев/347 событий/16 API-групп, все9 команд
  завершаются нормально; warnings0, cores1/0, coordinator0. Отдельный numerical
  checker проходит654 native coefficient/gain значения с прежними заранее
  выбранными пределами. Capture сам не объявляет numerical PASS.
  Compiler .su показывает максимум208B собственного frame на обеих целях;
  callee/libm/task high-water и физическая производительность не измерены.
  Component сохраняет raw-amplitude до63 бит и диапазон scaled polynomial/log
  gain, не делает Q24 clipping и не ограничивает положительное усиление unity.
  Это численный строительный блок: stable angle path и весь wide synthesis,
  public raw lifecycle/integration, PCM/G6/G8 ещё открыты. Прежний full31
  NONPASS не переобъявлен исправленным; deferred scopes не возобновлялись.

- 2026-10-25, CYD-C3-14: [original-angle floor0](../tests/results/vorbis-floor0-angles-20261025/CHECKPOINT.md)
  добавлен отдельными API к собственному numeric component. Integer phase
  reduction и scaled sine products сохраняют minsub/малые ненулевые углы;
  принимаются все finite binary64, включая отрицательные и DBL_MAX, orders1..255.
  Независимый Chudnovsky/Decimal800..1184 oracle проходит2376 host-случаев
  и28 metadata controls под ASan/UBSan. Точная рациональная проверка Machin/CF
  подтверждает2304-bit2/pi и достаточность1152-bit phase grid; она не подменяет
  проверку libm/всей арифметики. Оба SDK/QEMU проходят200 cases/212 events/8 API
  groups/9 commands, warnings0; отдельный checker повторно вычисляет весь host
  и принимает400 native значений. Собственные compiler frames максимум800/784B
  не включают callee/libm/task high-water. Прежние60541 outputs byte-identical.
  Новые API не подключены к production; сохранение исходных setup/dequantization
  данных, wide synthesis, raw integration и прежние full31 PCM/G6/G8 остаются.

- 2026-10-25, CYD-C3-14: [точные quantization/VQ/LSP значения](../tests/results/vorbis-quantization-20261025/CHECKPOINT.md)
  реализованы по [проекту](VORBIS_QUANTIZATION_DESIGN.md): исходные minimum/delta
  words, lookup1/2, sequence и отдельный floor0 carry сохраняются без раннего
  Q24/double sum. Measure/materialize и vector/scalar/partial LSP APIs используют
  caller storage, uint64 counts/spans и проверку до записи. Lazy scalar проходит
  dimension65535 без полного выходного массива. Affine floor API получает два
  точных слагаемых; phase grid2304/table4096 подтверждены отдельным рациональным
  сертификатом1904/400 bits, без заявления о полной libm/FP точности.
  Host6572/152 controls/79834 exact values/92 math проходят ASan/UBSan; оба native
  SDK/QEMU проходят200 cases/1061 events/152 controls/9 commands, warnings0.
  Отдельный checker повторяет весь host и принимает15036 exact values/184 math
  на400 native случаях. Compiler own frames floor1104/1072B, quant144/128B;
  callee/libm/task high-water не измерены. Обе прежние host-регрессии60541/2376
  проходят с byte-identical outputs. Это самостоятельный слой: полный entropy/
  setup/audio parser, residue/coupling/IMDCT/overlap, PCM/raw integration ещё
  нужны; production cores/display/audio и deferred scopes не менялись.

- 2026-10-25, CYD-C3-14: [полные собственные codebooks/Huffman](../tests/results/vorbis-codebook-20261025/CHECKPOINT.md)
  реализованы по [спецификации и проекту](VORBIS_CODEBOOK_DESIGN.md).
  [Точки входа](../idf/components/native_vorbis_numeric/include/native_vorbis_codebook.h)
  и [реализация](../idf/components/native_vorbis_numeric/codebook.c) разбирают
  sync, ordered/unordered/sparse lengths и quantization, сохраняют исходные
  sparse entry indexes и присваивают коды в порядке записей. Учтена поправка
  2015 года: singleton length1, расход одного бита, оба значения допустимы.
  Sticky EOP, caller storage и проверки capacity до чтения сохраняют retry;
  VQ/floor0 LSP получают настоящие audio words, включая final partial vector.
  Независимый greedy-interval/tree oracle проходит 382 host-сценария, 719 API
  controls, 24603 affine values, 318030 setup и 31580 payload truncation points
  под ASan/UBSan. Оба SDK/QEMU: по 200 cases/1405 events/719 controls/9 commands,
  без предупреждений сборки, worker core1/core0. Отдельное сравнение принимает
  все 400 native cases: 10930 words, 6378 entry/position и 26990 affine values.
  Отдельный ASan/UBSan supplement проходит 140 ошибочных fixtures/290 guarded
  status checks: ordered overrun/length33, reserved lookup3..15, singleton2..32,
  sync/flag truncation и lookup1/dim0. Полный sparse entries16777215/dim65535
  разбирается с одной активной записью и возвращает исходный индекс16777214;
  complete tree32768/dim65535 проходит measure и безопасный capacity refusal.
  Собственный compiler frame LSP wrapper1120/1104B не включает callees/task
  high-water. Clang-Tidy нового parser и quantization проходит без предупреждений
  для обеих архитектур; прежний bounded-int warning floor0 сохранён и разобран.
  Это завершённый слой codebook, а не весь decoder: остальные setup structures,
  floor/residue packet handling, wide coupling/synthesis/PCM и raw lifecycle
  ещё нужны. Прежний full31 PCM NONPASS/G6/G8 и physical acceptance остаются;
  production cores/display/audio и deferred scopes не менялись.

- 2026-10-25, CYD-C3-14: [собственный полный setup и audio prefix](../tests/results/vorbis-setup-20261025/CHECKPOINT.md)
  реализованы по [спецификации и проекту](VORBIS_SETUP_DESIGN.md).
  [Входы API](../idf/components/native_vorbis_numeric/include/native_vorbis_setup.h)
  и [реализация](../idf/components/native_vorbis_numeric/setup.c) сохраняют
  identification, все 256 books/64 floor-residue-mapping-mode descriptors и
  полный configured graph; проверяют scalar/VQ contexts, floor1 65 posts,
  residue powers/divisibility и ссылки. Игнорируемый mapping time byte может
  быть ненулевым; residue bounds и сырые zero floor0 metadata сохранены без
  придуманного constant-floor результата. Четыре caller-owned массива и
  компактный uint32 pool имеют preflight до записи; prefix читает mode/window
  без расхода данных при отказе и сохраняет sticky EOP.
  ASan/UBSan: все 300 host rows/60 controls, 855 books, 28270 config и 26212
  getter words проходят; 67570 ID/304814 setup/775 audio-prefix cut points.
  Все 255 generated positive и 2 retained real-header случая приняты;
  43 malformed остаются в полном сравнении (10 ID/30 setup/3 audio).
  Native SDK/QEMU: по 200 cases/60 controls/3551 events/9 commands, warnings0,
  worker core1/core0. Отдельный checker принимает все 400 native: 1310 books,
  42580 configuration и 39370 getter words; counters per-input cuts на native0.
  Compiler own setup frame2832B на обеих архитектурах не включает callees/task
  high-water. Clang-Tidy setup/codebook/quant проходит без предупреждений обеих
  целей; прежний bounded warning floor0 остаётся. Полные floor/residue packets,
  wide synthesis/PCM, raw lifetime и active zero-floor0 domains ещё нужны;
  full31 PCM NONPASS/G6/G8, deferred scopes и physical acceptance не закрыты.

- 2026-10-25, CYD-C3-14: [собственные floor0/floor1 packets и floor1 curve](../tests/results/vorbis-floor-packet-20261025/CHECKPOINT.md)
  добавлены по [спецификации и проекту](VORBIS_FLOOR_PACKET_DESIGN.md).
  [Пять API](../idf/components/native_vorbis_numeric/include/native_vorbis_floor_packet.h)
  сохраняют полный amplitude/selector, точные affine LSP и широкие scalar Y;
  различают fatal prefix EOP, nominal floor EOP, явный UNUSED и INVALID.
  Order0 потребляет одно слово, gain использует D=1; floor1 выполняет поздний
  clamp, повторную активацию соседей и рисует исходный наклон с endpoint tail.
  ASan/UBSan: 7345 rows/46 controls, 1297 affine/949 raw/83962 bins;
  239 prefix EOP и 6814 nominal floor EOP проверены отдельными входами.
  Native SDK/QEMU: по 200 cases/46 controls/2388 events/9 commands, warnings0;
  независимое сравнение принимает все 400 native cases. Worker cores1/0,
  coordinator0, priority3/stack16384; production affinity не менялась.
  Новый compiler own frame максимум1184B не включает callee/libm/task high-water.
  Clang-Tidy новых units проходит обе цели; прежний bounded warning floor0
  сохранён. General floor0 gain здесь проверяет внутреннюю композицию, кроме
  точных ABSENT/order0 unity identities. Остались residue/coupling, широкое
  умножение spectrum, IMDCT/overlap, production/raw integration и полный PCM;
  full31 NONPASS/G6/G8, zero-domain curve, deferred scopes и physical acceptance
  не переобъявлены закрытыми.

- 2026-10-25, CYD-C3-14: [точные residue0/1/2 и inverse coupling](../tests/results/vorbis-residue-20261025/CHECKPOINT.md)
  реализованы по [проекту и первичным источникам](VORBIS_RESIDUE_DESIGN.md).
  [Три API](../idf/components/native_vorbis_numeric/include/native_vorbis_residue.h)
  измеряют общий dyadic grid по mapped books, декодируют все submaps и сохраняют
  точный знак после cancellation. Нормативные classword modulo, нулевые cascades,
  unaligned type2 и per-word residue0 EOP не заменены упрощениями reference.
  Caller storage имеет динамические 0..34 uint32 limbs/sample и byte scratch;
  capacity проверяется до чтения/записи, INVALID сохраняет cursor/output/state.
  ASan/UBSan проходят 10980 rows/37 controls и 7143388 точных limb сравнений;
  полный host VQ word65535, восемь passes, channel255/coupling256 и signed границы
  включены. Оба SDK/QEMU: по200 cases/37 controls/1353 events/9 commands,
  warnings0; отдельный oracle принимает все400 native и57120 limb значений.
  Новые собственные frames максимум800/768B не включают callee/task high-water.
  Clang всех шести units проходит обе цели без новых warnings; семь protocol
  suites проходят. Сохраняются stream core0/decode-output core1 на CYD и core0 C3.
  Frame orchestration, floor multiplication, IMDCT/overlap, raw/production
  integration, исходный full31 PCM/G6/G8 и physical acceptance остаются.

- 2026-10-26, CYD-C3-14: [пакетная обработка отказов памяти Xiph](../tests/results/vorbis-xiph-packets-20261026/CHECKPOINT.md)
  добавлена отдельными exact edits поверх неизменённой upstream базы: всего33
  фрагмента, 11 изменённых C units и четыре private headers. Host41086 проходит
  ASan/UBSan, исходные31/434/738560 PCM bytes имеют max0 при прежнем допуске2;
  все14 relations сохранены. Есть оба floor × все3 residue, arena-cold/warm,
  оба zero-size allocator policies, каждый наблюдаемый allocation ordinal,
  nominal floor/residue EOP, optional realloc refusal и full close/header replay.
  Прямые48 no-work controls не допускают ненужного scratch allocation;
  counterfactual с исходным synthesis.c воспроизводит NULL store.
  Clang Xtensa/Picolibc проверяет25 units с308 warnings/0errors; это source
  analysis, а не SDK build. [Новый packet target не подготовлен](CYD_XIPH_PACKET_TARGET_DEFERRED_20261026.md)
  после «aborted before dispatch» без указанной причины, новых native случаев0.
  Старый DSP watchdog NONPASS, прочие deferred scopes, format/range,
  channel-sized stacks, radio integration и physical acceptance остаются.

- 2026-10-26, CYD-C3-14: [channel scratch](../tests/results/vorbis-xiph-channels-20261026/CHECKPOINT.md)
  ограничен локальными массивами на два канала; более широкие mapping и
  residue0/1 используют checked arena storage с прежним OOM propagation.
  Моно/стерео не добавляет allocation на этих пяти местах. Неизменённый packet
  fixture проходит 47166 сценариев ASan/UBSan: original 27875, synthetic 19268,
  arena 23; все исходные 31/434/738560 PCM bytes имеют max0 и все 14 relations.
  Собственные frames двух функций в source-only Xtensa GCC -O2 -fno-inline
  стали static 128/112 B вместо dynamic 96/112 B плюс переменные массивы.
  Это не измерение суммарного RAM или реального стека задачи. Clang 25 units:
  316 warnings/0 errors; новые восемь bounded pointer/narrowing сообщений
  сохранены и разобраны. SDK/runtime/255-channel heap qualification остаются.
  [Floor0 amplitude audit](CYD_XIPH_FLOOR0_AMPLITUDE_DEFERRED_20261026.md)
  выявил gaps 31–63 и отдельное ограничение signed-long rate API на ILP32;
  подготовка amplitude tests остановлена автоматической проверкой с сообщением
  possible cybersecurity risk. Новые файлы не созданы, amplitude не менялась.
  Прежние deferred scopes, radio integration и physical acceptance остаются.

- 2026-10-26, CYD-C3-14: [полный unsigned identification rate](CYD_XIPH_RATE_DESIGN.md)
  реализован поверх неизменённой Xiph базы. Conditional unsigned-long field на
  ILP32/LLP64 сохраняет положительный uint32 rate и исходный layout; это явное
  source-type расширение, потребители должны использовать matching overlay.
  Parser использует два checked16 reads, прежний zero guard и signed hints.
  [Квалификация](../tests/results/vorbis-xiph-rate-20261026/CHECKPOINT.md): по 13492
  metadata сценария на host ASan/UBSan и actual ESP32 SDK6.0.2/QEMU, включая
  rate0/INT32_MAX/high half/0xffffffff, все byte prefixes и обе ветви time API.
  12 C/C++ header orders проходят на host и Xtensa; два negative host probes
  подтверждают отказ при original-header shadowing. Native37 units, ABI32 и
  WDT/оба IDLE checks подтверждены. Host packet47166 и прежние31/434/738560 PCM
  bytes сохраняют max0 и14 relations. Clang25:306 warnings/0errors.
  Генератор теперь применяет35 exact edits,11 C units+один codec header,
  четыре private headers и overlay из трёх public headers; два siblings
  скопированы без изменения. Original116 files сохранены. Отложенные
  packet/DSP/amplitude scopes, full encoder/convenience rate, native audio,
  production integration и physical acceptance этим не квалифицированы.

- 2026-10-26, CYD-C3-14: [аудит VQ-диапазона Xiph](CYD_XIPH_VQ_RANGE_DESIGN.md)
  воспроизвёл изменение точно представимых значений из-за ограничения экспоненты.
  [Сохранённые измерения](../tests/results/vorbis-xiph-vq-range-20261026/CHECKPOINT.md):
  14 336 упакованных значений, 8 225 таблиц и 271 626 точных результатов VQ;
  ASan/UBSan без диагностик, Clang трёх модулей — 25 предупреждений / 0 ошибок.
  Существующий точный слой подтверждён независимо; исправление и подключение
  декодера остаются открытыми. Первый отказ компиляции сохранён, шесть
  повреждённых захватов отклонены отдельной проверкой архива. База Xiph,
  ресурсный порт, production-конфигурации и отложенные пункты не менялись.

- 2026-10-26, CYD-C3-14: реализован отдельный
  [владелец исходных данных setup](CYD_VORBIS_SETUP_OWNER_DESIGN.md).
  Полный host корпус и каждый отказ аллокации проверены с ASan/UBSan;
  5 378 успешных открытий, 399 810 ошибок разбора, 2 982 отказа памяти,
  19 038 727 assertions и шесть модулей Clang без предупреждений/ошибок.
  Оба host прогона сохранены; между ними изменён только формат сгенерированной
  тестовой таблицы для устранения padding. Компонент не выбран прошивками.
  Native подготовка остановилась до SDK/QEMU без объяснения причины инструмента;
  это не подтверждённый отказ по кибербезопасности. Полный target gate,
  выбор числового пути и подключение к аудиодекодеру остаются.

- 2026-10-26, CYD-C3-14: добавлен allocation-free
  [точный packet front end](CYD_VORBIS_PACKET_FRAME_DESIGN.md), использующий
  существующие публичные setup/floor/residue APIs. Оба полных host прогона
  совпадают с независимой моделью; сохранены все 434 исходных пакета и различия
  prefix/floor/residue EOP. При отказах workspace metadata/cursor сохраняются;
  результат занимает отдельные compact pools и точный residue grid.
  Новый компонент без Clang-предупреждений; тестовый аллокатор получил явные
  snapshot-инварианты без suppression. GCC LX6/RV32IMC компилирует C/C++ и
  показывает static собственные frames 464/544 B; полный task stack и SDK/QEMU
  этим не квалифицированы. Перед публикацией выполняется локальная проверка
  staged/outgoing файлов, архивов и новой Git-истории по новым правилам privacy.

- 2026-10-26, CYD-C3-14: добавлено точное применение floor1 после inverse
  coupling. Все 256 коэффициентов скопированы из Xiph с исходной лицензией;
  диапазон не сужается до float. Независимая rational/integer модель проверяет
  11 816 765 слов произведений; packet-интеграция сохраняет все прежние 1 311
  сценариев и добавляет два сценария с тихими/связанными каналами. Проверены отказы ёмкости,
  крайние экспоненты, signed domain, неизменность исходников и повтор после
  отказа. Полные исходные captures, диагностики и первые отказы запуска
  инструментов сохранены. Новый компонент Clang0/0; десять предупреждений
  тестовых fixtures разобраны без подавления. SDK/QEMU, floor0 и PCM ещё впереди;
  production CMake, affinity, стеки, backend и отложенные scopes не менялись.

- 2026-10-26, CYD-C3-14: добавлен отдельный адаптер IMDCT с неизменёнными
  butterfly/bitreverse/backward телами Xiph и явным power-of-two масштабом.
  Не добавлен новый алгоритм преобразования или float32 valuelist. Однократное
  округление limb-спектра проверено побитово для всех ширин1–1151; независимый
  complex FFT подтверждён 286 Decimal/rational anchors. Host3 084 случая проходят
  ASan/UBSan, максимальная нормированная ошибка 2.6506574712925612e-15 при
  границе5e-12. Первые отказы WSL и лишнего signed-zero assertion сохранены;
  данные корпуса, ожидания и capture при исправлении comparator не менялись.
  Оба C модуля Clang0/0, C/C++ GCC двух ISA и static frame records сохранены.
  Точная floor0 provenance и её отдельные численные домены, window/overlap,
  full31 PCM bound2/all14 relations, native integration и плата остаются.

- 2026-10-26, CYD-C3-14: независимый SDK/QEMU тест generic floor1 scale завершён
  на ESP32 LX6/core1 и C3/core0. Все выбранные scalar inputs прежнего host корпуса
  сохранены; большие вызовы разделены на bounded batches с прежней общей сеткой.
  Lossless RLE только сокращает передачу: сравниваются все 11 817 093 слова на
  каждой архитектуре. Первая ошибка генерации массива, финальная ошибка печати
  двух CLI и ошибка supplementary tool alias сохранены отдельно от успешного
  SDK/native результата. Чистый replay и 28 protocol controls проходят без
  повторного запуска native. Watchdog/IDLE/core/stack настройки сохранены;
  production, owner/frame/IMDCT и прежние deferred gates этим не закрыты.

- 2026-10-28, CYD-C3-14: добавлен [binary64 вход к прежнему Xiph IMDCT](CYD_VORBIS_NORMALIZED_IMDCT_DESIGN.md).
  [Host-квалификация](../tests/results/vorbis-normalized-transform-20261028/CHECKPOINT.md):
  1 729 сценариев/336 отказов/5 589 927 assertions проходят ASan/UBSan;
  301 248 значений побитово совпадают с прежним limb-входом. Отдельный common
  exponent сохраняет оба int64 endpoint без арифметики или ограничения формата.
  Normal/subnormal ошибки разделены; для underflow сохранён явный абсолютный
  допуск. Production units Clang0/0; три fixture snapshot warning разобраны без
  suppression; C/C++ GCC обеих ISA и собственные frames128/144B сохранены.
  Исходные API/kernel, production и deferred scopes не менялись. Это вход для
  другого представления спектра, а не готовый floor0 gain/PCM или его native gate.

- 2026-10-28, CYD-C3-14: добавлены [полные окна Vorbis](CYD_VORBIS_WINDOW_DESIGN.md)
  для scaled binary64 IMDCT blocks. [Host-квалификация](../tests/results/vorbis-window-20261028/CHECKPOINT.md)
  проходит все36 пар размеров и288 комбинаций flags: 8 160 коэффициентов
  сравнены с70-digit Decimal sine series, 587 520 выходов — с независимым
  scatter oracle; 5 272 отказа и3 494 013 assertions проходят ASan/UBSan.
  Каждый отказ сохраняет фактические input/descriptor bytes до восстановления
  injected NaN/Inf; восемь повреждённых captures отклонены pure reader.
  Reference trailing-zero граница сохранена; exponent не изменяется.
  Window Clang0/0, 16 fixture snapshot warnings разобраны без suppression;
  C/C++ GCC обеих ISA и static own frames сохранены. Overlap/history,
  granule/EOS, floor0/PCM, native gates и production integration остаются.

- 2026-10-28, CYD-C3-14: реализована [история и перекрытие соседних блоков](CYD_VORBIS_OVERLAP_DESIGN.md)
  с двумя независимыми exponent и геометрией Xiph по actual adjacent sizes.
  [ASan/UBSan квалификация](../tests/results/vorbis-overlap-20261028/CHECKPOINT.md)
  проходит864 blocks/648 emits/216 primes, все36 конфигураций,108 resets,
  1 197 984 term values и757 344 точных history values. Сохранены57 376
  cancellation pairs,144 silent-current rows,8 308 refusals и11 895 678 checks;
  десять повреждённых captures отклонены pure reader. Измерены17 962
  underflow operands, в том числе13 767 с exponent>=1074: это явный незакрытый
  full-range synthesis/PCM gate, а не разрешение сузить принимаемый формат.
  Core Clang0/0,19 fixture byte-snapshot warnings сохранены без suppression;
  C/C++ GCC обеих ISA, own push frame128B без callee/task high-water.
  Granule/EOS, floor0/wider fallback, конечный PCM, SDK/runtime и плата остаются.

- 2026-10-28, CYD-C3-14: реализована [точная PCM S16-граница двух scaled terms](CYD_VORBIS_PCM_PAIR_DESIGN.md).
  [ASan/UBSan квалификация](../tests/results/vorbis-pcm-pair-20261028/CHECKPOINT.md)
  проходит2 479 batches/478 388 exact samples,186 refusals/4 986 045 checks,
  все2 047 конечных binary64 exponent fields, widths1..53 и полный int64 scale.
  Сохранены огромная cancellation, half ties с infinitesimal обоих знаков,
  subnormal и все65 538 half-code boundaries;2 033 Fraction/symbolic anchors
  и семь повреждённых captures проходят pure replay. Integer/dyadic сравнение
  не materialize overflowing physical values, не clip отдельные слагаемые и
  не требует heap/VLA/__int128. Core Clang0/0,5 fixture snapshot warnings без
  suppression; C/C++ GCC обеих ISA, public own frame176B без callee/high-water.
  Это точность для переданных dyadic terms; window/IMDCT underflow/rounding,
  floor0, full31 PCM/all14 relations, runtime и производительность ещё открыты.

- 2026-10-28, CYD-C3-14: [подготовка совместного overlap/PCM стенда отложена](CYD_VORBIS_OVERLAP_PCM_DEFERRED_20261028.md).
  По отчёту субагента две записи нового Python-контроллера через apply_patch
  вернули «aborted before dispatch» без причины/operation ID. Это не
  подтверждённый cybersecurity rejection. Root проверил отсутствие controller
  и build directory; compilation/runtime/captures для композиции не запускались.
  Непроверенный C-wrapper сохранён в cold archive по точному SHA и удалён из
  active fixtures после byte-equality/containment проверки. Отдельные host
  overlap/PCM квалификации остаются действующими; совместный и full PCM gates
  не закрыты. После команды остановки повторных запросов/других маршрутов нет.

- 2026-10-28, CYD-C3-14: добавлен [целочисленный granule/EOS timing](CYD_VORBIS_TIMING_DESIGN.md).
  [ASan/UBSan квалификация](../tests/results/vorbis-timing-20261028/CHECKPOINT.md)
  проходит20 019 metadata actions/18 818 audio events, все36 конфигураций/64
  перехода размеров,588 restarts/1 576 gaps и26 359 refusals/1 521 715 checks.
  Все31 исходных потока/434 packet metadata сохраняют184 640 frames per channel;
  12 467 результатов совпадают с byte-identical Xiph metadata fragment на
  безопасном LP64 диапазоне. Unlimited integer model проверяет720 arithmetic
  seeds, включая значения выше counter cap, иEOS у INT64_MAX без лимита
  длины потока; ten damaged captures отклонены. Core Clang0/0,6 fixture
  object-byte warnings сохранены; C/C++ GCC обеих ISA, own push160/144B.
  Это только metadata: decoder/overlap/PCM/native не исполнялись. Initial-page
  transport validation, full31 PCM, floor0/wider synthesis, radio и прежние
  deferred/physical gates остаются; production tasks/configuration не менялись.

- 2026-10-28, CYD-C3-14: [аудит реального floor0 корпуса](CYD_VORBIS_FLOOR0_ROUTE_AUDIT_20261028.md)
  сохранён с [воспроизводимым pure reader](../tests/audit-vorbis-floor0-route.py)
  и161 096-byte JSON. Все434 packet/header identities и14 relation identities
  сохранены; actual host front-end capture совпадает с независимой точной
  моделью. Floor0:12 потоков/168 пакетов/336 каналов,116 736 mapped bins и
  5 376 nonzero residue bins; order5/6, rate48000, map64/128, amplitude6/8,
  offset60, точные LSP7/16..11/4 иresidue{-1,0,1}. Наблюдаемый log2 gain
  [-6.61494,4.01938] — обычный диапазон. Все2 846 distinct gain evaluations
  согласуются между800/150-digit независимыми моделями до1e-100; это convergence
  этого корпуса, не universal error certificate. Root replay byte-identical.
  Новых decoder/linear spectrum/PCM/native запусков нет. Следующее изменение
  должно подключить floor0 к фактическим packet frames и прежнему IMDCT;
  extreme finite gain, precision refinement, window underflow и все прежние
  full31 PCM/bound2/all14 relations/production/deferred gates остаются открытыми.

- 2026-10-28, CYD-C3-14: [floor0 из фактического packet frame](CYD_VORBIS_FLOOR0_SPECTRUM_DESIGN.md)
  подключён к прежнему binary64 IMDCT отдельным, не выбранным production
  компонентом. [Host-квалификация](../tests/results/vorbis-floor0-spectrum-20261028/CHECKPOINT.md)
  сохраняет все434 исходных пакета/336 каналов floor0/532 канала floor1 и
  добавляет13 raw-packet случаев. Точное умножение residue на dyadic factor
  предшествует одному округлению;116 960 joint values совпадают с integer
  oracle. Ошибка5 376 nonzero floor0 values максимум4.85044e-15 при прежнем
  пределе2e-12;751 360 IMDCT values дают error/L1<=8.88178e-16 при5e-12.
  4 522 отказы/5 155 393 guard checks и ASan/UBSan проходят; четырнадцать
  relation identities сохранены, полный PCM ими не квалифицирован.
  Отдельный math корпус покрывает81 384 строки/2 851 560 слов произведений/
  66 151 округление для всех допустимых ширин, включая ties/carries.
  Девять math и десять frame повреждённых captures отклонены pure reader.
  Оба production C-модуля Clang0/0; шесть C/C++ ELF32 source objects для
  LX6/RV32IMC и собственные static frames сохранены без SDK/task high-water
  claims. Все ранние отказы WSL и ошибки fixture/controller сохранены.
  General gain certification, полный wider/precision fallback, underflow окна,
  full31 PCM/bound2/all14 relations, raw/audio-task/native/resources, физическая
  приёмка и все прежние deferred scopes остаются открытыми. Привязки к ядрам,
  backend, приоритеты, стеки и production selection не менялись.

- 2026-10-28, CYD-C3-14: [точное произведение окна и borrowed view](CYD_VORBIS_EXACT_WINDOW_DESIGN.md)
  сохраняют до106 значащих бит без floating product и его underflow. Полный
  signed64 base scale хранится отдельно от shift[-2148,1023]; сумма показателей
  символическая. View копирует descriptors и читает готовое окно по индексу
  без full-block output array. [Host-квалификация](../tests/results/vorbis-window-exact-20261028/CHECKPOINT.md)
  проходит64 940 scalar rows и587 520 точных view products во всех288 shapes;
  все17 962 ранее потерянных произведения, включая13 767 с E>=1074, сохранены
  ненулевыми без deduplication. Все53 ширины обоих operands,106-bit product,
  полные sample exponent fields и signed64 endpoints проверены integer-ratio
  oracle. 8 160 коэффициентов сохраняют прежний Decimal bound2e-15; ASan/UBSan,
  10 360 refusals/14 889 244 guard checks и13 damaged captures проходят.
  Оба новых C-модуля Clang0/0; source-only GCC C/C++ даёт шесть ELF32 objects
  LX6/RV32IMC. Собственные frames product112/112 B, prepare144/160 B и at48/32 B
  не являются high-water задачи. Fixture lint сохраняет23 отображённых/44
  generated warnings, пять default system-header suppressions и0 errors;
  custom suppression нет. Все ранние host/lint/profile ошибки и отдельный
  metadata-only ремонт profile JSON сохранены. Полный pure replay и проверка
  exact artifacts проходят. Старые window/overlap/PCM, production, affinity и
  deferred scopes не менялись. Передача106-bit products в adjacent-block
  addition/PCM, prior transform/gain precision, wider fallback, full31 PCM,
  raw/native/resource/radio и физическая приёмка остаются открытыми.

- 2026-10-28, CYD-C3-14: [точное сложение106-bit продуктов и S16](CYD_VORBIS_EXACT_PCM_DESIGN.md)
  реализовано со связью lazy window views→полная сумма→одно nearest-even
  округление/clamp. Источник с полным int64 base+bounded shift не сужается
  в double. [Квалификация](../tests/results/vorbis-pcm-exact-20261028/CHECKPOINT.md)
  сохраняет все 2 479 старых PCM batches/478 388 outputs и добавляет 208 411 scalar
  случаев, в том числе 432 wide carry/merge и все 65 538 half-boundaries с тремя
  tiny signs. Все 864 DATA-перехода/648 emits дают 598 992 exact S16 outputs и
  1 197 984 точных оконных terms; сохранены 17 962 underflow identities, включая
  13 767 с E>=1074. Два независимых Fraction-набора проходят по 2 033 anchors.
  ASan/UBSan, 4 178 refusals/62 379 152 checks и 14 damaged captures проходят.
  Все старые данные и pre-matrix captures сохранены; поправлен только тестовый
  probe zero→zero, затем добавлен bounded carry matrix и fixture allocator cap.
  Оба новых C-модуля Clang0/0; C/C++ source profiles дают шесть ELF32 objects
  LX6/RV32IMC. Own scalar192/192 B и adapter112/112 B — без callee/high-water.
  Fixture lint сохраняет27 displayed/48 generated warnings, пять default
  system suppressions и0 errors, без custom suppression. Архив хранит все 431
  logical файла через 124 shared SHA blobs. Одинаковые bytes представлены одним
  blob; все случаи и данные сохранены. Полный pure replay и root artifacts
  verification проходят. Старые rounded overlap/PCM APIs и deferred controller
  не выполнялись, production/affinity не менялись. История/ownership, granule/EOS,
  actual packet/frame/IMDCT→этот PCM, full31/bound2/all14, general gain/wider,
  native/resource/radio и физическая приёмка остаются открытыми.


- 2026-10-28, CYD-C3-14: [stateful multi-channel synthesis](CYD_VORBIS_SYNTHESIS_DESIGN.md)
  соединяет actual packet/setup/frame/floor0/floor1/IMDCT с точными106-bit
  window products и конечным S16; caller-owned right-half history хранит
  независимые scale каждого канала. Общий granule/EOS trim применяется ко всем
  каналам, состояние публикуется после полного выхода; любой отказ атомарен.
  [Host и actual SDK/QEMU](../tests/results/vorbis-synthesis-20261028/CHECKPOINT.md)
  проходят все31 исходных потока/434 пакета/738560 PCM-байт, максимум2 к обоим
  host-эталонам при прежнем bound2 и все14 relations. ESP32/core1 и C3/core0
  дают полный PCM, побайтно равный host. Исходный full31 gate теперь закрыт
  для этого кандидата; прежние исторические NONPASS сохраняются как история.
  Host ASan/UBSan также проходит все864 overlap rows/598992 values,20019 timing
  actions, каналы1..255 и50 отказов/повторов;20447 pushes/17828274 values/
  46359453 guard checks. Native сохраняет watchdog/idle checks и stack16384;
  минимум свободного worker stack10876/11048 B, tracked payload peak128970 B
  и ноль live allocations после каждого потока. Это isolated emulator fixture,
  не radio/TLS/physical timing. Owner Clang0/0, source-only C/C++ LX6/RV32IMC
  проходят;17 fixture/helper warnings разобраны без suppression. Архив хранит
  все1487 logical files через424 shared SHA blobs, все попытки, source/object/
  image/config/receipt/log/PCM identities; rebuildable scratch явно учтён.
  Pure replay и отдельная root artifacts/receipt verification закрепляют gate.
  General floor0 gain/wider precision, raw/Ogg/audio-task integration,
  production OOM/backpressure/resources и physical остаются. Production backend,
  affinity/priority/stack и прежние deferred scopes не менялись.

- 2026-10-28, CYD-C3-14: [постоянный public raw owner](CYD_VORBIS_DECODER_DESIGN.md)
  добавлен отдельным, не выбранным production компонентом. Replace публикует
  новый setup/owner после подготовки и сохраняет старый при отказе; process
  проверяет точную S16 capacity до allocation/math, подготавливает все каналы
  и только затем публикует историю/PCM/position/EOS. Нет post-commit callbacks,
  входные пакеты не удерживаются; reset без allocations, clear обнуляет handle
  до освобождений. [Host и actual SDK/QEMU](../tests/results/vorbis-decoder-20261028/CHECKPOINT.md)
  сохраняют весь31/434/738560 PCM contract к обоим эталонам при bound2/all14;
  полный PCM host/ESP32/C3 равен прежнему квалифицированному результату.
  Host ASan/UBSan:589 open+589 replace+302 process OOM refusals,4017 recovery
  spans/4035840 actual PCM bytes,1212 capacity/14187 measures/265 other controls,
 17082734 final checks,13 typed numeric vectors и8 damaged captures проходят.
  Законный255×8192 host выдаёт1044480 zero S16 при достаточном caller budget;
  на MCU actual malloc8355840 отказывает с7 attempts/6 allocs/6 releases/live0,
  затем восстанавливается полный corpus. На каждом target434 resource/capacity,
 62 EOS,31 reset,62 warm retries/31 clears и4536 strict protocol lines проходят.
  Native stack16384/WDT/IDLE/core bindings сохранены; min free stack10348/10600B,
  owner payload peak125642B и caller PCM peak8192B наблюдаются отдельно. Это
  isolated fixture, не production radio/TLS/physical performance. Source-only
  C/C++ LX6/RV32IMC проходят, production Clang2 и fixture7 warnings разобраны
  без suppression. Все infrastructure/fixture failures сохранены отдельно.
  [Точный численный аудит](CYD_VORBIS_CERTIFIED_GAIN_REMAINING.md) фиксирует
  допустимый finite exponent минимум1572bits и следующий certified interval
  contract. General gain/wider IMDCT/history, Ogg/container/audio-task,
  production resources и physical остаются. Прежние deferred scopes не менялись.

- 2026-10-28, CYD-C3-14: добавлен [независимый MPFR-эталон floor0](../tools/codec_benchmark/vorbis_floor0_mpfr_oracle.md)
  с exact affine/rational input, direct-cosine directed intervals и целой частью
  log gain произвольной длины. [Host checkpoint](../tests/results/vorbis-certified-oracle-20261028/CHECKPOINT.md)
  сохраняет все447 исходных packet identities/894 каналов; все336 original active
  floor0 channels сопоставлены с запросами для каждого возможного Bark index.
  8192 уникальных набора и10 дополнительных дают8202 requests;8194 пары256/512-bit
  enclosures вложены. Два tiny finite запроса уточняются1024/2048/4096 bits до
  совпадающих integer floors, включая показатель не менее1572bits. Шестнадцать
  malformed records и явный caller precision budget проверены. Собственный C oracle
  проходит ASan/UBSan; MPFR4.2.2/GMP6.3.0 dependencies не собраны с санитайзерами.
  Это только host-эталон по supplied Bark index: MCU implementation, certified
  Bark selection, wider IMDCT/history, новый PCM, Ogg/audio-task/resources/physical
  им не закрыты. Предыдущие deferred scopes и core bindings сохраняются.

- 2026-10-28, CYD-C3-14: добавлена [проверяемая базовая арифметика LibBF](../idf/components/native_vorbis_bigfloat/README.md)
  для следующего certified gain слоя. Оригинальные файлы автора сохранены;
  отдельная portable-копия имеет две точные правки: корректный int temporary
  для SDK int32_t/long и guard нулевой длины memcpy, найденный UBSan.
  Операции готовят private result и сохраняют destination при отказе; память
  растёт до освобождения старого блока, shrink/free не требуют allocation,
  sticky OOM сохраняется до явного retry. Floor экспортирует signed integer
  произвольной длины без int64 narrowing. Engine envelope 1048576 bits является
  проверяемой границей ресурсов, а не новым ограничением формата Vorbis.
  [ASan/UBSan checkpoint](../tests/results/vorbis-bigfloat-20261028/CHECKPOINT.md):
  по 701 точному Fraction/isqrt сценарию на host64/forced32, 463/825 OOM ordinals,
  1643 capacity refusals и 1253 alias checks в каждом режиме; dense 8192-bit
  произведения исполняют настоящий NTT. [Source profiles](../tests/results/vorbis-bigfloat-20261028/SOURCE_PROFILES.md)
  дают восемь ELF32 объектов LX6/RV32 и чистые adapter/header -Werror проверки.
  [Разбор предупреждений](CYD_VORBIS_BIGFLOAT_WARNING_REVIEW.md) сохраняет 42
  creator diagnostics на цель: 11 относятся к проверяемому closure, остальные
  требуют отдельного контракта при использовании исключённых функций. Никакого
  подавления предупреждений или ослабления санитайзеров нет. Все actual failures
  сохранены. Это ещё не MCU runtime или полный floor0 gain: directed constants/
  trig bounds, Bark certificate, wider IMDCT/history, Ogg/audio-task и ресурсы
  полного radio/TLS/TFT остаются, вместе с физической приёмкой и прежними deferred.
