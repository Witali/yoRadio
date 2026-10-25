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
  --rom C:/Work/yoRadio/.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf
```

## Следующая реализация

Сам TCP inventory ещё не реализован. Нужен отдельный module, который читает
только selected fields и исполняет gate **до** обхода четырёх lists:
`tcp_bound_pcbs`, `tcp_listen_pcbs`, `tcp_active_pcbs`, `tcp_tw_pcbs`.
Снимать native `tcp_ticks` и при возможности `num_tcp_pcb`; последний не следует
автоматически приравнивать к числу зарегистрированных nodes: возможны CLOSED,
ещё не зарегистрированные PCB. Если gate busy, сохранять пропуск и его причину,
не объявлять пустой список/нулевые allocations.

Предварительно прочитанный DWARF текущего ELF: `tcp_pcb`208bytes,
`tcp_pcb_listen`76, `tcp_seg`16, `pbuf`16. `pbuf.ref` здесь **один** байт;
не предполагать стандартный u16 ABI. State enum также брать из ELF: CLOSED0,
LISTEN1, SYN_SENT2, SYN_RCVD3, ESTABLISHED4, FIN_WAIT_1=5, FIN_WAIT_2=6,
CLOSE_WAIT7, CLOSING8, LAST_ACK9, TIME_WAIT10. Эти цифры — сведения о текущем
ELF, не универсальная таблица offsets для будущих builds.

Проверить finite/cyclic lists, однократное membership PCB, state/list agreement,
segment/pbuf chains и длины. При допустимом shared pbuf не удваивать память;
отличать shared reference от цикла внутри цепи. TCP buffer payload не нужен.

Связать metadata object с **фактическим содержащим живым TLSF allocation** по
результатам ROM/linked instruction walker, сохраняя unclassified allocations.
Не угадывать скрытый malloc prefix и не считать requested size равным capacity.
Один allocation нельзя приписать нескольким owners без явного shared accounting.
Проверить allocator/list corruption и попытки dereference payload. Затем actual
QEMU positive/negative probes, archive/replay и длинный контроль обычного cadence
15s/outageEvery60. Полная цель, H10, whole-image audit и аппаратные gates открыты.
