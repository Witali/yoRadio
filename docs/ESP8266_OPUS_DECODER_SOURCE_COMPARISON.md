# Opus: сравнение исходников для оптимизации ESP8266/LX106

Дата проверки: 2026-09-13. Исследование кода, **не сравнительный бенчмарк**.
Прошивка и алгоритм декодирования этим исследованием не изменены.

## Вывод

Готовой открытой замены с доказанным преимуществом над нашим декодером на
LX106 не найдено. Наиболее полезны отдельные скалярные изменения
ESP32-audioI2S и новый экспериментальный FFT из Xiph. Предлагается сохранить
нашу модель памяти и ASM backend, проверяя заимствования по одному.
Чужие показатели ARM/ESP32-S3/настольного CPU нельзя переносить на ESP8266.

Дополнительный поиск: проверены micro-opus от ESPHome и CherryAVP.
У первого действительно есть открытые Xtensa-патчи, но ключевые инструкции
отсутствуют на LX106, а часть арифметики меняет младшие биты. У второго
11 проверенных горячих файлов CELT побайтово совпадают с Xiph 1.6.1.

Наша база — fixed-point Opus 1.5.2 из ESP8266Audio, с ограниченными
переиспользуемыми аренами, разделением IRAM/DRAM и собственными ASM overlays.
Проверенный лучший кандидат требует 88,136% CPU на 192 кбит/с; до 70% нужно
ещё примерно 20,6% сокращения времени. Это raw decode, не доказательство
непрерывного радио с сетью и PDM. См. [протокол](ESP8266_OPUS_ASM_BANDS_OPTIMIZATION_PLAN.md)
и [происхождение нашей библиотеки](../esp8266/rtos-sdk-native/components/opus_decoder/UPSTREAM.md).

## Сравнение вариантов

| Вариант | Что действительно доступно | Значение для LX106 |
|---|---|---|
| [Xiph Opus](https://github.com/xiph/opus) | Эталонный C, fixed-point, отдельные архитектурные оптимизации | Основной источник; обновление версии само по себе не гарантирует ускорения |
| [ESP8266Audio](https://github.com/earlephilhower/ESP8266Audio/tree/10d929ac01436dfe8856e0a06fd9ec35a848c6e2/src/libopus) | Та же импортированная нами база 1.5.2 | Проверенный HEAD совпадает с нашим исходным импортом; нового декодера здесь сейчас нет |
| [ESP32-audioI2S](https://github.com/schreibfaul1/ESP32-audioI2S/tree/8ac301323a2afa93e3c89fc4b8073ffe2b756a94/src/opus_decoder) | Fixed-point C++, decoder-only CELT/SILK, inline entropy, развёрнутые циклы | Хороший источник отдельных функций; полная замена имеет другую и более щедрую модель рабочих буферов |
| [codec-opus](https://github.com/pschatzmann/codec-opus/tree/c02de6316dddbb9dffdf976c159c4eaacecdf12f) | Arduino/IDF-упаковка libopus, заявлена версия 1.6.1, fixed-point | Не самостоятельный ускоренный алгоритм; временная арена по умолчанию 60 000 B |
| [micro-opus](https://github.com/esphome-libs/micro-opus/tree/93bf9c10196e368405ee1501bfd72f0be2518741) | Xiph + открытые LX6/LX7-патчи, Ogg streaming, ESP-IDF allocator | Изучать отдельные идеи; готовый ASM не для LX106, pseudostack по умолчанию 120 000 B |
| [CherryAVP](https://github.com/cherry-embedded/CherryAVP/tree/1b299a518949be0c695687ee00acba4d95f5adb4) | MCU-обвязка fixed-point Xiph 1.6.1, пользовательский allocator | В проверенных горячих файлах нет отличий от Xiph; ограниченной scratch-арены нашего типа нет, используются VLA |
| [Rockbox](https://github.com/Rockbox/rockbox/tree/1784c9b8a7f1f2c8c535d8cb9dc965db0fe29e29/lib/rbcodec/codecs/libopus) | Embedded fixed-point, ASM для ARM/ColdFire, собственный allocator | Полезен как пример порта; найденные ASM ветви не для LX106 |
| [NXP audio-voice-components](https://github.com/nxp-mcuxpresso/audio-voice-components/tree/0d09428ea5159df561e8a33b3175147d5b854629/opus) | Исходники Opus 1.3.1 и интеграция SDK | Более старая база; специализированного LX106 backend в просмотренном дереве нет |
| [FFmpeg native Opus](https://github.com/FFmpeg/FFmpeg/blob/master/libavcodec/opus/dec.c) | Независимая реализация, float-буферы, float DSP и ресэмплер | Источник алгоритмических идей, но не готовый fixed-point вариант для CPU без FPU |
| [Espressif esp_audio_codec](https://github.com/espressif/esp-adf-libs/tree/master/esp_audio_codec) | Открытые API/регистрация, кодеки подключаются как готовые `.a` | В таблице поддерживаемых SoC нет ESP8266; исходников ядра для переноса из этого пакета не получаем |
| [Cadence hosted-xaf](https://github.com/foss-xtensa/hosted-xaf) | Framework, плагины и тесты; Opus требует внешней `xa_opus_codec.a` | Наличие слова Xtensa не означает совместимость HiFi DSP и LX106 |
| [Concentus](https://github.com/lostromb/concentus), [go-opus](https://github.com/tphakala/go-opus) | Порты fixed-point на другие языки, тесты; у go-opus есть SIMD | Полезны для проверок и идей управления памятью, не готовы для встраивания в нашу C/ASM прошивку |

Старый [arduino-libopus](https://github.com/pschatzmann/arduino-libopus)
архивирован и сам направляет в codec-opus; считать их двумя независимыми
ускоренными декодерами неправильно.

## Конкретные находки

### ESP32-audioI2S: выборочный inline и скалярное разворачивание

В [range_decoder.h](https://github.com/schreibfaul1/ESP32-audioI2S/blob/8ac301323a2afa93e3c89fc4b8073ffe2b756a94/src/opus_decoder/range_decoder.h)
применяется `always_inline` к `decode`, `decode_bin`, `dec_update`,
`dec_bit_logp`, `dec_icdf`, чтению байтов и `tell`.
У нас уже испытаны tell/update и их комбинация: переносить всё без разбора
нельзя. [Комбинация ухудшила скорость](ESP8266_OPUS_ASM_TELL_UPDATE.md).
Позднее быстрый путь трёх вызовов `ec_dec_bits(ec, 1)` поверх tell-inline
был [проверен и отклонён](ESP8266_OPUS_ASM_TELL_BITS1.md): корректный PCM,
но замедление на плате. Другие контексты/`ec_dec_bit_logp` остаются гипотезами
из [нашего списка](ESP8266_OPUS_ASM_INLINE_CANDIDATES.md), не обещанным выигрышем.

В [celt.cpp](https://github.com/schreibfaul1/ESP32-audioI2S/blob/8ac301323a2afa93e3c89fc4b8073ffe2b756a94/src/opus_decoder/celt.cpp)
`celt_inner_prod_c` развёрнут на четыре отсчёта с четырьмя аккумуляторами
и хвостовым циклом. В нашем исходном C fallback — один аккумулятор.
Это кандидат на unroll2/unroll4 без дополнительного массива; возможны
рост регистрового давления и промахов кэша. Нужна проверка точной арифметики.
`MAC16_16` здесь C-макрос, не доказательство наличия такой инструкции LX106.
`celt_udiv`/`celt_sudiv` используют обычное деление: выигрыша для нашего CPU
из одного этого упрощения не следует.

### Xiph: стабильная версия и отдельный новый FFT

[Актуальный стабильный выпуск — 1.6.1](https://opus-codec.org/downloads/).
`celt/entdec.c` и `celt/entcode.c` побайтово одинаковы в тегах 1.5.2/1.6.1.
Изменение `silk/decode_core.c` относится к обходу ошибки Clang/VLA и комментарию,
а не новому быстрому циклу. Это не утверждение об отсутствии изменений
во всех остальных файлах.

В main найден отдельный [коммит PFA FFT/MDCT](https://github.com/xiph/opus/commit/503d81b138d76621aae4b12786e90de48aa8db3a)
от 11 сентября: generic C, fixed-point путь, FFT с разложением 15×M и
специализированными малыми преобразованиями. **Он не входит в 1.6.1.**
В `celt/mdct_pfa.c` есть временный массив `nfft` комплексных элементов:
для 480 точек это 3840 B. Это размер массива, не установленный прирост
пикового RAM относительно прежней реализации. Требуется анализ времени жизни
и наложения арен. Порядок вычислений/сдвигов отличается; точное совпадение
PCM с нашей базой ещё не проверено.

FFT не заменяет `quant_all_bands`/PVQ — основное горячее направление нашего
[инструментированного профиля](ESP8266_OPUS_FUNCTION_PROFILE.md).
Его доли нельзя выдавать за точные доли production или обещание общего ускорения.

### micro-opus: настоящие Xtensa-патчи, но не для LX106

Проверены сами патчи, Kconfig и исходники, а не только README.
Основа — Xiph как submodule (`22244de5a79bd1d6d623c32e72bf1954b56235be`).
Проект [заявляет примерно 17–25% ускорения на ESP32/ESP32-S3](https://github.com/esphome-libs/micro-opus/tree/93bf9c10196e368405ee1501bfd72f0be2518741).
Это результат авторов для других ядер, не наш замер и не прогноз для ESP8266.

В [fixed_lx7.h](https://github.com/esphome-libs/micro-opus/blob/93bf9c10196e368405ee1501bfd72f0be2518741/patches/celt/xtensa/fixed_lx7.h)
используются `MULSH` и `CLAMPS`. В
[pitch_lx7.h](https://github.com/esphome-libs/micro-opus/blob/93bf9c10196e368405ee1501bfd72f0be2518741/patches/celt/xtensa/pitch_lx7.h)
скалярное произведение развёрнуто по четыре и использует `MULA.DD`,
`LDINC`, MAC-регистры и `LOOPNEZ`.

| Возможность | Наш LX106, по `core-isa.h` установленного toolchain |
|---|---|
| `MULSH` / старшая половина умножения | `XCHAL_HAVE_MUL32_HIGH=0` |
| MAC16 / `MULA.DD` | `XCHAL_HAVE_MAC16=0` |
| Аппаратный цикл | `XCHAL_HAVE_LOOPS=0` |
| Насыщение `CLAMPS` | `XCHAL_HAVE_CLAMPS=0` |
| `NSA` / `NSAU` | `XCHAL_HAVE_NSA=1`; `nsau` уже есть в нашем GCC-ASM `entcode.c.s` |

Проверен toolchain `esp-2020r3-49-gd5524c1-8.4.0`, файл
`xtensa-lx106-elf/include/xtensa/config/core-isa.h`. Родство Xtensa не делает
эти патчи бинарно совместимыми; заменять недоступные DSP-команды длинными
эмуляциями ради самого переноса нецелесообразно без измерений.

Есть и важное отличие точности: Q15/Q31-пути через `MULSH` с последующим
сдвигом влево намеренно теряют младший бит. Для `MULT16_32_Q15(1, 32768)`
наша generic-формула даёт **1**, формула micro-opus — **0**. Это проверено
локальной целочисленной моделью операции; это **не** замер SNR и не сравнение
полностью декодированного PCM. Поэтому перенос этих формул не удовлетворяет
нашему требованию неизменного результата автоматически.

В [Kconfig](https://github.com/esphome-libs/micro-opus/blob/93bf9c10196e368405ee1501bfd72f0be2518741/Kconfig)
pseudostack задаётся в байтах: default **120 000**, диапазон 60 000–240 000.
Это настраиваемый резерв, не измеренный минимальный расход decoder-only.
Его нельзя складывать с чужими данными о heap и называть минимумом Opus.
Наша разделённая ограниченная арена предпочтительнее для ESP8266.

Полезная переносимая идея — выбирать короткий или развёрнутый цикл по `N`:
авторы отдельно отмечают, что накладные расходы DSP-варианта не оправданы
для малых скалярных произведений. Проверять такую специализацию у нас надо
на собственных LX106-инструкциях, без дополнительных массивов. Ускорение
пока не измерено. Патчи `celt_mathops.patch` с упрощением float log/exp
не ускорят наш fixed-point путь.

### CherryAVP: компактная обвязка, не новый быстрый CELT

[Сборка](https://github.com/cherry-embedded/CherryAVP/blob/1b299a518949be0c695687ee00acba4d95f5adb4/cherryavp.cmake)
включает `FIXED_POINT`, `DISABLE_FLOAT_API`, `VAR_ARRAYS` и версию 1.6.1.
[Адаптер](https://github.com/cherry-embedded/CherryAVP/blob/1b299a518949be0c695687ee00acba4d95f5adb4/avcodec/src/opus_decode.c)
вызывает обычные `opus_decoder_create` / `opus_decode` / `opus_decoder_destroy`,
заранее проверяет достаточность пользовательского PCM-буфера.
`custom_support.h` перенаправляет alloc/realloc/free на allocator проекта;
само это не сокращает память алгоритма.

Git blob SHA совпали с Xiph tag `v1.6.1` для всех 11 проверенных файлов:
`bands.c`, `entdec.c`, `entcode.c`, `cwrs.c`, `vq.c`, `pitch.c`, `kiss_fft.c`,
`mdct.c`, `celt_lpc.c`, `mathops.c`, `fixed_generic.h`.
Это доказательство идентичности **данных файлов**, не всего проекта.
Перенос обвязки не даёт основания ожидать ускорения `quant_all_bands`.
VLA также не заменяют наш контроль пикового scratch и стека.

### Другие embedded-порты

В codec-opus `entdec.c` отличается от проверенного Xiph только условием
подключения конфигурации и путём заголовка. `config.h` включает fixed-point
и heap-pseudostack размером 60 000 B; `stack_alloc.h` действительно использует
его при выделении. Это настраиваемый резерв, не измеренный минимум декодера.

У Rockbox включены fixed-point, отключён float API, заменены alloc/free,
но сохранены VLA. README описывает импорт снимка 2019 года; это не дата
всех последующих изменений. ARM/ColdFire ASM нельзя прямо копировать на LX106.
NXP публикует версию 1.3.1 и собирает обычные C-файлы. Более удобная SDK-обвязка
не доказывает более быстрый CELT.

## Что можно честно сказать о RAM

В ESP32-audioI2S семь постоянно выделенных рабочих массивов CELT дают:

| Массив | Размер, B |
|---|---:|
| `m_freq_buf` | 3840 |
| `m_scratch_buf` | 3840 |
| `m_norm_buf` | 2496 |
| `m_decode_i32_buf` | 840 |
| `m_collapse_masks_buf` | 42 |
| `m_mdct_norm_buf` | 3840 |
| `m_hadamard_tmp_buf` | 1920 |
| Всего | **16 818** |

Расчёт: размеры из `CeltDecoder::init`, типы и `nbEBands=21` из `celt.h`.
Это **не весь декодер**: исключены history/state, SILK, PCM, контейнер,
стек и служебная память allocator. `ps_ptr` допускает PSRAM и fallback на heap.
Перенос отдельных циклов не требует переноса этих массивов.

Espressif публикует для Opus decoder 26,6 KB heap и 5,86% CPU, но это
**ESP32-S3R8, 48 кГц/stereo и синтетический вход**, не наш ESP8266/192 кбит/с.
Стек в число не входит; рекомендация около 20 KB относится к задаче,
поддерживающей весь набор декодеров, а не к точно измеренному стеку Opus.
[Источник и ограничения таблицы](https://github.com/espressif/esp-adf-libs/tree/master/esp_audio_codec#performance).

Для честного численного ранжирования нужны одинаковые пакеты, настройки
каналов/PCM, компилятор, CPU/flash, учёт постоянной памяти, максимальной
scratch-арены, стека, DRAM/IRAM и одинаковое окружение Wi-Fi/WebUI.
В этом исследовании новые реализации на плате не запускались.

## Приоритет следующей проверки — не отметки о реализации

1. Выборочные быстрые пути entropy в нашем ASM: непроверенные контексты
   `ec_dec_bits`/`ec_dec_bit_logp`; не повторять отклонённый bits1 поверх tell-inline
   без новой причины. Нормализацию оставить холодным вызовом. Изучить
   `dec_icdf` как дополнительный кандидат, только если частота вызовов оправдает.
2. Скалярные unroll2/unroll4 для реально горячих скалярных произведений:
   сохранить точный результат, проверить spill/load и размер кода.
3. Отдельно оценить новый Xiph PFA: сначала RAM/PCM gate, затем скорость.
   Не обновлять всю библиотеку ради одного FFT и не обещать битовую точность.
4. Сохранять нашу разделённую IRAM/DRAM-арену. Не переносить чужие
   постоянные scratch-буферы и большие pseudostack как готовую конфигурацию.
5. По примеру micro-opus сравнить короткий цикл для малых `N` и unroll2/unroll4
   для длинных векторов. Не копировать отсутствующие LX106 DSP-инструкции
   и не применять арифметику с потерей младших битов как точную оптимизацию.

Для каждого кандидата: локальные крайние случаи/PCM, ASM-аудит,
не менее 10 запусков кандидата и контроль до/после на плате; отдельные RAM,
CPU и wall метрики. Приоритет 192 кбит/с с сохранением проверок низких битрейтов.
После принятия — отдельная проверка непрерывного I2S PDM с WebUI.
Соответствие стандарту Opus само по себе не равно побитовому совпадению PCM.
При переносе исходника сохранять его лицензию и авторство.

## Воспроизводимость исследования

Локальные sparse-копии сохранены в игнорируемой
`.build/opus-source-survey-20260913/`; в прошивку они не включены.

| Копия | Проверенный commit |
|---|---|
| xiph main | `503d81b138d76621aae4b12786e90de48aa8db3a` |
| esp8266audio | `10d929ac01436dfe8856e0a06fd9ec35a848c6e2` |
| audioi2s | `8ac301323a2afa93e3c89fc4b8073ffe2b756a94` |
| codec-opus | `c02de6316dddbb9dffdf976c159c4eaacecdf12f` |
| arduino-libopus | `bae0f8570b03071d0101445059e7178bed8bd144` |
| nxp | `0d09428ea5159df561e8a33b3175147d5b854629` |
| rockbox | `1784c9b8a7f1f2c8c535d8cb9dc965db0fe29e29` |
| micro-opus | `93bf9c10196e368405ee1501bfd72f0be2518741` |
| cherry-avp | `1b299a518949be0c695687ee00acba4d95f5adb4` |

Прочие строки сравнительной таблицы проверялись по открытым исходникам,
README и сборочным файлам по ссылкам; для них нет локального бенчмарка.

Проверка идентичности entropy-файлов:

```powershell
git -C .build/opus-source-survey-20260913/xiph rev-parse v1.5.2:celt/entdec.c v1.6.1:celt/entdec.c
git -C .build/opus-source-survey-20260913/xiph rev-parse v1.5.2:celt/entcode.c v1.6.1:celt/entcode.c
```

Для первой пары оба Git blob SHA — `027aa24bcaff848273d0a3615c71fb38fbf0528b`,
для второй — `70f32016ecee977045d9f05da7c7fa16346d4142`.

Проверку CherryAVP можно повторить для каждого файла из списка выше:

```powershell
git -C .build/opus-source-survey-20260913/cherry-avp rev-parse HEAD:third_party/xiph-opus/celt/bands.c
git -C .build/opus-source-survey-20260913/xiph rev-parse v1.6.1:celt/bands.c
```

Оба SHA для `bands.c`: `afde197ef8f4c42a7d13c49968f2cc33f3d71e8b`.
Идентичность проверена на зафиксированных commit, а не на будущих HEAD.
