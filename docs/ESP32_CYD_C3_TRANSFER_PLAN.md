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
| CYD-C3-05 | В работе | SMP-safe health подключён к pipeline и `/api/native/health`: heap/internal/DMA, input occupancy, ошибки, optional CPU/stack по двум ядрам. Host core/HTTP/lifecycle, SDK quiet/diagnostic и полный lint проходят; images `b7362172` сохранены. Backend DMA telemetry и физические измерения отдельно. |
| CYD-C3-06 | В работе | Общий radio controller, index recovery, last station/SmartStart, Next/Prev/Toggle и HTTP API подключены к CYD. Pending-state, boot/NVS failure, stale cache и concurrency проверены. Возобновлённый format/bitrate и audio settings [программно квалифицированы](../tests/results/cyd-c3-format-dsp-20261018/README.md): 51 stream/80 settings запросов, обе startup/format цели, SDK и полный lint проходят. Дальнейшие WebUI/runtime settings относятся к этапам 07/09; физическая приёмка отдельно. |
| CYD-C3-07 | Программная часть выполнена | Native UI, snapshots/events, два async static workers, bounded multipart uploads, восстановление файлов, публикация CSV/index парой и Wi-Fi save/reboot реализованы. [Host-проверки](../tests/results/native-web-transfer-20261018/HOST.md), [матрица RFC 6455](WEBSOCKET_RFC6455_AUDIT.md) и [TLS/WSS](WEBSOCKET_TLS_PLAN.md): полный host TCP pipeline — по164 сценария, combined WSS — по14. [Четыре GCC images](../tests/results/native-web-transfer-20261018/SDK.md) сохранены из чистого `6db5651a`. Полное соответствие на плате, ресурсы TLS/audio, две вкладки и медленный клиент требуют физической квалификации. |
| CYD-C3-08 | Программная часть выполнена | [Общий image sink](../idf/components/native_ota/include/native_ota_sink.h), остановка трёх audio owners, атомарная reboot reservation и capability-gated UI реализованы. [Host-квалификация](../tests/results/native-ota-transfer-20261018/HOST.md): CYD83/C3148 concurrent scenarios, реальный HTTP/HTTPS pipeline44 и целевые semantic mutants проходят с ASan/UBSan. [Четыре GCC images](../tests/results/native-ota-transfer-20261018/SDK.md) сохранены из чистого `ab1e4c6e` с прежними SDK настройками и core bindings. [Проект и входы кода](CYD_OTA_TRANSFER_DESIGN.md) описывает target/slot и timeout/cleanup. Физическая OTA/data/power-loss приёмка отдельно; автоматический rollback требует отдельного bootloader baseline. |
| CYD-C3-09 | В работе | Общий checked SNTP backend, coherent C3 time settings, CYD timezone/SNTP service и private Wi-Fi desired store реализованы. [Host-квалификация](../tests/results/native-runtime-transfer-20261018/HOST.md): время46 и Wi-Fi124 реальных HTTP/TLS сценария, полный clang-tidy CYD46/C364 units без tool errors. CYD startup/IP hooks сохраняют affinity; пустой файл не подключает старый профиль драйвера. HTTP/UI keep/set/revision и три legacy imports используют bounded I/O; публичное скачивание паролей закрыто. [Проект времени](CYD_TIME_TRANSFER_DESIGN.md) и [Wi-Fi](CYD_WIFI_PRIVACY_TRANSFER_DESIGN.md) перечисляют входы. [Четыре GCC images](../tests/results/native-runtime-transfer-20261018/SDK.md) сохранены из чистого `8bcacfe9`: core bindings прежние, единственная CYD SDK разница — два SNTP servers, C3 config неизменна. [Runtime N0–N3](CYD_NETWORK_RUNTIME_TRANSFER_DESIGN.md) реализован: immutable boot cache до пяти профилей, постоянный owner, late reconnect/wrap/APSTA, checked snapshot и RSSI validity/age. [Квалификация](../tests/results/cyd-network-runtime-20261019/README.md): owner44 + четыре controls, loader/netif/rollback/HTTP/WS/UI и Xtensa component compile проходят. [N4 power](../tests/results/network-power-transfer-20261019/README.md) подключён к обеим платформам: generation intent, bounded owner-only set_ps, actual audio/maintenance/retry и полный clang-tidy CYD50/C365 проходят без новых предупреждений. [Пять полных GCC exports](../tests/results/network-power-transfer-20261019/SDK.md) из чистого `489c9f819` сохранены, включая CYD custom FLAC PDM; target/OTA/configuration/affinity проверены. [N5 hostname/AP timeout](../tests/results/cyd-network-settings-20261020/README.md) подключён к runtime, HTTP и WebUI: 82 owner случая/12 controls, HTTP80/7, UI48/14, actual NVS/reboot и полный Clang52/86warnings/0errors проходят. Настройки сохраняются без разрыва online соединения; optional AP timeout default0 использует checked immediate reboot lease без durable pending запроса. [Шесть полных CYD exports](../tests/results/cyd-network-settings-20261020/SDK.md) из чистого `195cd3b0e` проверены для vendor/custom FLAC и всех трёх backend; конфигурации и core bindings сохранены. Физическая AP/client/DHCP/reboot проверка остаётся. |
| CYD-C3-10 | В работе | Gain рассчитывается один раз на packet; [общий normalizer](../tests/results/cyd-normalizer-20261018/README.md) подключён ко всем трём backend через owner-only DSP без изменения input PCM. [Итоговая квалификация](../tests/results/cyd-c3-format-dsp-20261018/README.md): HTTP controls, golden PCM, reset/layout/EOF и полный lint проходят. [PCM 8/16/24/32 и resampler](../tests/results/cyd-startup-pcm-web-20261018/HOST.md) квалифицированы: до 1359 сценариев/backend, исправлены PDM rate-tail и DAC priming/short writes. [Новые SDK images](../tests/results/native-warning-fixes-20261018/SDK.md) сохранены; PDM DSP/layout symbols — 555 B DRAM, soft-limit LUT — 1170 B flash (без linker padding). Физическая приёмка остаётся. |
| CYD-C3-11 | Исключён | Перенос дисплея, рендеринга, физических controls и других аппаратных функций C3 не входит в задачу по уточнению пользователя. |
| CYD-C3-12 | В работе | [Optional custom FLAC runtime](CYD_FLAC_TRANSFER_DESIGN.md) подключён к actual CYD decoder task; vendor остаётся default. [Квалификация](../tests/results/cyd-flac-runtime-20261019/README.md): 520 exact PCM сравнений, 4304 metadata-prefix случая, 24 allocation failure/reopen и lifecycle/maintenance controls, actual Xtensa custom/vendor component compile. Source depth и PCM16 разделены; workspace освобождается до maintenance ACK. [Полный custom PDM app export](../tests/results/network-power-transfer-20261019/SDK.md) проверен по ELF/image/configuration; текущий host rerun повторяет 520 точных PCM сравнений. [Все три custom backend exports](../tests/results/cyd-network-settings-20261020/SDK.md) собраны и проверены; custom-path QEMU, watchdog/ресурсы и физический vendor/custom A/B остаются. |
| CYD-C3-13 | Открыт | TLS/heap/IRAM/stack политика после измерений CYD. Full-record TLS, раннее освобождение старого codec, сохранение сетевого headroom. |
| CYD-C3-14 | Открыт | Отдельный аудит Xtensa AAC/Vorbis ABI и только затем compact owners/repair. Archive hashes, layout, OOM и PCM сравнены на ESP32. |
| CYD-C3-15 | В работе | [Production wrapper](../idf/esp32-cyd2usb-native/PRODUCTION_BUILD.md) и верифицированный экспорт реализованы; 42 host tests проходят, 1 symlink case пропущен. Изолированный sdkconfig сохраняет аппаратные настройки и обеспечивает минимум два SNTP servers. [Шесть CYD сборок после N5](../tests/results/cyd-network-settings-20261020/SDK.md) проверены: vendor/custom FLAC во всех трёх backend; [C3 N4 image](../tests/results/network-power-transfer-20261019/SDK.md) сохраняет отдельный baseline; конфигурации, image/ELF/compiler hashes, task affinity и запас OTA сохранены. Фактические DWARF размеры структур и static symbols зафиксированы без заявления об экономии heap. Единая физическая приёмка HTTP/HTTPS/кодеки/WebUI/OTA/длительное воспроизведение каждого backend ещё впереди. |

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
