# Opus: воспроизводимый тест на ESP8266 без сетевого аудио

Диагностический режим сохраняет обычные Wi-Fi, WebUI и OTA. Он не стартует
при загрузке, не отключает сеть и не требует UART RX. Тест запускается только
пустым `POST /api/native/opus-benchmark`; `GET` того же адреса читает результат.
Обычная production-сборка не содержит этих маршрутов и тестовых данных.

## Подготовка и запуск

Эталон обязан использовать `OPUS_FAST_INT64=0`, как Xtensa. Обычный x86-64
libopus выбирает другую fixed-point ветку: отдельные младшие биты PCM
различаются даже без изменений алгоритма. Генератор отклоняет эталон без
явного `-DOPUS_FAST_INT64=0`; default probe находится в
`.build/esp8266-opus-host-pristine-int64-0/probe`. Подготовка независимого
эталона описана в `tools/esp8266_opus_profile/README.md`.

```powershell
node tools/esp8266_opus_profile/build_board_fixtures.cjs
tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -Variant esp8266-opus-board-bench -EnableOpus -Diagnostic -OpusBenchmark -WebAudioPause short
node tools/esp8266_audio_profile/check_prefill_board.cjs ota --base http://192.168.100.6 --firmware firmware/development/esp8266-opus-board-bench/app.bin --output .build/opus-board-ota.json
node tools/esp8266_opus_profile/run_board.cjs --base http://192.168.100.6 --output .build/esp8266-opus-board-results.json
```

После обрыва наблюдения сначала читать статус либо использовать `--observe`,
не запускать тест заново и не сбрасывать плату. Перед application-only OTA
обновить совместимый `script.js.gz`, если плата ещё использует WebUI с другой
шкалой громкости. Wi-Fi и плейлист OTA приложения не заменяет.

## Что измеряется

В этой же диагностической сборке можно запустить реальный URL, не заменяя
плейлист: `POST /api/native/opus-stream`, тело — HTTP URL текстом (8–511 байт,
без переводов строк). Например:

```powershell
curl.exe --max-time 10 -H "Content-Type: text/plain" --data-raw "http://secure.live-streams.nl/opus.opus" http://192.168.100.6/api/native/opus-stream
node tools/test_esp8266_audio_continuity.cjs --base http://192.168.100.6 --seconds 25 --output .build/opus-live-continuity.json
```

Запуск проходит через обычную audio-task и HTTP/Ogg/PCM/I2S цепочку; метка
станции временно `OPUS TEST`, сохранённая станция и плейлист не меняются.
Для остановки используется обычный WebUI/`stop=1`. Этот маршрут отсутствует
в production так же, как raw benchmark. `/api/native/audio` дополнительно
возвращает `audio_stack_free` — lifetime watermark в байтах.

- Пять собственных фрагментов: SILK mono12, Hybrid mono24, CELT stereo64,
  stereo128, stereo510 кбит/с. Выход декодера mono 48 кГц, 20 мс на пакет.
- Первые 12 пакетов каждого фрагмента хранятся во flash (22756 байт вместе
  с word-aligned таблицами). Перед каждым измерением пакет копируется в DRAM.
- Один прогревочный проход и десять измеряемых проходов каждого фрагмента.
  На один режим — 120 пакетов / 2,4 секунды декодированного PCM. Это не тест
  непрерывности физического аудиовывода: PDM/DMA и normalizer не вызываются.
- Время охватывает только `yoradio_opus_decode_bounded()`, не копирование
  пакета, Ogg-demux, чтение HTTP или расчёт PCM checksum.
- `wall_us` включает вытеснение другими задачами. `task_us` использует
  микросекундный FreeRTOS runtime; другие задачи исключены, но остаются
  прерывания, приписанные текущей задаче, и небольшой overhead измерителя.
- `empty_task_us` — контрольный пустой интервал. Скрипт показывает сырой
  CPU-бюджет и отдельную оценку после вычитания этого overhead; не выдаёт
  её за точный счётчик CPU без ISR.
- CPU-бюджет = время / длительность полученного PCM × 100%. Более 100%
  означает, что этот режим не успевает в realtime даже без аудиовывода.
- Каждый проход сравнивает FNV-1a32 всего PCM с результатом pristine libopus
  на компьютере. Это аппаратная проверка fingerprint, не замена полного
  побайтового сравнения host-регрессий.
- Scratch high-water сбрасывается между режимами; `min_dram` относится к
  конкретному режиму. `stack_free_lifetime` — минимум свободного стека
  audio-task за всё время её существования, в байтах на этом SDK.

## Управление и безопасность памяти

POST ставит команду stop. Только audio-task освобождает активный декодер,
занимает общую IRAM, выполняет тест и освобождает четыре DRAM-выделения.
Новая команда плеера/OTA меняет generation и отменяет тест на границе пакета.
Повторный POST во время queued/running получает HTTP 409. Резерв DRAM теста
не ниже 2048 байт после выделений; это диагностический порог, не production
допуск длительного потокового воспроизведения.

`state`: 1 queued, 2 running, 3 complete, 4 error/cancelled. Ошибки libopus
передаются как есть; дополнительные коды: -9001 allocation/reserve,
-9002 cancelled, -9003 arena unavailable/busy, -9004 fixture bounds,
-9005 zero PCM, -9006 PCM mismatch, -9007 arena release failure.

Host harness выполняет настоящий модуль измерителя со stubs под ASan/UBSan:
успех, каждый allocation failure, отмена в разных режимах, busy, повторный
запуск, ошибки инициализации/декодирования/PCM, проверка пар malloc/free.
Команда: `node --test tests/esp8266-opus-board-benchmark.test.js`.

Физические результаты добавляются отдельно после OTA; сама успешная сборка
и host-проверки не доказывают скорость и непрерывность работы платы.

## Первый полный физический замер, 2026-09-09

Все пять PCM fingerprints совпали с независимым generic32-эталоном.
Сырой CPU-бюджет: SILK12 58,88%, Hybrid24 115,62%, CELT64 99,11%,
CELT128 120,55%, CELT510 198,72%. Пока только SILK12 имеет заметный запас
для сети и аудиовывода; это не результат проверки непрерывности радио.
Минимум свободного стека audio-task: 2788 из 6144 байт.

Подробности и JSON сохранены в
`firmware/development/esp8266-opus-board-bench/CHANGELOG.md`.
