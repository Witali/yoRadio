# Повторяемое измерение MP3 / AAC / Opus на ESP8266

## Что измеряем

- Wemos D1 mini, LX106 160 МГц, QIO40, fixed-point декодеры.
- MP3: актуальный Helix SSO с моносинтезом и shared-reorder; AAC: Helix
  AAC-LC с блочной выдачей 512 отсчётов. Opus: принятая цепочка 18 ASM-оптимизаций.
- PCM на выходе декодера: mono, 48 кГц. Стереоисточник декодируется в mono,
  как в обычной прошивке. Opus 12/24 кбит/с — исходный mono SILK/hybrid;
  64/128/192 — stereo CELT. Это разные режимы кодека, не только битрейт.
- Полные сжатые кадры копируются из flash в RAM **до** начала замера.
  Сеть, Ogg demux, нормализация, PDM, DMA backpressure и копирование входа
  не входят в измеряемый вызов. Код и таблицы декодера остаются во flash:
  их обычные cache miss включены.
- Wi-Fi/WebUI/OTA остаются доступны. FreeRTOS runtime counter исключает
  время других задач, но **не исключает ISR**, приписанные SDK этой задаче.
  Поэтому это приближение времени CPU декодера, а не цикл-точный замер
  при отключённых прерываниях. `wall_us` отдельно включает вытеснение.
- Два `vTaskDelay(1)` принудительно фиксируют runtime counter вне decode
  wall window. Пустой интервал замеряется 16 раз. Основная таблица использует
  необработанное task time; отдельная оценка вычитает его overhead.
- В Helix замеряется `helix_codec_process_one()` с минимальным PCM callback:
  проверка формата и счётчик samples. Полный PCM hash считается только в
  неизмеряемом прогревочном круге. В Opus hash считается после
  окончания замера. Проверки самих декодеров не заменяются этим бенчмарком.

## Сохранённые инструменты

- `tools/esp8266_audio_profile/generate_helix_timing.cjs`: MP3 64/128/320 и
  AAC-LC 48/128/320 из одного собственного tone/noise сигнала, 48 кГц stereo.
  20 последовательных кадров на вариант, без потери MP3 bit reservoir;
  заголовок хранит выровненные uint32 слова для безопасного чтения flash.
- `tools/esp8266_opus_profile/build_board_fixtures.cjs`: существующий
  генератор raw Opus пакетов и независимого generic32 PCM-эталона.
- `tools/esp8266_audio_profile/run_codec_timing.cjs`: серия измерений,
  по умолчанию 10; отказ от перезаписи старых результатов и остановка при ошибке.
  Не прошивает и не сбрасывает плату, не использует UART.
- `tools/esp8266_audio_profile/summarize_codec_timing.cjs`: единая таблица
  Markdown и JSON, медианы средних по запускам, диапазон CPU, максимум wall,
  остатки RAM/стека. Ошибки и неполные прогоны не исключаются молча.
- `tests/esp8266-helix-timing.test.js`: host ASan/UBSan для границ замера,
  повторных запусков, отмены, OOM и decode error; проверки парсера кадров.

## Воспроизведение

Точный использованный корпус сохранён в `tests/fixtures/helix_timing/`:
готовый заголовок, manifest и исходные кодированные файлы. Для повторения
того же измерения можно передать этот каталог в `-HelixTimingFixtures` и
`--fixtures` без генерации/FFmpeg. Генератор нужен для обновления корпуса;
другая версия FFmpeg может изменить байты и время декодирования.

Из корня рабочей копии, Node.js + FFmpeg + установленный SDK/toolchain:

```powershell
node tools/esp8266_audio_profile/generate_helix_timing.cjs .build/helix-timing-fixtures
node --test tests/esp8266-helix-timing.test.js tests/esp8266-opus-board-benchmark.test.js
```

Диагностическая сборка Helix, используя подготовленный каталог Opus fixtures
для существующего benchmark/runtime профиля. Этот каталог не встраивается
в Helix-измеритель; нужны его manifest/header для общего builder:

```powershell
./tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 `
  -SdkPath C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk `
  -RuntimeRoot C:/Work/yoRadio/.build -Variant esp8266-helix-timing-20260919 `
  -Diagnostic -EnableOpus -OpusBenchmark `
  -OpusBenchmarkFixtures C:/Work/yoRadio/.build/esp8266-opus-board-through192 `
  -HelixTimingFixtures .build/helix-timing-fixtures
```

Образ и manifest сохраняются в `firmware/development/<variant>/`. Только
по явному решению проводить тест на плате загрузить app через существующий
`check_prefill_board.cjs ota --firmware .../app.bin --output .../ota.json`.
Не записывать bootloader/разметку/SPIFFS, не переключаться автоматически на USB.

После загрузки подходящего образа:

```powershell
node tools/esp8266_audio_profile/run_codec_timing.cjs --mode helix `
  --fixtures .build/helix-timing-fixtures --runs 10 --output .build/timing/helix
```

Для Opus применяется сохранённый и проверенный raw образ
`firmware/development/esp8266-opus-ebands-final-candidate-v2/app.bin`.
Он содержит ту же принятую ASM-цепочку, что перенесена в main, но другую
компоновку диагностической программы. Это не замер live радио main.
Пакеты/PCM/hashes берутся из `.build/esp8266-opus-board-through192`;
если каталога нет, восстановить его существующим `build_board_fixtures.cjs`
с `--corpus tests/fixtures/opus_native/through192` и независимым pristine
generic32 probe согласно `tools/esp8266_opus_profile/README.md`. Builder
проверяет независимую эталонную конфигурацию; не подменять хеши.

```powershell
node tools/esp8266_audio_profile/run_codec_timing.cjs --mode opus `
  --fixtures C:/Work/yoRadio/.build/esp8266-opus-board-through192 `
  --runs 10 --output .build/timing/opus
node tools/esp8266_audio_profile/summarize_codec_timing.cjs `
  .build/timing/summary .build/timing/helix .build/timing/opus
```

После измерений вернуть `firmware/development/esp8266-main/app.bin` через OTA,
проверить смену слота и доступность `/api/native/status`. Тестовый бенчмарк
не является обычной радио-прошивкой и не доказывает непрерывность звука.

## Как читать таблицу

`CPU-бюджет = сумма task_us / длительность декодированного аудио × 100%`.
Например, 78% — около 780 мс CPU на секунду аудио, остаётся около 220 мс
для остальной работы до учёта Wi-Fi, PDM и других расходов; это не измеренный
idle всей платы. Времена одного кадра нельзя напрямую сравнивать без его
длительности: MP3 — 24 мс, AAC-LC — 21.333 мс, Opus — 20 мс.

Короткие собственные фрагменты повторяются с новым состоянием декодера между
кругами: сохраняются естественные зависимости между кадрами внутри фрагмента,
но результат зависит от контента и не является worst-case для всех потоков.
Для Opus проверяются независимый PCM hash и samples каждого круга. Для Helix
проверяются ненулевой PCM прогрева, точное число samples/кадров и стабильный
прогревочный hash между запусками; это проверка повторяемости, не независимый
эталон качества. HE-AAC/SBR этой AAC-LC матрицей не покрывается.
