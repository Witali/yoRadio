# Ogg Opus для ESP8266 native

Статус на 2026-09-09: экспериментальная реализация собрана, проверена на ПК;
чистый декодер измерен на физической плате с совпадением пяти PCM fingerprints.
Непрерывность реального радио ещё не подтверждена; Hybrid/CELT требуют ускорения.
В штатном профиле Opus **выключен**. MP3/AAC и их входной буфер 4096 байт
остаются прежними. Подключать USB для локальных тестов не требуется; обновления
платы выполняются через OTA, без автоматического перехода к UART.

## Реализация и ограничения

В проект перенесён fixed-point libopus 1.5.2 из ESP8266Audio,
commit `10d929ac01436dfe8856e0a06fd9ec35a848c6e2`. Arduino-обёртка не используется.
Сохранены лицензии, авторство и исходный вариант для регрессионного сравнения.
Готовая библиотека Espressif для ESP32 не подходит по архитектуре ESP8266 LX106.

- Незашифрованные HTTP Ogg Opus, mapping family 0, вход mono/stereo.
- Выход только mono, 48 кГц, PCM16; декодер сам выполняет downmix stereo.
- Пакет не более 20 мс / 960 отсчётов и 1536 сжатых байт. Проверяется до decode.
  Более длинные пакеты и multistream отклоняются с явной ошибкой.
- Pre-skip, signed Q8 output gain, granule offset, обрезка EOS, смена logical
  stream после EOS. OpusTags не подменяет ICY StreamTitle.
- Инкрементальный Ogg parser: один packet buffer 1536 байт, header/lacing,
  без загрузки полной страницы или потока. Tags ограничены 1 МиБ, из них
  сохраняются только первые 16 байт для проверки заголовка.
- CRC проверяется при завершении страницы. Пакет на её конце выдаётся после
  проверки; PCM уже выданных предыдущих пакетов страницы отозвать нельзя.
  Это сознательный компромисс без второго packet/page buffer. CRC, holes,
  concurrent multiplexing останавливают декодирование. Обрыв конечного файла
  обнаруживается strict finish; для live HTTP прежняя логика reconnect при
  TCP EOF/timeout сохранена, decoder при этом освобождается и сбрасывается.
- Кодек определяется по OggS/OpusHead, не по URL. Случайные MP3/AAC sync words
  внутри Ogg не переключают decoder. Vorbis и HTTPS не добавлены.
- WebUI получает `OPUS`, реальный bitrate пакета, частоту и число выходных
  каналов. Флаг Opus разрешает `.ogg/.opus` в фильтре и меняет версию индекса;
  возвращение к сборке без Opus тоже перестраивает индекс. `.ogg` может
  содержать Vorbis: окончательную проверку делает decoder по заголовку.

## Плейлист WebUI при включении Opus (2026-09-10)

HTTP `.opus` и `.ogg` уже разрешены фильтром при `CONFIG_YORADIO_OGG_OPUS=y`.
Исправлена отдельная ошибка gzip-кэша: он проверял только исходный CSV, но не
состав декодеров. После OTA браузер мог получать старые 511 строк без Opus,
хотя несжатый ответ и индекс уже содержали 522 строки, включая две Opus-станции.
Версия gzip-кэша теперь зависит от флага Opus: переходы OFF -> ON и ON -> OFF
перестраивают только производную копию. CSV, Wi-Fi и настройки не заменяются.
Регрессия компилирует настоящий фильтр и cache-модуль в обоих вариантах,
проверяет состав строк, повторное использование кэша и неизменность CSV.
HTTPS остаётся неподдерживаемым; наличие `.ogg` не гарантирует Opus вместо
Vorbis — окончательная проверка по OpusHead выполняется декодером.

После OTA на плате оба ответа содержат одинаковые 522 строки и две HTTP
Opus-станции. В корневом плейлисте 11 Opus-станций, из них 9 с HTTPS.
Для четырёх проверены HTTP-варианты адресов, но общий плейлист не переписан.
[Прошивка, отчёты и ограничения повторного PDM-теста](../firmware/development/esp8266-opus-batch-resume/CHANGELOG.md).

## Память и этапы

Один активный decoder владеет общей codec arena. При смене типа сначала
освобождается старое состояние, затем создаётся новое. Opus → Opus использует
reset без realloc. Ошибка на любом этапе открытия освобождает всё выделенное.
Внутри decode нет malloc/free, новый network/audio task не создаётся.

32-битная CELT history занимает 8672 байта существующей 16-КиБ IRAM arena.
Остаток используется как временная память; SILK и CELT выполняются последовательно
и возвращают её по завершении этапа. Автоматически в IRAM размещаются только
проверенные word-типы CELT. В SILK разрешены лишь `sLTP_Q15` и `res_Q14`:
остальные массивы остаются DRAM из-за byte-copy и 16-битных обращений.

VLA заменены ограниченными scratch arena с SAVE/RESTORE. Убраны неиспользуемый
scratch deemphasis при 48 кГц и encoder-only RDO-ветка с 1275 байтами стека.
OOM возвращается через C-only boundary, сбрасывает decoder и запрещает
продолжение до reset/close; частично изменённая history не используется далее.

| Область | Размер / смысл |
|---|---:|
| Opus state, host x64 | 6654 Б вместо исходных 17860 Б |
| Opus state, Xtensa GCC 8.4 | 6582 Б, рассчитано по сгенерированному коду |
| IRAM reservation | 16384 Б, уже общая с MP3/AAC |
| DRAM scratch reservation | 7680 Б |
| Ogg + adapter, host x64 | 2040 Б, включая packet buffer |
| PCM | 1920 Б, один mono frame до 20 мс |
| Opus read-ahead | 1024 Б, отдельная настройка; MP3/AAC по-прежнему 4096 Б |
| Audio task stack при включённом Opus | 5120 Б вместо 4096 Б |

Это не размер всей прошивки и не свободная память платы. Heap allocator,
bridge, TCP/Wi-Fi, WebUI и остальные стеки учитываются отдельно. При открытии
Opus контролируется остаток heap не менее 4096 байт либо больший резерв caller;
это аварийный порог, **не** прохождение production-гейта 8/6 КиБ free/min heap.

HTTP handshake выделен границей `noinline`: target frame `audio_task`
уменьшился с 1792 до 784 байт, а отдельный HTTP frame 1152 байта отсутствует
на глубоком пути декодера. Физический raw-тест всех пяти режимов оставил
2788 байт из 6144 свободными (максимальная измеренная глубина 3356 байт).
После замера stack уменьшен до 5120 байт: освобождается 1024 байта DRAM,
запас над измеренной глубиной 1764 байта. Полный сетевой путь ещё требует
проверки high-water, это не доказательство его максимальной глубины.
SILK excitation двух каналов перенесён в persistent IRAM: target state
уменьшился ещё на 2552 байта, persistent reservation составляет 11232 байта
вместе с CELT history. Указатели сохраняются при reset и mono/stereo переходах.
Word-path и найденные compiler narrowing проверяются target asm-тестом;
см. [аудит IRAM](ESP8266_IRAM_ACCESS_AUDIT.md).

Почему нельзя просто выдавать PCM по 32 отсчёта, как MP3: CELT entropy/folding
и синтез используют спектр полного кадра и предыдущее состояние. Полный PCM
frame пока сохранён, но выдаётся существующему output callback порциями до 512
отсчётов без второй PCM-очереди. Спектр `X` и folding `_norm` живут одновременно;
перекрывать их память нельзя. Обратная связь/предсказание между кадрами также
не является временным буфером и не может быть освобождена.

## Локальные результаты

Собственный детерминированный сигнал: тоны + шум, 48 кГц, 1,2 с.
Сравнены pristine upstream, локальный macro-off и bounded вариант:
5 файлов × 61 пакет = 292800 decoded samples; различий **0**, max error 0,
SNR между вариантами бесконечный. Это отсутствие дополнительных изменений PCM,
а не утверждение о безошибочности lossy-кодирования исходного сигнала.

| Fixture | Режим | Пик DRAM scratch | Пик word arena, включая history |
|---|---|---:|---:|
| mono 12 кбит/с | SILK | 1808 Б | 14112 Б |
| mono 24 кбит/с | Hybrid | 2904 Б | 15600 Б |
| stereo 64 кбит/с | CELT | 6736 Б | 15600 Б |
| stereo 128 кбит/с | CELT | 6736 Б | 15600 Б |
| stereo 510 кбит/с | CELT | 6736 Б | 15600 Б |
| смешанный поток + PLC | SILK/Hybrid/CELT | 7216 Б | 15600 Б |

Дополнительно 286 смешанных пакетов и 35 PLC-кадров дали 308160 одинаковых
отсчётов pristine/baseline/bounded, включая полный reset и mono/stereo.
Именно переход Hybrid→CELT обнаружил нехватку 48 байт при прежнем лимите
7168; резерв поднят до 7680, без изменения алгоритма декодирования.

Проверены reset, искусственный OOM/reinitialize, защитные границы arena,
2.5/10/20-мс пакеты, отказ 40/60 мс, gain, pre-skip, EOS, chains, отмена callback.
Демультиплексор проверен с ASan/UBSan, разрезами входа, CRC, повреждёнными
потоками и Tags до лимита. Числа sizeof выше относятся к host x64, не подменяют
замер target heap. [Машинный отчёт](../tools/esp8266_opus_profile/results.json).

## Воспроизведение проверок и сборка

```powershell
node tools/esp8266_opus_profile/run_regressions.cjs
node --test tests/esp8266-ogg-demux.test.js tests/esp8266-native-opus.test.js tests/esp8266-opus-memory.test.js tests/esp8266-codec-lifecycle.test.js
tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -Variant esp8266-opus-experimental -EnableOpus -WebAudioPause short
```

Host GCC используется через WSL на Windows. Первый запуск компилирует библиотеку,
следующие переиспользуют object files. `--no-build` предназначен только для
явного запуска уже собранного варианта. Генерация fixtures требует FFmpeg/libopus;
для обычных тестов достаточно сохранённых файлов.

Сборка сама не прошивает. Бинарник, sdkconfig и manifest сохраняются в
`firmware/development/esp8266-opus-experimental/`. Вывод I2S PDM32, GPIO3,
160 МГц/QIO40, OTA 2 × 960 КиБ и SPIFFS 256 КиБ не меняются.

## Осталось перед включением по умолчанию

- [x] Две SILK `exc_Q14[320]` перенесены в постоянные IRAM-слоты:
  экономия target state 2552 Б, cumulative allocator, reset/mono→stereo,
  CNG word-copy и целевые load32 проверены. Host mixed/PLC побитно совпадает.
- [ ] Проверить target min/free/largest heap при Wi-Fi + WebUI + Opus.
- [x] Измерить high-water audio stack raw-декодера: 2788 Б свободно из 6144.
- [x] Измерен high-water HTTP/Ogg/PCM/PDM для SILK/CELT на стеке 5120 Б:
  свободно 1704/1624 Б. Это не worst-case гарантия для всех потоков.
  См. [раздельный профиль](ESP8266_OPUS_LIVE_STAGE_PROFILE.md).
- [ ] Проверить IRAM accesses на устройстве, SILK/Hybrid/CELT и OOM/recovery.
- [ ] Измерить decode-only и полный I2S-PDM CPU, непрерывность не менее 20 с,
  затем час с открытым WebUI; переключения/stop без зависаний.
- [ ] Пройти production-гейты общего плана; до этого не менять default.

Источники: [ESP8266Audio/libopus](https://github.com/earlephilhower/ESP8266Audio/tree/10d929ac01436dfe8856e0a06fd9ec35a848c6e2/src/libopus),
[Opus decoder API](https://www.opus-codec.org/docs/opus_api-1.6/group__opus__decoder.html),
[Ogg Opus RFC 7845](https://www.rfc-editor.org/rfc/rfc7845),
[Ogg RFC 3533](https://www.rfc-editor.org/rfc/rfc3533).
