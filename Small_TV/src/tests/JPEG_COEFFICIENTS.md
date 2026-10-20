# Сокращение записи временных коэффициентов JPEG

Checkpoint2026-10-20 по просьбе пользователя уменьшить объём flash-записей.
Это actual libjpeg/NOR **host integration**, не включение нового decoder в UI:
main app3E03/TJpgd и transport probe6cb29771… не менялись.

## Представление и инициализация

`codec/jpeg_coefficients.c/.h` — отдельный portable converter без heap/globals.
Он не меняет JPEG, качество, число коэффициентов или вместимость scratch.
Каждое native signed16 значение обратимо преобразуется в LE16 temporary storage.
DC сохраняет two's-complement bits: DC refinement делает OR очередного bit,
а отрицательное coarse значение округлено вниз. AC использует sign/magnitude:
AC refinement увеличивает magnitude установкой bit. Negative-zero code сохраняет
INT16_MIN, так что отображение остаётся bijection для всех65536 значений.
Оба вида инвертированы: нулевой коэффициент хранится как FF FF. Correct successive
refinements программируют1→0. Применять magnitude к DC нельзя: negative DC/AC
уточняются по разным правилам.

NOR bridge выбирает converter только для direct progressive decode без palette
quantization, buffered-image и raw-data. Pinned jdmaster/jdcoefct создают здесь
только JBLOCK arrays; signed16 ABI/whole128-byte blocks проверены. Другие пути
сохраняют raw backing, включая lossless/sample/quantizer arrays. Host-only switch
`SMALL_TV_COEFF_PACKING=0/1` сравнивает raw/packed одним и тем же executable.
Это не API или настройка рабочей firmware.

Конвертируется максимум256bytes, кэш NOR остаётся4KiB. Ещё15bytes bitmap отмечают
113temporary sectors текущего layout. Перед первой packed-записью сектора его
ещё не инициализированные данные выставляются в FF через тот же RAM cache.
Устаревший мусор не восстанавливается при erase, чтобы не стирать его снова
при записи следующей строки. Сектор готовится один раз за job: соседний файл
уже может владеть частью этого сектора. Новый job сбрасывает bitmap, сохраняя
реальные physical bytes. Last-sector padding сохраняется. Preparation проверяет
cooperative checkpoint и I/O errors; partial fault transfers действительно
записывают/читают свой prefix. Это temporary-store initialization, не wear-leveling.

## Измерения одного decode

Одинаковые non-flat240×240 fixture bytes, executable/library, cap65536 для library
pools, один sector cache и начальная non-FF physical model. Каждый raw/packed
процесс декодирует дважды на одном JPEG object с сохранением physical temp data.

| Режим | Program bytes raw→packed | Erase calls raw→packed |
|---|---:|---:|
| progressive4208-bit | 1255680→843776 | 299→43 |
| progressive44412-bit | 2189824→1068544 | 533→85 |
| progressive CMYK8-bit | 3478784→2488832 | 848→113 |
| progressive CMYK12-bit | 3780608→2582784 | 923→113 |
| progressive YCCK12-bit | 2256896→1452288 | 551→71 |

CMYK12 program сокращён на31.68%, erase на87.76%. Read16850432→13532672,
calls61729→49114; scratch460800/library pool peak42275 прежние. Дополнительно
учитывать256byte conversion stack buffer и15byte bitmap. Это не whole-app RAM,
target stack/timing/endurance. JPEG size и готовый RGB565 frame115200 не меняются.
Durable cache нужен, чтобы не выполнять такой decode при каждом показе.

Flat tradeoff не скрыт: CMYK program460800→2048, но erase0→113. Raw zero может
программироваться поверх старых bytes без erase; FF требует initial clearing.
Flat YCCK program352768→115200, erase43→71. Нет обещания уменьшить стирания любого
изображения. Поведение на уже erased flash отличается; target оценка cache policy
остаётся обязательной.

## Проверки и область результата

-19726488native assertions:65536values во всех64positions(4194304pairs),
  unaligned/in-place, known vectors, invalid requests без записи,983040independent
  DC/AC refinement steps без stored0→1.
-7compiled converter mutants runtime-rejected, включая обратимые erase-heavy
  варианты;4compiled integration mutants отвергнуты по pixels/repeated erase.
  Compile/loader errors и crashes не принимаются за caught mutations.
-18traffic cases(14rich/4flat), два cycles каждого raw/packed, exact upstream
  pixels, одинаковые capacity и actual library pool peak.
-25resource/924lossless/16invalid/4optional/18budget;38912table entries,
  48rich12-bit/12truncated и18independent Pillow images pass.
-1227logical recoveries,36damaged recoveries/12format transitions;1573partial
  physical errors(all1345small callbacks,4full-size по57selected). Same-object
  recovery сохраняет physical partial data, exact pixels, closed stores/pool0.
  Arbitrary silent read corruption и exhaustive full-size sweep не заявляются.
-RV32IMC/ILP32 `-Os`: converter234code bytes, writable/readonly static0,
  individual frame0. Relocatable object, не target execution/full link.
-6artifact/10correspondence controls; SDK/frozen47files/oldH10 readonly checks.

Proof: [jpeg-coefficients-validation-20261020.json](../../qemu/parity/jpeg-coefficients-validation-20261020.json).
Промежуточный pack-only вариант сохранён отдельно от final first-use preparation;
его результаты не подменяют финальный input closure.

```powershell
pwsh -NoProfile -File Small_TV/src/tests/jpeg_coefficients/run.ps1 -OutputDirectory NEW_NATIVE
pwsh -NoProfile -File Small_TV/src/tests/jpeg_scratch/build-host.ps1 -OutputDirectory NEW_REFERENCE
pwsh -NoProfile -File Small_TV/src/tests/jpeg_scratch/build-host.ps1 -Nor -Fixtures PREPARED_SCRATCH -OutputDirectory NEW_NOR
python -B Small_TV/src/tests/jpeg_coefficients/traffic_contract.py --reference-build NEW_REFERENCE --candidate-build NEW_NOR --output NEW_TRAFFIC
python -B Small_TV/src/tests/jpeg_coefficients/mutation_contract.py --output NEW_MUTANTS
python -B Small_TV/src/tests/jpeg_coefficients/integration_mutations.py --build NEW_NOR --traffic NEW_TRAFFIC --output NEW_INTEGRATION_MUTANTS
```

Повторить qualify/flash_tables/independent/fault/physical gates из
[JPEG_SHARED_SCRATCH](JPEG_SHARED_SCRATCH.md) для этих exact builds. Independent
использует Python с Pillow, не меняя SDK. Error/resource preflight, expanded
sampling/capacity, actual source/journal/cache/native integration и target
memory/time/HTTP/LCD/full/24h/hardware остаются в IMPROVEMENT_PLAN.
