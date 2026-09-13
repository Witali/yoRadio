# ESP32-C3 OLED native: перенос улучшений ESP8266

Дата аудита: 2026-09-13. База Git: `main`, `895983e`.
Target: `idf/esp32c3-oled-native`. Arduino — эталон пользовательского поведения
и источник общих компонентов; основная прошивка остаётся native ESP-IDF.

Это план по истории Git, текущему коду и сохранённым результатам, а не отчёт
о выполненном переносе. В рамках аудита прошивки не собирались и платы не
прошивались. Парный документ: [план CYD](ESP32_CYD_ESP8266_IMPROVEMENTS_PLAN.md).

## 1. Изменения ESP8266 и применимость

Проверена история native/WebRadio/KaRadio, общих WebUI/Helix и двух native
ESP32 за конец августа — 11 сентября 2026 года. Последнее собственное изменение
каталога C3 в просмотренной истории — `3d29972`, async static files 30 августа.
Общие файлы менялись позднее: отсутствие новых коммитов в каталоге платы
не означает отсутствие изменений в следующей сборке этой платы.

| Изменения и коммиты-ориентиры | Что переносить |
| --- | --- |
| Потоковый multipart, recovery/OTA: `0da6a59`, `20a596f`, `472e983` | Прикладные контракты и тесты; реализация через штатный ESP-IDF HTTP/OTA. |
| Откат плейлиста при ошибке индекса, unchanged-file detection: `937173e` | Прямой кандидат: C3 удаляет старый CSV до успешной установки/индексации. |
| Две вкладки, Connecting/Playing, VBR heartbeat: `0ba0e4d`, `b9b7129`, `6b7cd9a` | C3 уже имеет async многоклиентскую рассылку; переносить проверки и недостающую семантику, не второй сервер. |
| Общий JS, initial scroll/settings snapshots: `c6d1418`, `c6e4427`, `6bb08e8`, `91889f4` | Уже в общих исходниках; проверить backend, capabilities и доставку новых gzip assets. |
| Громкость 0–100: `be0207e` | ESP8266 backend реализован; C3 пока принимает/отдаёт 0–254. |
| Source channels/AAC rate/UTF-8: `0645c41`, `8a6d2ce`, `fa1abc1` | Исправить C3 callbacks и сериализацию, отделить исходный формат от PCM. |
| HTTP ownership, cleanup, отмена connect: `609bbdc`, `6a24c14`, `95c66f9`, `96a818f`, `b5d7b7a` | Инварианты владения и fault-тесты; такой же дефект внутри ESP-IDF не доказан. |
| MP3 reorder reuse/блочный PCM: `f3138f2`, `b21979b`; AAC blocks/lookup: `9f991d6`, `d99f495`, `a1e49e9`, `851c7d2` | Общие исходники содержат API, но IDF adapter полнокадровый и часть флагов ESP8266-only. Нужен порт/A-B. |
| Fixed-point bounded Opus и packed frames: `b056590`, `9368c48`, `ff49a46` | Только экспериментальная альтернатива Espressif; непрерывное Opus-радио ESP8266 ещё не прошло приёмку. |
| Воспроизводимые CPU/memory/continuity tests: `37d5930`, `3b108c7`, `d155eaf`, `d61fb1b`, `e97e7ef` | Методика, фикстуры и сценарии ошибок; счётчики через API целевого ESP-IDF. |
| Debug log/экономный LED: `4005e04`, `4328492`, `19da0d4` | Log только opt-in debug; сохранить аппаратный LEDC C3 вместо ESP8266 sigma-delta. |

Native — основной источник. WebRadio (`469913a`) и KaRadio (`ca5b52e`) —
сравнительные реализации, не новая база ESP32. На дату аудита незакоммичены:
WebRadio PCM-счётчики/null-output, изменение буфера 5→4 КиБ и реорганизация
тестов; отдельно OFF-by-default `YORADIO_OPUS_CELT_SILK_SCRATCH`, временно
занимающий неактивное состояние SILK под CELT scratch. Это не часть `895983e`
и не подтверждённая аппаратно оптимизация. Изменения оставлены нетронутыми.

## 2. Что C3 уже имеет — не реализовывать заново

- ESP-IDF HTTP client/server, HTTPS с сертификатами, `/ws` на порту 80,
  async static workers и async status broadcast.
- Три задачи stream/decode/output с приоритетами 5/7/6 на одном ядре 160 МГц;
  PCM ring 8192 байта. Compressed ring вычисляется как `audio_buffer_blocks *
  1600`: фиксировать фактический размер, не считать название «16 КБ» точным.
- Стеки по плате, decoder stack 16384 байта. Минимумы стеков ESP8266 не подходят
  как обоснование уменьшения стеков ESP32.
- Общий fixed-point normalizer/limiter и кэш коэффициентов (`42f6ca4`), время
  нормализации 5 секунд, сброс накопленного boost при смене станции, NVS.
- OLED 72×40/8×15, программный скролл, яркость, логотип/часы, BOOT ISR,
  энкодер и low-priority SNTP; их сохраняем.
- Аппаратный аудиовывод C3 GPIO10/GPIO3 и LED GPIO8 через LEDC. Это не
  software PDM32/SLC-DMA ESP8266.
- Defaults: MP3 Espressif, AAC Helix, FLAC custom; Opus/Vorbis/Ogg включены.
  Итоговый `sdkconfig` проверять: старый build cache может выбирать другой AAC.
- Два app-слота по `0x1D0000`, SPIFFS `0x40000` (256 КиБ), coredump 64 КиБ.
  Наличие OTA-разметки не означает, что WebUI умеет прошивать приложение.

## 3. План работ

Каждый ID — отдельный логичный этап/коммит. Общий код переносить небольшими
компонентами, не заменяя одновременно весь audio и web core.

### C3-00 · P0 · Baseline и критерии измерений

- [ ] Зафиксировать commit/dirty-state, SDK/compiler/codec, конфигурацию,
  app/SPIFFS hashes, секции flash/RAM, реальные buffers/stacks.
- [ ] Собственные MP3/AAC/Opus: flash→decoder, flash→decoder→I2S, LAN HTTP,
  затем реальные HTTP/HTTPS. Отдельно capture WebUI при одной/двух вкладках.
- [ ] Использовать имеющийся `cpu_profiler.c`, учесть static workers в WebUI,
  проверить новые задачи/переполнение и overhead. Task runtime/IDLE, wall time
  и ожидания считать раздельно, явно описать включение ISR в измерение.

### C3-01 · P0 · Формат потока и текстовые статусы

- [ ] `decoder_task`, `custom_legacy_output`, `custom_flac_output`: обновлять
  формат каждого изменившегося PCM-блока, не только первого кадра/битрейт.
- [ ] Общий Helix adapter: source channels/rate отдельно от PCM/output;
  `AACGetStreamSampRate()` для статуса, `AACGetSampRate()` для вывода. Не
  объявлять SBR/PS каналов больше, чем подтверждено декодером.
- [ ] Замораживать только снимок одной OLED-прокрутки; Stop/смена поколения
  очищают старую песню/формат, reconnect даёт актуальный snapshot.
- [ ] Исправить побайтовый `json_escape`: валидный UTF-8, границы символов,
  кавычки/escape на краю буфера. Корректный ICY, включая JSON-текст, не фильтровать.
- [ ] Тесты stereo→mono→stereo, смены частоты при неизменном bitrate,
  AAC-LC/HE-AAC, UTF-8/truncation, Stop/reconnect. Основа:
  `tests/esp8266-stream-metadata.test.js`, `esp8266-native-websocket.test.js`.

### C3-02 · P0 · Потоковая загрузка файлов

- [ ] Заменить `receive_multipart()` и `upload_handler()`: сейчас тело
  выделяется целиком, в `/upload` до 96 КиБ. Использовать bounded parser по
  образцу ESP8266 `web_multipart.h`/`web_upload.c`, через `httpd_req_recv()`.
- [ ] Ограничить scratch/размер/имя/время; один владелец запроса и cleanup.
  Не делить изменяемый scratch между параллельными static workers/upload.
- [ ] Сохранить `/upload`, `/webboard`, recovery и Wi-Fi формы. Тестировать
  разрезанный boundary, бинарный gzip, медленного клиента, неполное тело,
  заполненный SPIFFS и disconnect. Ни одного allocation размером с файл.

### C3-03 · P0 · Надёжный плейлист и публикация файлов

- [ ] Убрать удаление старого CSV до готовности нового CSV+индекса. Temp/backup,
  откат при ошибке индекса и recovery на boot; блокировка выбора на время commit.
- [ ] Одинаковый CSV сравнивать частями: без rebuild/playlist event. Индекс
  проверять на устаревание, включая замену файлом той же длины.
- [ ] Event только после успешных write/close/index/install. WebUI/Wi-Fi файлы
  также не перезаписывать поверх рабочей копии; проверять свободное SPIFFS.
- [ ] Fault-тесты из `esp8266-playlist-install.test.js` и streaming tests;
  добавить обрывы установки/boot recovery. Пофайловый импорт не объявлять
  транзакцией всей формы или гарантией от любого сбоя питания SPIFFS.

### C3-04 · P1 · WebUI без лишних обновлений и конфликтов

- [ ] Один shared JS/CSS/HTML и актуальные `.gz`. Embedded bundles ESP8266
  подключать только после проверки генерации/revision/capabilities.
- [ ] Проверить две вкладки, player+settings, медленного клиента, reconnect,
  срок жизни async payload до completion и очистку pending при ошибке.
- [ ] Команды/станция — немедленные события, RSSI/VBR — bounded heartbeat.
  Не перезаписывать редактируемые settings постоянным статусом.
- [ ] Play: Connecting→Playing по реальному PCM; физические команды видны
  во всех вкладках. Клик строки не пересоздаёт список; initial scroll один
  раз, далее только согласованные действия пользователя.
- [ ] Optional playlist gzip cache (`b74e21b`, `de73cf0`) — отдельный A/B,
  инвалидация по данным/возможностям/формату. Не заменять индексируемый CSV
  единственным gzip-потоком, требующим распаковки с начала при Next/Prev.

### C3-05 · P1 · Громкость и сохранение настроек

- [ ] Выполнить [план 0–100](VOLUME_0_100_SYNC_PLAN.md): пересчёт на API-границе,
  сохранить старые NVS/gain, объявить `volumeMax=100`, без работы в PCM-loop.
- [ ] Сначала совместимый WebUI, затем новая семантика API. Проверить REST/WS,
  BOOT/энкодер/OLED, все 101 значение, старые 0/128/160/254, ±шаг и ошибки ввода.
- [ ] Для каждого поля таблица capability→видимость→setter→readback→NVS→
  применение. Проверять повторное сохранение без дрейфа и реальный reboot.

### C3-06 · P1 · Application OTA

- [ ] Добавить отсутствующий handler через `esp_ota_*`: streaming в неактивный
  app-слот, проверка размера/target/образа, abort при ошибке. `/webboard` сейчас
  не следует считать готовым application OTA endpoint.
- [ ] Согласовать форму shared UI. Не менять разметку ради ESP8266-порта.
  Rollback/self-test планировать вместе с совместимостью bootloader.
- [ ] Обрыв, неверный образ, первый запуск и восстановление старой версии;
  сохранить NVS/Wi-Fi/playlist. HTTP 200 сам по себе не доказывает успешную OTA.
  Сырой SPIFFS OTA не делать обязательным вместо пофайлового импорта.

### C3-07 · P1 · Ресурсы аудио и восстановление сети

- [ ] Сохранить поколения и decoder-release handshake C3. Fault-тестировать
  alloc/free, ring acquire/complete/return, HTTP init/cleanup и отмену Stop/Next.
- [ ] Совместимый workspace reuse после reset; несовместимый освободить до
  следующего TLS/decoder peak. Ошибка сохраняется до/после cleanup.
- [ ] Дедлайны и reconnect не отменяют новые команды; отдельно DNS/connect/
  headers/read, decode/output. Считать idle timeout только по поступлению данных.
- [ ] Проверить поздний Wi-Fi disconnect: event handlers ставят FAILED, но
  startup waiter не заменяет постоянный recovery loop. Основа — `180943d`.
- [ ] Не копировать 1/4-КиБ input и TLS-ограничения ESP8266; HTTPS и проверка
  сертификатов остаются. Число файлов/сокетов считать по своей конкурентности.

### C3-08 · P2 · Decoder memory и скорость

- [ ] Общий Helix adapter сейчас имеет `pcm[1152*2]`. Подключить MP3 block API
  и shared reorder отдельно, сохранив stereo и владение PCM до передачи ring.
- [ ] AAC blocks отдельно от Huffman/window ускорений. На ESP8266 вариант 512
  экономит 3072 байта, но исходный decode-only замер медленнее примерно на 6,1%:
  это RAM trade-off, а не автоматическое ускорение C3.
- [ ] Сравнить 128/256/512 на C3, SBR-enabled fallback и общий Arduino/CYD build.
  Нельзя просто включить ESP8266-only macros в IDF.
- [ ] Custom fixed-point Opus — OFF-by-default A/B против Espressif: SILK/
  Hybrid/CELT, PLC/FEC, packed frames, pre-skip/EOS, OOM/reset и PCM сравнение.
- [ ] Сохранять только подтверждённую выгоду. RAM, скорость и точность —
  разные метрики; SSO с иной арифметикой не считать bit-exact. MP3 default
  Espressif не менять без целевого сравнения.

### C3-09 · P2 · Вывод, LED и диагностика

- [ ] Использовать существующие три задачи/PCM ring, не добавлять ещё consumer.
  Измерить ready PCM/DMA и паузы; 8192 байта при stereo PCM16/48 кГц — максимум
  около 42,7 мс до overhead, заполняемый блок ещё не готовый звук.
- [ ] Dispatch mono/stereo и коэффициенты вынести из sample loop, только если
  GCC/плата подтверждают выигрыш. Mono-источник не равен физическому mono-output:
  не отменять баланс двух выходов C3 по правилам одноканального ESP8266.
- [ ] LED: sparse peak sampling, compile-out лишней работы при OFF, сохранить
  hardware LEDC. Обновление яркости 10–20 Гц не требует программной несущей.
- [ ] Bounded stage/heap/stack/FIFO counters; optional rotating SPIFFS log без
  записи из ISR/hot PCM, без секретов, HTTP log только debug и отсутствует
  в production. Heap измерять публичными API ESP-IDF.

## 4. Не переносить автоматически

- LX106 asm/SLC registers, UART GPIO3 конфликт, private heap/RX overlay,
  ESP8266 IRAM layout, QIO/частоты/численные лимиты PCB и Wi-Fi buffers.
- Software PDM/RCPDM/Simple вместо аппаратного PCM-to-PDM C3.
- PCM consumer/DMA256 (`8eca651`, `0fb3e1b`, `895983e`) и DMA768 (`4bf83c1`):
  аппаратная приёмка неуспешна. Не понижать reserve/стеки, чтобы убрать отказ.
- Opus rotation asm/div-once/decoder-only/yield как доказанное ускорение:
  есть сохранённые отрицательные результаты, default C оставлен.
- Forced mono, μ-law PCM, отключение HTTPS/SBR, полную паузу аудио ради обычного
  WebUI. CPU-budget 80/20 у ESP8266 пока TODO, одни приоритеты долей не задают.

## 5. Приёмка и общий слой

- [ ] Host protocol/state/allocator tests; при общем изменении сборка C3 и CYD,
  при алгоритмическом — PCM/overlap/bounds/OOM и затронутые Arduino-профили.
- [ ] Не менее 10 сопоставимых A/B попыток с теми же файлами/flags/сетью.
  Все ошибки и выбросы сохранены, network delays отдельно классифицируются,
  но не исключаются из пользовательской метрики.
- [ ] Smoke ≥20 с реального вывода без underrun с правильной длительностью PCM,
  затем длительный прогон/смены всех кодеков. Нулевые idle-DMA counters после
  отказа запуска не означают непрерывное воспроизведение.
- [ ] LAN цели: ready UI ≤500 мс, подтверждение команды платой ≤200 мс;
  median/p95/max и отказы, cold/warm load, две вкладки, uploads и controls.
- [ ] Успешные app.bin/sdkconfig/manifest/SHA/changelog/results — в
  `firmware/development/<variant>`; versioned releases не перезаписывать.

После C3-01…04 извлечь проверенные web/radio/settings части в `idf/components`
небольшими коммитами с сохранением поведения C3. Они станут основой CYD-01…04;
GPIO, display и audio output остаются адаптерами платы, не двумя копиями core.

## Источники

[C3 web](../idf/esp32c3-oled-native/main/web_service.c),
[C3 audio](../idf/esp32c3-oled-native/main/audio_service.c),
[shared Helix](../idf/components/custom_legacy_codecs/custom_legacy_adapter.cpp),
[ESP8266 upload](../esp8266/rtos-sdk-native/main/web_upload.c),
[ESP8266 playlist](../esp8266/rtos-sdk-native/main/playlist_service.c),
[C3 прежний TODO](ESP32C3_OLED_NATIVE_TODO.md),
[AAC blocks](ESP8266_AAC_PCM_BLOCKS.md), [PCM queue](ESP8266_OPUS_PCM_QUEUE.md),
[DMA results](ESP8266_OPUS_DMA_CAPACITY.md).

Официальные API: [ESP-IDF HTTP async lifecycle](https://docs.espressif.com/projects/esp-idf/en/release-v5.4/esp32c3/api-reference/protocols/esp_http_server.html#asynchronous-handlers),
[application OTA/rollback](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/ota.html).
При реализации сверять точные API с закреплённой версией SDK проекта.
