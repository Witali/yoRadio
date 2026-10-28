# Корректное декодирование заводского RV32/RVC

Checkpoint 2026-10-26 продолжает аудит всего заводского образа. Исправлены
инструменты анализа; исполняемый код Small TV, SDK, QEMU и исходный ELF не менялись.

## Подтверждённая ошибка интерпретации

Подготовленный `factory-analysis.elf` имеет ELF32/RVC заголовок, но не содержит
`.riscv.attributes`. Установленный GNU objdump, включая оба Espressif dispatcher
backend, интерпретирует bytes `71 2b` по адресу `0x420aeb6e` как RV64 `c.addiw`.
Параметр `-m riscv:rv32` не исправил этот результат ни для ELF, ни для raw binary.
Реальное выполнение этих bytes в отдельном RV32 CPU делает `C.JAL`:
PC становится `0x420af10a`, RA — `0x420aeb70`, s6 остаётся 17.

Новый `tools/reverse/rv32_disassembly.py` создаёт временное ELF-представление
только исполняемых секций с явной ISA RV32. Bytes и guest addresses копируются
без изменений. Метаданные используют `Tag_RISCV_arch` по
[RISC-V ELF psABI, раздел 10.11](https://riscv-non-isa.github.io/riscv-elf-psabi-doc/).
Это вспомогательное представление для анализа, без load segments и образа данных.
Перед экспортом реальный GNU должен правильно разобрать независимый C.JAL canary;
неверная ISA прекращает экспорт. SHA инструмента и его dispatcher backend
проверяются до и после работы. Временный каталог удаляется после проверки пути.

`assist_c_port.py` восстанавливает этот вид вызова непосредственно из 16-bit
encoding даже в старых exports с `c.addiw`, `.insn` или неверной целью перехода.
Расхождение сохраняется как `rv32_decode_corrected`; другие RV64 инструкции
отвергаются с требованием повторного экспорта. Подсказки stack frame теперь
понимают canonical compressed инструкции и числовые имена регистров.

## Результат полного экспорта

| Проверка | Результат |
|---|---|
| Исходный ELF SHA-256 | `8c9fd166a6536bc1bc236fc98018eb0daba9aad01ce8356511ad68eba03de882` |
| Секции | vectors 9 436 B, IRAM text 72 928 B, flash text 731 572 B |
| Непрерывно экспортировано | 813 936 B, 288 036 записей |
| Прежние записи и границы | Все 287 952 сохранены побайтно |
| Добавлено благодаря `-z` | 84 нулевых halfwords, 168 B |
| Кандидаты C.JAL | 453; раньше 443 `c.addiw` и 10 `.insn` |
| Ссылки в сохранённой Ghidra базе | 448 совпали по PC, bytes и цели; 452 цели известны |
| GP-based обращения | Все прежние 396 сохранены |

Канонический map SHA адресов/длин/bytes до исправления:
`67f4f41f9e2e5f398e7dcee65f4ca854d810e6ad4ed3efe010c5dff05fb7b81f`;
после добавления нулевых halfwords:
`d2d264eb0edb57e5a2e6761bd9456bdb2eb65bd913bc1d4897f401aedee5a4b7`.
Сравнение использует воспроизводимый snapshot из 5 143 функций после SDK gap
recovery. Более поздний snapshot из 5 161 функции в этот отчёт не подставлялся.

Открытые кандидаты без соответствующей ссылки в выбранном snapshot:

| PC | Цель | Цель известна в snapshot |
|---|---|---|
| `0x40380180` | `0x40380584` | Да |
| `0x4038018e` | `0x40380566` | Да |
| `0x420a3a12` | `0x420a3d32` | Да |
| `0x420a3a14` | `0x420a3da2` | Да |
| `0x420a3e32` | `0x420a3fd4` | Нет |

Это пять расхождений с картой анализа, а не пять доказанных дефектов прошивки.
Исполняемые секции могут содержать inline data и непройденные блоки; все 453
кандидата нельзя объявлять достижимыми только по корректному декодированию.
Далее проверить границы, реальные callers и соответствующие SDK тела.
Полнота семантического сравнения и аппаратная приёмка остаются открытыми.

## Проверки и воспроизведение

29 tool tests прошли без skips: 21 для помощника переноса и 8 для ISA/export.
Каждый из 2 048 C.JAL encodings исполнен в отдельном RV32 CPU с проверкой
PC/RA/s6; каждый также разобран реальным GNU и помощником переноса. Проверены
ELF layout независимым reader, сохранность bytes, запрет неверных ranges/ISA,
очистка временных файлов и существующий IROM exporter на настоящем capture.

Сохранённый [proof](../../qemu/parity/rv32-disassembly-validation-20261026.json)
содержит 10 source pins и три новых gzip payloads общим размером 11 468 B.
Прежний Ghidra graph и его SDK delta переиспользуются по хешам. Consumer заново
строит graph, полный byte/call audit и выполняет все 29 tests. Восемь изменений
отчёта и настоящая подмена GNU target отвергаются. Старый raw-byte GP audit
сохраняет силу; старые mnemonic-based поиски вызовов нужно повторять.

Из корня этой рабочей копии, с новыми output directories:

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
$python='C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$objdump='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
& $python -B -X utf8 Small_TV/src/tools/disassemble_factory_elf.py `
  --elf C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --objdump $objdump --output .build/factory-rv32-replay

& $python -B -X utf8 Small_TV/src/tests/verify_rv32_disassembly_evidence.py `
  --proof Small_TV/qemu/parity/rv32-disassembly-validation-20261026.json `
  --factory C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --before C:/Work/yoRadio/.worktree/small-tv-improvement-plan/.build/factory-all-executable-20261024.asm `
  --after .build/factory-rv32-replay/factory-rv32.asm --objdump $objdump `
  --dump C:/Work/yoRadio/.worktree/small-tv-timer-bounds/Small_TV/full-flash.bin `
  --scratch .build/factory-rv32-replay-tests
```

Новый export детерминирован: временные host paths исключаются из текста, bytes
нулевых областей печатаются явно. Полный assembly остаётся в ignored build;
в evidence не добавляются DROM, settings, credentials или RAM ВМ.

Следующий checkpoint установил владельцев пяти выбранных call sites и нашёл
общий factory/native OOM defect: [RUNTIME_CALL_GAPS.md](RUNTIME_CALL_GAPS.md).
Nothrow allocation failure затем исправлен:
[NOTHROW_ALLOCATION.md](NOTHROW_ALLOCATION.md). Отдельный read-only checkpoint
восстановил десять runtime ranges и все пять недостающих ссылок:
[RUNTIME_METADATA.md](RUNTIME_METADATA.md). Прежние Ghidra snapshots сохранены;
полнота образа этим не закрывается.
