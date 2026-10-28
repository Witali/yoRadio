# Ссылки во всём анализируемом заводском образе

Checkpoint 2026-10-24 расширяет поиск за пределы прежнего экспорта 176 функций.
Использована существующая база Ghidra 12.0.4 в режиме `-readOnly -noanalysis`.
Java-экспортёр сохраняет адреса, типы ссылок, границы/имена функций, bytes отдельных
инструкций и хеши блоков. Содержимое строк, пользовательские настройки и полный
дамп flash не экспортируются. Исходный проект и исполняемые bytes не изменяются.

Ghidra содержит 5140 известных функций и 286384 инструкции. GNU objdump дал
287952 записи из трёх исполняемых секций: IROM 731572 B, IRAM text 72928 B,
vectors 9436 B. Все разобранные GNU bytes и 17215 ссылок с кодом сверены с
неизменённым ELF `8c9fd166…`. Записи objdump могут включать данные внутри
исполняемой секции; это не доказательство достижимости каждой инструкции.
Отдельно 475 literal function pointers в payload data и три metadata references
сверены с четырьмя байтами по каждому адресу. Синтетическая ссылка Entry Point
согласована с ELF entry. Так проверяются источники всех найденных function refs;
семантика вычисляемых переходов остаётся отдельной задачей.

Учтены 1162 кандидата указателей на функции (`DATA`/`PARAM`), в том числе 772
цели вне прежнего экспорта. Среди найденных указателей в выбранном диапазоне
`0x4200826a..0x42011040` новых целей вне экспорта нет. Диапазон является окном
просмотра, а не доказанной границей всего пользовательского приложения.
Есть 3327 `COMPUTED_CALL` edges: число относится к найденным связям, не к
доказанно полному набору косвенных вызовов.

## Проверенные адреса

| Объект | Найденные обращения | Что установлено |
|---|---|---|
| NETWORK, `0x3fcc39f0` | WRITE `0x42008356` | В базе найдена запись таймера; прямого чтения не найдено |
| SLOW, `0x3fcc39f4` | WRITE `0x42008382` | Аналогичная запись таймера; прямого чтения не найдено |
| Сохранённый `browser_time`, `0x3fcb7d14` | 2 READ / 3 WRITE | Defaults, GET settings и POST settings |
| Рабочий `browser_time`, `0x3fcb41f0` | 1 READ / 3 WRITE через `gp` | GET `0x4200ee02`, POST `0x4200ef62`; обычный список ссылок Ghidra пуст |
| `clickCount`, `0x3fcc3a90` | WRITE `0x4200ec0c` | POST advancedset; прямого чтения не найдено |
| JPEG flash-output, `0x3fcc3a6c` | READ `0x4200c432`, WRITE `0x4200c54c` | Callback проверяет режим, `draw_jpeg` записывает ноль перед decode |

Рабочий `browser_time`: записи `0x4200ee60`, `0x4200eef8`, `0x4200efd2`, чтение
`0x4200ee6c`. Они восстановлены из настоящих startup bytes:
`AUIPC`/`ADDI` в `0x4038046c/0x40380470` устанавливают `gp = 0x3fcb49c0`;
смещение `-2000` даёт `0x3fcb41f0`. Стандартные integer load/store через x3
проверены отдельным RV32 decoder и GNU objdump. Основание для формата команд и
роли регистра: [RISC-V ISA](https://riscv.github.io/riscv-isa-manual/snapshot/spec/index.html),
[RISC-V psABI](https://riscv-non-isa.github.io/riscv-elf-psabi-doc/).

У timer callback `0x4200826a` найден указатель на стеке в `0x42008468`.
JPEG callback `0x4200c374` передаётся в `0x4200c50c`. Для `app_main` найден
вызов `0x420b1e70` из функции `0x420b1e4e`, за пределами прежнего экспорта.
У `draw_jpeg` найдено десять прямых вызовов из weather/GIF/photo paths.

Отсутствие прямого чтения **не объявляет объект мёртвым**: произвольные
вычисляемые aliases, bulk settings I/O и неизвестные косвенные пути остаются
отдельной работой. По этим данным не добавлялся новый функционал и не удалялись
поля восстановленной прошивки.

## Найденные пробелы анализа

В GNU-потоке 396 стандартных GP-based integer memory instructions, в Ghidra —
393. Три отсутствующих в базе участка сохранены явно:

| PC | Обращение | GNU bytes, little endian |
|---|---|---|
| `0x42058280` | READ32 `0x3fcb4858` | `83a781e9` |
| `0x420662da` | READ32 `0x3fcb4858` | `83a781e9` |
| `0x420757d2` | READ8 `0x3fcb4b0c` | `83c7c114` |

`gp_coverage_agrees=false` и `whole_image_completeness_proved=false` остаются в
отчёте. Эти места требуют восстановления границ/вызывающих функций и проверки
достижимости. Ещё открыты computed aliases, непрямые calls, callback/task/timer
registrations вне найденных связей и сопоставление соответствующих SDK boundaries.
Текущее дополнение покрывает x3-based 32-bit integer load/store; это не общий
символьный анализ всех способов вычисления адреса.

## Воспроизведение

[`full-image-xrefs-validation-20261024.json`](../../qemu/parity/full-image-xrefs-validation-20261024.json)
содержит 7 payloads, 361910 gzip bytes: полный адресный экспорт базы, проверенный
отчёт, исходники, symbol map и typed session metadata. Не добавлены полный dump,
ELF, DROM data, журналы UART, RAM ВМ или полный GNU-текст.

GNU-текст воспроизводится локально из исходного ELF; канонический instruction
map SHA `67f4f41f9e2e5f398e7dcee65f4ca854d810e6ad4ed3efe010c5dff05fb7b81f`
связывает адреса и bytes независимо от заголовков/путей в текстовом выводе:

```python
import subprocess
from pathlib import Path
command = [r'C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe',
           '-d', '-j', '.flash.text', '-j', '.iram.text', '-j', '.iram.vectors',
           '-M', 'no-aliases,numeric',
           r'C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf']
Path('.build/factory-all-executable-20261024.asm').write_bytes(subprocess.check_output(command))
```

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/factory_xrefs_test.py `
  --elf C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --assembly .build/factory-all-executable-20261024.asm `
  --proof Small_TV/qemu/parity/full-image-xrefs-validation-20261024.json `
  --source-revision 36adbd6f7
```

Replay проверяет snapshot исходников и ELF, пересчитывает отчёт, отвергает девять
реальных mutations: неверные program/block/code bytes, удалённый GP access,
подменённый literal pointer, пропавшую timer-store reference, неизвестный memory
block и изменённый ELF.
Для старого checkpoint нужны соответствующие исходники или их сохранённые
snapshots. Первые два неуспешных прототипа экспортёра исключены из приёмки:
исправлены `ram:` в числовых адресах и сохранение пространства `EXTERNAL`.
Ghidra может вернуть code 0 при ошибке Java script; успех определяется также
наличием валидного экспорта и независимой проверкой его bytes.

Production app, SDK и QEMU в этом checkpoint не изменены. Длительный H10
наблюдается отдельно; этот статический аудит не подключается к его QMP/RSP.

Следующий checkpoint идентифицировал все три GNU-only sites как функции
официальной Wi-Fi library и восстановил их в отдельной transient-копии анализа.
Там все396GP accesses согласованы, bytes исходной прошивки и обоих проектов
неизменны. Это дополнение не переписывает первоначальный результат и не
доказывает полноту всего образа. См. [SDK_GAP_RECOVERY.md](SDK_GAP_RECOVERY.md).
