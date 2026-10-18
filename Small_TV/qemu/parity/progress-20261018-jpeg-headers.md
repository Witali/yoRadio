# Продолжение полного сравнения: JPEG headers

Текущая ветка `codex/small-tv-jpeg-headers`, production correction `2cd72264`:
app `f1ada8b4da4338df3248ffb26a39a79e36bf5cf0e365eb2972b75c8721f7ea7b`,
ELF `91e26eb2583ea61fda24f81ef9f7fdfbe2ad5ecf35b476b17dee680d29b5089d`,
QEMU `d64f3013739f22b986e07aed39395b25bde474f52ef813b8ffaeedb0991edecc`.

По повторному требованию пользователя сеть и дисплей проверяются отдельно.
Сетевые результаты не подтверждают состояние кадра, результаты дисплея не
подтверждают Wi-Fi/DHCP/SNTP. Повторно прошли19 ELF/SDK/SNTP tests,9 display
tests и3 failure-isolation controls. Контекст сохранён до freeze в
`Small_TV/src/WORKING_NOTES.md`; proof `independent-subsystem-checks-20261018.json`.

Целевые JPEG checks завершены:133 новых header cases (14valid/119invalid),
107 public images,41 прежний extra input,128 DHT,5531 native C и6 artifact.
В HTTP before старая0592 принимает5 из6 malformed inputs; короткий DRI уже400.
На F1 все6 получают400 и отсутствуют в storage. Корректные произвольные
component IDs сохраняются побайтно. Proof `jpeg-header-correction-20261018.json`
и31 raw gzip сохраняют неуспешные before и успешные after без подмены результата.

Новый короткий supervised runtime preflight F1/D64 завершён успешно:
4цикла,32 runtime inputs,6 supervisor inputs,18.640695guest seconds;
HTTP/photo/weather,2 requested outages,20 ROM counter crosschecks,5 valid
weather generations. Workload/guard exit0, supervisor complete, VM PID37548
отсутствует по CIM. Это не H10. Proof `jpeg-header-runtime-preflight-20261018.json`
и12 raw gzip; все566 full inputs после preflight повторно совпали.

Полный новый прогон запущен18 октября2026 в16:34:14UTC. Controller PID17200,
creation16:34:14.2973860Z, Win32_Process.Create return0, IsProcessInJob=false.
Wrapper `.build/run_jpeg_header_complete_full.ps1`; output
`C:/Work/yoRadio/.build/small-tv-functional/jpeg-header-complete-full-20261018`.
Freeze `jpeg-header-complete-full-start-20261018.json` содержит146 test files
+420 extra inputs. Отдельный snapshot
`.build/jpeg-header-qemu-complete-20261018`:46 files+manifest, побайтная копия
полного проверенного D64 snapshot. Launch record не является terminal pass.

Не менять `Small_TV/src`, firmware archive, ELF/resources/SDK или snapshot,
пока полный прогон работает. Писать новые наблюдения только в parity.
Не запускать дубликат из-за timeout чтения. Проверять controller-exit/report,
логи и точные OS identities; сначала сохранить любой terminal failure.

Прежний full5610592/D64 в small-tv-reset-display остаётся отдельным прогоном,
controller30244, creation16:04:24.3281330Z. Последнее прочитанное состояние:
photo_settings прошёл; terminal результата на момент записи нет.
Прежний H10 в small-tv-runtime-supervision остаётся на0592/D64, supervisor13800,
workload31224, guard27200, VM19212/SmallTV-beea78179836. Последний file-only
prefix165cycles; это не полные24h и не проверка F1. Его31+41+6 frozen registries
не менять, новых QMP/RSP clients к нему не добавлять. После готовности F1
потребуется собственный24h H10 этой точной пары; старый prefix сохранить,
если прежний прогон будет сознательно заменён.

CYD compatibility по-прежнему не принята: modem DPORT clocks исправлены,
но matching libphy register_chipv7_phy читает немоделируемый0x60033c00.
Не маскировать это all-ones MMIO или принудительным PHY success. Физическая
плата и H10 F1 также остаются непроверенными. Main не объединять.
