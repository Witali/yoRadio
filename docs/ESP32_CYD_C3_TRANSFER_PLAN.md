# План переноса улучшений ESP32 C3 на CYD

Дата: 2026-10-18. Ветка: `codex/esp32-cyd-c3-review`.
Worktree: `.worktree/esp32-cyd-c3-review`, исходная база `42bc7bd4`.
Цель: нативный `idf/esp32-cyd2usb-native` для ESP32-2432S028 CYD2USB.
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

## Очередь реализации

Все строки со статусом «Открыт» — предстоящая работа. Размер буфера, порядок
allocation и численные настройки C3 являются кандидатами для CYD A/B,
а не готовыми параметрами нового профиля.

| Этап | Статус | Результат и критерий завершения |
| --- | --- | --- |
| CYD-C3-00 | В работе | План, базовая сборка и исправные host-проверки донорских модулей. Зафиксировать SDK, hash, размер приложения; аппаратные baseline отдельно. |
| CYD-C3-01 | Открыт | Generation на всех стадиях, освобождение decoder/PCM на Stop/EOF/error, terminal marker после последнего PCM, reset/flush output. Тесты реального кода и сборки трёх backends. |
| CYD-C3-02 | Открыт | HTTP/TLS read contract, redirects/status, timeout/retry, ICY metadata и fragmented signatures. Фрагментация 1/7/2048 байт, неверный MIME, ошибки и отмена. |
| CYD-C3-03 | Открыт | Подтверждение MP3/ADTS кадров, ID3, форматные переходы и codec drain. Byte-exact replay, truncated EOF, ложные headers и ограниченный search budget. |
| CYD-C3-04 | Открыт | Queue leases, независимый terminal/control slot, ограниченный рост, prefill и tail coalescing. Concurrent producer/consumer и OOM; выбрать ёмкости по CYD. |
| CYD-C3-05 | Открыт | Health, heap/largest block, ошибки allocation/decode/write, DMA и стеки; CPU по обоим ядрам. Отдельно quiet и diagnostic сборки. |
| CYD-C3-06 | Открыт | Общая модель radio/settings, CSV offset index и recovery, станции Next/Prev, корректный format/bitrate/title. Повторный boot и fault injection без потери файлов. |
| CYD-C3-07 | Открыт | WebSocket snapshot/events, динамические страницы, capabilities, async static workers, bounded uploads. Две вкладки, медленный клиент, reconnect и rollback файлов. |
| CYD-C3-08 | Открыт | App-only OTA, maintenance и recovery UI. Неверный target/image, оборванная/медленная загрузка и сохранение NVS/SPIFFS. |
| CYD-C3-09 | Открыт | Wi-Fi profiles/reconnect/RSSI, power policy, timezone/SNTP и runtime settings. AP/client и поздняя потеря сети. |
| CYD-C3-10 | Открыт | Общий normalizer, коэффициенты gain на блок, PCM layout, flush/reset ресемплера. Golden PCM и отдельные PDM/continuous/legacy сравнения. |
| CYD-C3-11 | Открыт | TFT станция/песня/состояние, brightness, clock/blank, touch/BOOT/optional encoder через общий radio control. Проверить GPIO и нагрузку SPI. |
| CYD-C3-12 | Открыт | Portable custom FLAC и оптимизации hot loops против Espressif. PCM exactness, 8–24 bit/decorrelation/LPC/Rice, watchdog и физический A/B. |
| CYD-C3-13 | Открыт | TLS/heap/IRAM/stack политика после измерений CYD. Full-record TLS, раннее освобождение старого codec, сохранение сетевого headroom. |
| CYD-C3-14 | Открыт | Отдельный аудит Xtensa AAC/Vorbis ABI и только затем compact owners/repair. Archive hashes, layout, OOM и PCM сравнены на ESP32. |
| CYD-C3-15 | Открыт | Воспроизводимый production wrapper, экспорт firmware и единая приёмка HTTP/HTTPS/кодеки/WebUI/OTA/длительное воспроизведение для каждого backend. |

## Карта функций и мест в коде

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
| Dynamic pages, recovery page и Arduino-free templates | [web_service.c](../idf/esp32c3-oled-native/main/web_service.c), [web_pages_bridge.cpp](../idf/esp32c3-oled-native/main/web_pages_bridge.cpp) | CYD сейчас только отдаёт SPIFFS assets; общие HTML сами по себе не реализуют API. |
| Async static workers, gzip и socket budget | [web_service.c](../idf/esp32c3-oled-native/main/web_service.c), [проверки](../tests/esp32c3-web-static-workers.test.js) | CYD synchronous `static_handler`, сейчас 4 sockets; пересчитать бюджет вместе с WS/OTA. |
| Streaming multipart uploads, temp/backup, playlist index rollback | [web_upload.c](../idf/esp32c3-oled-native/main/web_upload.c), [web_file_form.h](../idf/esp32c3-oled-native/main/web_file_form.h), [web_multipart.h](../idf/esp32c3-oled-native/main/web_multipart.h) | CYD новые upload routes; ограничить RAM размером chunk, сохранить Wi-Fi/CSV/assets при ошибке. |
| Firmware OTA, target/size validation, abort и maintenance | [web_ota.c](../idf/esp32c3-oled-native/main/web_ota.c), [ota_upload.c](../idf/esp32c3-oled-native/main/ota_upload.c) | CYD [partitions.csv](../idf/esp32-cyd2usb-native/partitions.csv), [CMakeLists.txt](../idf/esp32-cyd2usb-native/main/CMakeLists.txt); не менять partition table и bootloader автоматически. |
| Wi-Fi profiles, RSSI, reconnect и активное/idle power policy | [network_service.c](../idf/esp32c3-oled-native/main/network_service.c) | CYD [network_service.c](../idf/esp32-cyd2usb-native/main/network_service.c). Проверить AP fallback и подключение после поздней потери сети. |
| Timezone, SNTP retry и clock state | [time_service.c](../idf/esp32c3-oled-native/main/time_service.c) | CYD service task и TFT clock; не зависеть от OLED/deep sleep. |
| BOOT gestures, rotary encoder, volume и wake | [app_main.c](../idf/esp32c3-oled-native/main/app_main.c), [encoder_input.c](../idf/esp32c3-oled-native/main/encoder_input.c) | CYD [board_config.h](../idf/esp32-cyd2usb-native/main/board_config.h): BOOT GPIO0; touch и encoder выбирать по свободным выводам. |
| Brightness, clock/blank, scrolling и единый playback snapshot | [oled_display.c](../idf/esp32c3-oled-native/main/oled_display.c), [display_settings.c](../idf/esp32c3-oled-native/main/display_settings.c) | Перенос поведения в TFT [app_main.c](../idf/esp32-cyd2usb-native/main/app_main.c), сохранить [cyd_display.c](../idf/esp32-cyd2usb-native/main/cyd_display.c); OLED layout не переносится. |

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
