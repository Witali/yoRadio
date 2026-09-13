# Opus: function-call profile on ESP8266

Diagnostic-only `-OpusFunctionProfile`, CPU160/QIO40, raw benchmark, PCM48k
mono. The baseline Opus GCC-ASM objects and algorithm are unchanged. GNU
linker `--wrap` measures14 selected cross-object symbols. Same-object,
static/inlined functions are NOT independent observations: their work is
included in the nearest measured parent's self time. In particular, bands
contains quant_partition/quant_band and vector rotations can remain inline.

Every row reports call count, inclusive/self CPU and wall microseconds,
maximum inclusive CPU and wall duration. CPU is the SDK accumulated task
runtime plus current running slice, read coherently with its own timer;
other tasks are excluded, ISR time charged to the task is not. Wall includes
preemption. The downloaded SDK is untouched: the build-local tasks.c adapter
includes the original and appends only a getter. Its archive member basename
is preserved, so SDK linker rules still apply. Counter wrap/overflow, broken
nesting and longjmp-unwound scopes invalidate the profile.

The outer decode wall window also uses this getter in function-profile
builds. SDK runtime statistics use esp_get_time(), whereas esp_timer_get_time()
combines g_esp_os_us and CCOUNT. They must not be treated as one identical
clock for strict nested-window checks. The first three v1 pilot reports are
retained separately: the third failed that check (538 us excess over120
packets); none of the pilot series is used in the final function statistics.
No decoder/PCM error occurred in those pilots. The ordinary control timing
path remains unchanged.

Self time subtracts measured direct children. Consequently all self rows sum
to100% of the measured root; inclusive rows overlap and must not be summed.
Root self includes unmeasured functions and measurement bookkeeping, not
just the source statements of the root wrapper. Counts per second refer to
one second of decoded audio (samples/48000), NOT wall execution speed.

One bounded392-byte row array (14x28) is reused across fixtures. Only the last
completed fixture remains in the report (the selected corpus ends in192kbps).
The warmup round is excluded. No PCM/packet buffer or additional task is
allocated. Completed data are exposed by the existing benchmark endpoint;
live partial rows are hidden.32 empty clock pairs characterize minimum/maximum
clock cost, not full wrapper/cache overhead; no speculative cost is subtracted.
A matching uninstrumented control and repeated board trials are required.

`-OpusFunctionProfile -OpusFunctionProfileCoarse` intercepts only root,
quant_all_bands, clt_mdct_backward_c and opus_fft_impl. All other symbols
are linked directly, without even a disabled wrapper. This gives a second,
less intrusive estimate of the major-stage shares; its overhead must still
be measured against an uninstrumented control. Detailed and coarse self
shares are different decompositions and must never be mixed in one total.

Tests cover nesting, preemption, timestamps wrapping, totals overflowing,
OOM unwinding, disabled instrumentation, ABI and full exact PCM for five
fixtures plus mixed-mode PLC/reset. Host timing is synthetic, not LX106 speed.
Production remains uninstrumented and no playback qualification is implied.

```powershell
node --test tests/esp8266-opus-function-profile.test.js
node tools/esp8266_opus_profile/run_function_regressions.cjs
```

## Результаты на ESP8266, 2026-09-13

Проверены GCC-ASM fixed-point Opus, CPU160/QIO40, собственные пакеты из
flash/RAM, без сетевого аудио, demux, нормализации и PDM. Wi-Fi/WebUI работают.
Источник192кбит/с стерео декодируется в PCM48кГц mono. Каждый профиль:
10 запусков ×120 измеряемых кадров по20мс =1200 кадров /24с исходного аудио.
Это не24с непрерывного воспроизведения: raw-тест специально делает yield
между кадрами. Прогрев не входит в статистику.

**Это профиль измерительной сборки, не точные доли обычной прошивки.**
Подробные обёртки увеличивают медианный CPU-бюджет92.876% ->169.046%
(+82.011% относительно контроля). Даже крупностадийный профиль даёт около
122.777% вместо92.819% (+32.275%). Влияние включает инструментирование и изменённую компоновку/
поведение flash cache; их отдельные вклады этим опытом не установлены.
Нельзя просто вычесть одинаковое число микросекунд из каждой строки либо
масштабировать все функции одним коэффициентом и назвать это измерением.

### Крупные стадии: меньше вмешательства, но всё ещё инструментированный код

Проценты считаются от CPU-времени корневого вызова декодера, **не от всего
доступного времени процессора**. Self вычитает измеренные вложенные вызовы;
эта колонка вместе с «прочим» даёт100%. Среднее и максимумы — inclusive.

| Функция | Вызовов/с аудио | Среднее CPU, мкс | Max CPU, мкс | Max wall, мкс | Self CPU | Inclusive CPU |
|---|---:|---:|---:|---:|---:|---:|
| quant_all_bands | 50.00 | 16500.98 | 18968 | 23351 | 67.49% | 67.49% |
| clt_mdct_backward_c | 79.17 | 2542.06 | 4634 | 7157 | 9.07% | 16.46% |
| opus_fft_impl | 79.17 | 1140.99 | 2272 | 4795 | 7.39% | 7.39% |
| Остальное внутри root | — | — | — | — | 16.05% | — |
| Весь yoradio_opus_decode_bounded | 50.00 | 24450.47 | 27004 | 31487 | — | 100% |

Максимум CPU и wall не обязательно относится к одному вызову. Wall включает
вытеснение другими задачами; CPU исключает их, но включает начисленное ISR.
`quant_all_bands` здесь включает PVQ и энтропийные дочерние операции.
«Остальное» содержит неизмеренные этапы и служебный код измерителя.

### Часто вызываемые функции: подробный профиль

На один20-мс кадр / на секунду исходного аудио:

- ec_dec_uint:153.75 /7687.50;
- ec_dec_update:151.83 /7591.67;
- alg_unquant и decode_pulses:по137.33 /6866.67;
- ec_decode:109.83 /5491.67;
- ec_dec_bit_logp:75.83 /3791.67;
- ec_dec_bits:45.58 /2279.17.

Это именно перехваченные внешние вызовы. Например, обращения между
функциями внутри entdec не перехватываются GNU --wrap и остаются в parent
self. celt_decode_with_ec имеет0 перехватов на этом192k corpus: основной путь
в opus_decoder.c.s вызывает celt_decode_with_ec_dred, а не этот символ.
Нулевой счётчик не означает, что CELT не работает. Полные14 строк с
средними/max CPU, max wall, self/inclusive и количеством вызовов сохранены
в [подробной таблице](../firmware/development/esp8266-opus-functions-192-v2/summary.md).

### Корректность, память и ограничения

- 18 host-тестов измерителя, жизненного цикла raw/output benchmark и ASM
 backend проходят. Пять потоков12/24/64/128/192 и переходы/PLC/reset побитно
 совпадают; max PCM error0, SNR относительно эталонаInfinity. Скорость host
 не используется как скорость LX106.
- 110 оригинальных ASM object-файлов побайтово одинаковы в каждой паре.
 Профиль не меняет арифметику декодера. Проверено, что coarse ELF содержит
 ровно четыре __wrap_* символа; остальные вызовы идут без обёрток.
- Дополнительная static DRAM416B; static IRAM не меняется. Stack lifetime
 free:1260B detailed,1452B coarse,1660B у первого контроля. Стек не уменьшали.
- Minimum sampled DRAM:4252B detailed,7748B coarse. В первом контроле
 attempt6:884B, lifetime heap minimum860B, один HTTP observation timeout;
 decoder завершился с точным PCM, но CPU192 вырос до105.613%. Этот запуск
 не исключён. Причина давления RAM не установлена; отсутствие утечек всего
 приложения и запас памяти под живое радио этим тестом не доказаны.
- Приоритет дальнейшей оптимизации — bands/PVQ, затем synthesis/MDCT.
 Доли из detailed и coarse нельзя смешивать в одну сумму. Для оценки
 невозмущённой прошивки нужен менее инвазивный sampling/layout-controlled
 эксперимент. Цель192кбит/с <=70% CPU и непрерывность звука не достигнуты.

Первые три pilot-прогона с различными таймерами сохранены отдельно у v1,
не подмешаны к исправленным сериям. Все выбросы исправленных серий остаются
в raw reports. Все40 основных запусков завершены, пять PCM hashes в каждом
совпали. Вторая контрольная серия без ошибок наблюдения: CPU192 median92.819%,
mean92.859%, p95/max93.012%, maximum wall вызова22.878мс. Это raw-only, не
весь плеер. В первой контрольной серии выброс105.613% по-прежнему учтён.

Полные [coarse таблицы](../firmware/development/esp8266-opus-functions-coarse-v1/summary.md)
и [JSON](../firmware/development/esp8266-opus-functions-coarse-v1/summary.json)
содержат обе конфигурации пары, hashes и статистику всех попыток.
Отдельные [проверки машинного кода и секций](../firmware/development/esp8266-opus-functions-coarse-v1/build-audit.json).

Обычная прошивка восстановлена через OTA: app0x10000, Wi-Fi подключён,
RSSI-61dBm, ошибок нет, исходная станция сохранена, воспроизведение оставлено
остановленным, как до теста. Свободно27628B heap. SPIFFS не изменялся.
[Доказательство возврата](../firmware/development/esp8266-opus-live512-idle3s-20260913/restore-after-function-profile.json).

### Воспроизведение серий и отчётов

Сборка: `tools/esp8266_audio_profile/build_i2s_pdm_production.ps1` с
`-Diagnostic -EnableOpus -OpusBackend gcc-asm -OpusWordAsm
-OpusIcdfFlashWord -OpusFirFlashWord -NoSpiffsCache -Pdm32Iram -Pdm32Batch
-OpusBenchmark -OpusBenchmarkFixtures firmware/development/esp8266-opus-asm-library/fixtures`.
Добавить `-OpusFunctionProfile` для подробного профиля и дополнительно
`-OpusFunctionProfileCoarse` для крупных стадий; контроль без обоих флагов.
Остальные параметры, ревизия и hashes записаны в manifest.json каждой пары.

```powershell
& tools/esp8266_opus_profile/run_raw_series.ps1 -Directory .build/my-function-runs -Fixtures firmware/development/esp8266-opus-asm-library/fixtures -Attempts 10 -IntervalMs 15000
node tools/esp8266_opus_profile/summarize_functions.cjs --profile <profile>/reports --control <control>/reports --profile-artifact <profile> --control-artifact <control> --output <profile>/summary.json
```

OTA выполняется отдельно штатным инструментом, только app. Повторный POST
теста запрещён до выяснения состояния предыдущего незавершённого запуска.
Summary проверяет manifest/image hashes, совпадение конфигурации пары,
PCM, полное покрытие всех попыток, временные окна и сумму self-времён.
