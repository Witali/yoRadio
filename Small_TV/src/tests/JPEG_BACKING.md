# JPEG decoder с настоящим NOR backing

`codec/jpeg_backing.c/.h` соединяет portable decoder API с общим
`storage/jpeg_scratch`/`jpeg_nor`. Это `REQUESTED_CHANGE`: подготовка нового JPEG,
а не найденная заводская функция. Основная UI firmware3E03 пока использует TJpgd.

## Контракт

Владелец сначала проверяет ресурсы/карту через ownership guard, начинает общий
transport job, открывает NOR только на disposable scratch extents и вызывает
`jpeg_backing_begin`. После decode/cleanup — `jpeg_backing_abort`, затем можно
открыть NOR/transport следующего job. Abort/close не пишут грязный временный cache.
Старый port нельзя переиспользовать до освобождения всех его borrowers.

Один4KiB NOR cache обслуживает до16 byte-granular files. В адаптере нет heap или
mutable globals; на RV32 handle600bytes, дополнительно caller-owned15byte bitmap
для113sectors и256byte stack conversion buffer. NOR handle4352bytes хранится
отдельно. ID монотонны и не сбрасываются при abort/reopen; capacity не меняется,
пока decoder сохраняет callback descriptor.

Progressive coefficient arrays используют прежнее reversible DC/AC encoding.
Перед первым использованием сектора его logical portion становитсяFF; соседние
initialized files и last-sector padding сохраняются. Whole-range bounds, prefix,
128byte coefficient alignment и alias/wrap checks выполняются **до** подготовки.
Raw sample arrays остаются byte-granular; смешивание raw/packed в одном job
отклоняется до I/O. Это точный контракт текущего direct decoder, без quantization,
buffered/raw output. Проверка whole-array demand остаётся в `jpeg_memory`.

При неуспехе input/output/backing callback decoder сохраняет его code и спрашивает
owner о причине остановки: deadline/quota не становятся generic I/O. Owner
transport хранит исходную причину в `last_error`, даже если последующий check
возвращает STATE для уже отозванного job. Cleanup не зависит от оставшегося budget.

## Проверки

-15273 native assertions,134 partial/silent physical fault cases. Проверены четыре
  полных coefficient arrays, межфайловые границы секторов, refinement, raw bytes,
  stale IDs, aliases и остановка до первой очистки грязного сектора.
-61 JPEG с exact independent RGB565 oracle,7resource refusals,10negative inputs,
  12format transitions,827physical errors/recoveries и48deadline/quota/cancel
  остановок. Частично изменённые физические bytes сохраняются между jobs; повторный
  decode использует тот же JPEG object. За пределами scratch все4MiB сравниваются.
-При native-like65536pool/460800backing legal4x4 CMYK8 отклоняется с требованием
  backing524288. CMYK12 раньше достигает pool request70760/65536. При увеличении
  только host pool оба показывают независимый backing limit524288/460800.
  Во всех этих refusals physical calls0; insufficient RAM не называется corrupt JPEG.
-6compiled unsafe variants отклонены runtime assertions. Первый RAM-checkpoint
  mutant выявил пропуск в тесте: добавлен отказ до first-use sector preparation.
  Compiler/loader errors/crashes не засчитываются как caught mutants.
-Existing stdio API regression:63positive/7limits/10negative/1197callback faults/
  12transitions.6artifact и10correspondence checks pass; main app не менялась.

Host same fullCMYK12 fixture:2582784program bytes,113erases,13532672read bytes,
49114physical calls. Ранее raw coefficient backend:3780608program/923erases.
Уменьшение31.68%/87.76% относится к этому изображению и starting contents, не ко
всем JPEG и не к endurance настоящего чипа. Compressed source44402bytes и backing
capacity460800 не меняются. Flat-image tradeoff описан в
[JPEG_COEFFICIENTS.md](JPEG_COEFFICIENTS.md).

## ESP32-C2 target

Полная bootable standalone сборка включает тот же pinned libjpeg archive,
decoder/backing/NOR/scratch/guard/transport и ESP-IDF esp_flash/partition/PSA APIs.
Она сохранена в `firmware/development/small-tv-jpeg-decoder-probe/`, отдельно от
основной прошивки и предыдущей storage probe. Binary506784bytes; ELF/source hashes
и matching stamped assets находятся в manifest и proof.

Input — связанные const synthetic JPEG fixtures; backing — реальные SDK flash
calls в C2 QEMU. RGB565 hash сравнивается с независимым upstream oracle без full
frame allocation. Small/full CMYK12, losslessRGB16, gray, общий quota отказ,
same-object recovery и capacity460799 refusal проверяются в двух собственных
процессах на сохранённых flash bytes. За пределами scratch изменения запрещены.
Это отдельный codec/storage gate, без network/LCD criteria.

В первом финальном процессе fullCMYK12:40592pool +4984context =45576requested allocator bytes;
minimum free8bit heap149576, minimum free main-task stack1988 из4096bytes. Сюда не
добавлены UI framebuffer/Wi-Fi/tasks реальной программы; это не whole-app fit.
Full decode занял39137736guest microseconds. Probe даёт idle task один tick через
каждые64checkpoint calls; его время не является измерением платы или чистого CPU.
Counts — issued SDK requests, не число команд chip bus. ИсходноFF scratch требует
меньше стираний, чем уже использованная память; обе ситуации сохранены в proof.

Proof: [jpeg-backing-validation-20261020.json](../../qemu/parity/jpeg-backing-validation-20261020.json).

```powershell
pwsh -NoProfile -File Small_TV/src/tests/jpeg_backing/run.ps1 -OutputDirectory NEW_UNIT
pwsh -NoProfile -File Small_TV/src/tests/jpeg_backing/build-decoder.ps1 -LibraryBuild QUALIFIED_HOST_LIB -Fixtures NEW_UNIT -OutputDirectory NEW_HOST
python -B Small_TV/src/tests/jpeg_backing/decoder_contract.py --build NEW_HOST --oracle QUALIFIED_DECODER_CONTRACT --output NEW_CONTRACT
python -B Small_TV/src/tests/jpeg_backing/mutation_contract.py --fixtures NEW_UNIT --output NEW_MUTANTS
pwsh -NoProfile -File Small_TV/src/tests/jpeg_backing/build-idf.ps1 -BuildDirectory NEW_TARGET -LibraryBuild QUALIFIED_RV32_LIB -OracleDirectory QUALIFIED_DECODER_CONTRACT
python -B Small_TV/src/tests/jpeg_backing/qemu_probe.py --qemu-root FROZEN_QEMU_BUNDLE --build NEW_TARGET --output NEW_QEMU
```

Далее — source/upload privacy + atomic journal + physical source/frame hashes,
готовый durable RGB565 cache и matching assets deployment с сохранением фото и
настроек. Валидацию JPEG и заполнение cache следует объединить в **один decode**;
отрисовка готового кадра не должна повторять multi-scan decode и flash writes.
Затем реальный UI link/shared heap/stack/time, HTTP/reset/power-loss и независимые
LCD/network/full/24h/hardware gates. Новый decoder ещё не включён в UI.
