# Диагностика структуры heap ESP32-C2

Наблюдатель нужен для разбора семи retained-free-heap предупреждений прежнего
прерванного H10: медианная разница 12–220 байт пока не объяснена. Сам по себе
счётчик свободной памяти не различает новые живые allocations, служебные
заголовки и увеличенную ёмкость уже существующих allocations. Порог приёмки
не изменяется; короткий успешный тест не закрывает эти предупреждения.

## Что измеряется

Опция `--heap-topology` у `runtime_qemu.py`, либо `-HeapTopology` у
`start_runtime.ps1`, добавляет schema 6. По умолчанию остаётся schema 5.
Контроллер снимает дополнительные данные в своей ВМ на прежней остановке
у естественного входа в `vTaskDelay`. Другой debugger/QMP клиент не подключается.

- `runtime_memory.py` получает список зарегистрированных heaps и их границы
  по DWARF текущего ELF. Старый scalar snapshot сохраняет свой формат и ROM
  crosscheck. Повторное чтение метаданных обязано дать те же scalar counters.
- `runtime_heap_topology.py` проверяет весь фактический TLSF dispatch table:
  ROM default table с двумя связанными SDK patches, `tlsf_walk_pool_impl`
  и `tlsf_check_pool_impl`. Размер и offsets берутся из native DWARF.
- `runtime_instruction_image.py` загружает точные инструкции ROM и связанного
  walker в отдельный host Unicorn RV32. Гостевые инструкции и регистры не
  подменяются, allocator внутри QEMU хостом не вызывается.
- `runtime_tlsf_instructions.py` выполняет эти инструкции на копиях отдельных
  слов заголовков. Проверяются последовательность блоков, sentinel, отсутствие
  соседних свободных блоков, границы, счётчики и полный баланс физического pool.
  Любое чтение payload, выход за allowlist кода или запись вне host stack
  прерывают наблюдение. В replay нельзя подставить нули вместо пропущенного слова.

Дополнительный walker читает только четырёхбайтовые size headers. Существующий
stack observer по-прежнему читает префикс заполнения стеков задач; утверждение
о запрете payload reads относится именно к новому TLSF walker. В архиве остаются
числа, размеры, адреса и metadata words, а не содержимое allocations/стеков,
полный RAM, flash, UART или пользовательские HTTP bodies.

## Проверенный ABI и арифметика

ROM ESP32-C2 rev200 имеет SHA256
`289ce00e79c024d9efeb29a7fbc2d21853a1cbc383a2b9c2ece85c54fa829dd9`.
Другой ROM отклоняется. Для этой версии control занимает 1604 байта,
allocation overhead — 4 байта, pool overhead — 8 байт. Не следует переносить
константы из текущего SDK TLSF вместо проверки действительных ROM instructions.

В ROM dispatch table слоты с DWARF именами `tlsf_size` и `tlsf_align_size`
зарезервированы и равны нулю. Наблюдатель сохраняет и проверяет их нулевыми,
а geometry получает вызовом отдельного настоящего ROM getter в host CPU.
Первый прототип ошибочно требовал ненулевой слот: он исключён из приёмки.

Для каждого heap проверяется равенство:

```text
pool_size - control_size = allocated_capacity_bytes
                         + allocated_blocks * allocation_header_bytes
                         + free_counter
```

Отдельный баланс физических блоков учитывает headers между блоками и два
terminal/pool overhead words. Сохраняются число, суммарная ёмкость и гистограммы
живых/свободных блоков, а также наибольший свободный блок. Ёмкость allocation
включает возможный неразделяемый хвост; исходный requested size из этих
метаданных восстановить нельзя. Сумма minimum counters разных heaps остаётся
SDK метрикой, а не одновременным глобальным минимумом.

## Проверки

Host fixtures исполняют настоящие ROM register/malloc/free/realloc, а не
воссоздают их арифметику на Python. 11 instruction tests включают 180
детерминированных действий, сравнение ROM и linked walkers при продолжающем
callback, JSON replay, повреждённые counters/headers и намеренно опасные
host callbacks с чтением payload/записью heap. Ещё 8 topology tests проверяют
native dispatch, reserved slots, подмену linked walker на ROM, скрытые headers,
пропущенный heap и самосогласованно изменённый свободный счётчик.

Один контроль показывает разницу ровно 12 байт при одинаковых живых requested
sizes и числе allocations. В одном heap последовательно выделяются 20,32,32;
в другом — 32,32,32, затем первый блок освобождается и заменяется запросом 20.
ROM не может отделить слишком маленький остаток и сохраняет capacity 32.
После освобождения всех allocations оба счётчика полностью восстанавливаются.
Это доказанный пример padding, **не установленная причина предупреждений H10**.

Базовые 16 memory tests и 25 audit/trend tests также проходят. Настоящие короткие
нагрузки используют прежнюю app `9c1a83bd…`, ELF `76b5ce37…` и QEMU main
`9135fc89ce` / executable `2df90327…`. Новый consumer повторно исполняет точные
инструкции для каждого сохранённого snapshot, сверяет unit/source/ROM/ELF hashes
и отклоняет altered metadata, пропущенный replay и ложную model identity.

Оба qualification runs завершились с workload/guard/supervisor exit code 0,
одним ROM boot и неизменёнными входами; все 8 owner PID и same-run Python/QEMU
children затем отсутствовали по CIM. Genuine early record второго run снят
на cycle 0 в той же invocation, которая запустила supervisor.

| Нагрузка | Guest seconds | Отключения сети | HTTP | Snapshots / heap inventories |
| --- | ---: | ---: | ---: | ---: |
| Preflight, 4 цикла | 22.839657 | 2 | 32 | 5 / 10 |
| Churn, 40 циклов | 203.530398 | 20 | 320 | 41 / 82 |

Во втором run sampled free heap не опускался ниже 54804 байт, сумма SDK minima
равна 27104 байтам, минимальный наблюдавшийся stack fill — 428 байт. Max HTTP
4.038217 guest seconds при прежнем limit 6. Эти наблюдения не задают worst case.

[Архив](../../qemu/parity/heap-topology-validation-20261025.json) содержит 44
raw/payload references, 196599 новых gzip bytes с повторным использованием
прежних источников. Независимый replay проверил все 46 snapshots / 92 inventories
и отверг 38 negative controls: 18 обычных workload/guard, 16 metadata и 4 model.
H10 и полное отсутствие утечек этим результатом не подтверждаются.

Пример воспроизведения из этой рабочей копии:

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_runtime_candidate_evidence.py `
  --proof Small_TV/qemu/parity/heap-topology-validation-20261025.json `
  --rom C:/Work/yoRadio/.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf
```

## Ограничения и следующие действия

Новая диагностика разрабатывается в отдельной рабочей копии. Запущенный
25Oct11:23UTC основной H10, его исходники, app/ELF, SDK и frozen QEMU bundle
не меняются. Его 24-часовая приёмка остаётся самостоятельным пунктом плана.

После квалификации observer нужно добавить typed наблюдение TCP PCB/TIME_WAIT,
сопоставить одинаковые фазы нагрузки и только затем провести длительный
диагностический контроль с обычным cadence 15s/outageEvery60. Нужны причины
изменения живой capacity/count, а не общий вывод об отсутствии утечки по
короткому тесту. Память нового observer не определяет owner/requested size
каждого allocator блока и сама по себе этого не доказывает.

Первый этап TCP observer теперь проверен отдельно:
[mailbox quiescence gate](TCP_HEAP_ATTRIBUTION.md),15host tests и5same-stop
наблюдений в отдельной QEMU ВМ. Сам PCB/segment/pbuf walk ещё не реализован;
безопасная точка чтения не заменяет attribution и долгий контроль.

Сохранены также исключённые exploratory runs: первый prototype завершился
ошибкой dispatch qualification; отдельный успешный 40-cycle run был замечен
слишком поздно для genuine cycle-zero capture. Они не подменяют qualification.
При prototype failure redundant supervisor cleanup получил connection refused
после уже закрытой driver ВМ; все четыре owner PID затем отсутствовали.
Идемпотентность этого cleanup пути требует отдельного исправления и теста.
