# План возврата Ogg Vorbis и Ogg Opus в ESP8266 native

## Обновление 2026-09-09: локальная реализация Opus

Подробности и точные границы проверки: [ESP8266_OPUS_NATIVE.md](ESP8266_OPUS_NATIVE.md).
Исходный общий план ниже сохранён как целевой; смешанные Opus/Vorbis пункты
не считаются завершёнными лишь на основании Opus host-теста.

- [x] Перенести fixed-point libopus с лицензиями и фиксированной ревизией.
- [x] Добавить ограниченный Ogg parser, OpusHead/Tags, pre-skip/gain/granule/EOS/chains.
- [x] Ввести build-time Opus flag (OFF), состояние WebUI и условный фильтр/индекс.
- [x] Переиспользовать IRAM между кодеками и этапами SILK/CELT; ограничить scratch.
- [x] Проверить точное совпадение PCM с оригиналом на SILK/Hybrid/CELT.
- [x] Собрать ESP8266 experimental image, не меняя production default.
- [ ] Пройти физические RAM/CPU/stack/audio/WebUI и длительные тесты через OTA.
- [ ] Пройти production-гейты и только затем включать Opus по умолчанию.
- [ ] Vorbis — отдельная задача, в этой реализации не добавлен.

Решение по интерфейсу: расширен существующий codec bridge без массового
переименования совместимого Helix API. Это сохраняет MP3/AAC callers и тесты.

## Исходный целевой план

Цель — вернуть в нативную прошивку Wemos D1 mini воспроизведение
незашифрованных HTTP-потоков Ogg Opus и Ogg Vorbis, сохранив существующие
MP3/AAC, WebUI, BOOT-управление и оба варианта аудиовывода: SPI-PDM и I2S DMA.

В текущем плейлисте найдено 11 HTTP-кандидатов: 2 Opus и 9 Vorbis. Они сейчас
намеренно исключаются ESP8266-индексатором. Поддержка HTTPS в этот план не
входит.

## Исходные ограничения и выбранные реализации

- ESP8266 native использует ESP8266 RTOS SDK v3.4, одно ядро LX106 160 МГц и
  не имеет PSRAM.
- В полном MP3-профиле остаётся около 6–7 КБ свободной heap, а наблюдавшийся
  минимум — 5 452 байта. Новый декодер обязан использовать память
  взаимоисключающе с MP3/AAC и оставлять измеренный системный резерв.
- Официальный esp_audio_codec, используемый ESP32-C3/CYD, непосредственно не
  подходит: компонент требует IDF 4.4 или новее и линкует готовую библиотеку
  для CONFIG_IDF_TARGET; бинарника ESP8266 в нём нет.
- Для Opus основной кандидат — fixed-point libopus из актуального
  ESP8266Audio/Xiph. ESP8266Audio уже воспроизводит Ogg Opus на ESP8266, но его
  упрощённый демультиплексор с 1-КБ packet buffer нельзя переносить буквально.
- Для Vorbis основной кандидат — low-memory Tremor из micro-vorbis: fixed-point,
  потоковый Ogg demux, arena allocator и отсутствие выделений на каждом
  пакете. Обёртка требует IDF 5, поэтому переносится только переносимое ядро,
  а ESP8266 RTOS SDK adapter пишется отдельно.
- Обычный Tremor не рассматривается как production-вариант: Xiph оценивает
  типичные требования основного варианта в сотни килобайт. Даже micro-vorbis
  указывает около 76 КБ для типичного 48-кГц stereo-потока с выходным буфером,
  поэтому Vorbis сначала проходит отдельный feasibility-гейт.

Зависимости закрепляются точными commit SHA. В репозиторий включаются только
нужные decoder/demuxer-файлы, upstream manifest, лицензии и список локальных
изменений. Encoder, float API, file seeking и метаданные, не нужные радио, не
компилируются.

## Этап 0. Воспроизводимые образцы и исходные бюджеты

- [ ] Сгенерировать из одного собственного PCM-источника Ogg Opus 32/128/256 и
  510 кбит/с, а также Vorbis mono/stereo с низким, средним и максимальным
  практически встречающимся качеством.
- [ ] Сохранить небольшие фрагменты и эталонные PCM SHA-256/SNR в test fixtures.
- [ ] Добавить Ogg page/packet fixtures: пакет через несколько страниц,
  несколько пакетов на странице, continued packet, повреждённая CRC,
  неизвестный logical stream и обрыв каждого заголовка.
- [ ] Зафиксировать перед открытием декодера: free/min heap, largest free block,
  IRAM/DRAM, stack high-water и свободное место factory-раздела.
- [ ] Снять baseline decode-only и полный SPI-PDM/I2S-DMA профиль MP3/AAC, чтобы
  новые измерения сравнивались с тем же коммитом и той же платой.

## Этап 1. Общий Ogg и decoder interface

- [ ] Заменить Helix-специфичный интерфейс audio service на общий
  native_decoder: detect/open/feed/get_info/reset/close/memory_usage.
- [ ] Оставить существующий Helix bridge backend без функциональных изменений.
- [ ] Добавить независимые флаги CONFIG_YORADIO_OGG_OPUS и
  CONFIG_YORADIO_OGG_VORBIS; на экспериментальном этапе оба выключены по
  умолчанию.
- [ ] Добавить типы состояния CODEC_OPUS и CODEC_VORBIS и корректные имена
  для UART, OLED и WebUI.
- [ ] Сделать один инкрементальный Ogg demuxer для обоих кодеков: header 27
  байт, lacing table до 255 байт, packet continuation и ограниченная сборка
  пакета без чтения всей страницы/потока в RAM.
- [ ] Определять кодек по потоку: сначала OggS, затем первый complete packet
  OpusHead или 0x01vorbis. MIME и URL являются только подсказками и не
  определяют decoder.
- [ ] Не передавать ICY metadata в Ogg parser. Остановка обязана закрывать TCP,
  прекратить ICY/Ogg parsing и только затем освобождать decoder.
- [ ] Не выделять и не освобождать память на каждом Ogg packet. Packet buffer,
  decoder state и временные блоки создаются при open и сбрасываются при close.

## Этап 2. Ogg Opus

- [ ] Зафиксировать проверенную ревизию Xiph/ESP8266Audio Opus и собрать только
  decoder в FIXED_POINT, без encoder, float API, DRED, multistream и
  неиспользуемых расширений.
- [ ] Выделять opus_decoder_get_size(channels) из общей codec arena; сначала
  проверить stereo state, затем возможность переиспользовать 32-битную IRAM.
- [ ] Ограничить compressed packet буфер спецификацией Opus и измеренными
  потоками; запрещено оставлять 1-КБ лимит ESP8266Audio, недостаточный для
  максимального тестового битрейта.
- [ ] Для первого production-профиля поддержать mono/stereo 48 кГц и radio
  packets до 20 мс. До декодирования проверять число samples; более длинный
  пакет должен дать понятную UNSUPPORTED OPUS FRAME вместо переполнения.
- [ ] Выдавать PCM существующему callback небольшими блоками, не создавая
  дополнительную PCM-очередь. Проверить прямое mono и stereo-to-mono для
  SPI-PDM, stereo для I2S.
- [ ] Проверить Opus pre-skip, output gain, page granule position, holes,
  chained-stream reset и повреждённый packet.
- [ ] Добавить RAM-only benchmark и сравнение PCM с host libopus: одинаковое
  число samples, SHA-256 при bit-exact результате либо SNR/max error.

Гейт Opus: полная прошивка Wi-Fi + WebUI + decoder оставляет не менее 8 КБ
free heap и 6 КБ minimum-free, stack reserve не менее 1,5 КБ, decode-only
скорость не ниже x1,30 realtime. На физическом выводе не допускаются underrun
и watchdog; для SPI-PDM нужен измеряемый idle не ниже 5%, для I2S DMA — не ниже
10%.

## Этап 3. Ogg Vorbis

- [ ] Сначала собрать low-memory Tremor/micro-vorbis как отдельный host и
  RAM-only target benchmark без Wi-Fi и вывода.
- [ ] Портировать allocator на существующую codec arena: постоянный decoder
  state, отдельная ограниченная codebook arena и reset одним действием.
- [ ] Отключить PSRAM, ESP-IDF 5 allocation API, multichannel, seeking,
  concatenated streams и Vorbis comments, если они увеличивают RAM hot path.
- [ ] Поддержать сначала Vorbis I mono/stereo, 44,1/48 кГц и blocksize не выше
  измеренного безопасного предела. Неподдерживаемые setup/codebook/blocksize
  отклонять до начала PCM с точным сообщением.
- [ ] Не выделять полный PCM frame: забирать внутренний Tremor PCM порциями
  128–256 frames и сразу передавать normalizer/output.
- [ ] Измерить отдельно память трёх headers, codebooks, history/overlap,
  demux packet и PCM. Проверить, какие 32-битные области безопасно перенести в
  IRAM, а константные таблицы оставить во flash.
- [ ] Добавить Xtensa LX106 fixed-point multiply/MAC только после сравнения
  ассемблера GCC и физического A/B. Не сохранять усложнение без ускорения.
- [ ] Проверить все девять HTTP Vorbis-кандидатов текущего плейлиста, включая
  320-кбит/с Laza Rádió и streams без расширения .ogg.

Гейт Vorbis тот же, что у Opus. Если 48-кГц stereo setup требует больше
доступной внутренней RAM и не укладывается после освобождения MP3/AAC, Vorbis
остаётся отдельным экспериментальным build profile. Нельзя уменьшать системный
резерв или ломать стабильный MP3/AAC ради формального включения флага.

## Этап 4. Интеграция радио, плейлиста и WebUI

- [ ] При compile-time поддержке убрать фильтрацию имени Ogg и разрешить
  .ogg/.opus; HTTPS и остальные неподдерживаемые расширения оставить
  исключёнными.
- [ ] Повысить INDEX_VERSION, чтобы индекс автоматически перестроился после
  обновления прошивки и вернул поддерживаемые Ogg-станции.
- [ ] Сохранять исходные номера станций и корректно работать с next/previous,
  BOOT и кликом WebUI после изменения состава списка.
- [ ] Показывать VORBIS/OPUS, sample rate, channels и реальный обновляемый
  bitrate. Для bitrate использовать compressed bytes / длительность PCM, а не
  только серверный header.
- [ ] Сохранить стандартный ICY StreamTitle; OpusTags/Vorbis comments не
  должны ошибочно попадать в название песни.
- [ ] Проверить действия WebUI и физической кнопки во время тяжёлого Ogg frame:
  play/stop/next/previous должны завершаться без ожидания сетевого timeout.

## Этап 5. Lifecycle, переключения и длительные тесты

- [ ] При смене разных типов сначала остановить output, закрыть прежний decoder,
  вернуть/очистить его arena и только потом открыть новый. Для того же типа
  использовать reset без повторного выделения, если это безопасно.
- [ ] Прогнать все переходы MP3/AAC/Opus/Vorbis в прямом и обратном порядке,
  минимум 50 циклов каждого типа; heap после цикла должен вернуться к исходному.
- [ ] Проверить stop во время Ogg header, setup packet, decode и заполненного
  output buffer.
- [ ] Провести не менее часа на Opus и Vorbis с открытым WebUI/WebSocket:
  underrun=0, OOM=0, WDT=0, рост heap=0.
- [ ] Сравнить SPI-PDM и I2S DMA на одинаковом потоке: decoder time, output
  time, CPU busy/idle, stack, free/min heap и максимальный callback.
- [ ] Проверить app/IRAM/DRAM map. Factory image должен помещаться с запасом не
  менее 32 КБ; при нехватке flash оставить раздельные build profiles.
- [ ] После прохождения гейтов включить Opus по умолчанию. Vorbis включить по
  умолчанию только если он проходит full-radio RAM и realtime тесты.
- [ ] Обновить документацию, setup/build scripts, firmware manifest/changelog,
  сохранить production binary в firmware/development и вернуть обычную
  прошивку на плату после каждого экспериментального теста.

## Порядок реализации

1. Fixtures, измеритель RAM/CPU и общий decoder/Ogg interface.
2. Opus: host regression, RAM-only плата, I2S DMA, затем SPI-PDM и WebUI.
3. Vorbis feasibility: low-memory port и реальные размеры headers/codebooks.
4. Только после прохождения RAM-гейта — полная Vorbis radio integration.
5. Общая матрица переключений, длительный тест и production rollout.

Такой порядок даёт рабочий Opus как можно раньше и не связывает его выпуск с
более рискованным Vorbis. При этом оба backend используют один контейнерный
parser, один lifecycle и тот же PCM/output тракт.

## Зафиксированные upstream-источники

- ESP8266Audio: https://github.com/earlephilhower/ESP8266Audio
- Xiph libopus: https://github.com/xiph/opus
- Xiph Tremor: https://gitlab.xiph.org/xiph/tremor
- micro-vorbis low-memory fork: https://github.com/esphome-libs/micro-vorbis
- Espressif audio codec reference:
  https://github.com/espressif/esp-adf-libs/tree/master/esp_audio_codec
