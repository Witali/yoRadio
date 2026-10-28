# Снимок состояния до закрытия неуспешного runtime

В [неуспешном H10](RUNTIME_MAIN_FAILURE.md) остался traceback `/start_upload`,
но `finally` сразу закрыл RSP и ВМ. Добавлен `FailureCapture`: его context выходит
раньше существующего QMP context и внешнего cleanup. Первоначальное исключение
продолжает распространяться даже при отказе диагностики или записи файла.
Успешный workload не получает дополнительных остановок или диагностических I/O.

## Что сохраняется

`failure-state.json` содержит identity app/ELF/QEMU/ВМ, последнее действие,
число завершённых циклов, PC/SP/RA, connection flag, typed heap counters,
имена/адреса/границы стеков и membership задач. Дополнительно читаются состояния
photo worker/upload, длина и занятость очереди, ожидающие задачи и владельцы
codec/media mutex. Статические имена worker выбираются по compilation unit;
адреса, размеры, signedness и вложенные QueueDefinition offsets берутся из DWARF
точного ELF, а не из прежней сборки. Разбор типов находится в отдельном модуле.

Содержимое стеков, allocator payload, JPEG, HTTP bodies/headers и credentials
не экспортируются. Используются существующие соединения; новый observer не
подключается. Перед чтением CPU останавливается обычным debugger interrupt,
если QMP ещё не показывает stop. PC не присваивается, функции в госте не
вызываются, до удобного SDK entry point программа не доисполняется.

Это произвольная точка ошибки. Несогласованный список или heap может означать
незавершённую операцию в момент stop; такой component помечается как частичный.
Снимок не является стабильным allocator/TCP gate и не ослабляет allowlist нового
ELF для TCP topology. Остановленная ВМ затем закрывается прежним владельцем.

## Ограничения диагностики

- Общий I/O deadline — 5 host seconds. RSP учитывает его перед каждым send/recv,
  поэтому медленные частичные ответы и несколько запросов не продлевают бюджет.
- Не более 192 memory requests и 32768 запрошенных байт; одно чтение не больше
  4096 байт и только в известных C2 SRAM ranges. Повторные чтения остановленных
  typed metadata используют ограниченный cache.
- QMP разрешает только `query-status` и `info usernet`. Ограничены поток JSON,
  события и частичные строки. Сериализованный usernet ограничен 16 КиБ, чтобы
  большой список соединений не вытеснил CPU/photo observations.
- Итоговый metadata file ограничен 64 КиБ и создаётся эксклюзивно. Существующий
  файл не перезаписывается. Ошибка транспорта/файла не превращает workload в pass.

## Проверка на настоящей ВМ

`runtime_failure_qemu_test.py` запускает неизменённую C91294FC/9E4EC88D на
закреплённом main QEMU `2df90327…`. После настоящего `/start_upload` с HTTP 200
он намеренно создаёт host `TimeoutError`. Это проверка аварийного пути, **не
воспроизведение причины исторического таймаута**.

Финальный run подтвердил существование и SHA снимка **до** вызова stop, сохранение
того же exception object и выход исходного kernel process object ВМ без test
fallback cleanup. Capture занял 0,047 host seconds: 96 запросов, 2230 байт.
Все компоненты прочитаны, errors пуст; upload active, received=0 и length совпали
с настоящим JPEG fixture. Только `m`/`p` команды отправлены RSP во время capture.
Сохранены два завершённых цикла и четыре pending события исходного журнала;
сам намеренно неуспешный workload не объявляется успешной прошивкой или H10.

10 localhost RSP deadline tests и 10 transport/file/budget capture tests pass.
Отдельный consumer пересчитывает журнал, UART и native DWARF layout; 11 negative
controls отвергают неверный target, превышение bounds, запись/исполнение гостя,
ложное ordering/cleanup и неподтверждённую аппаратную приёмку.

[Архив](../../qemu/parity/runtime-failure-capture-validation-20261025.json):
31 payload reference, 22 source pins, 17 новых gzip / 37969 байт. Прежние blobs
повторно используются. Полные ELF/SDK/Flash/RAM не дублируются.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
python -B -X utf8 Small_TV/src/tests/verify_runtime_failure_capture_evidence.py `
  --proof Small_TV/qemu/parity/runtime-failure-capture-validation-20261025.json
```

После последующих изменений producer sources использовать `--source-revision`
коммита этого checkpoint, сохраняя соответствующие app/ELF. Это offline replay;
он не подключается к работающим ВМ.

Обычный preflight закоммиченного producer `70cd3e5be` также прошёл: четыре цикла,
32 HTTP, два переподключения, 18,816259 guest seconds. Workload/guard exit 0,
supervisor complete, все входы повторно хешированы, исходные четыре владельца
завершились. Ни failure-state file, ни `failure_capture` field на успехе не созданы.
Пересчитаны журнал/UART и 12 workload/ownership rejection controls.
[Девять raw records](../../qemu/parity/runtime-failure-capture-preflight-20261025.json)
занимают 10446 gzip bytes и сохраняют genuine cycle-zero и process observations.

25 октября в 16:42 UTC запущен один отдельный диагностический run с запросом
86400 guest seconds, interval 15, outage every 60; cycle-zero и четыре исходных
владельца сохранены. Это pending reproduction, не успешный H10. При проверке
16:45 UTC владельцы живы, три цикла завершены, UART guard без ошибок.
Исторические failed H10 и два matched controls сохранены отдельно.
Суточная приёмка, причина timeout, разбор retained memory, независимые
network/display gates и hardware остаются открытыми пунктами.
