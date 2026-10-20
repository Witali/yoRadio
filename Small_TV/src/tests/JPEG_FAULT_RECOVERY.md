# JPEG: отказ ресурсов и повторное использование декодера

Проверка от2026-10-20 относится к host-кандидату libjpeg-turbo3.2.0,
commit `c85e6b905bf237038faa936dab160ebfc5da0344`, с bounded/flash-tables/
compact-pools patches. Это продолжение [измерения таблиц](JPEG_FLASH_TABLES.md),
не интеграция библиотеки в прошивку и не проверка NOR.

## Что проверяется

`jpeg_library_probe/probe_faults.c` считает настоящие обращения и вводит сбой
на заданном порядковом номере. `probe_memory.c` проверяет allocations и temporary
backing. Отдельный `probe_reuse.c` владеет bounded input manager, строкой вывода,
ошибкой `setjmp/longjmp` и одним объектом JPEG. Mutable cleanup state хранится
в heap, чтобы сохраняться после `longjmp`.

После ошибки вызывается `jpeg_abort_decompress`; тот же объект читает исправное
изображение без перезапуска процесса. Если ошибкой завершилось само создание
объекта, разрешены только destroy и новое создание. Основание — раздел
«Aborting» в pinned upstream `doc/libjpeg.txt`: после `error_exit` безопасны
только `jpeg_abort`/`jpeg_destroy`. При смене изображения параметры output,
precision и source manager устанавливаются заново.

Инъекции охватывают:

- Разовый отказ allocation и продолжающийся отказ начиная с выбранного вызова.
  Pool manager может уменьшить запрос и восстановиться после разового отказа;
  такой исход принимается только с точными output pixels.
- Отказ открытия backing file и позиционирования перед read/write.
- Реальные короткие read/write backing file, после которых выдаётся ошибка.
- Частичное чтение JPEG с ошибкой источника и короткую запись строки результата.

Для31×17 перебираются все порядковые номера I/O, для240×240 — начало, середина
и конец с соседними номерами. Все исходные allocation/open ordinals перебираются
для каждого размера. Это не исчерпывающая проверка произвольных комбинаций сбоев.

## Результат

12fixtures: baseline/progressive/arithmetic8-bit,12-bit sequential/progressive,
grayscale/RGB/CMYK/YCCK и losslessRGB2/12/16-bit. В каждой паре recovery pixels
побайтово совпадают с отдельным decode исходной библиотеки.

| Инъекция | Проверенных сценариев |
|---|---:|
| Allocation: разовый и продолжающийся отказ |346|
| Открытие временного файла |22|
| Чтение временного файла |169|
| Запись временного файла |169|
| Позиционирование временного файла |317|
| Чтение JPEG |40|
| Выдача строки результата |164|
| Всего |1227|

Дополнительно прошли36восстановлений после усечённых JPEG и12переходов между
форматами/разрядностями на одном объекте. В63случаях разового allocation failure
библиотека восстановилась сама. В36случаях не завершилось создание объекта;
для recovery пришлось создать его заново. Остальные сценарии используют abort
и тот же объект. После abort нет открытых backing files, после final destroy
library pools равны0. Hard pool cap65536bytes не превышен. Максимум этого стенда
61421bytes, отдельный host session —4096bytes; это **не общий heap** прошивки.

На этих же новых binaries повторены прежние25resource/924lossless/16negative/
4optional/18budget cases,48rich12-bit/12truncated cases и сравнение всех38912
entries таблиц. Они проходят. Разница session/source manager означает, что
61421не заменяет прежнее измерение64869другого стенда.

## Воспроизведение и границы

```text
python Small_TV/src/tests/jpeg_library_probe/build.py --source PINNED_SOURCE --output .build/jpeg-reference
python Small_TV/src/tests/jpeg_library_probe/build.py --source PINNED_SOURCE --output .build/jpeg-candidate --adapted --flash-tables --compact-pools
python Small_TV/src/tests/jpeg_library_probe/fault_contract.py --reference-build .build/jpeg-reference --candidate-build .build/jpeg-candidate --output .build/jpeg-fault-contract
```

Для MSVC нужен Developer Command Prompt; `--cmake`/`--ninja` принимают абсолютные
пути. У каждого запуска свой новый output directory. Runner проверяет compiled
source/executable hashes. Старые output files перед каждой парой удаляются:
ошибка создания объекта не может получить hash результата предыдущего случая.

Proof: `Small_TV/qemu/parity/jpeg-library-fault-recovery-20261020.json`, raw reports,
build records, logs и synthetic fixtures. Production B50D и её замороженные
full/H10 inputs не менялись.

Нужны отдельные production allocator/source/output/NOR failures после интеграции,
общий heap/stack, RGB565 conversion, storage/privacy, HTTP/LCD и full/soak.
Host `tmpfile` допускает перезапись; эти тесты не утверждают корректность flash
erase/wear, прерывания питания или физической платы.
