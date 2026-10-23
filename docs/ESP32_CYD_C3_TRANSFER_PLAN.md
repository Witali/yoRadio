# План переноса улучшений ESP32 C3 на CYD

Обновлено: 2026-10-20. Ветка: `codex/esp32-cyd-c3-review`.
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
| CYD-C3-14 | В работе | [Аудит и план Vorbis/Ogg](CYD_VORBIS_TRANSFER_DESIGN.md) подтверждают шесть проблем в реальных Xtensa archives2.6.2. Изолированный ESP32 bridge добавлен в `cbb69fdad`, в основной radio runtime пока не подключён. [Квалификация](../tests/results/cyd-vorbis-bridge-20261020/README.md): actual SDK6.0.2/Xtensa, три canonical translation units, 535 raw packets/2,112,000 byte-exact PCM bytes и 1602 undersized retries; bypass-preflight variant даёт точный ожидаемый отказ, 21 CMake configuration проверена. Private layout подтверждён частично. [Raw8192 format regression](../tests/results/cyd-vorbis-format-20261020/README.md) закрывает одно ограничение G6: разрешены блоки 8192 при 48 000/63 999 Гц; пять пар дают 340 сравнений пакетов и 4 631 808 точных PCM байт, четыре bad-header controls и восстановление старого guard проходят. Полное G6 и radio integration остаются открыты. [Расширение Ogg target-проверок отложено](CYD_VORBIS_OGG_DEFERRED_20261020.md) после автоматической проверки безопасности: SDK compile завершён, observer-selection отказал до QEMU; ноль новых runtime случаев квалифицировано. Ogg EOF/reset, allocation failure/reopen, concurrent scopes, format/conformance, полная callback ABI и audio-task интеграция остаются. AAC compact owners требуют отдельной адаптации; ранее отложенный private owner-view не исследовался и остаётся отложенным. |
| CYD-C3-15 | В работе | [Production wrapper](../idf/esp32-cyd2usb-native/PRODUCTION_BUILD.md) и верифицированный экспорт реализованы; 42 host tests проходят, 1 symlink case пропущен. Изолированный sdkconfig сохраняет аппаратные настройки и обеспечивает минимум два SNTP servers. [Шесть CYD сборок после N5](../tests/results/cyd-network-settings-20261020/SDK.md) проверены: vendor/custom FLAC во всех трёх backend; [C3 N4 image](../tests/results/network-power-transfer-20261019/SDK.md) сохраняет отдельный baseline; конфигурации, image/ELF/compiler hashes, task affinity и запас OTA сохранены. Фактические DWARF размеры структур и static symbols зафиксированы без заявления об экономии heap. Единая физическая приёмка HTTP/HTTPS/кодеки/WebUI/OTA/длительное воспроизведение каждого backend ещё впереди. |

## Что осталось по переносу

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
- **Этап 14, Vorbis/Ogg:** завершить [изолированный ESP32 bridge](CYD_VORBIS_TRANSFER_DESIGN.md)
  и подключить к actual audio task после Ogg EOF/reset, allocation failure/reopen,
  concurrent scopes, полной callback ABI и format/conformance проверок. Raw PCM
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
  Следом проверить публикацию floor0 полей и actual публичную integer-кривую;
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
  Остальные gaps: sparse-single/map1-single, остальные wide widths/dimensions
  и mapping/format случаи.
  Полное G6 открыто; bridge в radio не подключён.
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
  Архив746 файлов/7535253 байт сохраняет27 hash-only binary omissions и
  фактический ELF header64. Manifest SHA256:
  `4126c63d4fa6c9699d094b965961055ed9ea4c112bcc9d7b2cfdf5c84d7ad237`.
  [Автономная проверка](../tests/results/cyd-vorbis-owned-book-verification-20261023/README.md)
  staged и конечного canonical каталога из другого cwd завершена0.
  Первый offline verifier ошибочно считал разные headers с одинаковым
  basename одним повторённым путём; его NONPASS и исправление на полные пути
  сохранены отдельно от actual unit PASS и успешного повторного verifier.
