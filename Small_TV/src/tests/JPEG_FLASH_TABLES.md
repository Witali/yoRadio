# Неизменяемые 12-битные таблицы JPEG — 2026-10-20

Продолжение [host-квалификации](jpeg_library_probe/README.md) и
[RV32-измерения](JPEG_RV32_FOOTPRINT.md). Production firmware B50D не меняется.
Из libjpeg-turbo 3.2.0/c85e6b90 удалены повторные heap allocations неизменяемых
таблиц 12-bit lossy: range-limit22528×2bytes и четыре YCC→RGB таблицы4096×4bytes.
Их **110592bytes** находятся в read-only секциях. IDCT, color arithmetic,
rounding и lookup indices сохранены. В частности, retained range table включает
не только clamp, но и исходные masked-IDCT wraparound segments.

Два новых отдельных patch применяются после bounded patch:

- `libjpeg-turbo-3.2.0-flash-tables.patch`: точные static const tables, полученные
  `generate_flash_tables.py` из pinned arithmetic. Generator читает Git objects,
  независимо от checkout EOL, и отказывается от неожиданного layout исходника.
- `libjpeg-turbo-3.2.0-compact-pools.patch`: запас первой IMAGE pool16000→4096,
  следующих5000→1024bytes. Размеры объектов, alignment, retries и lifetimes
  не изменены. Это понадобилось для rich12-bit progressive YCCK: с исходными
  запасами его рабочие буферы не помещались в выбранный64KiB pool cap.

Cast констант к legacy mutable pointer fields не разрешает их запись:
все штатные consumers читают эти таблицы. Их заменённые initializers больше
не заполняют таблицы на месте. Новый private helper `table_dump.c` служит только
host-тесту: использует layout из pinned `jdcolor.c` для чтения **действительных**
установленных указателей. Скопированный initializer переименован и не вызывается.
Этот helper не включается в RV32 library или production firmware.

## Проверенные результаты

Независимый C initializer неизменённого upstream — oracle для каждого из38912
элементов. Оба range dumps45056bytes и color dumps65536bytes совпали побайтово.
Generator не используется для получения expected output в этом сравнении.

Также прошли:

- 48non-flat12-bit lossy images: RGB420/422/444, grayscale, CMYK, YCCK,
  sequential/progressive, quality83/100, размеры240×240 и239×237;
- 12усечённых12-bit inputs с проверкой pool/backing cleanup;
- 25прежнихresource cases,924lossless cases2–16bits/7predictors/point transforms,
  16прежнихnegative inputs,4optional API controls и18budget cases;
- все pixels18non-flat8-bit baseline/progressive fixtures совпали с отдельным
  Pillow12.3.0/libjpeg-turbo3.1.4.1 decoder.

| 240×240, quality83 | Upstream pool peak | Новый pool peak | Host backing capacity |
|---|---:|---:|---:|
| 12-bit RGB420 sequential | 176345 | 37618 | 0 |
| 12-bit RGB420 progressive | 347927 | 45736 | 172800 |
| 12-bit YCCK progressive | 472885 | 64869 | 288000 |

Все48rich cases проходят с hard library-pool cap65536bytes. Максимум64869bytes
**не равен общему RAM**: отдельно нужны session, output row (до1920bytes),
allocator metadata, backing adapter, stack и остальные задачи/SDK.

Compact pools не дают монотонного уменьшения во всех режимах. При **unlimited**
full-image decode8-bit progressive420 со smoothingTRUE измерено205325 вместо
204180bytes (+1145): меньшие chunks могут потребовать больше служебных блоков.
Пиксели совпали. Этот optional API control проверяет поведение, не64KiB cap;
прирост сохранён в raw results. Тест исправлен с `FIXED_TEST`, а проверки реального
лимита и cleanup в рабочих режимах сохранены. Два lossless quantization controls
по-прежнему отвергаются обеими библиотеками; это не positive format acceptance.

На реальном Espressif RV32 compiler сохранён decoder со всеми8/12/16 scanline,
arithmetic/progressive/lossless roots: **144394text +120272read-only =264666bytes**,
data/bss0. `nm --print-size` подтвердил все5table symbols как `r/R` суммарно
110592bytes; parser sections независимо сверены с binutils size. Это на110360bytes
больше прежнего link-only измерения154306, с уменьшением кода на232bytes.
Это не размер готового приложения: libc/libgcc/adapter/final link не включены.
Крупный palette quantizer stack frame24928bytes остаётся отдельным вопросом
выбора output policy и проверки actual call-chain/SDK stack.

## Воспроизведение и ограничения

```text
python Small_TV/src/tests/jpeg_library_probe/build.py --source PINNED_SOURCE --output .build/jpeg-reference
python Small_TV/src/tests/jpeg_library_probe/build.py --source PINNED_SOURCE --output .build/jpeg-flash --adapted --flash-tables --compact-pools
python Small_TV/src/tests/jpeg_library_probe/qualify.py --reference-build .build/jpeg-reference --candidate-build .build/jpeg-flash --output .build/jpeg-qualification
python Small_TV/src/tests/jpeg_library_probe/flash_tables_contract.py --reference-build .build/jpeg-reference --candidate-build .build/jpeg-flash --output .build/jpeg-flash-contract
python Small_TV/src/tests/jpeg_library_probe/independent.py --reference-build .build/jpeg-reference --candidate-build .build/jpeg-flash --output .build/jpeg-independent
python Small_TV/src/tests/jpeg_library_probe/rv32_footprint.py --source PINNED_SOURCE --toolchain-bin RV32_BIN --output .build/jpeg-rv32-flash --flash-tables --compact-pools
```

Каждый output — новая папка. Для MSVC нужен Developer Command Prompt, для
independent.py — Pillow. `--cmake`/`--ninja` принимают абсолютные пути.
`apply_source_patch` ограничивает Git discovery родительским каталогом export
и проверяет, что enclosing repository не обнаружен: иначе mixed unified/Git patch
мог молча пропускать новые файлы внутри sparse worktree. Наличие обоих headers
проверяется до компиляции. Ошибочные промежуточные сборки сохранены как diagnostics.

Proof: `Small_TV/qemu/parity/jpeg-library-flash-tables-20261020.json` с source,
binary, fixture hashes и raw results. Прежние b7bfb69c/855e55507 результаты
относятся к прежним исходникам и не переименовываются в новые.

Остаются полноценный production link, общий heap/stack, NOR-aware temporary
storage и его износ, production I/O fault/reuse tests, RGB565 conversion с factory pixels,
HTTP/storage, отдельный LCD gate, full regression/soak и physical acceptance.
Это не заявление полного покрытия JPEG/T.81. Дополнительные subsampling cases
411/440/410 и другие допустимые таблицы/scan arrangements нужно включать при
дальнейшем расширении device matrix. JPEG-LS/JPEG2000/JPEGXL/WebP остаются планом.

Host allocation/I/O fault/reuse gate завершён отдельно2026-10-20:
1227инъекций,36truncated recoveries,12format transitions. См.
[JPEG_FAULT_RECOVERY.md](JPEG_FAULT_RECOVERY.md). Он не проверяет будущий NOR
backend или production source/output.
