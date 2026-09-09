# Ogg Opus для ESP8266 native

Статус на 2026-09-09: экспериментальная реализация собрана, проверена на ПК.
На физической плате ещё не проверены скорость, запас heap/стека и непрерывность
звука. В штатном профиле Opus **выключен**. MP3/AAC и их входной буфер 4096 байт
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
| Opus state, host x64 | 9198 Б вместо исходных 17860 Б |
| Opus state, Xtensa GCC 8.4 | 9134 Б, рассчитано по сгенерированному коду |
| IRAM reservation | 16384 Б, уже общая с MP3/AAC |
| DRAM scratch reservation | 7168 Б |
| Ogg + adapter, host x64 | 2040 Б, включая packet buffer |
| PCM | 1920 Б, один mono frame до 20 мс |
| Opus read-ahead | 1536 Б, отдельная настройка; MP3/AAC по-прежнему 4096 Б |
| Audio task stack при включённом Opus | 6144 Б вместо 4096 Б |

Это не размер всей прошивки и не свободная память платы. Heap allocator,
bridge, TCP/Wi-Fi, WebUI и остальные стеки учитываются отдельно. При открытии
Opus контролируется остаток heap не менее 4096 байт либо больший резерв caller;
это аварийный порог, **не** прохождение production-гейта 8/6 КиБ free/min heap.

По Xtensa disassembly `audio_task` сам резервирует 1792 байта, а суммарный
консервативный путь с рекурсией CELT и сменой режима может достигать примерно
4.7 КиБ до остаточных runtime/leaf расходов. Поэтому 4096 байт не оставлены
для Opus; даже 5120 дают слишком малый запас. Это статическая оценка возможного
пути, не фактический high-water. Word-path copy/clear проверен в ассемблере:
`l32i/s32i`, без byte/halfword обращений к IRAM.

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
| mono 12 кбит/с | SILK | 1808 Б | 11552 Б |
| mono 24 кбит/с | Hybrid | 2904 Б | 13040 Б |
| stereo 64 кбит/с | CELT | 6736 Б | 13040 Б |
| stereo 128 кбит/с | CELT | 6736 Б | 13040 Б |
| stereo 510 кбит/с | CELT | 6736 Б | 13040 Б |

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

- [ ] Следующий кандидат уменьшения DRAM: вынести две SILK `exc_Q14[320]`
  в постоянные IRAM-слоты (расчётная экономия 2552 Б с учётом указателей).
  Нужны cumulative persistent allocator, сохранение привязки при reset и
  mono→stereo, word-copy вместо `CNG.c` memcpy и повторный аудит Xtensa loads.
  Пока **не реализовано**; source type int32 сам по себе не исключает l16 load.
- [ ] Проверить target min/free/largest heap при Wi-Fi + WebUI + Opus.
- [ ] Измерить high-water audio stack и реальный запас, а не отдельные `.su`.
- [ ] Проверить IRAM accesses на устройстве, SILK/Hybrid/CELT и OOM/recovery.
- [ ] Измерить decode-only и полный I2S-PDM CPU, непрерывность не менее 20 с,
  затем час с открытым WebUI; переключения/stop без зависаний.
- [ ] Пройти production-гейты общего плана; до этого не менять default.

Источники: [ESP8266Audio/libopus](https://github.com/earlephilhower/ESP8266Audio/tree/10d929ac01436dfe8856e0a06fd9ec35a848c6e2/src/libopus),
[Opus decoder API](https://www.opus-codec.org/docs/opus_api-1.6/group__opus__decoder.html),
[Ogg Opus RFC 7845](https://www.rfc-editor.org/rfc/rfc7845),
[Ogg RFC 3533](https://www.rfc-editor.org/rfc/rfc3533).
