# Заводской NVS: полная идентификация чтения страницы

26 октября 2026 установлено: вызов выделения 512 байт в `0x42040efc`
принадлежит `nvs::Page::load(Partition*, uint32_t)`, полное тело
`0x42040e56..0x42040f8e`, 312 байт. Совпадение получено для всего тела
по неизменённому исходнику ESP-IDF5.5.4, включая локальные переходы,
relocations/RELAX и назначения вспомогательных вызовов.

Production app 4F2C / ELF EB20 сохраняется. Это новая проверка и карта SDK-кода;
нового изменения прошивки, общего SDK или QEMU нет.

## Сопоставление исходников и машинного кода

| Тело | Factory, байт | Наша текущая сборка, байт |
|---|---:|---:|
| `Page::load` | 312 | 304 |
| `Header::calculateCrc32` | 26 | 16 |
| Поиск первого непустого слова `std::__find_if` | 134 | Встроен в caller |
| `Page::mLoadEntryTable` | 970 | 822 |
| `Header` constructor | Встроен в caller | 16 |

Статически сопоставлены четыре полных тела в каждом образе: 1442 factory и
1158 native bytes. Для factory использован чистый SDK5.5.4 `735507283d5b` и
официальный GCC14 `esp-14.2.0_20260121`, SHA Win64 archive `c2734714…`.
Matching profile: RV32IMC, Newlib, `-Og -fno-shrink-wrap`, без C++ exceptions.
Это достаточный профиль для совпадения; версия заводского компилятора и его
полная конфигурация этим не установлены. Строгий relocation matcher не ослаблялся.

`compile_factory_nvs_fixture.py` использует только явно выбранный SDK, compiler
и analysis config. Учтены 258 зависимостей, из них 34 SDK files. Компиляция
повторена в другой новой папке: object, DWARF carrier ELF и provenance побайтно
совпали. Carrier разрешает debug relocations для чтения private layout и не
является ESP firmware image. Архив содержит object и carrier, не весь toolchain.

В обоих профилях DWARF показывает Page84B, base8/state12/seq16/version20,
used64/erased66/partition80 и `read_raw` vtable slot12. Полные C++ тела
`Page::load` и CRC wrapper совпадают между SDK5.5.4 и текущим SDK6.1.
Разный размер этих функций связан с компиляцией и inlining; поведение caller
сравнивается отдельно.

## Машинные проверки

- По 197 caller cases на factory и текущем ELF, всего 394: null partition,
  header I/O failure, восемь erased-page reads и ошибки каждого блока,
  каждое из128 dirty-word positions первого блока и позиции в остальных блоках,
  valid/invalid CRC result, состояния страницы, версии0/253/254/255,
  error propagation из entry-table loader и uint32 sector arithmetic.
- Проверены все84bytes частного Page, возврат, buffer ownership, порядок
  вызовов и сохранение ABI registers/stack. Union посещений включает все
  120 factory и118 native instruction starts caller.
- 442 отдельных выполнения полного factory find-helper: длины0..9/127/128/129,
  каждый возможный dirty index и all-erased. Посещены все51instruction starts;
  дополнительный memory hook запрещает чтение за концом, включая length0.
- Ещё два integrated cases оставляют настоящие allocator/helper/throw-stub
  инструкции. При mallocNULL/no-handler factory Page→nothrow new→abort;
  native Page→исправленный wrapper→ESP_ERR_NO_MEM с восстановленным ABI.
  Это подтверждает уже выполненный [nothrow fix](NOTHROW_ALLOCATION.md) на
  полностью идентифицированном заводском caller.

В основной caller matrix allocator является nullable boundary: заводская
NULL-return branch проверяется искусственно. Она не объявляется естественно
достижимой при старом abort-only runtime. Отдельный integrated case сохраняет
это фактическое различие. Partition I/O, CRC ROM и entry-table loader также
являются явными границами. Проверены seed/24-byte range CRC wrapper; вычисления
самой ROM CRC и entry-table repair не заявлены исполненными.

13 реальных input mutations отвергаются полным checker: stack frame, local
NULL branch, allocator/CRC/table/delete targets, scan bound, read length,
find instruction, native frame, source objects и отсутствие RELAX. Ещё пять
report mutations отвергают пропущенный case, ложную паритетность repair policy,
выдуманное исполнение allocator/entry loader и исправление factory OOM.

## Оставшееся различие в NVS

`mLoadEntryTable` статически сопоставлен полностью, но его source body изменился
между SDK. В SDK6.1 `DEFAULT_PURGE_AFTER_ERASE=true`: появились `purgeEntry` и
параметр purge при удалении повреждённых/повторных записей. Это может менять
flash writes и ошибки восстановления. Оно не скрывается за совпавшим caller
или synthetic entry-table boundary.

Следующий factory checkpoint — исполнить обе entry-table реализации на
corrupt/incomplete/duplicate records и I/O failures, проверить реальную запись
и намеренные исправления. Не отключать purge автоматически ради совпадения с
factory. Затем TIM/null-completion, station lifetime, BSS periods/overflow и
computed aliases. Пункты1–3 прежнего списка и финальные acceptance gates открыты.

## Воспроизведение

[Proof](../../qemu/parity/factory-nvs-validation-20261026.json): 11 новых gzip /
185441B /20sourcepins, прежние runtime/wrapper qualifications переиспользуются.
Consumer заново выполняет 394+442+2 cases и13+5 rejection controls без ВМ.
Свежая перекомпиляция выполняется отдельной командой fixture compiler;
обычный evidence replay её не объявляет выполненной.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
$taskBuild='C:/Work/yoRadio/.worktree/small-tv-factory-audit/.build/small-tv-nothrow-20261026'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_factory_nvs_evidence.py `
  --proof Small_TV/qemu/parity/factory-nvs-validation-20261026.json `
  --factory C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --native "$taskBuild/small_tv_reconstructed.elf" `
  --app firmware/development/small-tv-esp32c2-reconstructed/app.bin `
  --nvs "$taskBuild/esp-idf/nvs_flash/libnvs_flash.a" `
  --sdk C:/Work/yoRadio/.idf/v5.5.4 --native-sdk C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6
```

Production bytes и source inputs остаются прежними. Полнота всего образа,
full VM fault injection, весь NVS backend, full/24h и аппаратная приёмка
этим checkpoint не закрываются.
