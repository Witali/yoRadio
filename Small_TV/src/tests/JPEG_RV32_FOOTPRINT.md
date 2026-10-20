# Размер libjpeg-turbo на RV32 ESP32-C2

Это дополнение к [host-квалификации JPEG](jpeg_library_probe/README.md),
не сборка готовой Small TV. Измеряется точный libjpeg-turbo 3.2.0/c85e6b90 с
ранее проверенным bounded patch. Production B50D и его frozen tests не изменены.

`rv32_footprint.py` экспортирует pinned Git commit в новую папку, проверяет
archive/patch SHA, собирает static library и выполняет relocatable link с
удалением неиспользуемых секций. `footprint.c` удерживает header/start/finish,
обычный error manager и API чтения scanlines 8/12/16-bit. Отдельно проверяются
символы arithmetic, progressive Huffman и lossless Huffman декодеров.
`jpeg_CreateCompress` в результате отсутствует; размер всей `.a` с encoder
не выдаётся за размер decoder в приложении.

## Результат 2026-10-19

| Что измерено | Bytes |
|---|---:|
| Executable sections | 144626 |
| Allocated read-only sections | 9680 |
| Всего код и константы | 154306 |
| Initialized writable sections | 0 |
| Zero-initialized sections | 0 |

Итог — примерно 150.7 КиБ кода/констант. Отсутствие `.data/.bss` **не означает**
отсутствие RAM: рабочие таблицы и буферы создаются динамически. Размеры parser
независимо сверяет с `riscv32-esp-elf-size`; ELF32 little-endian/RISC-V/soft-float
проверяются отдельно. `readelf -A` подтверждает RV32IMC, 16-byte stack alignment,
Zicsr/Zifencei; hardware float или atomics не требуются.

Компилятор — Espressif GCC 15.2.0_20251204, ISA
`rv32imc_zicsr_zifencei`, ABI `ilp32`, tune `esp-base`, оптимизация `-Os`,
function/data sections. Используются заголовки picolibc того же toolchain;
ISA/tune соответствуют cflags существующей ESP32-C2 Small TV. SIMD выключен.
Сохранены SHA компилятора, specs, upstream archive, patch, входов и результата.

Это **не flash delta production firmware**: финальный link, linker relaxation,
libc/libgcc, flash adapter, преобразование RGB565 и остальное приложение сюда
не включены. Вместо подстановки фиктивных stubs сохраняются все unresolved
symbols, включая allocator/stdio и software float helpers. Объект `ET_REL`
нельзя прошить или запустить как самостоятельную программу. Runtime-проверок
на устройстве или в QEMU этот стенд не выполняет.

## Стек и следующий шаг адаптации

GCC `-fstack-usage` сохраняет размеры отдельных кадров. При сопоставлении
учитываются **object и function** в недискардированной части linker map:
одноимённые static functions в разных модулях/разрядностях не смешиваются.

- `fill_inverse_cmap` в `jquant2-12.c.obj`: 24928 bytes. Это palette quantization,
  а не обычный вывод RGB/gray/CMYK. Наш будущий RGB565 adapter не требует palette
  output. До его интеграции нужно явно зафиксировать эту output policy и
  рассмотреть отключение соответствующих output features, сохранив все JPEG
  input formats; такой профиль ещё не включён и не проверен в production.
- `jpeg_make_d_derived_tbl`: 1376 bytes.
- `jpeg12_idct_16x16` / `jpeg_idct_16x16`: по 656 bytes.

Эти числа не складываются в доказанный worst-case stack: нужны call graph,
запас SDK/task/interrupt и runtime high-water измерения. Наличие большого
quantizer кадра в linked code не доказывает его вызов обычным RGB output.

12-bit lossy host measurement по-прежнему требует 176345/347927 bytes pools.
По исходникам 45056 bytes приходятся на range-limit table, 65536 — на четыре
YCC→RGB lookup tables (без учёта pool overhead). Следующий вариант адаптации —
сравнить вычисление или размещение неизменяемых таблиц во flash с точным
upstream результатом. Текущие RV32 размеры позволяют оценить эту цену, но
окончательное решение принимается по полному firmware link и RAM/stack tests.
Также остаются NOR-aware backing storage, I/O faults/reuse, factory pixel
compatibility и production HTTP/LCD/full/soak gates.

## Воспроизведение

Запускать из корня рабочей копии, Python 3.12+. Нужны pinned checkout, CMake,
Ninja и каталог `bin` установленного Espressif RV32 toolchain. Папка output
должна быть новой. Общий SDK и production build directory не используются.

```text
python Small_TV/src/tests/jpeg_library_probe/rv32_footprint.py --source PATH_TO_LIBJPEG_3_2_0 --toolchain-bin PATH_TO_RISCV32_ESP_ELF_BIN --output .build/jpeg-rv32
```

При необходимости указать абсолютные `--cmake` и `--ninja`. Исходный checkout
не изменяется. Архив доказательств:
`Small_TV/qemu/parity/jpeg-library-rv32-footprint-20261019.json` с raw report,
link map, retained object, section/architecture outputs и всеми `.su` файлами.
Исходные лицензии/атрибуция остаются в `jpeg_library_probe/licenses` и README.
