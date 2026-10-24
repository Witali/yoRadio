# Форматы JPEG в текущей рабочей прошивке

Начато2026-10-24, app9C1A83BD/ELF76B5CE37/source7D95988C без изменения
production-кода. Лимит по умолчанию200KiB сохранён. Эта проверка относится к
HTTP→owner→decoder→physical cache, отдельно от network и LCD acceptance.

## Векторы и эталоны

Корпус70файлов читается из уже committed `jpeg-cache-pipeline-validation-
20261020.json` и его проверенного `fixtures.tar.gz`. Не требуется генерировать
новый JPEG или доверять байтам из заменяемой папки сборки. Проверяются archive
SHA, имена/размеры/полные SHA каждого файла. Исторический host успех используется
только как источник вектора и независимых ожидаемых pixels, не как target pass.

59host-positive полноразмерных240×240: baseline/progressive8/12, gray/RGB/CMYK/
YCCK/arithmetic и lossless2..16 с predictor4. Ещё5source-capacity и6negative/
sampling-resource случаев. Для extended modes эталон — unmodified upstream
samples с независимой Python RGB565 арифметикой из закреплённого host report.
Baseline8 намеренно сохраняет factory IDCT/byte clipping; его эталон заново
вычисляется буквальными RV32 инструкциями factory ELF с подачей только synthetic
SDK input. Нельзя сравнить этот путь с другим IDCT и объявить разницу ошибкой.

## Что проверяется

Настоящие `/start_upload`, multipart chunks и async `/finish_upload`; JPEG source
не исправляется тестом. Успех требует full source/frame SHA и canonical committed
journal, совпадающих с независимым эталоном, а также правильной publication через
обычный GET. После любого отказа немедленно загружается и обрабатывается известный
валидный gray progressive. Это проверяет последующее использование worker/cache.

Больший source отвергается до изменения flash. Остальные failures не могут
публиковать partial ready frame. Для валидных host-векторов допустим только
конкретный resource refusal с numeric required>available: write budget, heap,
pool или backing. Arbitrary decode/unsupported/I/O error таким результатом
не считается. Negative fixtures должны дать соответствующую invalid/truncated/
unsupported причину, а не произвольный resource error.

Аппаратные debugger breakpoints наблюдают реальный entry/return upload owner;
изменений guest PC/RAM/code нет. Сохраняются полные before/after flash и два
paused RAM snapshots на каждый finish. DWARF из точного ELF задаёт layouts;
адрес caller-owned diagnostic также сохранён, поэтому offline checker извлекает
все его поля из RAM, включая nested decoder diagnostic. Счётчик program здесь
получен из возвращённого transport ledger; независимая physical callback trace
остаётся отдельной проверкой JPEG_WRITE_BUDGET.

Worker stack high-water накопительный в одном процессе, а не peak только одного
JPEG. SDK individual heap minima дают conservative lower bound; их сумма не
является измерением одновременного aggregate minimum. Снимки entry/exit также
не являются полным allocator trace или worst-case RAM proof. Program≤204800
включает start invalidation; сохранение исходного JPEG отдельно.

## Текущее подтверждённое состояние

Pilot:6corpus vectors/9actual workflows,6successful preparations (включая3reuse
controls),2finish refusals и1source-slot admission refusal. Flat CMYK12progressive,
lossless-gray16 и rich baseline8 имеют точные physical pixels. Rich progressive12
остановлен по flash-write-limit205056/204800, source CMYK6 слишком большой,
SOF5 unsupported; после каждого корректное gray фото успешно. Worker untouched
minimum5012/8192. Heap-minima sum lower bound10548, не simultaneous whole-app peak.
Единственный pilot process остановлен/reaped. Independent saved-byte checker pass.
Proof: [jpeg-format-pilot-validation-20261024.json](../../qemu/parity/jpeg-format-pilot-validation-20261024.json),
19полных physical images через lossless sector deltas и16RAM snapshots. Команда
`verify_photo_format_matrix_evidence.py --proof ...` заново проверяет archive,
пиксели, diagnostic/heap/stack; QEMU при этом не запускается.

Полный70-vector прогон **завершён и independently verified** четырьмя
непересекающимися частями18/18/17/17.92реальных workflows:48primary images приняты,
17finish refusals,5source admission refusals,22немедленных successful recoveries.
Primary outcomes: write-limit8, heap-headroom5, backing-capacity1, unsupported1,
truncated1, invalid1 и source-slot5. Все4exec terminal0, owned VM stopped/reaped;
union70, actual source/frame/journal и RAM fields проверены offline.

Приняты baseline8с factory IDCT и baseline12, neutral CMYKprogressive8/12,
grayprogressive8 и43lossless gray/RGB/CMYK cases. Векторы lossless RGB6/CMYK6
превысили source slot: их refusal проверен, исполнение этих двух precision/color
paths требует меньших дополнительных fixtures. Тяжёлые progressive получили
точный отказ по текущей политике; это не отключение режима по имени. Список
успешных файлов не означает приёмку всех возможных JPEG streams.

Untouched worker minimum5012/8192 во всех4частях; наибольший observed decoder
pool47983bytes, context4984отдельно. Lower bound суммы individual heap minima
15468bytes; это не simultaneous aggregate minimum или whole-app requested peak.
Proof: [jpeg-format-matrix-validation-20261024.json](../../qemu/parity/jpeg-format-matrix-validation-20261024.json).
Сохранены192полных физических образа и174RAM snapshots. Lossless sector deltas
могут ссылаться на уже сохранённый полный образ: before часто совпадает с
предыдущим after. Полные SHA проверяются при восстановлении каждого4MiB image.
Schema2 запрещает forward/cyclic bases. Новые compressed payloads занимают
примерно12.3MB вместо хранения всех4MiB images/RAM без дедупликации.
Физическая плата не затрагивалась; app9C1A83BD остаётся прежней.

## Воспроизведение

```powershell
python -B Small_TV/src/tests/photo_format_matrix_qemu.py --qemu-root FROZEN_QEMU --output NEW_FORMAT_RUN
python -B Small_TV/src/tests/photo_format_matrix_contract.py --run NEW_FORMAT_RUN
```

`--names` выполняет явно выбранный pilot/subset. Несколько независимо завершённых
папок передаются одним `--run PART0 PART1 PART2 PART3`: checker требует один app/
ELF/source и отсутствие дубликатов первичных векторов. `complete_corpus=true`
получается только при точном union всех70имён. Все handles остаются у владельца,
после ошибки/успеха только его VM останавливается и reap-ится. Host time под
icount не является скоростью настоящей C2.

Остаток плана: current real I/O/allocation fault injection, actual publication/
program/erase interruptions, network lifecycle/churn, whole-image audit,
полная regression/24h/hardware. Данный matrix не подменяет эти проверки.
