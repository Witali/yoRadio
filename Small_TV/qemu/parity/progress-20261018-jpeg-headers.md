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

## Новый H10 и намеренная замена0592

Новый F1/D64 H10 стартовал16:37:04UTC: supervisor23208
(creation16:37:04.1096700Z), workload6908 (16:37:04.8768140Z),
guard15664 (16:37:39.9558250Z), VM26708 (16:37:10.2562310Z),
`SmallTV-c3536427c9be`. Launch outside Windows Job подтверждён, после границы
tool call все4процесса повторно проверены CIM, префикс уже содержит рабочие циклы.
Регистры frozen32runtime+47snapshot+8supervisor/launcher могут пересекаться.
Не менять эти входы и566full inputs; не открывать дополнительных QMP/RSP clients.
Output `.build/jpeg-header-h10-20261018`, соседний `-supervisor`.

Прежний0592 H10 сознательно заменён новой production сборкой. До остановки
сохранены179полных циклов,8raw gzip, все31+41+6старых входов совпали.
Intent45fa4da3 закоммичен до остановки. В16:41:07UTC закрыты только4старых
process handles после проверки PID, creation и command; старые PID отсутствуют,
новые4PID живы. Дополнительных QMP/RSP clients0. Raw report не переписан в pass.
Первый stop attempt не остановил процессов: ISO string автоматически стала
DateTime при JSON parsing. Failure сохранён; DateKind String и read-only OS probe
подтвердили точные строки, после чего отдельная попытка завершилась успешно.

Файловый анализ полного старого journal — pending, не24h. Старый ad hoc freeze
не соответствует consumer schema анализатора; его rejected attempt сохранён.
Для нового H10 `jpeg-header-h10-audit-start-20261018.json` детерминированно
проецирует неизменный pre-launch freeze27b3da92 в consumer schema. Все32expected
hash, image/ELF/QEMU, duration и guard взяты из committed freeze до старта;
оригинал сохранён побайтно. Анализ нового префикса pending/start identities
прошёл, без изменения условий H10. Следующий анализ писать в новый файл.

## Desktop/mobile controls и проверка после работы в другой ветке

В отдельной `codex/small-tv-browser-controls-verify` добавлены только тесты и
документация, production F1/D64 не менялась. Коммиты346d97fc/b5e844c9 сохранены
и отправлены:281UI checks (236mutate/45cold),96UI POST и5storage/source checks;
Chrome155.0.8059.80,1280×900/390×844, все4темы/5GIF/3формата даты, флаги,
цвета/яркость, ночной редактор и настройки фото. После reload DOM совпадает
с GET API, новый cold process выполняет только чтение; raw ABI совпадает со
всеми ожидаемыми значениями. Независимая свежая подготовка flash подтвердила
байтовую неизменность областей внеNVS/raw, включая фото. Все25inputs совпали,
по1ROM boot на процесс, console/page errors отсутствуют, обеVM PID закрыты.
Proof `browser-controls-validation-20261018.json` +12gzip+12PNG в той ветке.
Снимки desktop/mobile просмотрены. Это отдельная частьH03/H04, не LCD/RF/H10.

После этого повторно проверены все566F1 и5610592 full inputs и32+47+8новых
H10 registries: совпадают. Все6точных OS identities live; новый H10 сообщил39
циклов, это только prefix. См. `post-browser-full-h10-checkpoint-20261018.json`
и6raw gzip. Не добавлять новые браузерные тесты задним числом в frozen full
и не объединять их src в эту ветку до terminal full/H10. Старый0592 journal
окончательно сохранён:182complete cycles,16pending events, periodic report181;
исходные running reports не превращались в terminal pass. H10 F1 продолжается.

## Независимые cold LCD и network-without-LCD

В test-only ветке добавлены5ebe5184/fffcba9b/8e55f70d и результаты46791f27/
d37d691b, отправлены в origin. Production F1/D64 не менялась.

- Display gate:20factory+20native новых процессов QEMU, все40полных RGB кадров
  побайтно совпали с фактическим factory setup frameACC588AB. Boot и protected
  flash проверяются отдельно, network везде not_run и HTTP forwarding выключен.
  12unit cases отвергают wrong/black/partial/stale/truncated frames, deadlines
  и stalled counter. Все62inputs совпали. Максимум factory5.496407guest/
  9.547host s, native0.460610guest/1.391host s после начала наблюдения; не hardware
  benchmark. Offline fresh preparation также подтвердила protected flash/media.
  Proof display-cold-20-validation-20261018.json +86gzip в той ветке.
- Network gate: собственный copied profile devices=[], default-peripherals=off,
  QOM lcd absent. Factory/native HTTP и свежий processed SNTP проходят до/после
  reset, без captures/ожидания дисплея. NTP1→2,4контрольныхHTTP200 после probes,
  SDK/wire maxdelta0.191694s, native STA/DHCP10.0.2.15/time_synced подтверждены
  matching ELF. По2ROM boots, no panic, все59inputs совпали. Display not_run.
  Proof network-without-display-validation-20261018.json +12gzip в той ветке.
- Все44временные VM identities (40matrix,2preflight,2network) закрыты по CIM;
  2PID уже переиспользованы другими identities, эти процессы не затрагивались.

После работы вновь совпали566/561full inputs и32+47+8H10 registries; все6точных
OS identities live. File-only canonical H10 audit:104complete cycles/1outage,
start_record_matches=true, statuspending;24h ещё не приняты. Checkpoint
post-independent-gates-checkpoint-20261018.json +7gzip. Его live raw files
копировались последовательно после анализа, а не атомарно; analyzed prefix hash
сохранён отдельно. Новых QMP/RSP clients к H10 нет. Ближайший шаг — продолжить
ожидание существующих full/H10 и проверить terminal отчёты. Standalone тесты не
внесены задним числом в frozen full. Current browser/control/cold/network source
в ветке small-tv-browser-controls-verify; src этой frozen F1 ветки не редактировать.
