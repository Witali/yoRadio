# Наблюдение за heap и стеками Small TV

`runtime_qemu.py` выполняет ограниченную нагрузку на неизменной восстановленной
прошивке: все четыре темы и пять GIF, смена города с настоящим HTTP-ответом погоды,
два одновременных клиента чтения настроек и повторная загрузка публичного JPEG
в пятый слот. Наблюдение помогает готовить H09/H10; короткий запуск не закрывает
24-часовую проверку, радиоканал, прерывания физического чипа или аппаратную приёмку.

При использовании замороженного набора инструментов новый бинарник задаётся
отдельно: `--qemu <candidate.exe>`. Без этого параметра сохраняется прежний
`<qemu-root>/bin/qemu-system-riscv32.exe`. Заменять файл в frozen bundle не нужно.
PowerShell-обвязки `start_runtime.ps1` и `runtime_supervisor.ps1` передают тот же
выбор через `-QemuExecutable <candidate.exe>`.

Schema 5 сохраняет абсолютный `qemu_executable` и его SHA в `inputs_sha256`.
Аудитор требует, чтобы именно этот файл был среди pinned inputs и совпадал с
`qemu_sha256`; прежние schema 3/4 проверяются по старому имени. Погодные критерии
schema 4 сохраняются. Тест отвергает неприкреплённый кандидат, неверный SHA и
попытку использовать start record другой сборки.

Запуск из репозитория после подготовки обычных oracle dependencies:

```powershell
& ./.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe `
  ./Small_TV/src/tests/runtime_memory_test.py
& ./.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe `
  ./Small_TV/src/tests/runtime_heap_rom_test.py --dependency-root C:/Work/yoRadio
& ./.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe `
  ./Small_TV/src/tests/runtime_qemu.py --yoradio C:/Work/yoRadio `
  --qemu-root C:/Work/QEMU-ESP32 `
  --output C:/Work/yoRadio/.build/small-tv-parity/runtime-memory-new --cycles 40
```

Для длительного запуска вместо числа циклов задаётся гостевая длительность:

```powershell
& ./.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe `
  ./Small_TV/src/tests/runtime_state_test.py
& ./.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe `
  ./Small_TV/src/tests/runtime_qemu.py --yoradio C:/Work/yoRadio `
  --qemu-root C:/Work/QEMU-ESP32 `
  --output C:/Work/yoRadio/.build/small-tv-parity/runtime-24h-new `
  --duration-seconds 86400 --interval-seconds 15 --outage-every 60 --outage-seconds 1
```

Команда описывает будущий H10 workload, а не уже выполненный результат. Она
переключает все темы/GIF, повторяет публичные фото и HTTP, периодически выключает
внешнюю виртуальную точку доступа. Прошивка получает настоящие 802.11 management
frames и проходит свой reconnect/DHCP путь. Проверяются QOM state, наблюдаемые
guest disconnect/reconnect состояния и доступность station HTTP; флаги связи
не подменяются. Короткое отключение не заменяет проверку полного AP fallback.

Каталог результата должен быть новым. Из worktree тот же `--yoradio` позволяет
читать готовые ELF и архив основной копии, не пересобирая и не меняя их. Скрипт
создаёт только собственную локальную ВМ без SDL и закрывает её в `finally`.
Ни прошивка платы, ни NVS/flash физического устройства не затрагиваются.

## Результат на текущей прошивке, 24 октября

Checkpoint 2026-10-24 на app `9c1a83bd…`, ELF `76b5ce37…`, QEMU `a5be14c5…`:

| Запуск | Циклы / Wi-Fi outages | HTTP | Гостевое время | Минимум sampled free heap | Минимум stack fill |
|---|---|---|---|---|---|
| Preflight | 4 / 2 | 32 | 22,569796 s | 54820 B | 476 B |
| Churn | 40 / 20 | 320 | 200,910826 s | 54688 B | 332 B |

Все запросы уложились в прежний предел 6 guest s; максимум 4,084654 s.
Десять повторных загрузок JPEG в 40-cycle run прошли обычный HTTP upload path.
Независимые UART guards наблюдали один ROM boot без panic; workload, guard и
supervisor завершились с code 0 и неизменными входами. Оба owned VM остановлены.
Сумма накопленных минимумов отдельных heaps в churn достигла 23180 B;
это другая метрика, чем минимум sampled free heap, и не одновременный global peak.
Это две короткие проверки, а не доказательство отсутствия любой утечки или H10.

[`runtime-candidate-validation-20261024.json`](../../qemu/parity/runtime-candidate-validation-20261024.json)
содержит 34 typed raw items / 34 payloads, 114908 новых gzip bytes. Сохранены
полные численные журналы, отчёты/guard/supervisor, early start record 40-cycle
run, исходники и unit log; полные VM flash/RAM/UART не копируются. Replay
пересчитывает журнал и отвергает 16 испорченных отчётов. Отдельные 59 unit tests
для audit/memory/ROM/clock/weather прошли; в этом архиве сохранён log 25 audit tests.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_runtime_candidate_evidence.py `
  --proof Small_TV/qemu/parity/runtime-candidate-validation-20261024.json
```

Исторический replay принимает `--source-revision`; source snapshots и точные
app/ELF identities обязательны. В архиве есть ссылка по SHA на отдельный
network-stalled-peer checkpoint новой модели QEMU. Полные display и network
gates, 24h и аппаратная приёмка остаются самостоятельными этапами.

## Прерванный H10, проверка 2026-10-25

H10 `.build/runtime-h10-current-20261024` на app9C1A83BD/ELF76B5CE37 и
QEMU A5BE14C5 не завершился. Windows CIM подтвердил отсутствие всех четырёх
владельцев и других процессов того же запуска. Supervisor и guard остались со
статусом `running`; это устаревшие файлы, а не живые процессы. Последний heartbeat
—24Oct19:57:54UTC. Причина завершения неизвестна. В ограниченном20-minute окне
Application1000/1001 подходящих crash events не найдено, хост загружен14Oct.
Это не устанавливает ни ошибку прошивки, ни конкретную причину остановки.

Пересчитан весь численный журнал:1488 полных циклов, ещё4 незавершённых события,
25560.689541 гостевых секунд (7ч6мин),11909 HTTP requests с учётом частичного
цикла и24 настоящих STA outages. Промежуточный `completed_cycles=1487` отстаёт
от snapshot на один цикл; он не заменяет разбор журнала. Min sampled heap55116B,
один ROM boot/нет UART panic,1482 разных valid weather generations, максимальный
наблюдаемый интервал свежей погоды68.579137guest s. Нет terminal footer или
успешного terminal guard: строгая приёмка правильно отвергает run. `--diagnostic`
возвращает `pending` для проверенного **префикса**, а не утверждает живость.
В отдельном архиве этот случай классифицирован как `interrupted`.

Неизменённый анализ после часового warm-up дал6 полных часовых окон/60 фаз и
семь retained-loss warnings. По фазам1/13/25/33/37/49/59 разница первой/последней
медиан равна16/18/16/20/12/12/220B. Объяснение этих различий и отсутствие утечки
не установлены. Пороги не смягчались; soak этим не принимается.

[`runtime-interrupted-validation-20261025.json`](../../qemu/parity/runtime-interrupted-validation-20261025.json)
сохраняет24 raw/payload references,167082 новых gzip bytes: numeric journal,
report/guard/supervisor, early record, наблюдение владельцев, исходники и оба
offline результата. Full UART/RAM/flash не копируются. Независимый
`verify_interrupted_runtime_evidence.py` пересчитывает журнал/trend, сохраняет
все warnings и отвергает12 controls, включая ложный H10 pass, живого владельца,
скрытые flags, HTTP503 и неверную сумму heap. `evidence_verified=true` означает
проверенные данные прерванного запуска; workload/H10 passed остаются false.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_interrupted_runtime_evidence.py `
  --proof Small_TV/qemu/parity/runtime-interrupted-validation-20261025.json
```

Исторический replay принимает `--source-revision`; нужен соответствующий app/ELF.
Main QEMU9135fc89ce/2DF90327 закреплён отдельным `main-9135-riscv32.exe`; старыйV8
и frozen tools сохранены. Новый4-cycle preflight прошёл,40-cycle qualification
запущена отдельно. Это не H10 и не объяснение прежних memory flags.

## Разделение модулей и способ измерения

- `runtime_memory.py` извлекает размеры/поля из DWARF текущего ELF, обходит
  зарегистрированные heaps и все FreeRTOS state lists. Он отвергает неверные
  адреса, циклы, несовпадение количества задач, владельцев, ссылок и размеров.
- `runtime_heap_rom.py` исполняет два настоящих ROM getter в отдельном RV32
  Unicorn на копии ограниченного заголовка allocator. Чтения `free_bytes` и
  `minimum_free_bytes` должны совпасть с DWARF-декодером. RAM/регистры/инструкции
  QEMU при этом не подменяются, функции внутри гостя не вызываются хостом.
- `runtime_qemu.py` управляет нагрузкой, записью численных результатов и своей ВМ.
  Снимок снимается на входе в естественно вызванный `vTaskDelay`, после завершения
  изменений allocator и списков задач. Гость останавливается hardware breakpoint;
  программные breakpoints, запись RAM и присваивание PC не используются.
- `runtime_state.py` разворачивает переполнение low32 radio microseconds и
  сохраняет append-only `events.jsonl`. Счётчик QEMU глобален для жизни ВМ;
  guest reset его не сбрасывает. Между чтениями должно пройти меньше одного
  периода 2**32 us; runner опрашивает его многократно за цикл, интервал ограничен
  60 секундами. Переполнение около 71,6 минуты не сокращает заданные 24 часа.

Schema 3 сохраняет все события один раз в JSONL, а в `report.json` — счётчики,
минимумы, первый снимок и последние 32. RAM хоста и размер каждой перезаписи
summary не растут вместе со всем журналом. Digest журнала записывается после
закрытия; для анализа всех ранних samples нужен сам `events.jsonl`. Время запуска
не включает startup до ready. Целевой срок — минимум: начатый цикл завершается
целиком, поэтому итог может немного превышать запрос. 24h нельзя выводить из
короткого успешного smoke или из host duration.

Подтверждение reconnect больше не зависит от отладочных Wi-Fi строк в UART:
schema 3 читает одноимённый `connected` atomic bool по символу текущего ELF.
Видны последовательные состояния true → false → true, дополненные QOM AP state
и настоящим HTTP после восстановления. Это только чтение гостевой RAM; флаг
никогда не назначается наблюдателем. Прежние schema 2 отчёты с UART counts
сохраняют свои исходные хеши и область проверки.

Чтения sentinel links используют уже прочитанный xLIST; stack scan идёт блоками
до 1024 байт, помещающимися в RSP hex reply. Проба с 4096 bytes дала E22 и была
исключена как ошибка transport observer. На одной синтетической SRAM-фикстуре
45 memory requests уменьшены до20 при одинаковых decoded heap/tasks; это не
измерение ускорения физического чипа. В клиентском сокете отключён Nagle, чтобы
маленький debugger ACK не задерживал следующий read.

Проверки parser включают испорченные heap/list chains и счётчики, дублирующуюся
задачу, короткое чтение, недопустимый стек и нулевой запас. ROM-тесты используют
разные счётчики, NULL и намеренно ошибочный ABI-декодер. Тест не объявляет нулевой
запас невозможным: decoder возвращает его, а runtime workload считает это ошибкой.

`MALLOC_CAP_8BIT` суммируется по тем же правилам ORed capabilities, что ESP-IDF.
Сумма минимальных значений отдельных heaps повторяет SDK API; это не минимум,
когда все heaps одновременно находились в таком состоянии. Стек здесь растёт
вниз, `StackType_t` — один байт. Запас — непрерывный префикс `0xA5`, как в
`prvTaskCheckFreeStackSpace`. `recorded_stack_span_bytes` использует записанный
FreeRTOS верхний адрес после выравнивания; это не размер выделенного блока.
TCB-снимки не измеряют отдельный ISR stack, а короткая нагрузка не гарантирует,
что были достигнуты все пики. Наблюдатель приостанавливает виртуальное время;
его host duration нельзя считать непрерывной длительной работой гостя.

В отчёт попадают имена задач, размеры, счётчики и HTTP path/status/timing, а не
содержимое стеков, HTTP bodies или allocator payloads. Хеши связывают отчёт с
ELF/app/ROM, четырьмя образами flash, профилем, helpers, SDK и самим наблюдателем.
`passed` означает прохождение именно этой ограниченной нагрузки и проверок
входов; он не устанавливает полного соответствия заводской прошивке.

## Независимый контроль тихих перезагрузок

Для длительного запуска дополнительно запустите `src/tools/runtime_run_guard.py`
с `--run <каталог результата>` и `--qemu-tools <зафиксированный QEMU/tools>`.
Присоединять его следует после первой ROM-загрузки. Он читает весь UART capture
и отдельно сохраняет `uptime-guard.json`. Требуется ровно один настоящий ROM
banner с последующей строкой Build; reset, прервавший незавершённую строку
приложения, тоже обнаруживается. Проверяются panic/watchdog и потеря истории
из-за усечения файла. `runtime_guard_test.py` покрывает семь таких случаев.

Guard не изменяет входы нагрузки, память гостя или его выполнение и не открывает
второй QMP-клиент: основная нагрузка уже держит единственное соединение. При
ошибке guard заканчивается с отказом; результат нагрузки нельзя принимать без
его успешного terminal result, полного UART и анализа журнала памяти. Обычный
`passed=true` основного скрипта сам по себе не исключает тихую перезагрузку,
которая могла бы сбросить heap minima и скрыть утечку.
