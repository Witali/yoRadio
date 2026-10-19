# Квалификация библиотеки JPEG для Small TV

Кандидат — [libjpeg-turbo 3.2.0](https://github.com/libjpeg-turbo/libjpeg-turbo/releases/tag/3.2.0),
commit `c85e6b905bf237038faa936dab160ebfc5da0344`. Это отдельный host-стенд,
а не подключённый компонент прошивки. Текущий production decoder и сборка B50D
не меняются. Исходники upstream экспортируются из указанного коммита в новую
папку сборки; исходный checkout не исправляется и не компилируется на месте.

Библиотека поддерживает обычные JPEG baseline/extended sequential/progressive,
8/12-bit lossy и 2–16-bit Huffman lossless; arithmetic — для 8-bit lossy.
Согласно `doc/libjpeg.txt` этой версии, hierarchical, DNL и дробные отношения
subsampling не поддерживаются. Lossless arithmetic также не реализован.
Поэтому даже успешный перенос не означает автоматического покрытия всего T.81.
JPEG-LS/JPEG2000/JPEGXL/WebP остаются в отдельном плане WORKING_NOTES.

## Ограниченные изменения upstream

`libjpeg-turbo-3.2.0-bounded.patch` содержит две оптимизации, помеченные
`REQUESTED_CHANGE`, с сохранением исходных copyright и собственным уведомлением:

- `master_selection`: для прямого lossless output без palette quantization и
  buffered-image не создавать таблицу ограничения значений. Lossless predictor
  восстанавливает samples без IDCT; разрешённые здесь passthrough color paths
  не читают эту таблицу. Quantized и buffered клиенты сохраняют исходный путь.
- `jinit_d_coef_controller`: progressive требует пятистрочного окна для block
  smoothing. Когда non-buffered клиент явно отключил smoothing, достаточно
  одного iMCU row. Buffered клиенты сохраняют пять строк, поскольку могут
  включить smoothing в следующем output pass.

Стенд задаёт `do_block_smoothing=FALSE` одинаково для обоих сравниваемых
декодеров; отдельные controls сохраняют проверку `TRUE`. Настройка относится к
сглаживанию неполных progressive scans, не к chroma fancy upsampling или IDCT.
Вторая оптимизация не изменяет entropy decoder, коэффициенты или IDCT.

`probe_memory.c` заменяет только системный allocator/backing hooks. При заданном
лимите запрашиваются минимальные разрешённые окна, как допускает `jmemsys.h`;
каждый реальный pool allocation всё равно ограничен этим лимитом. Простая
передача всего остатка heap и даже 5% запаса оказались недостаточны: пять iMCU
строк сами не помещаются в 64 КиБ для цветных progressive. Не повышать лимит,
чтобы скрыть такие отказы. Временное хранилище — анонимный host-файл, не flash.

## Воспроизведение

Нужны Python 3.12+, Git, CMake, Ninja и C compiler. Проверенный вариант — Windows
x64 / MSVC 19.51, Release, SIMD/TurboJPEG/tools/upstream tests выключены.
Для независимой проверки нужен Pillow (проверено 12.3.0, libjpeg-turbo 3.1.4.1).
Upstream regression suite этой процедурой **не запускается**. В среде MSVC
запускать из Developer Command Prompt, чтобы были доступны compiler/linker/SDK.
`--output` каждый раз должен указывать новую папку: старые результаты сохраняются.

```text
python Small_TV/src/tests/jpeg_library_probe/build.py --source PATH_TO_PINNED_LIBJPEG --output .build/jpeg-reference
python Small_TV/src/tests/jpeg_library_probe/build.py --source PATH_TO_PINNED_LIBJPEG --output .build/jpeg-candidate --adapted
python Small_TV/src/tests/jpeg_library_probe/qualify.py --reference-build .build/jpeg-reference --candidate-build .build/jpeg-candidate --output .build/jpeg-qualification
python Small_TV/src/tests/jpeg_library_probe/independent.py --reference-build .build/jpeg-reference --candidate-build .build/jpeg-candidate --output .build/jpeg-independent
```

При необходимости передать абсолютные `--cmake`/`--ninja` в build.py. Указанный
checkout должен иметь HEAD ровно на pinned commit; `git archive` читает только
committed bytes, исключая локальные правки. `build.json` фиксирует archive, patch,
исходники стенда, исправленные upstream files, library и executable SHA256.

## Результаты 2026-10-19

Host qualification: 25 случаев 240×240, 924 lossless cases (все precision 2–16,
predictor 1–7, нулевой/средний/максимальный point transform), 16 усечённых inputs,
4 optional-mode controls и 18 проверок бюджета. Lossless matrix использует
нечётный размер 31×17 и чередует отсутствие restart и restart через две MCU rows.
Expected samples вычисляются отдельной целочисленной формулой с явным удалением
младших битов point transform. Для каждого сравниваются все выходные bytes.
Pillow независимо подтвердил все пиксели ещё 18 сложных baseline/progressive
RGB/grayscale/CMYK JPEG, включая прежние baseline/restart/odd fixtures.

| 240×240 case | Upstream pools без лимита, bytes | Adapted pools, bytes | Host backing capacity, bytes |
|---|---:|---:|---:|
| baseline RGB 8-bit | 32598 | 32598 | 0 |
| progressive 4:2:0 8-bit | 204180 | 42900 | 172800 |
| progressive 4:4:4 8-bit | 374358 | 40278 | 345600 |
| progressive grayscale 8-bit | 139491 | 28131 | 115200 |
| progressive CMYK 8-bit | 491325 | 45885 | 460800 |
| progressive YCCK 8-bit | 324338 | 55538 | 288000 |
| progressive arithmetic 8-bit | 203869 | 42589 | 172800 |
| lossless grayscale 16-bit | 750729 | 24802 | 0 |
| lossless RGB 16-bit | 755907 | 29980 | 0 |
| lossless CMYK 16-bit | 758496 | 32569 | 0 |

Adapted column использует hard pool cap 65536 bytes. **Это не общий RAM:**
session/error state, output row (до 1920 bytes), stdio, allocator metadata,
stack, Wi-Fi/SDK и остальные задачи сюда не включены. Это x64 measurement,
не оценка RV32 flash size или доказательство fit на ESP32-C2.
Baseline/progressive 12-bit lossy пока не укладываются в этот лимит: без лимита
получено 176345/347927 bytes. Это открытая работа, а не исключение из запроса.

Все library pools и backing files закрылись при success и failure. Budget sweep
включает четыре отказа после открытия одного/трёх временных файлов. Строгий
warning handler отвергает truncated input, даже если upstream мог бы его частично
восстановить. Примерные silent repairs не становятся успешным upload.

## Что требуется до переноса в production

1. Измерить RV32 code/rodata, общий peak heap, stack и время. Все нужные ordinary
   JPEG modes сохраняются в матрице; отключение 12-bit/lossless не заменяет перенос.
2. Снизить fixed-table memory 12-bit lossy с побайтовым сравнением IDCT/color.
3. Реализовать bounded temporary storage и отказ/cleanup. Host backing допускает
   произвольную перезапись, NOR требует erase перед 0→1. CMYK fixture занимает
   460800 bytes, но суммарно пишет **2764800 bytes** за decode: capacity нельзя
   путать с write traffic или износом. Нельзя просто направить fopen/fwrite во flash.
4. Вынести codec и RGB/CMYK/YCCK/bit-depth→RGB565 conversion в соответствующие
   модули; сохранить bounded reads, media mutex, privacy, clear rectangle и
   существующую pixel compatibility заводских ресурсов. Текущий стенд возвращает
   samples исходной разрядности, CMYK/YCCK — CMYK; LCD conversion не реализован.
5. Проверить allocator/I/O faults и повторное использование decoder после ошибки
   в одном процессе; текущие вызовы процесса проверяют cleanup каждой операции.
6. Добавить HTTP/storage/cold persistence, отдельный LCD gate и полный
   production regression/soak для новой конкретной сборки. B50D результаты
   не переносятся на будущую сборку с другим decoder.

## Лицензии

Сохранены неизменённые [LICENSE.md](licenses/LICENSE.md) и
[README.ijg](licenses/README.ijg) из pinned tree. Подробности происхождения и
хеши — в UPSTREAM.json. При распространении production binary/статически
связанного приложения сохранить предусмотренную IJG атрибуцию:

This software is based in part on the work of the Independent JPEG Group.
