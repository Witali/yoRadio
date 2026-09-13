# ESP32 CYD native: перенос улучшений ESP8266

Дата аудита: 2026-09-13. База Git: `main`, `895983e`.
Target: `idf/esp32-cyd2usb-native`, ESP32-2432S028 CYD2USB.
Arduino CYD — эталон возможностей, но целевая прошивка остаётся native ESP-IDF,
не Arduino и не `esp32-cyd2usb-minimal`.

Это план по исходникам, Git и сохранённым результатам. В этом аудите не
проводились новые сборки, прошивки или аппаратные замеры. Полная сводка
изменений ESP8266: [парный план C3](ESP32C3_ESP8266_IMPROVEMENTS_PLAN.md).
Все пункты реализации ниже открыты намеренно.

## 1. Фактическая исходная точка CYD

| Подсистема | Что найдено в коде | Следствие |
| --- | --- | --- |
| WebUI | REST status/play/stop/settings/reconnect, синхронная статика, 4 HTTP sockets; `/ws` отсутствует | Общих HTML недостаточно: backend ещё не поддерживает протокол YoRadio. |
| Радио | Play принимает URL; нет C3-модулей radio_control/playlist/runtime settings | Нужны модель станций, индекс, сохранение выбора и единые команды. |
| Метаданные | `Icy-MetaData: 0`, ограниченный status | Сначала полноценное состояние станции/песни, затем его отображение. |
| Pipeline | Compressed ring 16 КиБ, PCM ring 8 КиБ; stream core0/prio3, decode core1/prio5, output core1/prio6 | Разделение задач уже есть, четвёртая PCM-задача ESP8266 не нужна. |
| Codecs | MP3/AAC Espressif default, альтернативные Helix/minimp3; Opus/Vorbis/Ogg включены в sdkconfig.defaults | Сначала проверить штатные backends, не заменять вслепую Helix/Opus ESP8266. |
| Формат | Espressif получает info каждый кадр, legacy callback фиксирует первый | Исправлять legacy, не ломать уже динамический штатный путь. |
| DSP/settings | Q15 volume/balance, shared NVS; normalizer не подключён к output/CMake | Интегрировать общий normalizer и полный readback, не писать второй DSP. |
| TFT | Цветные зоны по network mode в app_main, аппаратный драйвер дисплея есть | Станция/песня/touch UI — отдельная работа, не просто замена HTML. |
| Wi-Fi | Читается первый допустимый профиль, startup retry/AP fallback | Нужны остальные профили/RSSI и проверка recovery после поздней потери связи. |
| Flash | Два app по `0x1B0000`, SPIFFS `0x90000` = 576 КиБ | Не копировать ESP8266-разметку 256 КиБ; OTA-слоты не равны готовому WebUI OTA. |
| Железо | Dual-core ESP32, default 240 МГц, GPIO26 audio, PDM/continuous DAC/legacy DAC, LED default OFF | Не копировать LX106/RISC-V asm, GPIO3, OLED layout или ESP8266 DMA. |

Проверенные файлы: [web_service](../idf/esp32-cyd2usb-native/main/web_service.c),
[audio_service](../idf/esp32-cyd2usb-native/main/audio_service.c),
[app_main](../idf/esp32-cyd2usb-native/main/app_main.c),
[board_config](../idf/esp32-cyd2usb-native/main/board_config.h),
[partitions](../idf/esp32-cyd2usb-native/partitions.csv).

## 2. Источники и границы переноса

| Коммиты-ориентиры | Переносимое улучшение | Ограничение |
| --- | --- | --- |
| C3 `3d29972`; ESP8266 `0ba0e4d`, `92cb522` | Async static files, несколько вкладок, events | Штатный ESP-IDF HTTP/WS, не собственный socket scheduler ESP8266. |
| `c6d1418`, `c6e4427`, `6bb08e8`, `91889f4` | Общий JS/initial snapshot/settings | Уже общие файлы, нужен backend и актуальная доставка assets. |
| `0da6a59`, `937173e`, `20a596f` | Streaming upload, index rollback, recovery/OTA | Контракты/тесты общие, flash/OTA backend — ESP32. |
| `0645c41`, `8a6d2ce`, `fa1abc1` | Source/PCM format и корректный UTF-8 | Общий Helix adapter исправляется один раз для C3/CYD. |
| `be0207e`, `cd955f1` | 0–100, capabilities, round-trip настроек | Сохранить старый NVS/gain и совместимость WebUI. |
| `609bbdc`, `96a818f`, `5c4391f`, `b5d7b7a` | Владение ресурсами, отмена/reuse, deadline | Дефект ESP8266 socket port не доказывает такой же дефект ESP-IDF. |
| `f3138f2`, `b21979b`, `9f991d6`, `851c7d2` | Reorder reuse, blocks, AAC lookup | Подключать к shared adapter после PCM и физических A/B. |
| `b056590`, `ff49a46`, `bf82ca2` | Opus fixed-point/bounds/владение PCM | Portable C кандидат/тесты, не доказанное ускорение LX6. |
| `3b108c7`, `d155eaf`, `d61fb1b`, `e97e7ef` | CPU/heap/continuity диагностика | Учёт двух ядер; публичные heap_caps API вместо private heap walker. |

Native/WebRadio/KaRadio не объединять в новую кодовую базу. WebRadio и KaRadio
остаются сравнительными стендами. Незакоммиченные WebRadio и SILK-scratch
правки, перечисленные в плане C3, не считать выпущенными или проверенными.

## 3. План по этапам

Каждый ID — отдельный логичный этап/коммит со своими регрессиями. При общем
изменении проверяются C3/CYD и затронутые Arduino-профили. Приёмка одной платы
не является приёмкой другой.

### CYD-00 · P0 · Baseline

- [ ] Зафиксировать SDK/compiler/sdkconfig/audio backend, hash, flash/DRAM/IRAM,
  heap/largest block, стеки, cores/priorities. Не выводить размеры из старого README.
- [ ] MP3/AAC/FLAC/Ogg-Opus/Vorbis через существующий URL API, HTTP/HTTPS;
  записать дефекты текущего управления и недостатки REST-only WebUI.
- [ ] Отдельные сборки/результаты для hardware PDM, continuous DAC, legacy DAC.
  Ввести базовые CPU/idle/continuity счётчики из CYD-08 уже на этом этапе.

### CYD-01 · P0 · Общий native WebUI core

- [ ] После C3-01…04 извлечь web/protocol/settings adapters в `idf/components`
  небольшими коммитами, проверить эквивалентность C3, затем подключить CYD.
  Не создавать два расходящихся web core.
- [ ] Shell/variables/capabilities, `/ws` на порту 80, initial snapshot,
  status/heartbeat/reconnect, shared gzip assets и recovery page.
- [ ] Async static workers: ограниченные queue/scratch, begin/complete/cleanup
  на всех ветках; медленная вкладка не блокирует команды и не портит payload.
- [ ] Рассчитать socket budget с HTTP/WS/TLS/listener/control по своему SDK.
  Четыре нынешних сокета и численные лимиты ESP8266 не считать достаточными.
- [ ] Старые `/api/native/*` оставить для тестов/совместимости, не удалять как
  побочный эффект переноса. Версионировать будущие несовместимые изменения.
- [ ] Browser tests: две вкладки, player+settings, cold/warm, reconnect,
  spinner, Play pending и ошибки статических файлов.

### CYD-02 · P0 · Станции, индекс и устойчивость плейлиста

- [ ] Общий radio_control: ID/name/URL, Play/Stop/Next/Prev, last station NVS,
  единый владелец команд от браузера и физических органов управления.
- [ ] Offset index для CSV: валидный индекс загружается на boot, rebuild только
  при необходимости; весь список не выделяется в RAM при Next/Prev.
- [ ] C3-03/`937173e`: temp/backup, откат при неуспешном индексе, same-file
  detection, boot recovery, повреждённый/устаревший индекс и equal-size CSV.
- [ ] Event только при успешной реальной замене. Выбор строки запускает её и
  выделяет без reload/scroll; начальная прокрутка один раз, аппаратные Next/Prev
  и согласованные пользовательские действия — отдельные события.
- [ ] Не копировать HTTP-only filtering ESP8266: сохранить HTTPS/FLAC/Vorbis/
  Opus и другие реально поддержанные target потоки. Возможности входят в
  проверку актуальности индекса/кэша, не в постоянный запрет станций.
- [ ] Исполняемые install/index/streaming тесты, faults и concurrent selection.

### CYD-03 · P0 · Аудиосостояния, ICY, переключение ресурсов

- [ ] Координация generation/decoder-release из C3 с ESP8266 fault/reconnect
  тестами. Старые retry/PCM callbacks не отменяют новую команду пользователя.
- [ ] Stop прекращает stream read/ICY, старые очереди дренируются/отбрасываются
  с корректным ownership. Несовместимый decoder освобождается до нового TLS
  peak; совместимый workspace переиспользуется после reset.
- [ ] Вместо `Icy-MetaData: 0` — стандартный ICY parser: чистые audio bytes
  декодеру, StreamTitle в bounded snapshot; без фильтрации корректного текста.
- [ ] Requested/Connecting/Playing/Stopped/Error разделены. Playing означает
  прогресс PCM, а не принятие POST `/play`; ошибка сохраняется через cleanup.
- [ ] Кодек по содержимому, включая Opus/Vorbis внутри Ogg; URL — лишь подсказка.
  Реальный bitrate приоритетнее icy-br, старый формат очищается при смене.
- [ ] First-format legacy и HE-AAC исправить общим C3-01 adapter. Штатный
  Espressif per-frame info сохранить. Source и output channels/rate не смешивать.
- [ ] Все порядки MP3/AAC/FLAC/Vorbis/Opus, Stop на DNS/TLS/decode/output,
  битые headers/ICY/UTF-8 и каждый allocation failure с полным освобождением.

### CYD-04 · P1 · Settings, Wi-Fi, uploads, OTA

- [ ] Общая модель settings/capabilities и проверка readback/save/apply каждого
  поля. AP — Wi-Fi, client — полная страница. Touch/SD/weather/EQ не объявлять
  работающими до реализации в соответствующем профиле.
- [ ] Несколько Wi-Fi профилей, RSSI/reason, поздний disconnect/recovery,
  предупреждение о пробелах SSID без trim. AP-delay и stream timeout различать.
- [ ] Low-priority timezone/SNTP из C3 time service; не копировать ESP8266
  private lwIP работу без проверки соответствующего ESP-IDF API.
- [ ] C3-02/03: bounded multipart, прежние `/upload`/`webboard` формы,
  rollback Wi-Fi/CSV/WebUI и error feedback; память не зависит от размера файла.
- [ ] Application OTA через `esp_ota_*` в неактивный слот: target/size/validity,
  abort, первый запуск/self-test, rollback и совместимость bootloader.
  Не менять разметку без необходимости/бэкапа; сохранить NVS и файлы пользователя.
- [ ] Обслуживание firmware/files — явный режим с безопасной остановкой;
  обычный WebUI не приостанавливает всё аудио. HTTP log только opt-in debug.

### CYD-05 · P1 · DSP и громкость 0–100

- [ ] Подключить общий fixed-point AudioNormalizer/табличный limiter из C3,
  кэш параметров и предвычисления; время 5 секунд, сброс накопленного boost
  до 0 dB на Next/Prev. Не вводить второй независимый normalizer.
- [ ] Настройки сохраняются/readback и реально применяются в output owner;
  reset DSP не выполняется одновременно из другого ядра.
- [ ] C3-05/[общая шкала](VOLUME_0_100_SYNC_PLAN.md): 101 уровень, старый
  NVS/gain, capability, совместимый JS до новой семантики API, все органы управления.
- [ ] Разделить физический mono и mono-вход: текущий mono-вход уже игнорирует
  balance, но stereo перед downmix взвешивается по balance. Для mono-output
  согласовать правило «balance не влияет»; не применять его к двум выходам C3.
- [ ] Golden PCM для L-only/R-only/противофазы, mute/extremes, normalizer/limiter,
  round-trip после питания и всех PDM/DAC backends. Стоимость DSP мерить отдельно.

### CYD-06 · P1 · TFT UI и физическое управление

- [ ] Заменить цветные зоны станцией/песней, Connecting/Playing/Stop/Error,
  codec/bitrate, RSSI/буфером из того же snapshot, что получает WebUI.
- [ ] Arduino CYD поведение адаптировать к native driver: dirty regions,
  асинхронные TFT transfers, без audio mutex во время вывода.
- [ ] Touch/BOOT/optional encoder через radio_control, обратные события в
  WebUI; проверить GPIO-конфликты TFT/touch/SD/audio, без копирования C3 GPIO9.
- [ ] Яркость, clock/blank и wake-on-input — CYD layout, не OLED-глифы/вторая
  строка 72×40. Существующий аппаратный драйвер дисплея сохранить.
- [ ] SD playback отдельным последующим этапом: ошибки, индекс, выбор Web/SD;
  скрывать capability, пока этот тракт не реализован и не испытан.

### CYD-07 · P2 · Скорость и память аудиотракта

- [ ] До изменения buffers измерить ready PCM time, самый большой burst,
  DMA/FIFO underrun и decode/output задержки. Сохранить имеющиеся три задачи.
- [ ] В `pcm_mono_sample` gain вычисляется каждый отсчёт: вынести коэффициенты
  на блок/изменение, mono/stereo dispatch за loop; сравнить PCM и GCC assembly.
- [ ] Shared Helix MP3 block/reorder, отдельно AAC block/window/Huffman A/B
  по C3-08. Не уменьшать stereo/SBR buffers ниже необходимого. Выбор 512 AAC
  frames и показатели экономии/CPU ESP8266 не являются готовой нормой CYD.
- [ ] 32-битная arena/IRAM — поддержанный allocator, типы/выравнивание и аудит
  всех accesses. Не помещать byte/halfword/float buffers в 32-bit-only память.
- [ ] Custom fixed-point Opus против Espressif — отдельный OFF-by-default
  target после базовой функциональности; PCM/PLC/FEC/packed packets/OOM corpus.
- [ ] LX106 asm не переносить на LX6 только из-за общего названия Xtensa.
  Portable C обязателен, target A/B отдельно; SSO с иной точностью не default.

### CYD-08 · P2 · CPU/idle, RAM, непрерывность

- [ ] Адаптировать C3 cpu_profiler: два ядра, IDLE0/IDLE1, pinned tasks и
  явный denominator; отдельно проценты по ядрам и суммарная шкала. Не делить
  сумму двух idle counters на однокорный интервал.
- [ ] Stream/decode/output/WebUI/TFT/Wi-Fi/TCP runtime отдельно от wall time,
  DMA/TCP waits. Оговорить ISR и измерить overhead профилирования ON/OFF.
- [ ] Free/min/largest CAP8, DMA-capable heap, stack watermark каждой задачи:
  boot→Wi-Fi→TLS→decoder→first PCM→switch→cleanup, через `heap_caps_*`.
- [ ] Bounded stage counters/optional rotating SPIFFS log без hot-loop writes
  и секретов. HTTP log endpoint отсутствует в production.
- [ ] Перенести flash/RAM corpus и 10-attempt runner: codec-only, physical
  output, LAN, интернет раздельно. Интервалы одного поколения реально
  играющего потока; отказы запуска не превращать в успешные нулевые счётчики.

## 4. Не переносить и не ухудшать

- Software PDM/RCPDM вместо hardware PDM/DAC, GPIO/разгон/flash profiles ESP8266.
- Отключение HTTPS/FLAC/Vorbis/Opus/SBR/stereo-capable output ради чужих лимитов.
- Четвёртую PCM-задачу и уменьшенные стеки: PCM queue ESP8266 не прошла приёмку
  (`895983e`). DMA768 и Opus asm/div-once/yield также не доказаны как улучшение.
- Private heap walker/RX overlay/численные PCB лимиты ESP8266; использовать
  публичный ESP-IDF API и собственный бюджет concurrent allocations.
- HTTP debug logs в production. При этом явные ошибки приложения должны
  оставаться доступными в пользовательском статусе/консоли.

## 5. Зависимости и приёмка

Очередь: CYD-00 → CYD-01/02 → CYD-03/04/05 → CYD-06 → CYD-07/08.
Базовые счётчики CYD-08 нужны уже CYD-00; глубокую оптимизацию делать после
работающего управления. Общие C3-01…05 выполнить один раз, аппаратная приёмка
у плат независимая. Не делать массовый cherry-pick ESP8266-коммитов.

- [ ] Исполняемые protocol/state/allocator tests, не только regex по исходникам.
  Shared WebUI совместим со старыми backends и отсутствующими capabilities.
- [ ] Две вкладки, settings readback, Play/Stop/Next/Prev, touch/BOOT, сохранение
  после питания, upload/OTA, reconnect без потери/постоянной прокрутки списка.
- [ ] Не менее 10 сопоставимых A/B попыток; LAN цели ready UI ≤500 мс,
  подтверждение команды ≤200 мс. Сохранять median/p95/max/отказы и сетевые
  выбросы; время до первого физического звука — отдельная метрика.
- [ ] Smoke ≥20 с непрерывного реального вывода; затем длительный HTTPS +
  WebUI + TFT прогон и многократные смены кодеков/источников. CPU/IDLE и heap
  измеряются, а не выводятся из количества пропусков звука.
- [ ] MP3 до 320 кбит/с, AAC low/high по поддержанным режимам, FLAC/Vorbis,
  Opus 12/24/64/128/192 — набор тестов, не программный лимит битрейта.
- [ ] PDM/continuous DAC/legacy DAC — отдельные приёмки. RAM, скорость и
  точность оценивать раздельно; экономию с замедлением указывать честно.
- [ ] Успешные app.bin/config/manifest/SHA/changelog/results сохранять в
  `firmware/development/<variant>`, не перезаписывать versioned releases.

## Источники

[Прежний CYD TODO](ESP32_CYD_NATIVE_PORT_TODO.md),
[общая native стратегия](NATIVE_FIRMWARE_PARITY_PLAN.md),
[AAC RAM/CPU trade-off](ESP8266_AAC_PCM_BLOCKS.md),
[PCM queue: отрицательная приёмка](ESP8266_OPUS_PCM_QUEUE.md).
Размеры partition и функции выше сверены с кодом на дату аудита; прежние планы
с иными размерами SPIFFS не являются текущей конфигурацией сборки.

Официальные API: [ESP-IDF HTTP async lifecycle](https://docs.espressif.com/projects/esp-idf/en/release-v5.4/esp32c3/api-reference/protocols/esp_http_server.html#asynchronous-handlers),
[OTA/rollback](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/ota.html),
[heap capabilities/MALLOC_CAP_32BIT](https://docs.espressif.com/projects/esp-idf/en/v5.2/esp32/api-reference/system/mem_alloc.html#bit-accessible-memory).
Проверять API по закреплённой версии ESP-IDF проекта. Обновление SDK —
отдельный этап, не неявное условие синхронизации прикладной логики.
