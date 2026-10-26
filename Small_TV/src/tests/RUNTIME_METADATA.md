# Границы заводских runtime-функций

26 октября 2026 восстановлена разметка десяти полных тел, ранее сопоставленных
с SDK/compiler objects в [RUNTIME_CALL_GAPS.md](RUNTIME_CALL_GAPS.md).
Изменение касается инструментов анализа. Production app 4F2C / ELF EB20,
заводской flash, SDK и QEMU не менялись.

`RecoverFactoryRuntime.java` исполнялся в копии проекта Ghidra 12.0.4 с
`-readOnly -noanalysis`. Программа отбрасывает изменения после сеанса. Исходные
и скопированные десять файлов проекта имеют прежние SHA-256 после обоих
успешных запусков. Сохранён воспроизводимый рецепт восстановления, а не
изменённая база Ghidra.

## Что исправлено в разметке

| Функция | Прежняя разметка | Квалифицированный результат |
|---|---|---|
| `_panic_handler`, `0x40380102` | Нет владельца и инструкций | Полные 214 байт, включая два коротких вызова |
| Array nothrow new, `0x420a3a0a` | 14 байт с пропущенным landing pad | Полные 20 байт и оба вызова catch |
| TLS exception destructor, `0x420a3e0a` | Нет функции | Полные 48 байт, вызов DeleteException |
| `__cxa_end_catch`, `0x420a3da2` | Захвачены лишние два байта | 102 байта до исключительной границы `0x420a3e08` |
| Unwind Resume, `0x420a3fc8` | Захвачены соседние stubs, всего 32 байта | Собственные 12 байт |
| Unwind DeleteException, `0x420a3fd4` | Внутри Resume | Отдельные 12 байт |

Оставшиеся scalar new, array veneer, allocate-exception и throw получили
проверенные имена и прежние точные границы. Всего проверено 508 байт в десяти
телах; создано три отсутствовавших функции и добавлено 116 инструкций.
Число перечисляемых функций выросло с 5140 до 5143. API FunctionManager
возвращает отдельно 5145 и 5148; прежнее различие в пять записей сохранено
явно и не интерпретируется как полнота анализа.

Участки `0x420a3e08..0x420a3e0a` и `0x420a3fe0..0x420a3fe8` остаются
декодированными, без владельца. Первый содержит return, второй — переход
через Resume в abort. Десять байт явно сохранены в отчёте. Им не присваивается
предположительное SDK-имя по совпадению короткого тела.

## Независимая проверка

Python заново сопоставляет полные семь объектов с неизменёнными factory и
frozen native ELF. Из результата выводятся границы, хеши и каждая инструкция
манифеста. Это не распознавание функций только по прологу.

Затем проверяются весь граф до/после, владельцы всех изменившихся ссылок,
сырые цели RV32-переходов и AUIPC/JALR, а также прежний аргумент с указателем
на деструктор bad_alloc: для него требуются data relocation полного объекта
и исходная ссылка. Неизменённые области графа должны остаться прежними.
Хеши всех инициализированных memory blocks также совпадают.

Полный проход по 813936 executable bytes находит прежние 453 C.JAL. После
восстановления у каждого есть ровно одна соответствующая call reference и
функция по адресу назначения. До этого не хватало пяти ссылок и владельца
DeleteException. Это закрывает конкретные пробелы в разметке C.JAL; достижимость
всех вызовов, indirect calls, aliases и семантика всего образа остаются открытыми.

20 altered-input controls проверяют неверные границы/хеши, потерянные функции
и инструкции, неправильные call target/type, ложный data alias, присвоение
владельца отсоединённым байтам, изменение посторонней функции, потерянные
ссылки/владельцев, изменение памяти/счётчиков и выдуманную полноту образа.
Все они отвергнуты настоящим consumer. Native suite и VM не перезапускались:
исполняемые production байты не изменились.

## Воспроизведение

[Proof](../../qemu/parity/runtime-metadata-validation-20261026.json): шесть новых
gzip payloads / 11097 байт / 17 source pins. Прежний полный граф и семь объектов
переиспользуются по хешированным ссылкам. В архиве нет нового полного образа,
DROM, пользовательских настроек, RAM или UART журналов.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_runtime_metadata_evidence.py `
  --proof Small_TV/qemu/parity/runtime-metadata-validation-20261026.json `
  --factory C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --native C:/Work/yoRadio/.worktree/small-tv-timer-bounds/.build/small-tv-esp32c2/small_tv_reconstructed.elf
```

Для нового сеанса Ghidra сначала получить qualification штатным
`audit_factory_runtime_calls.py`; `reverse.runtime_metadata.specification`
выводит из него JSON-манифест. На новой копии проекта выполнить последовательно
`ExportFactoryXrefs.java before.json`, `RecoverFactoryRuntime.java manifest.json
recovery.json`, `ExportFactoryXrefs.java after.json` с `-readOnly -noanalysis`.
Сам exit code headless не подтверждает успех: требуются выходной recovery JSON,
его независимая проверка, terminal log и сравнение файлов проекта до/после.

Далее по пользовательскому пункту 4: полная идентификация factory caller
`0x42040efc` (Ghidra приписывает его телу `0x42040e56..0x42040f8e`, 312 байт,
но SDK-source identity ещё не доказана), TIM/null-completion, station lifetime,
BSS periods/overflow и computed aliases. Приоритет и оставшиеся gates не меняются.
