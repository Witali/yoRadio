# Отнесение heap к TCP: подготовка наблюдателя

Цель — проверить, связаны ли прежние retained-loss warnings 12–220 байт с
живыми TCP PCB/буферами, TIME_WAIT, ёмкостью allocator blocks или другой частью
прошивки. Это продолжение [TLSF inventory](HEAP_TOPOLOGY.md), а не уже найденная
причина утечки. Основной H10 на прежних inputs не изменяется.

## Выполнено: безопасная точка чтения

`runtime_tcp_gate.py` получает выбранные offsets из native DWARF. Текущая policy
квалифицирована только для ELF `76b5ce3700d299b607774467a57bc95e07d3cd39f6385bc3a1befd0504c2dad8`.
Другая сборка отклоняется до чтения гостя: её synchronization policy нужно
проверить отдельно. Текущий build имеет `CONFIG_LWIP_TCPIP_CORE_LOCKING=n`;
связанная `sys_thread_tcpip` (`0x42034632`,132bytes) сверена с assembly и
`sys_arch.c`. Её persistent task pointer найден по DWARF variable location,
без зависимости от compiler suffix в имени `lwip_task.1`.

На одном ядре остановка чужой задачи у `vTaskDelay` может застать TCP/IP task,
вытесненную посреди изменения списка. Поэтому новый gate требует одновременно:

1. Известные инициализированные `lwip_task` и `tcpip_mbox`, текущая задача другая.
2. `xEventListItem.pxContainer` TCP/IP task указывает именно на receive wait list
   настоящего mailbox. Queue находится **внутри** `sys_mbox_s.os_mbox`; это не
   ещё один pointer, который нужно разыменовать.
3. Очередь пуста; её receive wait list содержит единственного owner TCP/IP task.
   Проверены оба направления links, sentinel, число элементов, container и
   точная identity TCB event item. Один stale container не доказывает ожидание.

Для текущего ELF: `sys_mbox_s` и `QueueDefinition` по84байта,
`xTasksWaitingToReceive` offset36, `uxMessagesWaiting` offset56; TCB96bytes,
`xEventListItem` offset24/size20. Код извлекает их из DWARF. `xQUEUE` — typedef,
а имя структуры — `QueueDefinition`. Ненужные поля и flexible array members
не интерпретируются. Недопустимые pointers/links означают ошибку; корректное
busy состояние возвращает явную причину и не разрешает последующий TCP walk.

В read transcript только linked scalar globals, счётчик queue и list metadata.
Queue message storage, полный TCB/его регистры, IP-адреса, packet payload и
пользовательские данные не читаются. Replay требует ту же последовательность
чтений без пропусков и лишних bytes. Гость не переводится в искусственный idle.

15 host tests используют настоящий native ABI и synthetic host metadata:
running task, другая ожидаемая очередь, pending message, initialization,
недопустимые pointers, broken links/owners, другой event item с тем же owner,
пропущенные/лишние reads, short transport, unknown policy/ELF и ABI overlap.

`runtime_tcp_gate_qemu_test.py` дополнительно оборачивает только host callback
существующего heap sampler. Одна отдельная ВМ, прежние app/QEMU, 4цикла,
2STAoutages/32HTTP,23.110207guest s: все5snapshots действительно показали empty
mailbox с blocked TCP/IP owner. Сохранены binding к полному same-stop snapshot
и каждый metadata read. ВМ завершилась, PID39284 и same-run processes после
выхода отсутствовали по CIM. Один ROM boot/noUARTerrors. Независимый UART guard
не запускался: это gate probe, не ещё одна полная qualification/H10.

[Архив](../../qemu/parity/tcp-mailbox-gate-validation-20261025.json):27raw/payload
references,45308newgzipbytes с reuse source payloads. Consumer повторно проверяет
native ABI, heap instructions и все5gate transcripts, source/unit/app/ELF/ROM
bindings.12negative controls отвергнуты, включая false quiet count, missing
snapshot/read, подмену same-stop identity, ложный scope и skipped heap replay.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_tcp_gate_evidence.py `
  --proof Small_TV/qemu/parity/tcp-mailbox-gate-validation-20261025.json `
  --source-revision 82d901e2d `
  --rom C:/Work/yoRadio/.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf
```

## Выполнено: TCP inventory и отнесение памяти

Опция `-TcpTopology` у launcher/supervisor и `--tcp-topology` у Python runner
включает schema7 и подразумевает heap topology. Обычные schema5/6 сохранены.
Гость, его firmware и QEMU model не меняются. Модули разделены по назначению:

- `runtime_tcp_layout.py` извлекает selected fields, native state enum и globals
  четырёх списков: bound/listen/active/TIME_WAIT. Ненужные IP/port/callback fields
  не читаются. Native `pbuf.ref` здесь один байт, ABI проверяется явно.
- `runtime_tcp_allocations.py` получает живые ranges из callbacks **точных**
  ROM/linked walker instructions. Metadata object должен целиком помещаться в
  живой allocation; интерпретация свободной памяти, чужого payload или переход
  через конец блока отклоняется до чтения. Shared ranges учитываются один раз.
- `runtime_tcp_snapshot.py` сначала исполняет mailbox gate, затем читает PCB,
  unsent/unacked/ooseq segments и pbuf chains/refused data. Проверяет ownership,
  циклы, state/list agreement, packet/chain lengths, send queue count, refs и
  wrapped `tcp_ticks` ages. Busy сохраняет явный пропуск, без ложных нулей.
- `runtime_tcp_journal.py` повторно проверяет каждое наблюдение и сохраняет
  небольшой ряд: TCP/unclassified capacity с headers, block counts и состояния.
  Непривязанные allocations не объявляются TCP или утечкой.

Current native ABI: `tcp_pcb`208bytes, listen76, segment16, pbuf16. Путь
`do_memp_malloc_pool`→`mem_malloc`→`malloc` сверён с assembly; pool size округляется
до4 без prefix, helper возвращает исходный pointer. Heap task tracking/poisoning
и lwIP stats выключены. Для **этого ELF** qualified metadata offset равен нулю;
другие layouts нельзя угадывать. Header/PBUF pointer должен начинаться в живом
allocation; payload reference может указывать на отдельную RAM/ROM область,
содержимое которой не читается. Contiguous pbuf обязан ссылаться на свой block.

`num_tcp_pcb` может включать ещё не зарегистрированные CLOSED objects. Остаток
сохраняется отдельно; отсутствующие PCB не выдумываются. State enum и offsets
взяты из ELF, а не из таблицы предполагаемой версии lwIP. Внутри pbuf chain
разрешены документированные packet boundaries; shared references отличаются от
цикла и не удваивают allocated capacity. Исходный requested size из block size
не восстанавливается.

33 host tests используют настоящий ROM allocator и native ABI: четыре списка,
shared buffers, RAM/ROM references, free/crossing/interior pointers, metadata
alias в packet data, corrupted queues/lengths/refs, wrap и future timer, busy
actor, точный read transcript и additive partition с unclassified памятью.
31 исходный тест прошёл до добавления двух journal tests; accepted report — v2
с33тестами. Дополнительно прошли25 прежних audit/trend tests.

| Нагрузка | Guest seconds | STA outages | HTTP | TCP snapshots |
| --- | ---: | ---: | ---: | ---: |
| Preflight4 | 22.240650 | 2 | 32 | 5 / 5 observed |
| Churn40 | 203.479499 | 20 | 320 | 41 / 41 observed |

Оба workload/guard/supervisor завершились с0, sources unchanged, один ROM boot,
noUARTerrors. Min sampled free heap второго run54672B, SDK sum minima20308B,
min task fill428B; maxHTTP4.118874guest s при прежнем limit6. Все92heap inventories
и46TCP snapshots воспроизведены. В этих снимках были LISTEN/FIN_WAIT_2, максимум
три PCB: listener76+4=80B и закрывающиеся208+4=212B каждый; TCP consumed80..504B.
У наблюдавшихся PCB capacity padding равен0. Это не объясняет старые7flags.

Живых segments/pbufs в моменты этих коротких снимков не было. Их сложные chains
проверены на real-ROM host fixtures, **не** на реальном queued guest traffic.
Нужен отдельный controlled pending-traffic probe; краткий idle/churn не закрывает
его, полный сетевой lifecycle, длинный soak или аппаратную приёмку.

[Архив](../../qemu/parity/tcp-inventory-validation-20261025.json):54raw/payload
references,242895newgzipbytes с reuse прежних producers. Отдельный consumer
перепроверяет оба полных журнала, source/unit/model/app/ELF/ROM, early0, ABI,
typed TCP reads и additive series;76semantic negative controls отвергнуты.
Старые heap/gate checkpoints отдельно воспроизведены с их source revisions.

При cleanup check Windows уже переиспользовала preflight workload/guard PID
для других images, созданных **после** успешного terminal supervision. Новый
owner record различает отсутствие исходного процесса и отсутствие самого номера
PID. Сверяются4roles, retained supervisor IDs, VM identity и immutable creation
time; alive/before-terminal/replaced-role controls отклоняются. Чужие процессы
не останавливались. В следующем run все4PID действительно отсутствовали.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_tcp_inventory_evidence.py `
  --proof Small_TV/qemu/parity/tcp-inventory-validation-20261025.json `
  --rom C:/Work/yoRadio/.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf
```

Далее — сопоставимые длительные metadata controls с interval15/outageEvery60
на main и прежнем V8, controlled queued traffic, разбор unclassified deltas и
retained-loss flags. Не складывать короткие runs с основным24hH10, не смягчать
thresholds и не считать новый контроль объяснением старого run без воспроизведения.
Idempotent already-stopped-VM cleanup также остаётся отдельным follow-up. Полная
цель, whole-image audit, final full suite и аппаратные gates остаются открытыми.

## Запущенные matched controls

После commit23b641680 запущены `.build/tcp-inventory-qemu-20261025/soak-main`
и `soak-v8`:по28800guest seconds, interval15/outageEvery60/schema7. Первый
started25Oct13:40:41UTC, второй13:42:23UTC;app/ELF/ROM и observers одинаковы,
исполняемые QEMU соответственно2DF90327/A5BE14C5. Early0 и4positive process
identities сохранены отдельно для каждого. На13:47:42UTC процессы ещё те же,
13/9completecycles,oneROMboot/noerrors. Это запуск/префиксы, не итог сравнения
и не объяснение7retained-loss flags. Основной H10 остаётся отдельным run.

Pinned inputs здесь не менять; дальнейшие producer changes делать в другой
task worktree. По завершении нужны полный журнал, guard/supervisor exit0,
источники и разбор TCP/unclassified по тем же phases/warmup, что runtime_trend.
Суммы отдельных medians не равны median суммы: для additive attribution нужно
брать одинаковые центральные snapshots. Никакие thresholds этим не меняются.
