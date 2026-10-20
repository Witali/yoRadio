# Продолжение работы: полный561 и PHY классического ESP32

Рабочая ветка yoRadio — `codex/small-tv-reset-display`. Production app
`0592b510…`, ELF `aea10675…`, source `d338a294…`, RISC QEMU `d64f3013…`
остаются прежними. Соответствие всей прошивки пока не доказано.

## Полный557 завершён, причина установлена

Контроллер 18940 завершился 2026-10-18 15:59:22 UTC с exit 1. Восемнадцать
других обязательных групп прошли. Независимые boot/network/display проверки
после reset прошли у обеих прошивок. Затем Wi-Fi fallback остановился ещё
до запуска первого гостевого сценария: выбранный автономный снимок не содержал
`configs/boards/small-tv-c2.json`, который читает `seed_setup_network`.

Старый результат сохранён как failed, 557 входов совпали. Сырые материалы:
`reset-display-full-terminal-20261018.json` и соседняя папка `-raw`.
Исходный snapshot и его `frozen-inputs.json` не редактировались.

## Исправление состава снимка и сетевой preflight

Новый `.build/reset-display-qemu-complete-20261018` содержит те же 42 исходных
файла и четыре существующих board JSON, всего 46 файлов плюс manifest. Все
код/исполняемые файлы прежние; профиль по умолчанию канонически совпадает с
явно выбранным Small TV профилем. Реальная подготовка setup images обеих
прошивок прошла без запуска ВМ.

Отдельный `wifi_fallback_qemu.py` terminal pass: задержанный DHCP и настоящий
отказ внешней AP с переходом в setup у original/reconstructed, все четыре
сценария успешны. Пройдены 26 отрицательных контролей потребителя отчёта.
См. `complete-snapshot-preflight-20261018.json` и 42 сырых файла `-raw`.

## Новый полный561 жив

Контроллер PID 30244, создан 2026-10-18 16:04:24.328133 UTC. Запущен через
локальный `Win32_Process.Create` с ShowWindow=0 и нативными путями; удерживаемый
OS handle подтвердил `IsProcessInJob=false`. Первый WMI-запрос вернул код 21
без создания процесса; исправленный запрос создал единственный контроллер.

Зафиксированы 141 test file и 420 дополнительных входов, всего 561. Запуск
и checkpoint лежат в `reset-display-complete-full-start-20261018.json`,
`reset-display-complete-full-launch-20261018.json`,
`complete-runtime-live-checkpoint-20261018.json`. Повторно совпали и 557 старых,
и 561 новых входов. Пока full561 жив, не менять src, archive/ELF/SDK или новый
snapshot. Следующие записи вести здесь, в `qemu/parity`.

Наблюдать существующий PID/его terminal record. Не перезапускать по истечению
тайм-аута наблюдения. После terminal pass использовать стандартные publisher
и artifact verifier с output в parity, сохранив frozen test sources, а также
все их raw results. Старые failed records не заменять новым pass.

## H10 продолжает работать отдельно

В `small-tv-runtime-supervision` supervisor/workload/guard/VM PID
13800/31224/27200/19212 подтверждены по OS identities. Checkpoint сохранил
92 цикла; guard видит один ROM boot и не обнаружил panic. Повторно совпали
31 runtime, 41 snapshot и 6 supervisor записей (реестры могут пересекаться).
Это пока не 24-часовая и не memory-trend приёмка. Новых QMP/RSP клиентов к H10
не добавлено; единственные соединения принадлежат workload.

## QEMU DPORT и ещё открытая совместимость CYD

В QEMU закоммичены отдельно `b3619c8b4b` (DPORT clock/reset latches),
`2924ab54d2` (исправление ложной ROM/console-only приёмки CYD) и
`c4d285f486` (43 raw evidence files). Итог: одинаковый окончательный MMIO
тест падает во всех четырёх случаях на старом Xtensa и проходит все четыре
на исправленном. NOR 11 групп/3 SoC и modular-peripheral tests пройдены;
16 tool tests включают пять контрпримеров ложного CYD pass.

RISC бинарник побайтно прежний D64. Исправленный Xtensa `2099ed93…`
находится в `.cache/esp32-phy-clock/bin`; установленный `bin` не объявляется
этой новой сборкой. Точные значения и ссылки — `cyd-phy-followup-20261018.json`.

CYD ещё не принят. После устранения clock assertion неизменный app faulted
на `0x401b9920`, чтение `0x60033c00`. Matching SDK lib-builder 14a0af9 /
IDF 735507283d идентифицировал `register_chipv7_phy`: entry instructions
совпадают за исключением l32r relocation. Classic ESP32 сейчас предоставляет
OpenETH и не имеет соответствующей Wi-Fi/PHY модели. Нужен обоснованный путь
периферии, а не успешный результат, выведенный из ROM-only ожидания.

Main пока не сливать. Следующие действия: terminal full561, продолжение H10,
проверка его footer/UART/memory trend после завершения и восстановление
документированного PHY/MAC пути CYD. Физическая плата не прошивалась.
