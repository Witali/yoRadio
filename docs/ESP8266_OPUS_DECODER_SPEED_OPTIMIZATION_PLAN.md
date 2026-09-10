# ESP8266: аудит алгоритма Opus и план ускорения

Дата: 2026-09-10. Native fixed-point libopus1.5.2, целевой GCC8.4 из
сборки `391a85b`, CPU160/QIO40. A1 проверен на плате и сохранён как отдельный
флаг. Два pulse-cache варианта A2 отклонены после измерений. Остальные
пункты ниже — проверяемые гипотезы, не обещание ускорения.

## Вывод

Приоритет — статические таблицы, программные деления и специализация циклов,
а не снижение точности или ещё одна очередь PCM. Конкретный кандидат был
в SILK FIR: восемь narrow flash loads на каждый отсчёт. Его исправление
уже подтвердило выигрыш. Следующий приоритет — профиль этапов CELT и его
decoder-only специализация; pulse-cache больше не менять без новой гипотезы,
объясняющей два отрицательных A/B.

У LX106 есть MUL16S/U, MULL и NSA/NSAU, но нет MULUH/MULSH, аппаратного
деления, MAC16 и zero-overhead loops. Проверено по core-isa.h используемого
SDK; [официальный источник Espressif](https://github.com/espressif/ESP8266_RTOS_SDK/blob/master/components/esp8266/include/xtensa/config/core-isa.h).
Не предлагать отсутствующие инструкции как готовое ускорение.

## Измеренная исходная точка

| Поток | Чистый декодер, CPU-бюджет прежнего A/B | Flash → PCM → PDM, новый CPU-бюджет |
|---|---:|---:|
| SILK mono12 | 58.20% | 70.84% |
| Hybrid mono24 | 91.85% | 104.92% |
| CELT stereo64 → mono | 74.35% | 86.48% |
| CELT stereo128 → mono | 90.03% | 107.94% |
| CELT stereo510 → mono | 150.91% | 189.97% |

Это разные режимы теста, не разложение одного одновременного замера.
Разность столбцов нельзя точно назвать временем PDM. Во втором есть flash
copy, PCM hash, нормализация, output и ISR, начисленные задаче. Аудиосеть
отсутствует, но Wi-Fi/WebUI продолжают работать.
[Методика, RAM, ошибки и ограничения](ESP8266_OPUS_FLASH_OUTPUT_BENCHMARK.md).

Только SILK12 прошёл один 24-секундный интервал без DMA miss. CELT64 имеет
средний запас, но отдельные вызовы не укладываются в срок. Hybrid24/CELT128
нуждаются в снижении вычислительных затрат: только входной буфер это не
исправит. CELT510 сейчас далеко от realtime.

## Карта пути и что уже оптимизировано

Все исходники ниже относительно `esp8266/rtos-sdk-native/components/opus_decoder/`.

```text
HTTP/read-ahead
  → ogg_opus_demux.c: header, lacing, CRC, один packet buffer
  → native_opus.c: Head/Tags, длительность, pre-skip/granule
  → upstream/src/opus_decoder.c: TOC, кадры, режим, переходы
      ├─ SILK: indices/pulses → NLSF/LPC/LTP → PCM ядра → resampler
      ├─ CELT: energy/allocation → PVQ/bands → IMDCT/FFT → postfilter
      └─ Hybrid: SILK + CELT с сохранением порядка и округления
  → PCM16 mono48k, gain, pre-skip/EOS
  → callback ≤512 отсчётов → PDM32 → DMA
```

Range decoder общий, символы зависимы последовательно. Predictor, overlap,
energy и history живут между кадрами, это не свободная временная память.
Сверка структуры: [RFC6716, раздел 4](https://www.rfc-editor.org/rfc/rfc6716#section-4),
Ogg/pre-skip/granule: [RFC7845](https://www.rfc-editor.org/rfc/rfc7845).

Уже сделано, не выдавать за новые предложения:

- Fixed-point, `OPUS_FAST_INT64=0`, float API выключен, soft-float imports нет.
- `-O3`; многие умножения уже разложены на 32-битные операции.
- Общая 16-КиБ IRAM arena для history/проверенного word scratch. Bounded
  scratch/OOM boundary; malloc/free внутри packet decode нет.
- MDCT/FFT читают 16-битные константы через word loads. В target
  `clt_mdct_backward_c` и `opus_fft_impl` narrow loads отсутствуют.
- WordASM в private helpers; static flash ICDF через 32-bit loads.
- Убран ненужный 48 кГц deemphasis scratch; folding может занять ещё не
  используемый PCM. Для Hybrid такое перекрытие запрещено.
- CELT stereo→mono уже суммирует спектры до **одного** IMDCT.
- Ogg CRC уже 16-entry nibble table, не побитный 8-шаговый цикл.
- SILK LTP5/LPC10/16 MAC частично развёрнуты, FIR8 тоже развёрнут.
- Пропуск post-packet yield отменён после отрицательного A/B. Loan128
  diagnostic-only: аппаратный тест не показал устойчивого общего выигрыша.

## Кандидаты без изменения PCM

### A1. SILK FIR: четыре 32-битные загрузки вместо восьми 16-битных

`silk/resampler_private_IIR_FIR.c`, внутренний INTERPOL, строки 52–59 на
ревизии аудита. Восемь коэффициентов `silk_resampler_frac_FIR_12` на каждый
выходной отсчёт. Таблица 96 байт в `.flash.rodata`, адрес 0x402d8424 в данном
ELF. Target действительно содержит восемь `l16ui` из двух строк таблицы.
Остальные narrow loads функции читают PCM/стек и сами по себе корректны.

Предложение: читать четыре пары существующим word helper, извлекать signed16,
сохранив порядок восьми MAC, rounding и saturation. Не копировать таблицу
в DRAM; не держать все коэффициенты одновременно, если появляются spills.

`silk_DWORD_ALIGN` включается только при EMBEDDED_ARM и пуст на LX106.
Поэтому нужна явная гарантия 4-byte alignment определения этой таблицы,
не зависимость от случайного текущего ELF. Данные остаются 96 байт, максимум
padding flash; новая постоянная RAM не нужна. Проверить stack-frame GCC.

Для 48000 отсчётов/с этот FIR-путь выполняет 384000 narrow coefficient loads/с.
Это число операций, **не измеренное число исключений или прогноз ускорения**.
Другие варианты ресэмплера такого выигрыша не получат.

Эксперимент: `-OpusFirFlashWord` в production-builder (требует `-EnableOpus`),
CMake `YORADIO_OPUS_FIR_FLASH_WORD`, по умолчанию OFF. Сохранён исходный
путь для A/B. ASan/UBSan:35 случаев,357590 отсчётов интерполяции, все12 строк
таблицы и дробные фазы; результат точный. Полный PCM:5 фикстур и смешанный
SILK mono/stereo/Hybrid/CELT/PLC — без отличий; scratch не вырос. Xtensa:
4 word loads, таблица96 байт с alignment>=4, stack80 байт у обоих вариантов,
добавленная `.data/.bss`0. A/B на плате,10+10 raw-прогонов: медиана CPU
SILK59.416→23.401%, Hybrid94.477→58.484%. PCM одинаковый, дополнительной
статической RAM нет. У чистого CELT FIR не исполняется; его небольшие изменения
не являются доказательством алгоритмического ускорения. Полный вывод всё ещё
имеет пропуски, поэтому цель непрерывного радио не завершена.
[Подробности, исходные данные и ограничения](ESP8266_OPUS_FIR_WORD_BENCHMARK.md).

Воспроизведение проверок:

```powershell
node --test tests/esp8266-opus-fir-word.test.js
node tools/esp8266_opus_profile/run_regressions.cjs --fast-int64 0 --fir-word --output .build/opus-fir-regression.json
```

[Полный PCM-отчёт](../tools/esp8266_opus_profile/fir-word-results.json),
[целевой assembler/stack](../tools/esp8266_opus_profile/fir-word-xtensa-results.json).

### A2. Остальные статические таблицы

- SILK `NLSF_decode.c`: CB1_NLSF_Q8, CB1_Wght_Q9; `NLSF_unpack.c`,
  `NLSF_stabilize.c`: codebook/predictor/min-distance constants.
- SILK `decode_parameters.c`: signed8 LTP codebook и 16-bit LTP scales;
  `decode_pitch.c`: pitch tables.
- CELT `rate.h:bits2pulses/pulses2bits`: byte cache,16-bit index.
- CELT `quant_bands.c`: probability/mean-energy tables.
- CELT `celt.c`: comb_filter gains/window и init_caps byte caps.
- CELT `celt_decoder.c`, `bands.c`, `rate.c`: eBands/allocation constants.

Они не вызывают ICDF helper, поэтому прежняя ICDF-оптимизация их не ускоряет.
Проверять по одной семье массивов: полное читаемое слово, signedness,
выравнивание, последний элемент. Не превращать все DRAM16/packet-byte
обращения в word loads. Новая RAM-таблица не нужна; эффект измерять.

Первый эксперимент A2 был static pulse-cache: `rate.h` bits2pulses/pulses2bits,
проверка split в quant_partition и caps в init_caps. В ревизиях9e40898/f20ed03 флаг
`-OpusPulseFlashWord` / `YORADIO_OPUS_PULSE_FLASH_WORD`, default OFF.
Работает только bounded fixed-point без CUSTOM_MODES; динамические таблицы
остаются на обычном доступе. cache_index50 дополнен 2 байтами flash padding,
все 3 таблицы явно aligned4. 202233 unit-сравнения / 1991405 word reads под
ASan/UBSan и 22 полного PCM-сценария проходят exact. Статическая RAM и
GCC stack frames modes/bands/celt не выросли. Два board A/B выполнены,
по10 завершённых OFF/ON: обычный helper замедлил CELT64 на10.57%, pure ROM
helper — на6.61%. Pure OFF также имел одну failed allocation attempt,
она сохранена отдельно; медленные завершённые попытки не исключались.
Оба варианта отклонены, экспериментальный код/флаг удалены из рабочего
дерева, доступны в9e40898/f20ed03. Дальнейшие семейства таблиц пока не
проверены. [Измерения и ограничения](ESP8266_OPUS_PULSE_WORD_BENCHMARK.md).

### A3. Точные деления и предварительные коэффициенты

`celt/entcode.h:celt_udiv` сейчас использует `/`. Small-div table upstream
включается для ARM_ASM, не для LX106. В target `ec_decode`2 call-sites
`__udivsi3`, `ec_decode_bin`1, `ec_dec_uint`4; `quant_all_bands`11,
`clt_compute_allocation`3. Это static sites, **не вызовы на кадр**.

1. Сначала знаменатели B/stride/M, для которых доказано 1,2,4,8: передавать
   log2/специализировать ветвь и использовать shift. Проверка степени 2 в
   каждом вызове сама имеет стоимость; сохранять fallback других значений.
2. Для 1<=d<=256 сравнить upstream reciprocal table129×uint32=516 байт flash
   с коррекцией остатка, RAM0. На LX106 нет MULUH, поэтому наивное 64-bit
   произведение может превратиться в `__muldi3` и ухудшить результат.
   Сначала GCC/микробенчмарк exact high-product через 32-bit частичные произведения.
3. `_this->val/_this->ext` требует точной частной части. Приближённая
   арифметика без строгой коррекции ломает range state и оставшийся пакет.

Маленький отдельный кандидат:64-bit деление bitrate в `native_opus.c`.
При packet<=1536 и rate48000 числитель<=589824000, помещается в uint32.
Можно точно уменьшить разрядность, проверив все допустимые длительности.
Это один расчёт на пакет, не основной CPU.64-bit granule/позиции сохранить.

### A4. CELT: compile-time decoder-only путь

`bands.c:quant_all_bands/quant_band/quant_partition`, `rate.c` имеют общий
encode/decode код. Радио передаёт encode=0, но это не гарантирует сквозную
специализацию без LTO. В ELF остаётся `alg_quant`1788 байт (encode-path),
а `quant_all_bands` занимает 9420 байт.

Проверить внутренний decoder-only вариант/compile-time encode для нашей
component, сохранив upstream fallback. Возможны меньше ветвей, register
pressure и flash working set; RAM прежняя. Наличие linked encode-кода не
доказывает, что он исполняется во время decode. Защиты/API не удалять наугад.

Повторная проверка исходников: единственный production caller
`celt_decoder.c` вызывает quant_all_bands с первым аргументом0; публичного
opus_encoder.c в vendored subset нет. Однако пять внутренних функций
считывают ctx->encode как переменную. Для эксперимента можно сделать её
compile-time0 только в bounded decoder-сборке; сохранить обычную ветку
для unbounded reference и явно отклонять невозможный encode-вызов, а не
незаметно выполнять вместо него decode. Не удалять обработку stereo,
intensity, transient, PLC и memory guards вместе с encoder-ветвями.

### A5. SILK: специализация LPC и инварианты подкадра

`silk/decode_core.c` проверяет LPC_order==16 в sample loop. Выбрать LPC10
или LPC16 цикл один раз на подкадр; сохранить развёрнутые MAC и rounding.
Сначала проверить, не сделал ли GCC loop unswitching сам. Если target/time
не улучшились — не усложнять C.

В LTP gain-rescaling остался volatile32 read с MEMW. Можно проверить тот же
private-word helper, сохраняя single-owner семантику и 32-bit width IRAM.
Это редкая gain-change ветвь, ожидаемую пользу не завышать.

`inv_gain_Q31` пересчитывается на подкадр. При равном gain можно проверить
локальное переиспользование reciprocal. На k=0 переменная меняется через
LTP_scale: повторно использовать только исходное значение. Не добавлять
persistent RAM ради этой микрооптимизации.

### A6. CELT: постфильтр, вращения, deemphasis, FFT

- `vq.c:exp_rotation1`: unroll2/4 при строгом прежнем порядке. Проходы
  обновляют пересекающиеся элементы X, независимо векторизовать нельзя.
- `celt.c:comb_filter_const_c`: generic путь по одному отсчёту. Проверить
  exact unroll2/4 с x0..x4. ARM-вариант развёрнут, но использует другой
  Q16/shift путь; слепое ARM_ASM влияет и на другие модули и rounding.
- Переходный comb_filter: предвычислить во flash точные squared window
  values, около 240 байт flash/RAM0. Помогает только overlap при смене параметров.
- `deemphasis`: mono48k specialization без j*C и N/downsample, отдельный
  accum для Hybrid. Ветка accum **уже** вне sample loop, не заявлять обратного.
- FFT/MDCT: сравнить spills, MUL16/MULL scheduling, пары вращений и -O2/-O3
  для конкретного файла. Word-access таблиц уже исправлен.

Результат должен совпасть побитно. Saturation/rounding особенно нельзя
произвольно переносить через операции с обратной связью.

### A7. Меньший приоритет

- NLSF stabilization: суммы min-distance двух кодбуков предвычислить во
  flash, сохраняя 20-iteration/fallback; полезно только при частых итерациях.
- Ogg CRC:256×uint32 вместо 16-entry nibble, +960 байт flash/RAM0, однаlookup
  вместо двух на байт. CRC не отключать; raw-codec benchmark это не ускорит.
- Header/CTL: убрать повторные расчёты только при доказанной неизменности
  native48k/mono конфигурации. TOC/channels/mode/LM могут меняться в потоке.
- Private word copy/clear: unroll2/4 без MEMW при single-owner условиях;
  overlap-safe copy не заменять memcpy, DMA/SDK барьеры не трогать.
- Фьюзинг downmix с denormalization в celt_synthesis: убрать отдельный
  N-sample проход, сохранив `HALF32(a)+HALF32(b)`, а не `(a+b)>>1`, прежнее
  насыщение и lifetime spectral/history.

### A8. Длинные Opus-пакеты без полного большого PCM-буфера

Физический тест2026-09-10: Deutschlandfunk24 по HTTP проходит redirect и
распознаётся как Opus24, но native adapter возвращает `Opus packet exceeds
20 ms`. PCM не выдавался. Это ограничение нашей памяти/адаптера, не ошибка
радиостанции и не доказательство медленного декодера. Лимит20мс не повышать
просто увеличением PCM-массива: RAM уже ограничена.

Проверить TOC/packet layout записанного фрагмента: несколько отдельных coded
frames или один SILK40/60мс frame. Repacketizer может разделять лишь первые;
один SILK40/60мс frame нельзя произвольно разрезать по байтам. Для него изучить
callback после внутренних подкадров, сохранив entropy/predictor/resampler,
gain, PLC/FEC и Ogg pre-skip/granule. Сравнить полный PCM с upstream, без
нового persistent/scratch расхода, затем замерить полный I2S pipeline.
Этот пункт расширяет набор реальных low-bitrate потоков, но сам по себе
не ускоряет вычисления. Ускоренный FIR может сделать их более перспективными.

## Что пока не применять

- SILK side channel: mono API всё ещё должен потреблять entropy symbols.
  Отдельная более рискованная гипотеза — пропустить только side synthesis,
  сохранив entropy state и неизменный mono API. Нужны FEC/PLC/переходы и
  доказательство состояния, а не просто отбрасывание difference bits.
- Снижение 48 кГц/точности, отключение anti-collapse/postfilter/PLC — отдельные
  режимы качества, не exact-ускорение. HTTP не исключает переходный PLC.
- Удаление полного PCM/history как у MP3: CELT использует полный спектр,
  overlap и переходы; безопасные перекрытия уже частично реализованы.
- Большая функция в IRAM: live наблюдения оставляли 36 байт свободной IRAM;
  сначала доказать запас после dynamic allocations, не только по link map.
- QIO80: `d2bc15c` документирует сбои этой платы сразу после ROM; default и
  bootloader ради этого аудита не менять.
- Повышение приоритета/убирание yield не ускоряет инструкции и может
  ухудшить Wi-Fi/WebUI; предыдущий yield A/B отрицательный.

## Чек-лист выполнения

- [x] Разобран путь Ogg/adapter/Opus/SILK/Hybrid/CELT/PCM/output, включаяPLC.
- [x] Проверены fixed-point, возможности LX106, текущий target assembler.
- [x] Сохранены raw CPU и flash-to-DMA A/B с ошибками, не только успехи.
- [ ] P0: профиль SILK indices/pulses/parameters/core/resample и CELT
  energy/allocation/bands/synthesis/postfilter/deemphasis. Один выбранный
  этап на сборку или малый bounded набор counters; измерить timer overhead.
- [x] P1: A1 FIR word-pairs, target alignment/asm, regression и10+10 board A/B.
  Сохранён отдельный флаг; raw SILK/Hybrid ускорены. Continuity — отдельный gate.
- [ ] P2: A2 pulse-cache/energy/LTP/NLSF, по одной группе на коммит.
  Pulse-cache проверен в двух вариантах и отклонён: регрессия CELT64;
  energy/LTP/NLSF остаются гипотезами. Не повторять отклонённый вариант.
- [ ] P3: A3 exact divisions: power-of-two / reciprocal / bitrate отдельно.
- [ ] P4: A4 decoder-only CELT specialization, code-size/cache A/B.
- [ ] P5: A5 SILK specialization, A6 exact loop scheduling/unroll.
- [ ] P6: A7 только при заметном времени соответствующего этапа.
- [ ] P7: A8 bounded block-output для длинных пакетов, начиная с анализа
  реального DLF24; не повышать20мс лимит без доказанного RAM/PCM-контракта.
- [ ] Реальный HTTP Opus ≥20 с без пропусков, затем длительный прогон с
  WebUI, stop/play, сменой кодеков и OOM/reconnect recovery.

На каждое изменение: reference/macro-off и candidate на одинаковых данных
SILK/Hybrid/CELT, mono/stereo, transient/steady,2.5/5/10/20 мс, FEC/PLC/DTX,
переходы, malformed/OOM/cancel. PCM побитно одинаковый; при различии изучить
max error/SNR, но не принимать изменение как exact. ASan/UBSan, scratch,
malloc/free, target width, stack и linker sections обязательны.

На плате: raw-only → flash+PDM → сеть. Для решения об ускорении минимум 10
окон на A/B с прогревом, одинаковые данные/частоты/output, median/p95/max,
taskCPU отдельно отwall. Не скрывать timeout/OOM. Без улучшения revert
candidate, сохранить заключение. Успешный пункт — отдельный логичный коммит.

## Статический аудит воспроизводим

```powershell
node tools/esp8266_opus_profile/audit_target.cjs --build .build/esp8266-opus-flash-output512 --output .build/opus-target-audit.json
node --test tests/esp8266-opus-target-audit.test.js
```

[Сохранённый отчёт](../tools/esp8266_opus_profile/target-audit-results.json)
содержит static sites21 translation units и linked ELF symbols. Это не
CPU-профиль, не число исполнений и не доказательство ошибки всех narrow
loads. Есть также скомпилированные encoder/PLC ветви: проверять достижимость.
