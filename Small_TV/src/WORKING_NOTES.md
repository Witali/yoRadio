# Контекст работы над восстановленной Small TV

## Текущий приоритет — заводской образ, 2026-10-26

Текущая рабочая копия `.worktree/small-tv-storage-fixes`, ветка
`codex/small-tv-storage-fixes`, создана отa3ebb45d0. Локальная NVS component copy
исправляет upper I/O errors и temporary40Bleak;45vendor SHA/35copies/17TUs.
App8758/ELFDA1E сохранены и проходят236fault/retry,4OOM,compat/geometry/Page652,
native6300 и отдельные network/LCD checks. Old34CB/73BE оставлены неизменными в
small-tv-nvs-fixes. См. [NVS_STORAGE_FIX.md](tests/NVS_STORAGE_FIX.md).
Final proof reader59401/fd6be3 terminal0: before/after,8input+8overlay+5report
controls,6300native и network/LCD witnesses повторно проверены.
NEXT — TIM/null-completion/station+820/BSS/aliases; full NVS API/powercut и
deferred1–3/full/24h/hardware остаются открытыми. Shared SDK/QEMU не менять.

Новый analysis checkpoint в той же `small-tv-nvs-fixes`: полный Storage.init/read
qualified71factory/53native.18baseline+18reopen,460fault/retry+6six-sector cases
подтвердили BLOBfix, но верхние PageManager/Storage ещё скрывают134native I/O
ошибки (factory130). NEXT — исправить этот error propagation в новой локальной
NVS component copy с согласованными private cleanup signatures; сохранить
текущие 34CB/73BE before inputs. См. [NVS_STORAGE.md](tests/NVS_STORAGE.md).
Первый reader53022 повторил матрицу, но выявил JSON shape mismatch int/str keys
в retained_allocations; wire evidence не менялось, ключи нормализованы в fixture.
Ещё4malloc failures доказывают40Btemporary leak при втором BlobIndexNode OOM.
NEXT исправление должно очистить temporary list на всех выходах. Final reader
47042/2a9a74 terminal0: вся матрица повторена,8input+6report controls проходят.

Актуальная рабочая копия `.worktree/small-tv-nvs-fixes`, ветка
`codex/small-tv-nvs-fixes`, создана от7ebe96846. Factory-audit оставлена чистой
с неизменными before inputs. Локальный NVS recovery patch исправляет счётчики,
коллизии ключей/BLOB chunks и скрытые I/O errors. App34CB/ELF73BE собраны,
архивированы и проверены отдельно CPU/native/network/LCD gates. Детали:
[NVS_RECOVERY.md](tests/NVS_RECOVERY.md). Final proof reader62193/e7059c terminal0,
включая шесть report/runtime controls. NEXT — full Storage/multisector faults, затем TIM/null/
station+820/BSS/aliases. Оставшаяся цель не сокращается.

Рабочая копия `.worktree/small-tv-factory-audit`, ветка
`codex/small-tv-factory-audit`. Продолжать пользовательский пункт4; к1–3 вернуться
позже. Последний checkpoint и NEXT сохранены в конце этого файла. Ниже остаётся
исторический контекст; старые `running` JSON не подтверждают живые процессы.
Все12 прежних duration владельцев отсутствуют по CIM26Oct; прогоны не приняты.
NTH-ALLOC-FAIL исправлен: app4F2C / ELFEB20. Десять runtime ranges восстановлены
в transient read-only Ghidra: все453C.JALrefs есть,20negativecontrols pass.
Factory caller qualified как Page::load312B. Partial-record bitmap/purge repair
проверен652CPU executions. Следующий checkpoint воспроизвёл три настоящие NVS
ошибки; исправить их локально, сохраняя failing-before inputs. Затем расширить
fault/reopen проверки и TIM/null/lifetime/BSS/aliases. Текущие документы:
[NVS_RECORDS.md](tests/NVS_RECORDS.md),
[NVS_PARTIAL_REPAIR.md](tests/NVS_PARTIAL_REPAIR.md),
[FACTORY_NVS.md](tests/FACTORY_NVS.md),
[RUNTIME_METADATA.md](tests/RUNTIME_METADATA.md),
[NOTHROW_ALLOCATION.md](tests/NOTHROW_ALLOCATION.md),
[RUNTIME_CALL_GAPS.md](tests/RUNTIME_CALL_GAPS.md),
[RV32_DISASSEMBLY.md](tests/RV32_DISASSEMBLY.md),
[WIFI_EVENT_LIFETIME.md](tests/WIFI_EVENT_LIFETIME.md).

## Исторический checkpoint — heap metadata, 2026-10-25

Разработка продолжена в `.worktree/small-tv-memory-retention`, ветка
`codex/small-tv-memory-retention`, от `b4a851041`. Основной H10 остаётся в
`.worktree/small-tv-improvement-plan/.build/runtime-h10-main-20261025`, pin
main-9135/2DF90327. Не менять его runtime helpers, SDK, ROM, app/ELF, profile,
assets или frozen47files, не добавлять второй QMP/RSP client и не перезапускать.
PID19884/8080/18380/18652 с creationUTC сохранены в исходном early process record;
проверять реальные процессы, не один JSON status. Latest observation этой работы
подтвердила все четыре owner/creationUTC и362cycles, oneROMboot/noerrors;
это не terminal H10 pass.

Opt-in `-HeapTopology` квалифицирован отдельно: реальные C2 ROM и linked SDK
walkers, metadata-only allocation geometry, 11+8 новых tests, базовые16+25,
actual4+40cycles/22outages/352HTTP; replay46snapshots/92inventories и38negative
controls pass. Архив heap-topology-validation-20261025.json; детали
[HEAP_TOPOLOGY.md](tests/HEAP_TOPOLOGY.md). Factory/production binaries не менялись.
ROM контроль показывает возможный padding12B при тех же requested sizes, но
семь retained-loss warnings12..220B прежнего прерванного H10 пока не объяснены.

TCP gate **и inventory/attribution** готовы:33real-ROM host tests+25baseline,
actual4+40cycles/22outages/352HTTP,46observed snapshots и76semantic controls pass.
Schema7/-TcpTopology подразумевает heap topology; gate/layout/allocations/walk/
journal разделены. Qualified zero metadata prefix проверен по assembly текущего
ELF, unknown ABI и free/interior/alias pointers отвергаются до чтения. Shared
pbuf не удваивает capacity, busy остаётся явным пропуском. Source/app/QEMU не
менялись. Документ/оставшиеся gates: tests/TCP_HEAP_ATTRIBUTION.md; архив
tcp-inventory-validation-20261025.json (54refs/242895newgzipbytes).

Actual sampled states только LISTEN/FIN_WAIT_2: listener80B, closingPCB212B с
headers, TCP consumed80..504B, padding0 в этих46snapshots. Queued segments/pbufs
пока проверены real-ROM host fixtures, не pending guest traffic. Старые7flags
по-прежнему не объяснены. Windows переиспользовала2preflightPID послеterminal:
новый owner record различает original exit и исчезновение PID,8controls/run.
Ни чужие процессы, ни живые ВМ из-за этого не останавливались/перезапускались.

Следом matched длинные controls main/V8 с interval15/outageEvery60, controlled
queued traffic и unclassified deltas. Не заменять ими основной H10 и
не смягчать thresholds. Исправить отдельным изменением redundant cleanup, когда
driver уже закрыл ВМ: prototype получил connection refused, все owners отсутствуют.
Failed prototype и exploratory40 без early0 не включены в qualification. Полный
план, whole-image/fullsuite/fault/hardware scope остаются открытыми.

## Два действующих metadata controls — producer23b641680, 2026-10-25

В **этой** рабочей копии запущены отдельные `soak-main` и `soak-v8` в
`.build/tcp-inventory-qemu-20261025/`, каждый28800guest seconds/interval15/
outageEvery60/schema7. Main started13:40:41UTC, V8started13:42:23UTC; оба имеют
genuine `-start.json` наcycle0 и `-processes.json` со всеми4positive owners/
creationUTC. Pins:main2DF90327 иV8A5BE14C5, app9C1A83BD/ELF76B5CE37/ROM289CE00E,
frozen47files без изменений. Actualinputs перечислены в каждом start/report.
Не менять их, не перезапускать runs и не подключать второй QMP/RSP. Изменения
producer или новые firmware builds выполнять в другой task worktree; новые
offline analysis files/notes допустимы, если не меняют pinned inputs.

Main owners supervisor40876/workload10056/guard2560/VM37236;
V8owners27244/1044/10128/10776. Создание сверять **по файлам identity**, не только
PID. На13:47:42UTC CIM подтвердил все12originalowners трёхruns:mainH10362cycles,
soak-main13,soak-v8=9;oneROMboot/noerrors каждый. Это pending prefixes, не8h/24h
приёмка. Не складывать их длительности. Сопоставимые controls нужны для воспроизведения
старых7warnings на том же V8 и сравнения с main, а не для автоматического waiver.

После terminal анализировать каждый fulljournal отдельно через current
runtime_evidence.audit_run (extra roots C:/Work/yoRadio и C:/Work/QEMU-ESP32),
tcp_coverage/tcp_series и runtime_trend. Сохранять вывод вне run directories.
Для8h существующий analyze_runtime запускать с --diagnostic: это не H10.
В объяснении median-loss не складывать независимые component medians: выбирать
те же центральные observations, чтобы TCP+unclassified точно давали total loss.
Thresholds/warmup/phases прежние. Реальный queuedtraffic, idempotentcleanup и
whole-image/fullsuite/fault/hardware пункты остаются открытыми.

Актуальные решения и рекомендации для продолжения сравнения заводской прошивки
ESP32-C2 с собираемым C-проектом в `Small_TV/src`. История действий и результатов
сохраняется отдельно в [рабочем журнале](WORK_LOG.md). Обновлять этот контекст после
завершённых исправлений; при продолжении читать оба файла и проверять Git-статус.

Актуальная последовательность следующих этапов и критерии завершения:
[план улучшений](IMPROVEMENT_PLAN.md). CITY-REINIT закрыт scoped native/QEMU
проверками (app3E03); следующий этап — production JPEG/NOR, затем сетевой
lifecycle, аппаратные различия, full-image audit и приёмка окончательной сборки.
Старый H10 B50D не изменять.

JPEG/NOR checkpoint20Oct: portable core в storage/jpeg_nor.c/.h, вне production.
Один4096byte cache, sparse allowlisted extents, RMW только при0→1, проверка erase
и окончательных bytes, poisoned handle после I/O/verification failure.3000random,
83fault,7actual stores и6compiled negative mutations pass. Первоначальный
allowlist mutant выявил test gap конца последнего range; FIXED_TEST и failed
evidence сохранены. RV32 object1848/handle4352/cache4096/maxframe304; не whole
firmware RAM/stack. App3E03/TJpgd не меняется;6artifact tests pass. Следом runtime
immutable guard и journal/publication/cold recovery. Backing arrays должны быть
bounded logical subfiles одного scratch store, без per-file sector rounding или
независимых dirty caches общих sectors. Детали tests/JPEG_NOR_STORAGE.md.

Ownership guard checkpoint20Oct: storage/jpeg_guard.c/.h и tools/jpeg_guard_layout.py
подготовлены вне production. Verify all boot partitions/flash geometry, sector
ownership,27immutable payloads +64byte stamp в protected animation padding
0x28f720. Stamp нужен для changed allocation со старыми payloads; SHA known
payloads без marker этого не доказывает. Новый assets copy только для host gate,
production archive3E03 не меняется.49layout/84corruption/3050read/3010hash faults,
12generator invalid inputs+12controls и10compiled mutants pass. RV32 code1150,
const descriptors1448,maxsingleframe320, не runtime/link/whole stack.85rawproof;
6artifact checks pass;6old H10 original owners readonly-confirmed, VM не трогать.
Следом atomic journal invalidation/publication/cold recovery. ESP-IDF adapter
обязан enumerate ALL partitions, provide SHA и gate write capabilities только
после OK. Build должен связать stamped assets/header без потери photos/settings;
на неизвестной flash marker автоматически не записывать. Детали
tests/JPEG_OWNERSHIP_GUARD.md. Полная цель IMPROVEMENT_PLAN остаётся активной.

Journal checkpoint20Oct: storage/jpeg_journal.c/.h подготовлен вне production.
Два metadata banks полного snapshot пяти entries, durable invalidation перед
source/frame overwrite, commit page после erase/body verification. Publish и
каждый lookup требуют adapter flush/full physical SHA. Newest foreign IDs не
откатываются к старому matching bank; ties fail closed/MAX generation не wrap.
33400fault cases(128/256pages),769corruptions,6boot failures,12compiled mutants
и independent Python wire gate pass. Все ready recovery frames целые; прочие
4frames/protected bytes сохранны. RV32 code2976/const24/handle1032/open448
(оптимизировано704→448), не whole stack/runtime/link.118raw proof,6artifact pass,
app3E03/TJpgd unchanged;6oldH10 owners readonly-confirmed, VM не трогать.
Следом ESP-IDF authorization/SHA/budgets и shared scratch subfiles, actual upload
invalidation/source identity, matching assets build и codec integration.
Журнал сам не восстанавливает source JPEG после interrupted upload. Детали
tests/JPEG_CACHE_JOURNAL.md; цель/остальные пункты плана сохраняются целиком.

Transport checkpoint20Oct: storage/jpeg_transport +jpeg_espidf обеспечивают shared
physical read/program/erase/call/time budgets, revocable bounded ports/epochs,
monotonic pre/post/check deadlines и true ESP-IDF/PSA. Both physical+configured
flash sizes; full raw MD5 table/unknown flags +ALL SDK partitions cross-check.
31host cases/14mutants pass. Probe app6cb29771…(135504bytes) отдельно archived
firmware/development/small-tv-storage-probe;19inputs frozen BEFORE build и checked
after.4target variants/5final processes: actual RMW/cross-sector writes, fresh
process cold persistence, guarded rejection of unmarked/extra partition/raw flags;
whole4MiB comparison only35expected bytes. Earlier10successful processes also
stopped. Main3E03/TJpgd unchanged;6artifact pass,6oldH10 owners readonly-confirmed.
155raw proof:jpeg-transport-validation-20261020.json. Нет network/LCD/hardware
acceptance. Port memory borrowed: abort/drop all old borrowers before reuse;
RAM-only operations need explicit jpeg_transport_check, not just I/O callback.

Scratch checkpoint20Oct: byte-bounded files over ONE NOR cache выполнены.
Pinned upstream c85e6b… src/jmemmgr.c first_undef_row contract подтверждён actual
libjpeg/NOR pixels matrix:25resource/924lossless/48rich12-bit/18Pillow images,
16+12negative/4optional/18budget cases. Native16432assertions/5000random/134faults,
13compiled mutants;1227logical faults/36damaged recoveries/12transitions и
2238partial physical I/O errors с same-object recovery прошли. Small physical
calls exhaustive2010, четыре full-size sampled по57; silent read corruption не
обещается detect. Byte prefix/token IDs/checkpoints/cleanup без temp flush.
Pool allocator, stdio oracle и NOR bridge разделены по своим модулям. RV32
scratch code1240/handle576/token24/region32/frame48; не target runtime/UI link.
RichCMYK12 использует3780608program bytes/923erase calls на один tested decode;
нужен persistent RGB565 cache вместо повторного scratch decode при показе.
Current460800bound всё ещё только fixtures: расширить sampling matrix/rounded
coefficient capacity, не исключать редкие требуемые варианты ради старого лимита.
Source readonly C:/Work/yoRadio/.build/libjpeg-turbo-3.2.0. Production3E03/TJpgd
и targetprobe6cb29771… unchanged; SDK clean, frozen47files/H10 original six
owners проверены readonly. Proof jpeg-scratch-validation-20261020.json;
tests/JPEG_SHARED_SCRATCH.md. Далее sampling/budgets, source/upload journal
invalidation, actual source/frame SHA, matching assets build/native codec bridge
и HTTP/target memory/time/LCD/full/24h/hardware gates. Весь план остаётся активным.

Уточнение пользователя20Oct: объективно невозможный для устройства JPEG должен
быть отклонён с правильной причиной, вплоть до отказа до decode. В native codec
contract различать unsupported mode, malformed/truncated input, RAM/scratch limit
и I/O failure. Для resource refusal сохранить required/available; preflight по
реальным header/sampling/rounded allocations до backing writes, где это возможно.
Отказ по нынешнему reserved scratch не означает, что сам JPEG испорчен или что
все файлы этого coding mode невозможны. Нужны отдельные tests точной причины и
отсутствия опубликованного частичного cache. Новый контракт ещё не включён в UI.

Coefficient checkpoint20Oct по запросу уменьшить объём: codec/jpeg_coefficients
сохраняет DC two's-complement, AC sign/magnitude, complement both(zeroFF).
Exact signed16 bijection/INT16_MIN reserved negativezero. Pinned direct progressive
JBLOCK path, other backings raw.256byte buffer, same4KiB cache,15byte first-use
bitmap. Prepare FF once per sector/job, preserve initialized adjacent-file bytes;
reset bitmap on next job, keep physical flash. RichCMYK12 program3780608→2582784,
erase923→113; scratch460800/pool42275 прежние. FlatCMYK program460800→2048, но
erase0→113: не universal wear gain.19726488native assertions/4194304value-position
cases/983040refinements,7pure+4integration compiled mutants;18traffic cases,
standard JPEG matrix,1227logical+1573physical recoveries pass. RV32converter234code/
frame0/static0, не target execution/full app memory. Proof jpeg-coefficients-
validation-20261020.json; tests/JPEG_COEFFICIENTS.md. Main3E03/TJpgd/probe6cb
unchanged;6artifact/10map controls, SDK/H10 readonly. Следом precise error/resource
preflight и actual native source/upload/journal/cache/codec integration; весь план
сохраняется активным.

## Независимость проверок подсистем — 2026-10-18

Native decoder checkpoint20Oct: codec/jpeg_decoder.c/.h +jpeg_memory.c отделены
от CLI, public API без libjpeg типов для network/LCD. Bounded reader1024/oneRGB565
row, mandatory pre/post checkpoints, per-context allocator cap/backing. Wrapped
virtual requests считают actual padded rows; complete preflight before ANY open.
Typed unsupported/invalid/truncated/pool/backing/dimension/I/O/cancel/time/quota
diagnostics; required/available с known flag. Post-open deadline orphan очищается
после library abort без dereference freed owner/flush. Mutable jmp state в heap;
созданный JPEG object сохраняется после fail, recreate только если create failed.
63positive/7limits/10negative/1197faults/12transitions/6compiled mutants pass.
Rare legal4x4 CMYK needs524288 vsnative460800; positive oracle at262144pool/1MiB
backing не считать C2 fit. Host context5232+poolpeak42275(fullCMYK12); RV32context
4984, decoder2384code+311rodata/memory1870/color586, static writable0. Complete
relocatable binding148672code+120581rodata, libc/libgcc unresolved by design;
не runtime/full UI link/whole heap/stack/timing. Proof jpeg-decoder-validation-
20261020.json; tests/JPEG_DECODER.md. Main3E03/TJpgd/probe6cb unchanged;6artifact/
10map controls. Далее NOR/packed backend adapter для нового API, target execution,
actual upload/source/journal/cache/physical hashes/matching assets/UI integration
и full/final/hardware gates. Весь IMPROVEMENT_PLAN по-прежнему активен.

## План улучшений форматов изображений — 2026-10-19

По уточнению пользователя текущая задача — подобрать свободную библиотеку и
расширить поддержку вариантов обычных `.jpg/.jpeg`: progressive, grayscale,
CMYK/YCCK, различная разрядность и допустимые способы кодирования. Полное
покрытие не заявлять без матрицы поддерживаемых режимов и реальных тестов.
Отдельно измерить размер firmware, peak heap/stack и время декодирования наC2;
проверить сохранение требуемого заводского изображения и обработки ошибок.

**Отложенные улучшения по прямому запросу пользователя:** JPEG-LS, JPEG2000,
JPEGXL и WebP. Не включать их внедрение в текущую замену обычного JPEG decoder.
Для каждого формата последовательно выполнить:

1. Выбрать свободную библиотеку, проверить лицензию, зафиксировать version/commit
   и исходники; описать реальные поддерживаемые режимы и ограничения.
2. Измерить flash/RAM/stack/время для240×240 наESP32-C2. Учесть stream/seek,
   потребность во временном хранилище и последствия для износа flash.
3. Сделать отдельный codec module с единым bounded read/output interface.
   Сеть, хранение uploads и LCD transport не должны знать внутренности codec.
4. Добавить настоящие positive/negative fixtures и независимые reference pixels:
   lossless/lossy режимы по формату, размеры/края, повреждённый и усечённый input,
   metadata privacy, отказ памяти и повторный decode после ошибки.
5. Для WebP отдельно определить обработку alpha и анимации; кадры, длительности,
   disposal/blending и ограничения числа/размера кадров проверять явно.
6. Выполнить HTTP/storage/cold persistence и отдельный display gate, затем общий
   regression/длительный тест конкретной сборки. Только после этого включать
   формат в публикуемый список поддержки. Для будущих форматов не обещать
   совместимость только по наличию библиотеки или browser preview.

Текущий обычный JPEG — отдельная ветка `codex/small-tv-jpeg-library` от7f26262e.
Host-кандидат libjpeg-turbo3.2.0, pinned c85e6b905bf237038faa936dab160ebfc5da0344;
production B50D не изменён. Проверены25resource/924lossless/16invalid/4optional/
18budget cases и18неплоских JPEG с независимым Pillow. Патч сохраняет pixels:
не создаёт unused range table для direct lossless и уменьшает progressive
window только при явно выключенном smoothing у non-buffered клиента.
LosslessRGB16 pool755907→29980bytes; progressiveCMYK8 —45885pool+460800backing,
но2764800logical write bytes/decode. Это host temporary file, не готовый NOR
backend. 64KiB — только library pools, не весь RAM. 12-bit lossy всё ещё не
помещается:176345/347927bytes без лимита. Далее RV32 size/общий RAM/stack,
12-bit fixed tables, NOR-aware scratch, RGB565 converter/factory pixels,
I/O faults/reuse и отдельные HTTP/LCD/полный regression для новой сборки.
Документация/воспроизведение: tests/jpeg_library_probe/README.md. Proof:
../qemu/parity/jpeg-library-host-qualification-20261019.json,13raw artifacts,
983реальных fixtures. Полный T.81 и fit наC2 этим не объявляются.

RV32 измерение2026-10-19: codec154306bytes (144626text+9680rodata), ET_REL,
RV32IMC/ilp32/soft-float, GCC15.2.0, все8/12/16 scanline и arithmetic/progressive/
lossless roots сохранены, encoder удалён section GC. Это ещё не app flash delta:
libc/libgcc и adapter остаются unresolved. Stack diagnostics привязаны к object+
function через linker map; palette `fill_inverse_cmap`12 имеет24928byte frame,
обычный RGB565 output palette не требует. Не считать это runtime stack overflow
или доказанным запасом стека: output policy/config и call-chain/high-water tests
ещё нужны. Далее оценить12-bit fixed lookup tables45056+65536bytes в flash либо
вычисления с exact upstream pixels, затем полноценный link/RAM/stack/storage.
См. tests/JPEG_RV32_FOOTPRINT.md и jpeg-library-rv32-footprint-20261019.json.

Обновление2026-10-20: host12-bit RAM адаптация выполнена отдельными optional
flash-tables/compact-pools patches. Все38912actual upstream table entries exact;
48rich12-bit cases +12truncated, прежние25resource/924lossless/16negative/
4optional/18budget и18Pillow images проходят. RichRGB12 pool176345→37618,
progressive347927→45736; worstYCCK12progressive64869 +288000host backing.
RV32 decoder264666bytes (144394text+120272rodata); все5const symbols r/R,
110592table bytes, data/bss0. Это ещё не production link/общий RAM/stack.
Optional unlimited smoothing420 pool вырос1145bytes при exact pixels;
FIXED_TEST убрал неверную monotonic-memory проверку только этого control scope,
не hard cap. Сборочный helper исправлен: Git ceiling должен быть parent export,
иначе new files смешанного patch молча пропускались в sparse worktree.
Нужны NOR-aware backing, allocator/I/O fault/reuse, RGB565/factory parity,
полная сборка/heap/stack/HTTP/LCD/full/H10. См. tests/JPEG_FLASH_TABLES.md.
B50D19Oct full/H10 больше не live:20Oct исходные5identities отсутствуют,
host boot остаётся14Oct, terminal footer нет; cause unknown. Report178cycles,
journal179+5pending,3034.24guestsec; не24h pass и не firmware failure. Исходные
raw files сохраняются отдельно в baseline branch перед любыми новыми запусками.

На20Oct09:29UTC baseline-префиксы сохранены в bf3618f2 (86raw), новый actual
preflight8cycles/4outages прошёл с32inputs/guard/supervisor/cleanup. До повторного
запуска frozen581full и32+47+8H10 expectations закоммичены2996eea2/08e3366.
Новый full output: root/.build/small-tv-functional/jpeg-selector-complete-full-20261020;
controller29928 created09:22:52.898648Z. НовыйH10: baseline/.build/jpeg-selector-h10-20261020,
supervisor22184/workload32636/VM32580/guard18268, VMnameSmallTV-131b35021705.
Exact creations в baseline/Small_TV/qemu/parity/jpeg-selector-baseline-launch-checkpoint-20261020.json
(c8e56f932), оба launchers in_job=false. Они live на этой отметке, не приняты как
полный/24h pass. По-прежнему freeze baseline SRC/ELF/resources/SDK/snapshot и
не добавлять guest QMP/RSP clients. JPEG library меняется только в отдельном tree.

На20Oct host fault/reuse проверка JPEG завершена:1227инъекций allocations/open/
backing read/write/seek/input/output,36усечённых inputs и12format transitions.
После ошибки выполняется abort и reuse того же объекта; при36отказах самого
create —destroy/recreate.63разовых allocation failures восстановились внутри
pool manager, output pixels exact. Все backing files закрыты после abort,
final pools0; hard cap65536, peak этого стенда61421, session4096отдельно.
На новых binaries прошли прежние25/924/16/4/18 и48rich12-bit/12truncated/
38912table entries. Это host gate, не production/NOR/общий RAM. Детали
tests/JPEG_FAULT_RECOVERY.md; proof jpeg-library-fault-recovery-20261020.json.
Далее RGB565 module, NOR-aware backing/износ, production link/heap/stack и
HTTP/LCD/full/soak. Frozen baseline app/resources/SDK по-прежнему не менять.

RGB565 checkpoint20Oct: `app/media/color_convert.c` отделён от settings. Прежние
pack/expand exact factory:65536expand+3304pack actual RV32 inputs. Новый row
API2–16-bit gray/RGB/CMYK с явной полярностью, no heap/I/O, bounded buffers и
no-write-on-error:61host rows/549676samples,141RV32 rows,65host+68RV32negative,
66JPEG/18Pillow cases pass.540code+4rodata, frame96byte; это scoped module.
Row API поканеподключён, productionTJpgd остаётся. Новая compile C8FD/app1170032,
ELF368AB7B5/sourceE34BEBEB сохранена в firmware/development веткиlibrary.
5531native pass, отдельные LCD2factory+2native exact full frame и network
withoutLCD HTTP/freshSNTP до/после reset pass (62/59inputs unchanged).
Первый sandbox LCD QMP timeout сохранён failed, outside-sandbox retry отдельный.
Детали tests/COLOR_CONVERSION.md; proof color-conversion-validation-20261020.json.
Не переносить full/H10 B50D на C8FD. Далее libjpeg/NOR-aware scratch/износ,
codec adapter/privacy и общий production RAM/stack, затем HTTP/LCD/full/soak.

Storage capacity checkpoint20Oct: новый read-only tools/jpeg_storage_layout.py
проверяет manifest/partition/header/frame ownership нашего sanitized assets.bin.
Free:121gap+112animation tails+29media tail=262erase sectors. Measured backing
460800(113sectors)+metadata2+пятьRGB565cache115200(145sectors)=260, spare2(8KiB).
Все5полных photo slots, active animation sectors, weather/status slots и settings
защищены.30unsafe cases/4controls pass; +2animation sectors fits, +3fails.
Plan ID4508149b...51ad9ca6; exact sparse extents в proof. Это capacity/ownership,
не NOR backend и не универсальный JPEG bound. Runtime должен проверить immutable
resources перед writes, source/codec/layout invalidation, atomic publication,
physical erase/write counters и no periodic decode writes. Нельзя исключать
всю assets partition из integrity checks. См. tests/JPEG_STORAGE_LAYOUT.md и
jpeg-storage-layout-validation-20261020.json. C8FD app/source/SDK и baseline
full/H10 не менялись. Следующий implementation шаг —bounded sparse NOR store,
затем codec/cache integration и фактический общий heap/stack/full link.

Обновление2026-10-19: исторический F1 full завершился успешно,19automatic
groups и566frozen inputs совпали. Его старый publisher отдельно отвергает
24HTTP checks из-за прежнего списка22; исправление списка уже входит в56010f00.
У F1 H10 нет terminal footer/guard: все четыре исходные process identities
отсутствуют, два PID заняты другими процессами и не трогались. Periodic report639,
полный journal640циклов+4pending events,10855.93guest seconds. Cause unknown;
не считать это24h pass или доказанным firmware failure/отсутствием утечек.
Raw72gzip и отдельные OS/analysis/publication records сохранены в
f1-terminal-and-interrupted-20261019.json. Следующий прогон — exact B50D/85FC;
до него сохранять эти артефакты, старый F1 run не переименовывать и не продолжать.

Новая отдельная ветка `codex/small-tv-jpeg-selectors` продолжает409f4333.
Candidate: appB50D15A1 / ELF85FCCF00 / sourceFC337C9B / тот жеQEMUD64.
Из59production inputs изменены только tjpgd.c/.h. SOS сохраняет отдельные
DC/AC destinations каждого компонента; все136valid+32invalid RV32 cases проходят
вместо34/168 наF1. Pillow12.3.0 независимо проверил136малых и3upload fixtures.
JDEC124→128bytes, tail selector offset123, прежние member offsets неизменны.
App1170048bytes (+16 кF1), partition free365952; DEBUGoff/WARN.
Прежние107JPEG/35errors/7placements, inputs/DHT/header gates,5531host и6artifact
checks pass. Тот же HTTP harness прошёл26checks наB50D, включая3valid selectors,
2missing-table rejection, byte-exact downloads, cold/interrupted persistence.
Before F1 отверг все3valid и позже получил отдельный cold-stage timeout с
WSAEventSelect warning QEMU; этот failure сохранён. Новый full/H10 ещё не принят.
Proof: jpeg-selector-correction-20261018.json +42raw gzip;8decoder и5HTTP
consumer rejection controls pass. Все собственные HTTP ВМ завершены; старые
F1 full/H10 exact identities сохранены на17:59:39UTC, новых debug clients нет.
См. tests/JPEG_SELECTORS.md. Изменения помечены FIXED_FACTORY; IDCT/color не менялись.
Текущие F1 full/H10 находятся в прежнем frozen tree: не менять их inputs и не
добавлять QMP/RSP clients. Их результат не переносится наB50D candidate.
Исторический0592/full561 завершён:19automatic groups pass,561inputs неизменны,
published/verifier pass; proof в ветке codex/small-tv-reset-display,6d8816d9.

Отдельные F1/D64 browser gates повторены без изменения production/firmware:
photo23UI+6storage/source,27inputs; Wi-Fi93UI+18role/storage,26inputs.
Все inputs повторно совпали при публикации. Все восемь ВМ завершены;
один PID уже переиспользован другим процессом и не трогался.
Новые browser-*-f1-validation-20261018.json сохраняют собственный scope:
загрузка/Canvas/raw persistence отдельно от Wi-Fi/DHCP/SNTP и от LCD pixels.
Ожидаемый HTTP400/console при коротком пароле сохранён, не скрыт.

В той же test-only ветке отдельно завершены cold LCD matrix и network-without-LCD.
Cold matrix:20factory+20F1 процессов, все172800RGB bytes совпали с фактическим
factory setup frameACC588AB; boot и source-integrity также прошли, network not_run.
Все62inputs совпали;12unit cases exact-frame observer проходят и pin source SHA.
Сеть: LCD полностью убран из копии профиля, VM machine default-peripherals=off,
QOM lcd absent; обе прошивки прошли HTTP/SNTP до/после reset без captures.
NTP1→2,4HTTP200, SDK/wire maxdelta0.191694s; native DHCP10.0.2.15/STA/SNTP flags
подтверждены в matching ELF. По2ROM boots, panic нет,59inputs совпали.
См. tests/DISPLAY_COLD_BOOT.md и NETWORK_WITHOUT_DISPLAY.md. Это самостоятельные
QEMU gates, не physical power/RF/PWM или24h/H10; в live full/H10 их не добавлять.

Отдельная ветка `codex/small-tv-browser-controls-verify` продолжает F1 candidate
без production/firmware изменений. Реальный Chrome155 прошёл281UI +5storage/source
checks, включая обе ширины1280/390, все доступные настройки Clock/Advanced/Photo,
96настоящих UI POST и новый cold process без POST. Все25входов совпали,2ROM
boots по1напроцесс, console/page errors отсутствуют. См. tests/BROWSER_CONTROLS.md
и browser-controls-validation-20261018.json. Это частьH03/H04, не RF/physical/LCD/H10.
Full566 и новый H10 F1 живут в `small-tv-jpeg-headers`, их входы не редактировать.
H10 supervisor23208/workload6908/guard15664/VM26708, SmallTV-c3536427c9be;
не добавлять QMP/RSP clients. Старый0592 H10 сознательно остановлен, не принят.
Его финальный journal содержит182complete cycles/16pending events; last report181,
оба raw сохранены. Полные0592/full561 иF1/full566 пока проверяются отдельно.

Проверять сеть и дисплей отдельно, с собственными результатами и ошибками.
Wi-Fi association, DHCP, HTTP и SNTP относятся к сетевым проверкам; наличие
содержимого, геометрия, пиксельное соответствие и анимация — к дисплейным.
Успешная синхронизация часов не доказывает исправность дисплея, а готовый кадр
не доказывает работоспособность сети. Сценарий интеграции может выполнять обе
проверки, но обязан сохранять каждый результат, даже при сбое другой подсистемы.
Загрузка/перезапуск и неизменность исходных артефактов также имеют свои результаты.
В QEMU это `checks_by_subsystem` и `reset_subsystems`; сетевой timeout не
пропускает наблюдение дисплея. Повторно прошли19 ELF/SDK/SNTP checks и отдельно
9 проверок дисплея +3 проверки изоляции результатов. Ошибка первого запуска
сетевых unit tests связана с запрещённой записью временных файлов за пределами
workspace; повторный запуск с `--temp-root` внутри workspace успешен.

## JPEG segment headers — 2026-10-18

Текущая ветка `codex/small-tv-jpeg-headers`: appF1ADA8B4 / ELF91E26EB2 /
sourceF849F5BF, production correction2cd72264. Проверены133 случая заголовков:
14 корректных сохраняют пиксели,119 повреждённых отклоняются до декомпрессии.
Прежняя сборка принимала115 из119. Старые107 public JPEG,41 extra inputs,
128 DHT cases,5531 host C checks и6 artifact checks проходят. HTTP на одном
неизменном D64/harness: раньше5 из6 повреждённых upload принимались, теперь
все6 получают400 и отсутствуют в storage; custom RGB component IDs0/17/255
сохраняются побайтно. Evidence `jpeg-header-correction-20261018.json` +31gzip.
Это отдельные декодерные и HTTP проверки; полного suite/H10 этой F1 пока нет.
Full561 и H10 в прежних замороженных деревьях продолжают проверять0592/D64.
Не менять их входы и не подключать новых QMP/RSP клиентов к H10.

## JPEG DHT grammar — 2026-10-18

Текущий candidate в codex/small-tv-jpeg-uploads: app0592b510/ELFaea10675/
sourceD338a294. Из59production inputs изменён только tjpgd.c/create_huffman_tbl:
резервируется all-one prefix и проверяется baseline AC symbol. Factory
0x42011208 пропускает AC check; старый C принимал121malformed unused branches.
Новые128RV32 cases:4valid/124invalid pass; прежние41case проходят отдельно.
107public JPEG/35errors/7placements, native5531,
artifact6 pass. App1169936bytes (+32), app free366064; DEBUGoff, development
archive обновлён, releases не менялись. Specification — T.81 AnnexC/F.1.2.2.1.
Тот же photo_qemu.py наBC68 сохраняет три362-byte malformed JPEG (200/exists),
на0592 все400/absent. Все22candidate HTTP/storage checks pass, другие21checks
также проходят наbefore. Кадры/validation guards не маскировались. Seven report
mutation controls pass; DHT child обязательный внутри machine_jpeg_inputs,
общий contract используется runner/publisher/verifier. Все128fixture и6test/helper
hashes в before/after одинаковы, как и HTTP harness/helpers. Raw before failure,
положительные отчёты и3disassembly сохранены12gzip + jpeg-dht-validation-20261018.json.
Подробнее jpeg-dht-checks-20261018.md. Scope: table grammar, не arbitrary JPEG
compliance, физическая плата, H10 или full acceptance новой сборки.
Старые live full533/H10BC68 не менялись, подтверждены живыми. Их будущие
terminal results не подтверждают0592; нужен новый полный прогон этого candidate.

## Browser Wi-Fi setup — 2026-10-18

Ветка codex/small-tv-browser-wifi продолжает browser-photo21943e31 и содержит
перенесённый metadata fix H10 (b1bba736, original c0fc3cb3). Production/archive
не менялись: BC68/4FDE/source5586/QEMU20B. Новый настоящий Chrome155 gate
прошёл93browser+18storage/role checks;25inputs совпали. Три собственные пары ВМ
проверяют discovered SSID, буквальное имя `manual` и manual entry после реального
пустого scan с выключенным внешним AP. Cancel/empty prompt не отправляют POST;
короткий пароль получает400, сохраняя444raw bytes/AP role/один ROM boot.
Успех: about:blank, STA DHCP192.168.43.15, SNTP и новый cold process с теми же
credentials. SDK UTC сравнивается с wire timestamp с учётом HRT offset/correction,
расхождение всех шести наблюдений менее27ms. Это не точность реального кристалла.
Переключатели страницы сверены с `/getsettings`;390×844 без горизонтального выхода.
Proof browser-wifi-validation-20261018.json +13gzip+2PNG. Все6VM PID отсутствуют
по CIM; по2ROM boot в setup+intentional restart, по1в cold, panic нет.
Два failed harness runs сохранены: ожидание отсутствующего loading overlay;
затем неверная жёсткая нижняя граница для приблизительной RTC/lifetime оценки.
Ни один не объявлен firmware failure или passing acceptance. Этот standalone
gate не закрывает весь H03, desktop/physical RF/WPA/captive portal или H10.
Входы live full533 и H10 не менялись. File-only H10 prefix58cycles/31inputs
остаётся pending; текущий полный прогон дошёл до photo_settings pass.

## AP memory comparison — 2026-10-18

Browser/Canvas/photo gate добавлен в отдельной ветке codex/small-tv-browser-photo,
production C и development firmware неизменны (BC68/4FDE/source5586, QEMU20B).
Настоящий Chrome155 прошёл23browser+6storage checks: рамка мышью shrink/grow,
RGB выбранных blue/yellow областей,240×240безAPP/COM, Cancel/Escape,390×844,
noise47773bytes/12actual multipart chunks, HTTP/raw bank equality и новый cold
процесс с точными обоими JPEG. По одному ROM boot на процесс; console/errors=[],
26inputs unchanged. Proof browser-photo-validation-20261018.json +5gzip+2PNG.
Это standalone gate, не часть уже замороженного full533 и не H10/physical test.
Браузерные REPL инструменты дали kernel-assets os error3; использованы уже
установленные headlessChrome/Playwright через CLI, без сторонних загрузок.

Текущий H10: appBC68/ELF4FDE/QEMU20B стартовал12:30:54UTC в независимой
ветке codex/small-tv-h10-ap-services. Supervisor23548, workload5036, guard22392,
VM18128/SmallTV-f65d8d848a9a. Все4идентичности подтверждены CIM;31runtime и11
snapshot QEMU inputs совпали. Не открывать второй RSP/QMP к этой ВМ и не менять
входы. Start proof ap-services-h10-start-20261018.json; полный H10 ещё pending.

Перед этим 8-cycle supervised preflight BC68/20B прошёл:64HTTP/4outages,
9valid weather generations,36ROM checks; workload/guard обаexit0 безpanic/boot reset.
Проверенный старый26C6/B44 H10 намеренно заменён после committed intent2f9f81e3:
prefix214cycles/31inputs сохранён, оригинальный supervisor failed/-1 и cleanup0
не переписаны в pass. Все4oldPID отсутствуют. См. ap-services-h10-superseded-20261018.json.

Полный BC68/20B suite отдельно идёт в codex/small-tv-flash-full (controller10836,
startce6a1254), заморожены533inputs. Production/UI/ELF этих деревьев не менять.
Контекст active full обновлять в его parity journal, который не входит в533.

За время flash audit завершился старый frozen full app6324/source53D3/B44:
terminal_passed в12:10:15UTC,19groups pass, hardware/browser/soak not_run.
Все273inputs повторно совпали; proof apsta-full-completed-20261018.json +4gzip.
Это исторический результат, не full acceptance26C6/BC68/нового flash QEMU.
Суточный26C6/B44 H10 остаётся pending: file-only diagnostic не открывал RSP/QMP.

Flash audit QEMU сохранён в codex/flash-write-audit, commit0860e568d4.
Тестированная final RISC-V20B / Xtensa1845: общее NOR ядро исправляет WEL,
page wrap, erase alignment/protection; C2 GD25Q32 имеет типовые virtual WIP
timings и byte dummy/QE; C2/C3 cache refresh больше не читает старый backing.
Все11QTest groups на ESP32/C2/C3, matrix17rows/476checks и modular peripherals
pass. Подробный scope/raw evidence: QEMU docs/ESP_FLASH_WRITE.md и
docs/validation/flash-write-validation-20261018.json.

Важное оставшееся ограничение CYD: короткие25hostseconds не доказывают завершение
boot. Длинный60s candidate и same-toolchain pre-change NOR control оба достигают
assert esp_phy_enable phy_init.c:332; после reboot есть и cache errors. Полную
CYD compatibility не принимать. Этот дефект воспроизведён с исходным NOR blob,
его не скрывать успешными flash unit/module и C3 OLED checks. Старый installed
Xtensa control дополнительно отказывает на QIE. Все UART/failed reports сохранены.

Raw persistence observer исправлен отдельно: erased/partial field не вызывает
ASCII exception, но остаётся pending до bounded timeout. Native проверяет ELF
dirty flag до и после чтения raw key, чтобы холодный stop не прервал запись после
первой страницы. Все5unit controls обязательны для suite/publisher/verifier.
15factory+15native regional keys, максимальные city64/country19, cold boot и
NVS v1→v2 migration прошли на промежуточном QEMU9DA. Окончательный20B прошёл
initial setup16factory/21native checks и отдельную station isolation.
Различие QEMU версий указано в flash-persistence-observer-validation-20261018.json;
это scoped proof, не full/H10 acceptance BC68. Firmware C при этом не менялся.

Перед следующим полным прогоном: AP service candidate BC68/ELF4FDE уже собран и
сохранён в development archive. Production меняет только services.h,
time_sync.c и weather.c: при фактическом AP режиме создаётся weather cache/mutex,
но не station-only time_sync/weather_http tasks. Factory AP branch
0x42009032..0x42009052 остаётся в setup loop; штатный STA с ожидающим DHCP
сохраняет оба worker. Перезагрузка при смене режима уже предусмотрена.

Scoped gates прошли на прежнем B44: 50 platform cases/1 182 393 checks,
native5531, artifact6; оба новых AP теста падают на прежних двух service
модулях при неизменном финальном harness. Реальные AP настройки через6HTTP
маршрутов не меняют cache/time state или setup frame; все четыре factory/native
RGB кадра совпали. В AP ready heap86604→98112bytes (+11508), tasks11→9;
сравнение относится только к ready, последующие workloads различаются.
STA control: 8cycles/64HTTP/4outages/9weather generations; исходная настройка
Wi-Fi и холодное сохранение также прошли. Proof и8gzip:
ap-services-validation-20261018.json. Новый mandatory AP gate включён в suite,
publisher и verifier, но полный прогон BC68 ещё не запускался.

Старый frozen full app26C6/B44 завершился terminal_failed на raw observer:
ASCII decode byte0xff при ожидании максимальной country/city записи. Все273
входа повторно совпали. Ошибка и исходные отчёты сохранены как failed в
network-roles-full-failure-20261018.json; успешным этот прогон не считать.
Проверка самой flash модели QEMU идёт в отдельной ветке codex/flash-write-audit.
Не менять входы продолжающихся старых full/H10 и не приписывать им BC68.

Теперь измерен и AP режим на app6324 против26C6, один B44/SDK/settings:
по4настоящих HTTP scan и4setup pages,9read-only snapshots на vTaskDelay.
Оба workload pass,24input hashes каждого совпали; по36ROM counter crosschecks,
одинROMboot безpanic. Задач12->11, исчезла только wifi_fallback. Ready free heap
83928->86604bytes, gain2676; медиана парных phase gains2672, range2332..4596.
Медианы отдельных free series отличаются на2660. После HTTP временные buffers
могут ещё жить: эти числа не заявляют идентичную allocator instruction phase.
Proof network-roles-ap-memory-20261018.json +2rawreports+2UART+one-off probe source gzip.
Это короткое измерение ресурсов, не долгосрочная стабильность или H10.

Историческая точка до этого изменения: services_start
создаёт time_sync(3072stack) и weather_http(8192stack) также в AP. Они наблюдались
в обоих task sets. Перед оптимизацией сравнить AP branch factory app_main,
браузерное время/часовой пояс/cache init и доступные setup HTTP handlers;
по одному отсутствию STA нельзя объявлять эти задачи ненужными или удалять их.

## Повторяемый netif gate — 2026-10-18

Активная новая ветка codex/small-tv-netif-observer в одноимённой .worktree,
basefe592a8b. Production C и development archive26C6 не менялись. Добавлены
netif_observer.py, netif_roles_qemu.py и общий evidence contract; suite/publisher
теперь требуют этот gate. Native head/node/if_key/settings берутся из DWARF
текущего ELF, factory addresses привязаны к dump5321 и прежним assembly exports.

Реальные factory/native STA+setup-with-retained-credentials потоки прошли,
setup HTTP scan сохраняет единственный AP netif. Factory STA создаёт собственные
публичные credentials; его NVS скопирован в обе setup fixtures. Native использует
WIFI_STORAGE_RAM и сам не пишет sta.ssid/sta.apinfo, поэтому требование одинаковых
SDK write side effects было ошибочным для этой ограниченной netif проверки.
Raw failed v1/v2 probes сохранены в .build, успешный v3 отдельно. NVS-парсер5.5.4
проверяет CRC header/data и два публичных payload; никакой owner NVS не копируется.

Negative app6324 на том же B44 и byte-identical observer воспроизвёл AP+STA в
station. Исправленная26C6 имеет ровно STA или AP;27inputs каждого report неизменны.
7offline observer tests и17evidence rejections прошли. Интеграция в общий suite
добавлена здесь; два уже идущих frozen full run не получают новый gate задним
числом. Их входы и H10 не менять; полный автоматический acceptance пока pending.

## H10 replacement запущен — 2026-10-18

Intent был закоммичен f97d8739 до stop. В11:13:48 UTC через повторно проверенный
handle остановлен только прежний workload23672; supervisor сам закрыл guard/VM,
cleanup exit0. Исходный supervisor outcome failed/exit-1 сохранён без подмены.
Файловый audit префикса:200полных циклов/3292.590422guest s/1605HTTP/3outage,
31input совпал, UART2447bytes/одинROMboot/безpanic. Это не24h и не pass;
4pending journal events сохранены. Raw7gzip и manifest:
network-roles-runtime-superseded-20261018.json. Все4oldPID отсутствуют в CIM.

Новая frozen26C6/FE9B/B44 ВМ запущена11:14:24UTC на86400guest s,interval15,
outageEvery60. Supervisor21928, workload20664, guard35272, VM7412; проверены
CIM PID/creation/command всех4,31runtime inputs,11frozen QEMU files и launcher
hashes. Start proof network-roles-runtime-start-20261018.json; это running start,
не passing H10. File-only analyzer подтверждает соответствие start record.
Не подключать второй RSP/QMP observer к этой ВМ и не менять её frozen inputs.

### Подготовка замены — историческая запись11:13UTC

Создана frozen worktree .worktree/small-tv-h10-netif-roles, branch
codex/small-tv-h10-netif-roles atf0375b14. В неё скопирован совпадающий ELFFE9B
и11файлов QEMU B44 (aab05d5de6) в .build/runtime-qemu-b44-frozen-20261018.
Её detached preflight завершён: supervisor/workload/guard pass, exit0,4cycles,
32HTTP,2outage,31unchangedinputs. Proof network-roles-runtime-preflight-20261018.json.

До остановки старого H10 записан network-roles-runtime-supersede-intent-20261018.json.
В11:13:01 UTC все4oldPID/creation/command и31input совпали;196cycles/
3267.751527guest s/1573HTTP/3outage. Причина замены — новая production26C6 и
QEMU B44; старый prefix не24h. На момент intent следующий шаг был: проверить и остановить
только old workload23672 с creation10:06:56.5451710Z через удержанный handle;
supervisor17788 должен сам закрыть guard28632 и VM35664. Сохранить его terminal
failed outcome как intentional supersession, raw report/events/UART не переписывать.
Затем запустить86400guest s/interval15/outageEvery60 из новой frozen worktree
в .build/netif-roles-detached-24h-20261018. Исполнение и evidence записаны выше.
Не менять ни одну frozen копию до terminal её workload/full run.

## Полный network roles regression — 2026-10-18 11:07 UTC

Новая app26C6 / ELFFE9B / sourceD628 сохранена и опубликована в16c277ed.
Полный набор без Skip идёт в .build/small-tv-functional/netif-roles-integrated-full-20261018.
Controller PID28968, creation11:07:17.1947460Z, вне Windows Job; после выхода
launcher PID/creation/command совпали. Заморожены121tests+152extra inputs=273,
после старта все хеши совпали. Не менять входы до terminal! Controller пишет
controller.log/controller-exit.json. Start proof network-roles-full-start-20261018.json.
SDK доступен через ignored .idf junction к основному SDK: при cleanup удалять
только запись junction, не целевой каталог. История коротких проверок ниже.

Прежний full app6324 PID2448 ещё работает, дошёл до реальных weather/field HTTP.
Его273 inputs неизменны. H10 app6324 на A74 тоже жив:4 личности и31input совпали,
prefix180cycles/3005.344746guest s/1445HTTP/3outage. Это не новые26C6 acceptance
и не24h. Для новой26C6 нужен собственный frozen H10; до его запуска сохранить
явный intent и prefix прежнего H10, не терять его evidence и не останавливать
процессы без проверки PID/creation/command. Текущие результаты — scoped only.

## Текущая ветка network roles — 2026-10-18

Работа идёт в `.worktree/small-tv-netif-roles`, ветка codex/small-tv-netif-roles,
base9c8a6747. Текущий full APSTA regression в другой рабочей копии остаётся
замороженным; его 273 входа и H10 app6324 не менять.

По factory netif observation новая C-инициализация создаёт только STA или AP,
конфигурирует только выбранный Wi-Fi interface, captive DNS запускает только
для AP, wifi_fallback task — только для STA. APSTA driver scan сохраняется
без STA TCP/IP netif. Вынесена configure_access_point_netif; network_init получил
FIXED_RECONSTRUCTION. Это один network module, прочие категории не менялись.

Новый host negative control на прежнем C упал в wifi_setup: создавались оба
netif. После изменения прошли 48 платформенных cases / 1 182 327 проверок,
включая AP scan без station retries, отдельные ошибки AP/STA allocation и
station retry supervisor failure. Логи .build/netif-roles-platform-{before,after}-20261018.log
в основном репозитории. Пока это не доказательство реальной экономии RAM или
SDK/QEMU корректности; обязательны реальные AP scan/configure/reboot->STA,
DHCP waiting/failure, idle heap/tasks before/after и полный regression.

Production build session58887 завершён exit0; development archive сохранён.
App26c6ca74940dbfa5f27b67a308515a2901bcdab2968e2a45954055b59cbe1234;
ELFfe9be9577dd82294b86710e61e25f5d1f54f92d4bf78dce8b3d578e9fc34adc9;
source d62847d868de1b6cc806fbc8f0ff6426405a55200d3f7d0578d9db508bbce734.
App1 169 872 bytes, free366 128; DEBUG off. Это новая VM test build, физические
платы не прошивались. Старый полный run и H10 по-прежнему app6324.

Независимые короткие проверки завершены exit0: actual AP scan/configure/reboot->
STA/persistent relaunch/reset (21 проверка), четыре delayed-DHCP/missing-AP
сценария factory+новая C и 26 rejection controls. До/после runtime по8 циклов,
64 HTTP,4 outage,69events на одном B44 и одинаковом sdkconfig прошли.
В STA после изменения нет captive_dns task (11 задач вместо12); free heap
при ready87876 ->92036, медианный gain9 snapshots4160 bytes. Это не H10 и
не AP RAM measurement. Все31 runtime inputs каждого workload повторно совпали.

Production inputs59, изменён ровно app/network/wifi.c. Bootloader BIN hash
поменялся из-за SDK compile date/time; весь остальной образ совпал после
проверки checksum/SHA и маскирования только24байт date_time и33байт integrity.
Raw bootloader hashes не выдавать за одинаковые. Scoped report и5rawgzip —
network-roles-validation-20261018.json. Полный regression новой26C6 ещё нужен;
старый full и H10 на6324 не переписывать как его приёмку.

Factory netif scratch prototype заменён reusable netif_roles_qemu.py в ветке
codex/small-tv-netif-observer; проверенные flows и ограничения описаны выше.
Native layout берётся из ELF/DWARF, factory offsets привязаны к dump5321.
Runtime heap снимать read-only Observer на vTaskDelay, а не в случайном allocator
critical section. Baseline app6324/ELF9E2C сохраняется в .worktree/small-tv-ap-http-ready;
QEMU B44 общий. История замены H10 и его исходный prefix сохранены отдельно.

## Заводские netif в APSTA — уточнено 2026-10-18

Read-only проверка списка SDK netif в двух настоящих factory VM прошла.
STA mode=1: ровно WIFI_STA_DEF и HTTP200 clock page. Setup mode=2: ровно
WIFI_AP_DEF и HTTP200 configure page, GOT_IP event=false. Для второго запуска
сохранён настоящим драйвером синтетический SSID: namespace nvs.net80211,
keys sta.ssid/sta.apinfo, CRC header/data совпадают. Отсутствие STA IP здесь
не объясняется потерей сохранённого SSID.

SDK netif list 0x3fcc3c0c и if_key+92 подтверждены инструкциями 0x42036770 ->
0x420352ee -> 0x42034e32 -> 0x42036f98 и ESP-IDF v5.5.4 primary sources.
AP init вызывает create_default_wifi_ap (0x420459d6), STA init — отдельную
create_default_wifi_sta (0x42045a7a). Factory APSTA connect остаётся L2-вызовом
без STA netif/DHCP пути. Нынешняя idle STA нашей настройки не теряет показанный
factory STA-IP функционал. Полную идентичность SDK внутренних состояний не заявлять.

Отчёт factory-netif-observation-20261018.json и raw gzip; scratch prototype
.build/probe_factory_netifs_20261018.py перенести в воспроизводимый тест после
terminal текущего full run. Сейчас не менять 273 frozen inputs. Есть кандидат
оптимизации: C network_init создаёт оба netif и captive DNS во всех режимах;
фабричный код создаёт только нужный netif. Проверить wire behavior и память
перед отдельным изменением, не называть это доказанной ошибкой прошивки.

## Полный APSTA regression запущен — 2026-10-18 10:41 UTC

В `.build/small-tv-functional/apsta-integrated-full-20261018` идёт полный
host/machine/QEMU набор без Skip. Изолированный controller PID 2448 создан
10:41:21.7725480Z, вне Windows Job; после завершения launcher его PID/creation/
command повторно совпали. Заморожены 121 test file и 152 extra inputs (273),
после старта все хеши проверены. App6324/ELF9E2C/QEMU B44; source QEMU aab05d5de6,
yoRadio355cf73e. Контроллер пишет controller.log и controller-exit.json; ждать
именно этот процесс/его terminal record, не запускать новый из-за тишины stdout.
Входы до terminal не менять. Start checkpoint — apsta-integrated-full-start-20261018.json.

SDK доступен через ignored `.idf` junction на основной SDK: при будущей очистке
удалять только запись junction, не обходить и не удалять его целевой каталог.
Длительный H10 отдельно работает на frozen A74: проверены четыре личности и
31 вход; префикс 103 цикла / 1737.66437 guest s, 832 HTTP / 1 outage. Суточной
приёмки нет; этот префикс не подтверждает новую модель QEMU B44.

## APSTA investigation — 2026-10-18

Раннее восстановление внешнего AP воспроизводимо блокирует factory setup HTTP
на прежнем QEMU A74. Факторный контроль отделил возврат сети от времени HTTP.
Подключённая STA подавляет AP beacon в общей peer state модели; начатый AP
портит последующую STA/DNS. Это воспроизведено через DMA на C2 и C3 (4 subcase).
Исправлено в QEMU `.worktree/small-tv-apsta`, коммит aab05d5de6, отдельный
executable B44D1A05. Пять тестов / 10 C2/C3 subcase прошли; те же входы дают
10 ошибок на прежнем A74. Прошли 12 прежних network tests, модульные SPI/I2C
и запуск неизменённых CYD/C3 OLED. Оба delayed-DHCP и оба missing-AP сценария
настоящих прошивок прошли с неизменными входами; 26 rejection controls прошли.
Scoped report — apsta-validation-20261018.json, семь исходных отчётов в gzip.

Прежнее `ap_active=mode!=1 && boots>=2` было эвристикой и не доказывало AP init.
Реальный маркер окончания init — factory byte 5 после сканирования. AP handler
также вызывает esp_wifi_connect на STA_START; его GOT_IP не меняет byte на 2.
Прежнее утверждение «в mode=2 STA не подключается» этим byte не доказано.
В отдельном сбойном probe оба HTTP недоступны и event bits=0, так что успешную
STA тоже не утверждать. Подробности и следующие проверки — tests/APSTA_INVESTIGATION.md.
Отрицательные raw отчёты сохранены в apsta-before-20261018.json и четырёх gzip.
Observer теперь отличает mode/restart от конца AP init (state 5) и читает
отдельный APSTA GOT_IP event; false byte 2 больше не единственное свидетельство
этого missing-AP case. Раннее восстановление сети в тесте сохранено. Исходная
прошивка и app6324 не изменялись. Старый full regression остаётся failed;
следующий шаг — полный неизменный прогон с новой QEMU моделью. DEBUG-off отдельно
не проверялся на aab05d5de6; H10 продолжает использовать прежний frozen A74.

## Текущее состояние — 2026-10-18

- После чистки запущен НОВЫЙ detached H10 текущей 6324/9E2C/53D3:
  `.worktree/small-tv-h10-wifi/.build/wifi-detached-24h-20261018`, с 10:06:56 UTC,
  86400 гостевых секунд, интервал 15, AP outage каждые 60 циклов. Запись —
  `wifi-detached-24h-start-20261018.json`, все 31 входной хеш совпали;
  начальный file-only аудит pending/start_record_matches=true. CIM identities:
  supervisor 17788, workload 23672, guard 28632, VM 35664 (SmallTV-8d278f099216).
  Все четыре повторно сверены по времени создания и команде. Supervisor
  запущен вне Windows Job через проверенный launcher. Между turn нужно снова
  сверить реальные процессы и prefix; только status=running не доказательство.
  Не менять frozen H10 checkout/bundle, supervisor/guard и launcher-модули.
  Суточной приёмки пока нет. Полный regression остаётся terminal_failed на
  factory setup HTTP; после чистки исследовать это отдельно, не повышать timeout
  без понимания причины и не подменять проверку ответа страницы флагом AP.

- По запросу пользователя применён git-repo-cleanup. Удалены 12 завершённых
  worktree Small_TV, их текущие коммиты включены в origin/main. Все ignored
  файлы сохранены и побайтово проверены в `.build/worktree-retention/20261018`;
  локальные ветки оставлены. Прежний amended observer `4d2e9555` закреплён в
  `codex/recover-runtime-observer-pre-amend` и incremental bundle. Отчёт —
  `worktree-cleanup-20261018.json`. Старые абсолютные пути удалённых worktree
  теперь отсутствуют: для воспроизведения исторического run потребуется архив.
  Сохранены H10 Wi-Fi и runtime-launch; остальные семь worktree с работой
  ESP8266/C3 и SDK не трогались, staged diff каждого совпал с исходным аудитом.
- В QEMU удалена только дополнительная `.worktree/small-tv-wifi-link`;
  установленный RISC-V/Xtensa executable побайтово прежний, main 2a593f8d.
  Локальные артефакты и Git bundle двух Meson-зависимостей сохранены в его
  `.build/worktree-retention/20261018`. Старый amended `158b65e28a` оставлен
  в `codex/recover-wifi-link-pre-amend` и incremental bundle. Его отличие от
  принятой версии — устаревший QOM path в двух строках README; не сливать его.
  Приватный retention-каталог исключён точным правилом в local info/exclude;
  исходники и tracked ignore rules QEMU не менялись.

- Полный прогон session 92602/PID 22772 завершился неуспешно в 09:51:51 UTC.
  Все 18 host/machine/profile групп прошли; QEMU прошёл boot/reset/SNTP обеих
  прошивок и оба delayed-DHCP сценария, затем factory missing-AP case не дождался
  setup HTTP. До ожидания заводская прошивка уже имела mode=2 в RAM/flash,
  AP active, boot=2; исполняемые области не изменились. Это ещё не установленная
  причина ошибки и не доказанное расхождение нашей прошивки. Все 195 входных
  хешей повторно совпали. Отчёт — `wifi-integrated-full-failed-20261018.json`
  и четыре исходных отчёта в gzip. Старую публикацию этим run не заменять;
  после чистки исследовать HTTP-готовность заводского AP и повторить этот case.

- Ветка `codex/small-tv-runtime-launch` добавляет независимый Windows launcher:
  `tools/start_runtime.ps1` и `runtime_process.psm1`. CIM запускает скрытый
  supervisor с CREATE_BREAKAWAY_FROM_JOB; реальная проверка ядра подтверждает
  отсутствие Job. Восемь интеграционных проверок прошли: ребёнок жив после
  выхода родителя, argv с пустыми/Unicode/специальными значениями точен,
  завершение получено, ошибки запуска и дубликат имени отклонены. Только
  проверенный процесс может очищаться после ошибки; PID reuse учтён.
  Это инструмент длительного тестирования, не изменение производственного
  приложения и не суточная приёмка. В main не переносить до завершения
  текущей полной регрессии: новый тест меняет её зафиксированный набор файлов.

- Полный прогон текущего образа 6324 запущен в 09:41:53 UTC: session 92602,
  PID 22772, `.build/small-tv-functional/wifi-integrated-full-20261018`.
  После старта проверены все 195 входных файлов (102 тестовых и 93 остальных),
  app 6324/ELF 9E2C/QEMU A74. Запись старта —
  `wifi-integrated-full-start-20261018.json`. До завершения не менять эти файлы;
  перед публикацией повторить проверку хешей. Успешного полного результата нет.
- H10 от 17 октября прерван: оригинальные supervisor/workload/guard/VM
  отсутствуют. PID 34036 уже переиспользован новым machine oracle; это другой
  процесс, останавливать его нельзя. Последний supervisor сообщил 89 циклов;
  независимый аудит журнала подтвердил 90 полных циклов и 1486.761343 гостевой
  секунды, 31 неизменный входной файл, 91 актуальное поколение погоды. Один
  ROM boot, panic нет; 24 часа, окна памяти и terminal guard не достигнуты.
  Windows не перезагружалась с 14 октября. Причина исчезновения процессов
  неизвестна; старое status=running не является доказательством работы.
  Свидетельства и исходные журналы сохранены в
  `wifi-runtime-interrupted-20261018.json` и трёх gzip. Старый каталог не
  возобновлять; перед следующим H10 проверить способ независимого запуска.

## История возобновлённой работы — 2026-10-17

- Новый H10 образа 6324 начат в 19:45:25 UTC в `.worktree/small-tv-h10-wifi`,
  ветка `codex/small-tv-h10-wifi`, коммит `7f7dc110`. Зафиксированы 11 файлов
  QEMU (A74/6B7F). `wifi-runtime-24h-start-20261017.json` связывает 31 входной
  файл, ELF 9E2C и исходники 53D3. Длительность — 86400 гостевых секунд,
  интервал — 15 секунд, отключение AP — каждые 60 циклов. PID: supervisor
  21336, workload 34036, guard 27092, VM 9760. Время создания взято из CIM.
  При сохранении прогресса PID, время создания и команды всех четырёх процессов
  повторно сверены: процессы работают. Начальный аудит — pending, запись старта
  соответствует входным файлам. Суточный результат ещё не получен.
- Короткий прогон образа 6324 завершён: 8 циклов, 40.349966 гостевой секунды,
  4 отключения AP, 8 разных актуальных поколений погоды; максимальный промежуток
  между ними — 8.161277 секунды. Проверены 31 входной файл, все три процесса
  завершились с кодом 0, VM закрыта. Отчёт —
  `wifi-runtime-preflight-validation-20261017.json`, исходные журналы — в gzip.
  Статус аудитора scope_requires_review ожидаем для короткого прогона.
- Старый H10 образа 83 остановлен намеренно после аудита: 230 циклов,
  3800.976347 гостевой секунды, 31 входной файл проверен. Намерение записано
  перед остановкой проверенного worker 2252. Supervisor завершил VM и guard;
  все четыре старых процесса отсутствуют. Статус failed/missing-footer вызван
  внешней остановкой и не доказывает сбой прошивки. Данные сохранены в
  `uri-runtime-superseded-20261017.json` и gzip-журналах. Этот каталог не
  возобновлять; его результаты не засчитывать образу 6324 или суточной проверке.
- Photo night observation исправлен и проверен на текущей6324/9E2C/53D3.
  Все6profiles обеих прошивок:102whole frames/0pixel differences,9normalized
  scenes,14contract guards. NTP внешне блокируется до двухначальныхcycles,
  далее full cycles до actual sync/night restore, cap6. Наблюдалось5cycles:
  clock_validFalse×4, затемTrue/night duty4095; порядок1,3,1,3,1 сохранён.
  Proof `photo-night-observation-validation-20261017.json`. Firmware59inputs
  с моментаWiFi fix не менялись. Это scoped pass; нужен fresh full новой6324.
- Wi-Fi27f1b23e интегрирован после сохранения terminal failed mainfull.
  Current ordinary6324C55A/ELF9E2C7719/source53D38223; BIN/ELF/map скопированы
  byte-exact из worktree без CMake cache, предыдущие83/62E0 сохранены в
  `.build/pre-wifi-fallback-main-20261017`. Resources подготовлены заново.
  Следующий шаг — исправить photo night observation, затем fresh full новой6324.
  Старые full/H10 остаются83 и не являются full/24h proof текущего приложения.
- Bounded full42964/30656 terminalfailed photo_frames/native masked-night.
  Все10frames/pixels/PWM совпали, но обеrestore2.814699/7.163766guest s были
  до первого SNTP: clock_validFalse, поэтому synchronized_night_restoreFalse.
  Это невыполненный night target, не доказанная brightness ошибка приложения.
 193inputs заново verifiedunchanged в terminal checkpoint; полный raw report
  и scoped JSON сохранены как `uri-bounded-full-failed-20261017.*`. Не публиковать.
- Отдельная `codex/small-tv-wifi-fallback`/27f1b23e готова: исправляет ложный
  mode2/reset после18s pendingDHCP и stale failure послеGOT_IP. Ordinary6324C55A,
  ELF9E2C7719/source53D38223,59inputs (менялся только app/network/wifi.c).
 47platform cases,4realnetworkQEMU cases и23contract guards, RV32eventoracle
  проходят.12ownedVMs остановлены; доказательство в feature branch. Перед
  интеграцией сохранить terminal currentfull (сделано); затем исправить photo
  observation и запускать новый full. Existing H10 остаётся83, не proof6324.

- Изолированная `codex/small-tv-wifi-fallback`: исправлено преждевременное
  mode2/reset после18s безIP. Factory0x4200cc0e..cc30 ждёт SDK success/failure
  с portMAX_DELAY;181display ticks не network timeout. Actual delayedDHCP:
  factory держала mode1/boot1 до30guest, старая8304 стала mode2/boot2; новая
 6324C55A/ELF9E2C7719/source53D38223 сохраняет STA и подключается послеrelease.
  GOT_IP также очищает старый failure latch. Before2host cases fail, after47pass;
 4realQEMU cases(factory/native DHCP и missingAP) и23contract rejections pass.
  RV32network4traces/16dispatch states pass. Production binary архивирован здесь
  в firmware/development. Main83 full/H10 этим не заменяются и не засчитываются
  новой6324; branch не объединять, пока не сохранён terminal main report.
- Main bounded full42964 завершился failed photo_frames/masked-night: все
 10frames pixel/duty equal, но обеrestore были доSNTP(guest2.81/7.16s), так что
  synchronized_night_restore=False. Это невыполненная цель night-case, не
  доказанная ошибка firmware. Main193inputs не менялись; сохранить failed
  evidence, затем поправить детерминированность этого теста отдельно.
- Fresh full после mergecdc54723 запущен19:05:32UTC: session42964, OS pwsh30656,
  `.build/small-tv-functional/uri-bounded-full-20261017`. Immutable freeze100tests+
  93extras=193inputs повторно проверен после старта; sourceBE58/app8304/ELF62E0/
  QEMUA74 прежние. Start record `uri-bounded-full-start-20261017.json` сохраняет
  все identities и controller command. Full ещё выполняется, не публиковать
  старый failed run. Не менять frozen test/verifier/production/QEMU inputs.
- H10 независим и жив: OS19:06:07UTC подтвердил прежние4PID/start times.
  File audit113cycles/1868.948064guest s,31inputs verified,start matchtrue,
  111valid quiescent weather generations/maxgap65.741273s,UART1boot/noerrors.
  Statuspending:нет24h/terminalguard/steady-hour windows. В следующем turn
  снова сверить OS identities; controller timeout не означает остановку.
  Tests README обновлён: старые31DAF browser cases исторические, current8304
  имеет отдельный8case proof; weather_wait/machine_network уже включены в gate.
- Tooling6b10c200 объединён после terminal failed full и перед новым freeze.
  Повторно16unit/CLI pass; actual read_clock_theme report50instructions/
  12blocks/4calls/0natural loops. Конфликты только в журнале/контексте,
  обе истории сохранены. Historical validation пока не перепубликуется;
  verifier при следующем passing full заменит устаревшее «untested draft»
  точным ограничением: review tool не выдаёт и не доказывает C implementation.
  Frozen isolated H10 inputs остались прежними.
- Failed full/reset-date исследован: кадр показывал startup, не неверную дату.
  Unchanged8304 baseline прошёл; после reset startup31→181 ticks занял15.284530
  guest/19.672host seconds. Старый30host deadline воспроизводимо отклоняет
  модель медленной ВМ. `date_capture` теперь ограничен30guest/90host seconds
  (для factory minute case90guest/270host), пишет оба elapsed; pixel comparison
  не ослаблен.6unit cases:slow guest,guest timeout,stalled guest,one wrong pixel,
  counter wrap,resume after capture error. QEMU suite/publisher требуют эту
  проверку; `FIXED_TEST` описан в CORRECTION_MARKERS.md. Повторный actual SNTP
  factory+native прошёл, включая reset/no fresh notification→recovery/post2038.
  Proof `time-reset-observation-validation-20261017.json`; production59inputs и
  app8304/ELF62E0 не изменены. Это scoped pass, ещё не новый successful full.
- Browser8304 focused flow завершён:8passing observations, включая настройки
  часов/advanced, photo interval3/60, mask17/0 и настоящий cold boot persistent
  raw. Public API и выбранные raw settings до/после совпали; все4image regions
  неизменны,19source fingerprints совпали. Доказательство:
  `uri-browser-controls-validation-20261017.json`, screenshot `uri-photo-cold-20261017.png`.
  Прежние zero-size previews были ещё без src во время последовательной загрузки;
  затем все5decoded240x240, browser errors отсутствуют. Firmware fix не нужен.
  Final advanced20→8/brightness12 теперь подтверждены API/raw и cold UI.
  Owned VM18416 и cold VM1960 остановлены, OS подтвердил отсутствие; tab2 закрыт.
  Upload/crop/mobile и полный manual checklist этим8case flow не засчитываются.
- Последний checkpoint по запросу commit/push: full90679 завершился
  **неуспешно** в18:50:53UTC. 18групп passed, QEMU failed, manual acceptance
  not_run. `time_qemu.py/reset_before_notification` не дождался даты2025/9/19:
  last state unsynced1900/1/0, boot_time_seconds2147483574.466206. Причина пока
  не установлена. Все192frozen inputs совпали; raw report сохранён отдельно
  в `uri-full-failed-20261017.report.json.gz`, результаты/continuation в
  `uri-progress-checkpoint-20261017.json`. Published EF66 не заменять этим
  прогоном; сначала изучить reset/time failure. Ниже running full — история.
- Browser8304 продвинут дальше initial scan: setup success alert, затем
  about:blank; SDK connected/APfalse/IP192.168.43.15/SNTPtrue, UTCerr0.871993s.
  Settings query-page reload сохранил units/date/brightness63/GIF5/Dial и
  RGB565 colors; synthetic cityPerth/AU-W сохранён. Advanced night20→8,
  brightness12 и NTP192.168.43.2 подтверждены UI. Initial fill+Tab для чисел
  не сохранился; keyboard stepping/digit entry с OK сработали, failed attempt
  сохранён, firmware bug этим не доказан. Intermediate API snapshot ещё start19,
  final start20/cold-boot API пока не проверены. Photo page: interval5/mask31;
  две preview240x240, три complete с natural size0 — исследовать до acceptance.
  Скриншоты settings/advanced и scoped JSON сохранены; VM18416/tab2 handoff
  остаются для продолжения и последующего cleanup. Upload/crop в этом flow
  не повторяли, cold persistence и photo controls ещё pending.
- H10 продолжает отдельный неизменяемый run: checkpoint77cycles/1outage,
  supervisor/guard running, no reported error. OS audit18:52:31UTC подтвердил
  все четыре PID/start times/commands; full controller9896 уже отсутствует,
  browser VM18416 принадлежит этой задаче. Это не24h/trend acceptance; не
  менять H10 inputs и заново проверить identities/footer в следующем turn.
- По запросу commit/push сохранён browser checkpoint на текущем8304F1A4:
  IABbrowser2/tab2, `http://127.0.0.1:18082/?probe=1` показывает WiFi Setup,
  scan завершён и даёт literal signed RSSI -21/-22/-39dBm. Screenshot/JSON:
  `uri-setup-browser-checkpoint-20261017.*`. Browser tab marked handoff для
  продолжения; VM SmallTV-af1d9b420488/PID18416, state
  `.build/small-tv-browser/uri-current-20261017-2`, station18083. Это только
  page/scan checkpoint: submit, about:blank, station settings/photo/advanced и
  persistence ещё не проверены в этом browser flow. Полныйrun90679 и H10
  продолжаются; H10 на момент сохранения43cycles/statusrunning/noerror.
  Первая browser VM PID33980 остановлена после слишком строгого test-only
  query-block length assertion; штатный owned raw matcher во второй прошёл.
  После продолжения сверить browser/VM identity и закончить flow/cleanup.
- Проверка после границы assistant turn пройдена: все четыре H10 roles живы,
  точные PID/start times совпали с launch record, команды принадлежат этому run.
  Evidence: `uri-runtime-process-survival-20261017.json`. Это устраняет прежнюю
  неопределённость detached supervisor survival; не доказывает24h completion.
  File audit35completed cycles/587.116241guest s,31inputs verified,36weather
  generations/maxgap20.006810s, start_record_matches=true, statuspending.
  До первого outageevery60 ещё не дошли. Старые строки «survival unproven» ниже
  являются initial checkpoint; при продолжении заново сверять OS и footer.
- Tooling branch `codex/small-tv-port-assistant` / `6b10c200` pushed, worktree
  `.worktree/small-tv-port-assistant`. Рабочий CLI для CFG/loops/prologue/
  epilogue/calls/C branch conditions;16tests и61assembly excerpts/9796decoded
  instructions проходят. Точный getclocktype excerpt50instructions/12blocks/
  32-byteframe/4calls/0natural loops. Tool не исполняет машинные инструкции и
  не генерирует готовую C реализацию. Merge оставить после frozen full terminal
  и публикации; не менять текущие192frozen identities во время прогона.
- Новый full90679 продолжает QEMU: boot/reset/SNTP обеих прошивок, body deadline,
  H09concurrency и URI targets gates прошли; идёт photo fade/frames. Full report
  ещё не terminal. Source/app остаются BE5802D6/8304F1A4, publishedfull — EF66.

- Отдельная `codex/small-tv-port-assistant` завершает запрошенный review tool:
  рабочий CLI/JSON/Markdown, exact bounds, logical symbol bindings,16CFG/CLI
  tests и61factory excerpts/9796instructions/44natural-loop edges проходят.
  Example read_clock_theme:50instructions,12blocks,32-byteframe,4calls,0loops.
  Отчёты не исполняют инструкции и не заменяют C/manual parity проверки.
  Новая tooling ветка подготовлена отдельно от frozen full/H10; объединять
  после terminal/full publication, чтобы не менять его зафиксированные входы.
- Main/origin now0fe92f18; transport candidate8304F1A4/ELF62E040B5/sourceBE5802D6
  интегрирован и отправлен. Canonical resources59 совпали с archive; BIN/ELF/map
  перенесены без CMake cache, прежняя922 сохранена в pre-uri-dispatch-main-20261017.
  Fresh full `.build/small-tv-functional/uri-integrated-full-20261017` запущен,
  controller90679 (OS pwsh9896), freeze99tests+93extras=192 identities, unchanged
  при начальном аудите. Full ещё НЕ завершён; published full остаётся EF66.
- Совместный latest preflight:8cycles/33.975877guest s,9quiescent valid weather
  generations/maxgap5.419394s,4outages,31inputs unchanged. Workload/guard exit0,
  supervisor complete. File-only audit подтверждает journal/weather/guard;
  H10 duration/window/start conditions ожидаемо не пройдены коротким тестом.
  Scoped proof `uri-runtime-preflight-validation-20261017.json` + gzip journals.
- H10 запущен через hidden supervisor из `.worktree/small-tv-manual-ssid`,
  новая immutable branch `codex/small-tv-h10-uri` на0fe92f18. Frozen QEMU view
  `.build/uri-runtime-qemu-frozen-20261017`,11files; exeA74/helper6B7F source2a59.
  Run `.build/uri-runtime-24h-20261017` внутри worktree, request86400guest s,
  interval15/outageevery60. Start record `uri-runtime-24h-start-20261017.json`
  binds31inputs and guard; file auditor pending/start_record_matches=true.
  External OS audit18:24UTC: supervisor30128,workload2252,guard18740,VM26440.
  Это launch snapshot, НЕ completion. В следующем assistant turn ОБЯЗАТЕЛЬНО
  проверить PID/start time/args: survival across turn пока не доказана; stale
  running JSON недостаточно. Не менять isolated files/QEMU/SDK inputs до footer.
- Transport audit завершён в `codex/small-tv-uri-dispatch`: factory принимает
  query/absolute targets, тогда как922 native давала400 либо settings вместо
  setup/photo. Shared callbacks теперь получают SDK-selected static path через
  user_ctx; полный req->uri и photo query сохранены. Нет второго URI parser.
  Обычная8304F1A4/ELF62E040B5, debugA8C337BC/ELF86B7275D, sourceBE5802D6;
 59 inputs, ordinary1169904/free366096. Host5531/platform46/frontend18/
  integrity6/timezone9/aggregation14 и DEBUG OFF/ON/OFF unit проходят.
  Actual QEMU: factory36/native124 acceptance conditions,160 HTTP requests,
  четыре полных upload/download cycles с точным JPEG, inputs unchanged,
  обе ВМ закрыты и PID отсутствуют. Новая regression включена в qemu_suite
  и publisher; scoped JSON `uri-targets-validation-20261017.json`.
  Это не новый full/H10. Следующий шаг: интеграция кандидата, fresh full freeze,
  совместный supervisor/schema4 preflight и isolated24h workload.
- Следующие строки о query «гипотезе» и candidate922 — предыдущий checkpoint;
  они сохраняют историю, актуальный transport результат приведён выше.
- Текущее main10557472 объединяет все подготовленные fixes/tools; новая
  ordinary922DA963/ELF71DED1E1/source9D2367EB и debugC37B7B5E/BA060CE6 в
  development archives. Точные ordinary ELF/BIN/map перенесены в canonical
  .build без CMake cache;59 production inputs совпали, A543 build backup в
  pre-setup-redirect-main-build-20261017. Старые branch/not-integrated строки
  ниже — исторические. Published full всё ещё относится к EF66/81CF/A74.
- Все созданные preflight/browser VM завершены; новых full/H10 сейчас НЕТ.
  Следующий шаг — actual factory/native query-suffix probe до нового freeze.
  SDK httpd_uri.c:314 выбирает callback по UF_PATH, но req->uri сохраняет query
  (httpd_parse.c:1037). В native server/settings/photo dispatch есть strcmp
  полной строки. Нужно проверить не только GET/POST с `?probe=1`, но и page
  selection; нельзя глобально обрезать req->uri, потому что /get_Photo_File
  использует штатные query parameters. Учитывать SDK absolute-form UF_PATH.off.
  Пока это гипотеза, не объявлять исправленным или доказанным без native/factory.
- После transport проверки: latest build, совместный supervisor/schema4
  preflight, новый frozen full и isolated24h H10. Для H10 сохранить отдельный
  неизменяемый worktree и QEMU bundle, проверить реальные PID/start time/args
  после границы assistant turn. Старый rssi H10 прерван и не засчитывается.
- `codex/small-tv-setup-redirect`: восстановлен factory `about:blank` после
  Wi-Fi configure/reset. Local exporter ошибочно делал `/`, reload старого AP
  после его shutdown. Это объясняет часть прежних browser CDP/error-page сбоев;
  прежнее «только tooling» было неполным выводом. Factory target controls2pass,
  before2fail/new18scan-submit-success-error cases pass; сохранён timer3000ms.
  Real browser на новой ordinary922DA963/ELF71DED1E1: success, auto about:blank,
  штатный close, tabs0. SDK connected/APfalse/IP192.168.43.15/SNTPtrue,
  UTCerr0.471599s; VM закрыта. Первый clock-only probe ожидал10.0.2.15 и
  timeout; correct setup-context read прошёл, это не firmware fault.
  Ordinary922DA963/71DED1E1 и debugC37B7B5E/BA060CE6 сохранены, source9D2367EB/59inputs,
  только generated/web_pages.c изменён, SDK config прежний. Host checks pass.
  Full/H10 этого кандидата ещё не запускались. Перед ними подготовить отдельный
  неизменяемый app/QEMU worktree для H10 и проверить detached supervisor через
  границу assistant turn. Published full остаётся на EF66/81CF/A74.
- Возможный следующий пробел для проверки, ещё НЕ подтверждённый баг: SDK
  выбирает handlers по path, а native web dispatch сравнивает req->uri через
  strcmp. Проверить query suffix (`/getclocktype?probe=1` и подобные) на factory
  и native, прежде чем фиксировать следующий финальный full/H10 набор.
- Следующий кандидат runtime schema4 (`codex/small-tv-runtime-weather`) закрывает
  пробел фактического weather workload. Четыре числовых поля читаются по точному
  ELF/DWARF только при idle worker; никаких строк/ключей/URL или вызовов гостя.
  8 observer +24 analysis tests проходят, включая частично скопированный кеш,
  неверный ABI, регресс поколения и сутки чтения старого валидного кеша.
  Real preflight на A543/8485:8 cycles/27.549604guest s,9 synthetic responses200,
  9 quiescent valid snapshots/9 разных поколений, max fresh gap5.009813s,
  31input hashes unchanged. UART guard сделан posthoc по полному capture;
  он подтверждает отсутствие reset/panic, не concurrent supervision этого case.
  VM закрыта. Ошибка первой команды guard была неверным --qemu-tools (root
  вместо tools); повтор корректен. Старый schema3 audit также читается, но
  остаётся прерванным/pending в file-only анализаторе, не H10 pass.
- В main уже включены RSSI/manual-SSID/analysis/supervisor до8ab53a27; ordinary
  A5439306/8485A233 и source721E26BD перенесены в canonical .build с backup
  прежнего EF66 build. QEMU main2a593f8d00 отправлен; C executable A74 прежний.
  Main helper rawSHA6B7FF996 отличается от branch FF0819 лишь CRLF; normalized
  SHA FF0819 совпадает. 19 canonical readiness units прошли на фактическом файле.
  Новый полный прогон текущего app ещё не запускался; published full — EF66.
- Новое продолжение в `codex/small-tv-runtime-supervisor`: Windows tool
  `tools/runtime_supervisor.ps1` держит handles workload/guard, фиксирует выход
  без footer как failed и закрывает только собственную VM. Real preflight4
  cycles/2outages завершён, worker/guard exits0; независимый journal audit pass
  в коротком scope, не H10. Два отдельных failure-injection прогона (kill только
  своего worker или своего guard) дали expected failure и удалили все свои
  дочерние процессы/VM. Source SHA8C91874B. Выживание через assistant turn пока
  не подтверждено; running JSON требует внешнего process audit. До нового H10
  проверить, что workload подтверждает фактический разбор погодных ответов,
  а не лишь постановку запроса `/updateCity`.
- Full `debug-integrated-full-20261017` ЗАВЕРШЁН: 19 automatic groups pass,
  finished UTC17:04:52, EF66/81CF/8FCE/A74. Все184 frozen SHA совпали;
  publish-report.py и verify_artifacts.py прошли. Опубликованы functional-
  validation.json и validation.json: 84 natural calendar transitions/168 frames,
  24 strict scene frames с pixel diff0, native3950/platform46. Entry comments162,
  correction markers56, DIRAM80540, app1169888/free366112. Теперь можно
  интегрировать подготовленные ветки и обновить main helper; не приписывать
  этот completed full более поздним RSSI/manual-SSID images.
- H10 ПРЕРВАН: runtime/guard tool handles missing, VM PID13544 отсутствует,
  системных runtime/guard процессов нет. Raw report без terminal footer,
  последний journal187 cycles/3096.125371 guest s,188 snapshots/1504HTTP/3outages,
  pending4 events. Один ROM boot, panic нет,30 inputs совпали, но это НЕ24h pass.
  Причина остановки не установлена. Полный numeric JSONL и UART сохранены gzip
  в ../qemu/parity/runtime-rssi-interrupted-20261017-*, отдельный JSON фиксирует
  внешний process audit. Старые running строки ниже — исторические checkpoint.
  Нужен новый долгий запуск на следующем кандидате с контролем жизни workload.
- Сохранены и отправлены новые follow-up ветки, пока НЕ включённые в main:
  `codex/small-tv-runtime-analysis` / `e0d276ac` в worktree
  `.worktree/small-tv-runtime-observer` — read-only полный JSONL audit и анализ
  heap по равным фазам, 20 unit tests. `codex/small-tv-manual-ssid` / `c72b4b45`
  в `.worktree/small-tv-manual-ssid` — исправление factory setup HTML: настоящая
  сеть `manual` больше не вызывает prompt. 15 scan/submit cases, host checks и
  настоящий browser/QEMU setup проходят. Scoped MD/JSON/PNG находятся в ветке.
  Ordinary A5439306/8485A233 и debug D1E7660D/EB4FDFB5 сохранены в её development
  архивах, source721E26BD; только generated/web_pages.c отличается от RSSI.
  До terminal/publish frozen full не интегрировать ни эти ветки, ни QEMU helper.
- Последний read-only audit H10: 99 полных циклов, 1 632,639162 гостевой секунды,
  30 входных SHA совпали, один ROM boot, panic нет. Это pending, не 24h pass;
  для trend после прогрева пока недостаточно часовых окон. Controller31890 и
  guard99431 живы. Full67941 прошёл все 42 factory calendar transitions и
  продолжает native classic. Его 184 frozen inputs повторно совпали.
  Временная VM проверки manual остановлена, STA browser tab закрыта; старую
  setup error-tab блокирует browser URL policy. Она временная, без handoff,
  для штатной очистки конца turn. Основной full и H10 не останавливать.
- Следующие исправления уже готовы в отдельных отправленных ветках: FW
  codex/small-tv-rssi-label /56df5baf (папка .worktree/small-tv-rssi-label),
  QEMU codex/small-tv-wifi-link /2a593f8d00. Signed RSSI formatter/8cases/browser
  и два новых archives: ordinaryD78A7639/F5F39276, debug5E468EB3/8FAE6071,
  sourceF8A3A6A8/59inputs (только generated/web_pages.c изменён). Host reduced pass.
  QEMU helper ждётactual SNTP reset readiness,19unit/3VM/29consumer pernative pass.
  Старый debug fixed8host failure сохранён; configrandomdelayдо5guest s подтверждён.
  См. branch rssi-ui-checks/validation-20261017. Интегрировать после terminal/save
  текущего root full67941; добавить wifi_network.js в следующий freeze collector.
- H10/24 guest hours ЗАПУЩЕН: handle31890,
  .build/small-tv-parity/rssi-runtime-24h-20261017; controller/log одноимённые
  в .build/small-tv-parity, НЕ запускать дубль. AppD78A/ELFF5F3/sourceF8A3,
  executableA74 и helperFF0819 взяты в отдельный frozen bundle внутри RSSI worktree:
  .build/runtime-qemu-frozen-20261017. Canonical QEMU/main могут быть обновлены
  после root full, bundle H10 менять нельзя. Также сохранять 30 input files
  ветки/SDK из H10 report; не архивировать RSSI worktree до terminal H10.
- H10 preflight8cycles/27.160648guest s/9snapshots/64HTTP/2real outages/67events
  прошёл,30inputs/journalSHA unchanged, no panic/ВМclosed. Min sampledheap87036,
  sumSDKminima55352, minstack480. Внешний launcher после Python дал quoting error;
  raw workload result проверен отдельно, ошибочный launcher сохранён. H10 controller
  — отдельный literal .ps1 без этой ошибки. Pending H10 report passed=false при
  живом handle и error=null не является terminal failure. После24h отдельно
  анализировать trend по полному events.jsonl; ранние samples не доказывают leak-free.
- H10 read-only UART guard handle99431 также жив: uptime-guard.json в H10 run,
  source в RSSI branch2e85ab8d (отправлен). 7unitcases pass; ROM banner+Build
  считается даже после незавершённой строки приложения. Нужен terminal guard pass
  и полный UART сcount1; основной runtime passed сам по себе не исключает silent
  reset, radio counter продолжаетвремяпослеreset. Guard не подключается кQMP,
  workload держитsoleconnection; перваяattach-попытка получилаtimeout, guestнеизменён.
  GuardfileSHA записанв runtime-rssi-h10-start-*.json; кодguard тоже сохранять.
- Root full67941 всё ещё жив; host/machine/profile, boot/reset, startup/weatherwait,
  body/concurrency/photo и initial setup/weather/fields gates прошли; продолжается
  SNTP/time. Canonical A74 CYD/C3 legacy run85263 terminal0/pass. 184 fingerprints
  проверялись повторно unchanged; текущие новые ветки их не меняют. Browser tabs0.

- Новый immutable full ЗАПУЩЕН: handle67941,
  .build/small-tv-functional/debug-integrated-full-20261017, controller log
  .build/small-tv-parity/debug-integrated-full-20261017.log. Не запускать копию
  и не считать poll timeout завершением. Frozen92 test files +92 extra inputs;
  EF66/81CF/8FCE/QEMU A74, qemu sourceadb66701b3, pre-run HEADdef6914d.
  Все184 fingerprints повторно совпали после старта. Host groups pass;
  machine oracle ещё выполняется. Audit debug-integrated-full-inputs-* —
  только identities, НЕ completed pass. Tests/helpers/production inputs не менять.
- Дополнительный exact-installed A74 CYD/C3 boot run handle85263 ещё выполнялся
  при записи этого checkpoint; не дублировать. Ранее обе mode-регрессии0B3F/F3D7
  уже завершились успешно. После завершения общего full проверить unchanged
  fingerprints, publisher/verifier, сохранить результаты; затем отдельный RSSI
  UI fix и H10. Перед заменой installed QEMU дождаться terminal full.

- Canonical diagnostic QEMU main adb66701b3 собран и установлен: executable
  A74F3324430B306618AA88A52649DBB93C32EAC6D0B87926D335754346ABBF0B,
  marker commit/mode совпадают;12 packet tests и modules на нём прошли.
  Main обоих репозиториев отправлен. Новый full готовить в отдельном каталоге
  debug-integrated-full-20261017; не переиспользовать старые output folders.
- Browser initial Wi-Fi setup на quiet EF66 прошёл19 scoped conditions:
  scan/invalid password без restart или сохранения, valid open test AP,
  один restart/STA/DHCP/SNTP, реальная STA settings page и controls loaded.
  См. ../qemu/browser-setup-quiet-20261017.json. ВМ закрыта, station tab закрыта;
  старую setup-tab на generated error page блокирует browser URL policy,
  unmarked temporary tab оставлена для штатной automatic turn cleanup.
- Найдена отдельная UI ошибка: local_site/pages/setup.html:187 и settings.html:464
  применяют Math.abs(network.rssi) перед подписью dBm. Исправить знак и добавить
  frontend regression следующим отдельным изменением после immutable full;
  сейчас production/test inputs нового full не менять. Это не ошибка RSSI DMA.

- Интеграция завершена: main merge5e41962d включает HTTP body/H09/runtime/DEBUG
  и quiet boot gate. QEMU main fast-forward доadb66701b3; идёт каноническая
  diagnostic сборка из main для расширенных transport tests. Старый installed30F
  и marker сохранены в pre-debug-qemu-install-20261017. Не запускать full, пока
  новый executable и marker не готовы.
- В main перенесены точные проверенные ELF8FCE/BINEF66/map, без копирования
  CMake cache. Все59 production inputs и ELF SHA в app header совпали. Старые
  ELF/BIN/map сохранены в pre-debug-main-build-20261017; CRLF-only sdkconfig
  отдельно сохранён до merge. Host reduced3950/platform46/frontend/integrity/
  timezone/aggregation и DEBUG config reuse test после merge прошли.

- Актуальное продолжение DEBUG: boot helper больше не требует INFO. Matched-ELF
  flags и SDK timekeeping offsets читаются read-only; QEMU `last-ntp-reply`
  доступен при esp_debug OFF/ON. Все6 boot/reset scenarios,12 ELF units,
  29 consumer controls и по12 network cases/modes прошли. Ordinary EF66/8FCE,
  debug11DD/DBE5, source81CF; новые QEMU0B3F6F69/F3D7B024. См. quiet-boot-state-*
  MD/JSON. Не путать с историческими E210/9994/76A DEBUG smoke runs.
- Для нового full нужны интеграция feature веток, точные ordinary BIN/ELF и
  diagnostic QEMU (остальные transport gates ещё читают его события). До запуска
  заморозить также esp_elf.py и tests/esp_elf_test.py. Во время full не менять
  helpers/tests/production inputs. Обязательны body_http, concurrency_http,
  boot_observer_unit и29 boot consumer controls. H10/24h пока не запускался.

- Пользователь явно разрешил «Возобновить проверки». Прежние контроллеры общего
  прогона остановлены, оставшиеся две собственные ВМ были закрыты через QMP с
  проверкой имени; остальные 32 session уже не работали. Временная вкладка
  браузера закрыта. Состояние: `.build/small-tv-functional/controls-integrated-full-20261016/paused-by-user.json`.
- Общий run `controls-integrated-full-20261016` прерван, успешного общего
  результата и публикации для DAF нет. Прежние указания опрашивать handle96792
  больше не актуальны. При возобновлении сначала оценить сохранённые частичные
  результаты и состав входов, затем отдельно планировать новый полный запуск.
- Ветка `codex/small-tv-photo-settings` / `459b93bd` объединена с main;
  новый gate обязателен для suite/publisher/verifier. Её отдельный успешный
  результат не заменяет общий прогон. При интеграции повторно прошли14 guards,
  сохранность74 исходных test pins/57 production inputs/8 instruction ranges.
  Collector перед новым full обновить.
- Серия DAF/C839/B06 до оптимизации проверена в новом raw-backed browser guest:
  31 финальная браузерная проверка и21 storage/identity checks прошли. Ночное
  расписание на обеих границах/яркость2–99/off, все4 темы/5 GIF/3 даты, флаги,
  day0 и3 цвета RGB565, desktop resize/crop, mobile390px portrait, отмена/Escape,
  mask0/31, interval3/60 и cold boot persistence. См.
  `../qemu/browser-controls-20261017.md` и отдельный JSON; это не полный H03.
  Две неверные промежуточные oracle assertions сохранены с объяснением; новых
  дефектов firmware этот набор не установил. ВМ24764 и временная вкладка закрыты,
  viewport сброшен. User подтвердил: штатное поведение factory сохранять,
  её доказанные ошибки исправлять; оптимизации разрешены с проверкой результата.
- В .worktree/small-tv-photo-upload-waits выполнена оптимизация uploader:
  canonical photo_upload.js встроен exporter; удалены50ms после успешного ACK
  и2500ms после пятой неудачи, backoff между попытками сохранён. Native ACK
  следует за esp_partition_write. Комментарий REQUESTED_CHANGE и отдельные tests.
- Candidate этой ветки: appDD4EB76E/source96A111EC/ELFB7BE7CCC,1 176 880 bytes,
  free359 120. Код четырёх native upload/HTTP functions побайтово прежний.
  Final frontend11 pass; тот же MJS на старой странице даёт6 ожидаемых failures.
  Host3924/platform46/frontend/integrity/timezone/aggregation pass (reduced);
  SDK photo HTTP21 pass. Actual browser/raw22 checks pass: JPEG47837 bytes,
  12chunks, SHA a73dc807 полностью идентичен baseline DAF. Metadata отсутствуют,
  slots1–4 и executable/media regions unchanged; helpers/QEMU unchanged.
- JSON manifest теперь пишется LF без BOM (отдельный c5f51a04); после этого
  выполнена новая финальная browser series, не подменявшая первую CRLF-проверку.
  Все собственные ВМ и tabs этой серии закрыты. См. photo-upload-waits-checks.md.
  Ветка объединена в main через1a946c38. Root build84004 terminal0:
  текущий main appDD41A536/source96A111EC/ELFB4AF3C2A,1 176 880 bytes/free359 120;
  bootloader3FB735A3. Обе executable sections совпадают с проверенной веткой,
  см. photo-upload-waits-main-build.json; её scoped reports сохраняют DD4EB76E.
  B06/DAF ELF/BIN/map/resources сохранены в controls-pre-upload-build-20261017.
  Единственный full upload-integrated-full-20261017 завершился ошибкой calendar
  HTTP latency (terminal report 2026-10-17 13:47:20), handle62455 больше не жив.
  Все75 test sources и88 дополнительных inputs повторно совпали с frozen hashes.
  Все18 pre-QEMU groups прошли; QEMU дошёл до calendar после остальных gates,
  включая photo_settings. Все84 natural transitions/168 полных кадров прошли.
  Native /setclocktype dial/post-2038-midnight занял6.150371 guest seconds при
  границе6; ещё два ответа заняли5.702424 и5.882957. Причина пока не установлена.
  Порог не ослаблять; воспроизвести и измерить обработчик/транспорт/flash.
  Complete-scene и diagnostic comparison не достигнуты, общий pass отсутствует.
  См. ../qemu/parity/upload-integrated-full-20261017-failure.json. Не использовать
  passing-only archive_immutable_run.py для этого failed run; исторические
  опубликованные full reports не заменять. H03/setup, H09/H10 и physical остаются.
- Отдельный main browser proof DD41/B4:16 checks pass, реальный DOM script SHA
  654c2ee3 совпал с generated page; JPEG47837 bytes полностью прежний. Raw backing,
  соседние4 slots, inputs и protected regions проверены; ВМ18016/tab4 закрыты.
  См. photo-upload-waits-main-ui.json. Это не результат полного62455.

## Текущий результат диагностики HTTP — 2026-10-17

QEMU main и origin/main теперь0d27a7ca98; installed executable30F9A68E.
RSSI1a142bcf51 и trace3279a6c2f1 дополнены sparse SYN trace72f106db81 и
finite-link timing0d27a7ca98. Последний устраняет схлопывание просроченных
RX/TX frames в один virtual instant; учитывается полный transfer time на всех
пяти scheduling sites, unlimited bandwidth0 сохранён. Link calculations выделены
в свой модуль. Новый QTest на oldD18 ожидаемо failing, на30F все10 pass.
Modules и CYD/C3 legacy/modular boots pass с прежними source/pixel hashes.
Quiet five-route180 на неизменных appDD41/source96A/ELFB4: old correct-RSSI6238
max6.186934, new30F max.238274. Все200/no panic, ВМ закрыты. Исправление merged
и pushed в QEMU main и feature branch; canonical EXE и marker проверены.
См. ../qemu/parity/wifi-link-timing-checks-20261017.md и отдельный JSON.

Следующий шаг — один новый frozen full на canonical30F. Старый failed run
не переименовывать в passed, порог6 не менять; firmware и75+88 test/extra inputs
не менять во время нового прогона. Данные ниже сохраняют ход диагностики до
исправления; прежний запрет нового suite после локализации больше не актуален.

Общий link-timing-integrated-full-20261017 завершён успешно (terminal0),
handle11075 больше не жив. InitialHEADaf7c8c17, QEMU30F/source0d27a7ca98,
appDD41/source96A/ELFB4. Все75 test files/88 extra inputs повторно совпали.
Все19 groups прошли, включая84 natural calendar transitions/168 frames,
24 completed frames с0 различий и40 normalized diagnostic captures. Последние
проценты сходства не являются gate или процентом покрытия. Publisher/verifier
прошли;32 positive artifacts сохранены, historical negatives не переписаны.
Audit: link-timing-integrated-full-inputs-20261017.json. Это checkpoint DD41,
который не включает новый HTTP deadline, observer и DEBUG branch. Их отдельные
проверки не приписывать этому общему результату. Запрет изменений frozen inputs
после его сохранения снят; следующему кандидату нужен собственный полный прогон.

Независимая ветка codex/small-tv-runtime-observer /a3707eb5 сохранена и отправлена,
worktree .worktree/small-tv-runtime-observer. В ней standalone read-only observer
и19 parser/ROM tests; main/test pins не менялись, merge до terminal full не делать.
Новый40-cycle runtime-workload-20261017-02 завершён:121.076406 guest s,
41 samples всех12tasks,10 uploads,240 recorded HTTP +80 concurrent GET,
max.405659s, inputs unchanged/no panic/ВМclosed. SDK heap minima sum47 028,
lowest task stack480bytes(settings); last free heap86 268. ROMcrosschecks164.
Scoped doc/JSON runtime-memory-* находятся в ветке; они не объявляют H09/H10,
24h leak-free/physical/ISR stack или factory memory equivalence выполненными.
Ошибки прежних попыток harness сохранены отдельно. Root app/source/ELF прежние.
В a3707eb5 добавлены duration, unwrap low32 guest microseconds, append-only
JSONL и последние32 samples в summary. 16 decoder +6 journal/clock tests pass;
на одной SRAM-фикстуре чтения45→20 с теми же результатами. Два коротких native
запуска прошли:4 cycles/15.689122s/2 реальных disconnect/reconnect и запрос8s,
завершённый после8.135430s. Это проверка инструмента, не H10/24h. Ошибка попытки
4096-byte RSP/E22 сохранена; рабочий transport block1024. После immutable full
объединить, затем запускать длительный workload на окончательной сборке.

Вторая независимая ветка codex/small-tv-http-body-deadline /6c5360d4 (основной
фикс35b6bdce) отправлена; worktree .worktree/small-tv-http-body-deadline.
Доказан новый дефект НАШЕЙ HTTP-обвязки: partial JSON блокирует второйGET24.69s,
trickle27.61s, oversized9.70s. В factory0x4200d7f0 один recv на0x4200d808;
нашего3-timeoutloop нет. Новыйrequest_body.c:5s absolute budget, remaining
SO_RCVTIMEOceil1ms, SHUT_RD при отказе против SDK purge, restore при успехе.
App3C599124/source1741EA14/ELF342C0127,1 177 216bytes/free358 784,58 source inputs.
Все4 identical actual HTTP cases pass:4.695327/4.703467/.204119s; native3950,
platform46/frontend/integrity/timezone/aggregation reduced pass; SDK photo21pass.
15 consumer controls pass; body_http обязателен в НОВОМ suite/publisher/verifier.
ASM hashes проверены через checkout filter, LF attribute сохранён. Старый main
не изменялся, текущий full11075 НЕ включает эту исправленную сборку/новый gate.
После terminal/publish текущего DD41 объединить завершённые ветки, восстановить
root build и запустить один новый frozen full с обязательным body_http. Результаты
веток не приписывать root app с другим ELF/BIN identity. Код/документы/сборка
находятся в feature branches, все собственные диагностические ВМ закрыты.

В этой же ветке2d31a617/6c5360d4: реальный concurrent HTTP workload прошёл34
conditions,16 paired batches и68 sequential requests, max pair2.847167s,
single.306982s. Upload/scan/held weather/settings/retry/warm+new-process cold
boot и5 protected flash ranges проверены. 20 consumer rejection controls pass;
новому полному suite обязателен concurrency_http вместе с body_http. Это один
ограниченный H09 сценарий. Первый harness preflight с double-stop и слабым
renderer oracle сохранён отдельно, не считается acceptance.

Пользователь17 октября потребовал отключаемую при сборке отладку В ОБОИХ
проектах. Готовы и отправлены: FW codex/small-tv-debug-logging /cf220f21,
QEMU codex/small-tv-wifi-link /04443f07dc. FW branch включает завершённые body/
concurrency/runtime ветки через8fecd9e1. По умолчанию OFF; -DebugLogging включает
FW CMake DEBUG и QEMU esp_debug. FW SDK/app/bootloader levels2/4; отдельный debug
archive. Полные OFF/ON/OFF builds и20 logging conditions/run проходят. Обычный
UART0 I/D/V/3W. QEMU11 packet tests в3 режимах, modules иlegacy boot gates pass;
normalpixels прежние, debugC3modular scroller/AP phase другая — equality не заявлена.
FW finalEF66/source81CF/ELF8FCE; debug11DD/DBE5. QEMU OFF76A, ON9994; canonical
main/installed остаются0d27/30F. Новые scope JSON/MD находятся в FW worktree.
Quiet runtime4cycles/16.475576s/2outages читает настоящий connected bool вместо
UART; H09 quiet34/16/68 иbody4cases прошли, все собственные ВМ закрыты.

Старый boot-console gate всё ещё ищет INFO строки FW: перед новым quiet full
адаптировать его к настоящему гостевому состоянию с проверкой соответствующего
ELF/BIN (либо достоверному HTTP/LCD наблюдению), не ослаблять проверку readiness.
Если добавляется отдельный Python helper, включить его во все transitive input
pin lists и новый frozen collector. Transport parity использует DNS/NTP traces
QEMU: для него нужен diagnostic EXE, firmware при этом должна остаться обычной.
Затем объединить сохранённые ветки в main, сохранив passing DD41 checkpoint61d1f8ee
и не приписывая его новому кандидату; подготовить root ELF/BIN/resources с одной
identity и новый full сbody_http/concurrency_http. Точный протестированный EF66/
8FCE можно перенести из worktree при совпадении всех59 production inputs; новый
root rebuild может изменить app descriptor/ELF и требует новых identities.
Root sdkconfig имеет прежнюю CRLF-only generated правку: проверить/сохранить её
перед merge, не стирать посторонние файлы. Actual24h/H10 ещё не запускался.
Browser initial-setup ещё не начат: CUA inventory пустой, VM/tab не создавались.

### История измерений до исправления timing

Пользователь напомнил прежнюю шестисекундную ошибку QEMU и попросил изучить
весь путь до обработчика и другие места его использования. Старый фикс
9d4da15732 присутствует в main962cda7a6f и установленном FDE38D53; повторные
8 packet regressions проходят. В Esp32_sendFrame только один caller —
исправленный inject timer. web_settings_post используется16 POST routes.
Три read-only probes по180 POST завершены, ВМ закрыты. Порог не менялся:
новый SYN retry даёт5.8s до HTTP, сам handler <=11ms; RX-drop trace не выдал
событий. См. ../qemu/parity/http-admission-investigation-20261017.md и JSON.

Corrected TCP preflight60 завершён: в одном1.55s запросе первый SYN пришёл
в TCP через20ms, listen pending0/backlog5, tcp_alloc вернул ненулевой PCB.
Наблюдается накопление weather TCP FIN_WAIT_2 до13 при active TCP limit16;
это ещё не доказанная причина5–6s stalls. Первый TCP observer зациклился на
непродвинутом breakpoint и был остановлен; layered observer остановился на
вмешавшемся breakpoint во время естественного entry advance. Эти две ошибки
harness сохранены ignored и не являются firmware failures.

Admission180 завершён: TCP PCB refusals0. Netif180 завершён; один DATA repeat
появился в observed netif только через1.4s. Внешний packet может быть потерян
до передачи Wi-Fi→stack; debugger scheduling/entry-return gaps требуют passive
подтверждения. Все ВМ этих попыток закрыты, полного passing gate по-прежнему нет.

В прежней чистой QEMU worktree .worktree/small-tv-wifi-link, branch
codex/small-tv-wifi-link, выполнены и отправлены1a142bcf51 (общий constructor
RSSI -25 вместо uninitialized heap) и3279a6c2f1 (отдельный passive trace module).
Тот же queued8-data-frame test на FDE дал2 failures C2/C3; на candidate62386F10
все9 pass. Modules и CYD/C3 legacy/modular boots pass, pixels/source hashes
совпали с прежними. Main QEMU/installedFDE и firmwareDD41/B4 не заменены.
Trace-only before F207BA0D и after62386F10 сохранены как отдельные immutable EXE.

Одинаковый quiet five-route A/B34683 завершён: before180 max6.167475,
after180 max6.186934, оба превышают6. RSSI — реальный отдельный дефект,
НЕ установленная причина stall. Four-route240 after max.214052 не заменяет
этот отрицательный результат. Passive five-route87774 с подробным log дал
180/max.220060, drops0, RX_CTRL=0x80000000 (кроме двух startup writes).
Подробное логирование меняет наблюдаемые timing; следующий шаг — малошумная
SYN-only queue/DMA trace с CPU PC/IRQ context. Все текущие ВМ закрыты.
См. ../qemu/parity/rssi-frame-validation-20261017.json. Не ослаблять gate и
не запускать новый общий suite до локализации оставшегося network пути.

## Цель и принятые решения

Предыдущие этапы ниже сохраняют историю; актуальный порядок продолжения указан
в верхнем блоке. Старые live handles и запрет merge до завершения96792 отменены
после явной паузы пользователя и подтверждённой остановки этого прогона.

- Интегрирован photo_settings gate из459b93bd: шесть actual HTTP scenarios на
  обеих firmware,24 completed frames/0 pixel differences и14 contract rejections.
  Исторический scoped result2990 относится к прежним DAF/C839/B06; это не новый
  полный запуск main. RAW/media/panic/ROM,74 initial pins и8 instruction ranges
  сохранены. См. photo-settings-checks.md. H09/H10 и physical остаются.

- Main объединён с photo branch aded56bf merge95eddf55. Root photo buildD978 /
  source0BAA / ELF8AC сохранён и отправлен в ba349b5a. Исправлены idle brightness,
  повторный выбор темы и заводской чёрный экран после отменённого fade;84 full
  photo frames/9 scenes и46 platform cases проверялись на branch6BF6.
- Последний завершённый общий checkpoint — dbbef80d: все19 automatic groups
  на AD7A/F411/6D7B,63 initial/final files,84 calendar transitions,24 complete
  frames и40 normalized scenes. Он исторический и не проверяет новую сборку.
- Текущий production candidate: appDAF5595D/sourceC83941FF/ELFB06CE810,
  1 177 568 байт/free358 432, сохранён в firmware. advanced_page показывает
  сохранённый NTP с bounded HTML escaping; empty setting не обрывает chunked
  страницу. Host3924 pass, включая15 новых проверок; оба negative server-source
  controls с теми же final test/adapter воспроизведены. Реальный SDK HTTP:
  D978 before expected fail, DAF after4 cases pass. Actual final browser:
  prefill/save/reload/empty/HTML isolation pass; нет console errors.
  Источники/assembly/SDK/C/browser evidence — advanced-editor-checks.md.
- Все собственные ВМ30908/14684/12152 и CUA tab1 закрыты после сохранения
  scoped evidence. Новый full96792 описан ниже. Browser2 binding
  smallTvBrowser остаётся выбранным, но smallTvTab закрыт. Для продолжения
  использовать новую временную вкладку в том же IAB. computer-use skill,
  guidance/confirmations, browser docs и local-web-development прочитаны.
- Важная обнаруженная граница старых тестов: при -snapshot базовый flash.bin
  не содержит guest writes. Старые проверки basefile гарантировали сохранность
  исходника, но не весь гостевой носитель. Новые advanced_qemu/qemu_storage
  уже используют raw backing и проверяют его через query-block. Snapshot
  negative и final raw image checks сохранены в .build/small-tv-browser.
- Усиление четырёх photo storage gates завершено: новые собственные raw-копии,
  live query-block proof, обязательный direct_flash_backing в contracts и
  utility fingerprint. Batch26076 terminal exit0 на DAF/C839/B06: brightness,
  три theme commands, active reinit,84 frames/9 scenes pass. Все ВМ закрыты.
  Actual paused snapshot/raw probe pass;12 frame guards/12 backing guards и
  четыре historical rejections pass. Исторические отчёты не изменены;
  см. photo-storage-checks.md. Production source/BIN прежние.
- NTP044e488f, software-wait auditac187b10 и storage65d7be99 отправлены main.
  Новый единственный full run уже идёт: handle96792,
  .build/small-tv-functional/controls-integrated-full-20261016, initialHEAD65d7be99.
  Frozen72 test files, appDAF/ELFB06/QEMUFDE3, также7 firmware files,6 QEMU
  helpers/profile/marker/source commit и verifier. Native3924/platform46,
  frontend/integrity/timezone_sources и все machine groups уже pass. QEMU:
  boot/reset/SNTP, startup/weather UI wait,advanced,upload,84 photo frames/9 scenes,
  brightness/theme commands/reinit,setup,weather,fields и SNTP transport pass
  на обеих firmware. Идёт UTF8 (original pass), далее regional/calendar/scenes.
  Опросить тот же handle, не перезапускать. До terminal не менять production,
  tests, generated media, BIN/ELF и QEMU/helpers; разрешены контекстные Markdown.
  Затем сверить initial pins и использовать archive_immutable_run.py: он уже
  адаптирован к advanced_http/4photo/extra pins, сначала strict publisher/verifier,
  потом canonical artifacts и integrated-controls-run-inputs.json. Не выдавать
  scoped passes за полный результат и не переименовывать прежние identities.
- Browser controls на6BF6 сохранены отдельно в browser-controls-partial-20261016:
  flags,4 themes,5 GIFs,3 date formats,3 colors,brightness0,London/GB,mask0/10/31,
  intervals60/3/4 и5 previews. Это частичное наблюдение старого образа. Остались
  night/setup/crop/upload/responsive,mask/interval during fade,soak/heap/stack
  и physical acceptance. NTP scoped checks не превращать в полный H03 pass.
- Независимо от frozen main создана .worktree/small-tv-photo-settings на ветке
  codex/small-tv-photo-settings от cc65d379. Ветка завершена и отправлена:
  6ae7373f tests/evidence,459b93bd exact assembly EOL. Production C/BIN прежние
  DAF/C839/B06. Final2990 terminal exit0, output photo-settings-all-20261016-03:
  12 actual mask/interval scenarios,24 completed frames/0 pixel differences,
  14 consumer mutations pass.74 initial test files/57 production inputs/BIN/
  ELF/ROM/helpers/staged proof pass; ВМ набора закрыты.8 factory/native instruction
  ranges сохранены. Actual counter17 при60->3 корректен; формула учитывает >=.
  Preliminary30669 пропустил первый native frame после API wait; hardware capture
  двух кадров теперь идёт до response wait. Smoke4374 и final2990 подтверждают
  правильную работу неизменённого C. Main не сливать до terminal/publish96792.
  Branch suite/publisher/verifier уже требуют новый gate. Не подменять старый full
  новым scoped report; после интеграции обновить collector для photo_settings.
- Для H10 получен только layout audit ELF/SDK: root .build/small-tv-parity/
  native-memory-layout-20261016.json содержит heap/TCB/list offsets и source IDs;
  StackType_t здесь byte. Guest RAM не читалась, heap/stack/soak ещё не проверены.
  Browser skill/guidance/confirmations перечитаны; в этом этапе UI не открывался.
  Для H03 сначала cua.rewriteDocumentation, новый raw guest/tab; старые tab1 и
  ВМ закрыты, не переиспользовать прежний state dir без явной проверки источников.
- Подтверждённые factory bugs исправлять, метки/комментарии сохранять. Лишние
  software waits убирать; normal task yield, периоды эффектов и необходимый
  ST7789 timing сохранять. OTA/SD/audio не добавлять. Physical boards/QEMU
  не менялись; посторонние .karadio patches/tmp/.tmp_async_pdm не трогать.

## Исторические записи

Ниже сохранены прежние наблюдения. Их live handles и «следующие шаги» относятся
к моменту записи; порядок продолжения задаёт актуальный блок выше.

Последний завершённый этап: photo branch отправлена до `a8b119e3`.
Повторный `/setclocktype` с прежним номером теперь остаётся командой
переинициализации, как безусловный сброс флага `0x4200d854` у factory.
Отдельная временная ревизия и единый mutex snapshot восстанавливают команду
без новых NVS commits при неизменённых настройках; persisted ABI прежний.
Candidate app `2eb7bb69` / source `efc9fc36` / ELF `4dc4e444`, 1 176 480 байт,
свободно 359 520. Host3909 и platform45/1,182,288 pass. Batch47090 exit0:
тот же HTTP observer до/после, три перехода фото1/0/1, idle brightness,
84 полных кадра/9 сцен,10 frame guards и9 command guards проходят. Все ВМ
этой серии закрыты. Source/image/ELF/staged proof прошёл; assembly и scoped
reports сохранены в photo-reselect-checks.md ветки. Main ими не подменять.

Root92411 остаётся жив на AD7A: native classic calendar через
fractional-midnight. Все63 initial tests и BIN/ELF/QEMU hashes повторно совпали.
До terminal менять только контекстные Markdown. Затем сначала опубликовать
его19-group result, после этого merge всей photo ветки, root build/full suite
с новыми photo_frames/photo_brightness/photo_controls gates. Между переходами
проверки завершены; команды во время fade, browser/physical/soak остаются gaps.
Уточнение пользователя про программные задержки сохранено в software-delays.md:
убирать лишние ожидания после готовности данных, сохранять необходимый timing
и task yield. Дополнительных обоснованных удалений текущий просмотр не выявил.

Новая завершённая ветка `codex/small-tv-photo-frames`, worktree
`.worktree/small-tv-photo-frames`, отправлена до `2a949010de70`.
`57ef94ae` добавляет84 full photo/fade frames и9 canonical scenes на AD7A,
`31fce447` усиливает evidence/real decoder checks, `2a949010` исправляет реальный
photo-idle brightness bug. Factory POST50 сразу даёт duty4095; oldAD7A принимает
GET50, но держит819 до следующего фото. Новый candidateE3902939 / sourceB9787790 /
ELFD73C9146 (1,176,288 bytes/free359,712) применяет cached schedule на idle или
finished, сохраняя active fade. Сборка в firmware ветки; source/assembly proof и
same-observer before/after в `photo-idle-brightness-checks.md` ветки.
Все44 platform cases /1,182,252 checks, actual HTTP обеих app, повтор84 full
frames/9 scenes и10 negative contract checks прошли; owned VMs закрыты.

Root full92411 подтверждён живым: все machine/boot/waits/photo HTTP/AP->STA/
weather/scroll/SNTP/UTF8/regional/NVS stages прошли; идёт natural calendar
factory classic (через noon). Все63 initial test inputs и appAD7A/ELF6D7B
сохранены. Не менять root source/tests/helpers, не перезапускать этот handle.
После terminal сначала опубликовать его19-group result со сверкой initial pins,
затем интегрировать новую photo ветку, build root и полный набор с дополнительными
photo_frames/photo_brightness QEMU gates. Старый full результат не считать
проверкой E390 candidate. Collector archive_immutable_run.py уже адаптирован для
report_aggregation/machine_jpeg_inputs/photo_http этого19-group run; перед запуском
прочитать его текущий код. Phase0/1 до первого полного фото и изменения маски
во время fade/browser/physical/soak остаются отдельными границами доказательств.

Новый завершённый этап: исправлен подтверждённый чёрный экран при повторной
инициализации фототемы во время fade. Заводские init очищают дисплей, сохраняя
фазу 3…5, и теряют изображение до следующего интервала. В обеих программах
до исправления наблюдались все чёрные pixels и состояние [0,1]; настоящая HTTP
команда подтверждена аппаратной точкой на фазе 3. C теперь начинает фазу 0,
сохраняя следующий slot. Метка FIXED_FACTORY, инструкции и детали —
photo-reinit-checks.md. Candidate app6bf6a61c/source0baa7e03/ELF7de6fec2,
1 176 480 байт/free359 520 сохранён в firmware. Same-observer before/after:
новое фото/IP за1.094945 guest s,0 differing pixels. Batch77905 terminal exit0:
idle theme commands, brightness,84 frames/9 scenes и20 guard checks pass;
host3909/platform46/1,182,310 pass. Все ВМ серии закрыты. Четвёртый gate
photo_reinit включён в branch suite/publisher/verifier; другие scoped результаты
не переименованы. Root92411 всё ещё жив на AD7A: native dial fractional-midnight,
до terminal и публикации root19-group result исходники root/tests не менять.

Актуально после terminal handle47090 exit0: исправлен повторный выбор той же
темы. Factory0x4200d854 безусловно сбрасывает theme-init latch; старый C терял
команду при одинаковых bytes. Новый transient revision и единый mutex snapshot
восстанавливают reinit без дополнительных NVS writes. Candidate app2eb7bb69 /
sourceefc9fc36 / ELF4dc4e444,1,176,480 bytes/free359,520 сохранён в firmware.
Тот же actual HTTP observer до/после: старый E390 fail, новый три раза запускает
photo1/0/1, все pixels совпали, каждый переход1.04…1.12 guest s. Host3909,
platform45/1,182,288, idle-brightness HTTP,84 frames/9 scenes,10 frame guards
и9 control guards pass. Все ВМ этой серии закрыты; actual assembly и отдельные
scoped reports в photo-reselect-checks.md. Исторические E390/AD7A не заменены.
Root full92411 по-прежнему жив на frozenAD7A: native classic natural calendar
через us-spring, до terminal не менять root source/tests/helpers. После terminal
сначала19-group publisher, затем интеграция всей этой ветки и новый full suite.
Новая photo_controls проверка обязательна в branch suite/publisher/verifier;
photo_controls_contract объединяет прежний brightness и новый command contract.

Candidate проверки завершены: handle86675 exit0. E3902939/B9787790/D73C9146
прошёл actual HTTP idle brightness обеих app, повтор84 full photo/fade frames,
9 canonical scenes и10 negative contract checks. Все input/image/helper hashes
unchanged, все ВМ закрыты. Пакет results и actual factory/native assembly
сохранён в parity; platform44/1,182,252 pass. Это scoped candidate result,
полный root92411 на AD7A не завершён, source/test bytes main не менять.
Следующий шаг — дождаться terminal root run, сверить63 initial pins, опубликовать
его через 19-group publisher, затем интегрировать эту ветку с новыми photo gates
и выполнить полный объединённый набор. До этого candidate full parity не заявлять.

Подтверждён и исправлен photo-idle brightness gap: oldad7a9009 принимает HTTP50,
но оставляет duty819 до следующей фотографии; factory сразу4095. Один observer
до/после + новый C-case воспроизвели fail. Clock_task теперь применяет schedule
на idle/finished, сохраняя active fade. Candidate app e3902939 / source b9787790 /
ELF d73c9146,1,176,288 bytes/free359,712 архивирован в firmware ветки; все44
platform cases /1,182,252 checks и actual HTTP обеих app проходят. Повтор84
photo/fade frames сейчас идёт handle86675 (после успешного HTTP stage), source/
test/image bytes этой ветки не менять до terminal. Root full92411 жив отдельно
на ad7a9009, региональная стадия. Новые сведения — photo-idle-brightness-checks.md.

Новая ветка codex/small-tv-photo-frames от main6a02d8c0, worktree под .worktree.
Полный photo/fade baseline на том же ad7a9009/f411bf0e/6d7b586f/FDE3 прошёл:
84 QEMU frames (обе app × masks31/10/0, все фото/шесть фаз, day/night/dark),
0 differing pixels, плюс9 canonical raw scenes на реальном JPEG/glyph pipeline.
Production code не менялся, все ВМ закрыты. Новый branch gate включён в
suite/publisher/verifier, общий результат root92411 им не подменять.
См. ../qemu/parity/photo-frames-checks.md. Дальше проверить actual HTTP смену
яркости между фото: C вызывает backlight_update только на finished, тогда как
factory handlers ставят update flag для следующего main pass. Это пока
подозрение по коду, не подтверждённый runtime defect.

Живой новый full run: `.build/small-tv-functional/jpeg-integrated-full-20261016`,
shell handle `92411`, старт после commit `9a7e341c` (отправлен main). Initial pins
фиксируют 63 test source files, appad7a9009/ELF6d7b586f/QEMUfde38d53. Уже прошли
report_aggregation14, native3,884, platform43/1,182,204, frontend, integrity и
timezone_sources; идёт machine. Финального результата ещё нет. Опросить тот же
handle, не запускать второй run; root source/test/helpers заморожены. Контекстные
Markdown менять можно. После terminal сверить pins, затем штатные publisher и
verifier; при успехе обновить canonical raw scoped reports из этого же run.
Ignored collector `.build/small-tv-parity/archive_immutable_run.py` написан для
прошлого 17-group запуска: перед новым использованием добавить новые
machine_jpeg_inputs/report_aggregation/photo_http artifacts, не применять его
вслепую. Новый сборщик уже сохраняет DateKind String, восстановление дат не нужно.

Текущая интеграция: merge `3aede06f` включил JPEG branch28bfa638 в main и
сохранил JSON DateKind fix39e666e1, оба журнала и все 19 mandatory groups.
Root rebuild успешен: app `ad7a9009` / source `f411bf0e` / ELF `6d7b586f`,
1,176,272 bytes / free359,728. Архив firmware обновлён; source identity совпадает
с проверенным JPEG candidate131ce792, ELF/app root отличаются и не переименованы.
Actual instructions девяти функций — `../qemu/parity/native-jpeg-integrated.asm`
и manifest. Следующий full output: `.build/small-tv-functional/jpeg-integrated-full-20261016`.
Сохранить initial input pins, один живой handle, не менять source/test/helper
байты до terminal result. Полный positive checkpoint73687652 пока относится к
старому app0d8b7585 и 17-group набору; текущий root ещё не объявлен прошедшим full.

Актуально 2026-10-16, после предыдущих промежуточных записей:

JSON reader исправлен: общий Read-SmallTvTestResult использует DateKind String,
минимум PowerShell7.5 указан явно. Новый обязательный report_aggregation gate
проверяет 14 условий, включая настоящий повторный serializer/reader и aggregate.
Все шесть групп reduced host run pass; machine/QEMU для этой script-only правки
не повторялись. Полный завершённый checkpoint сохранён commit73687652 и остаётся
историческим набором до добавления этого gate. Следом объединить JPEG branch.

Полный root run `22926` завершён с exit0. Все 17 automatic groups pass;
84 natural calendar transitions / 168 complete frames, 24 completed scene frames
с 0 differences и 40 normalized scenes прошли. Все 58 initial test files,
app `0d8b7585` / source `9d9c5c8c` / ELF `97adeb91` / QEMU `fde38d53`
неизменны. Published functional-validation/validation и 21 scoped artifacts
обновлены из этого одного запуска. Для startup измерено .061207 guest s,
при held weather следующий кадр через .879886 guest s.

Первый publisher выявил автоматическое преобразование 207 ISO date strings
PowerShell ConvertFrom-Json в host timezone. Исходные child JSON корректны.
Агрегат восстановлен из всех 17 child files с проверкой, что изменилось только
представление тех же aware instants; raw results и исходный aggregate сохранены.
Audit: `../qemu/parity/responsiveness-report-aggregation.json`. После восстановления
строгие publisher/verifier прошли. Следующий шаг — DateKind String в сборщике,
затем merge JPEG branch, build и новый полный набор. Старые live записи ниже
теперь исторические; никакой terminal run не продолжать и не перезапускать.

- JPEG branch `codex/small-tv-jpeg-inputs` отправлена до `28bfa63881bb`.
  `9a59cb07` исправляет три header ошибки, `49a50986` — oversubscribed Huffman
  trees, `28bfa638` добавляет настоящий HTTP/flash upload/download и cold boot.
  Candidate app `131ce792` / source `f411bf0e` / ELF `9184b08b`, 1,176,272 bytes,
  сохранён в firmware этой ветки. Root app `0d8b7585` пока не заменён.
- Все 41 machine JPEG cases (12 valid / 29 invalid), 107 public assets с 35
  errors / 7 placements и 3,884 host checks проходят на candidate. Общий producer
  JPEG выделен в helper; после рефакторинга 41-case gate повторно прошёл.
- Permanent photo HTTP observer проверил 21 сценарий на четырёх процессах без
  debounce-пауз. Malformed363 раньше получал200/exists, теперь400/absent. Valid
  gray/RGB, chunks, busy/order/retries, точное скачивание, finish→cold boot,
  start незавершённой замены→cold boot и следующая загрузка проходят.
  settings_photo_size() уже сохраняет размер синхронно; гипотеза о RAM-only окне
  опровергнута, дополнительные flush/задержки не нужны. Подробности/точные hashes
  в `../qemu/parity/{huffman,photo-http}-checks.md` JPEG worktree.
- Root full run `22926` всё ещё жив: региональный HTTP/NVS и все 42 factory
  natural calendar transitions прошли; native classic/simple завершены, dial
  продолжается. Впереди complete scenes. Все 58 start test inputs и app/ELF
  оставались неизменными. Не перезапускать живой run и не выдавать его за terminal.
- До terminal result менять только эти context/log Markdown в root. Затем
  проверить исходные hashes, публиковать только настоящий результат, объединить
  JPEG branch, пересобрать root и выполнить полный набор с новыми обязательными
  machine_jpeg_inputs/photo_http gates. Ни один отдельный JPEG/photo report не
  заменяет весь suite. Browser cropper/photo-fade frames/soak/physical остаются gaps.

Ниже сохранены исторические записи; их «далее» и live progress относятся к
моменту записи. Текущий порядок действий задаёт блок выше.

Новый независимый результат: branch `codex/small-tv-jpeg-inputs`, worktree
`.worktree/small-tv-jpeg-inputs`, commit `9a59cb07`, отправлен в origin.
В нём закреплены восемь JPEG variations и 12 malformed cases. Найдены и исправлены
три подтверждённые factory/C ошибки: DQT ID 4 превращался в 0, игнорировалась
SOF precision 12 и лишняя component payload. Candidate app a33788db / source
731815d5 / ELF c2c6ae3b, 1,176,256 bytes / free 359,744 сохранён в firmware ветки.
Все 8 valid / 12 invalid, 107 public JPEG / 35 errors / 7 placements и 3,884
host checks pass; actual factory/native инструкции и before/after в branch
`Small_TV/qemu/parity/jpeg-header-checks.md`. Gate обязателен в branch full set,
но полный suite кандидата ещё не проходил. Main run 22926 НЕ заменён этой сборкой.

Далее исправить отдельный выявленный Huffman bug: 363-byte synthetic grayscale
с тремя 1-bit DC codes проходит draw в обеих прошивках и native validation.
Entropy использует первый код, поэтому прежний random-entropy mutation не ловил
отсутствие проверки дерева. Probe/fixture/report в
`.build/small-tv-parity/probe_oversubscribed_gray.py` и
`.build/small-tv-parity/jpeg-extra-fixtures/oversubscribed-gray*`.
Для before следующего исправления сохранён точный header candidate BIN/ELF
в `.build/small-tv-parity/jpeg-header-before-huffman/` (app a33788db, ELF c2c6ae3b).
Продолжать в JPEG worktree; root source/tests/helper bytes заморожены до конца 22926.

Последний live опрос 22926: пройдены все RV32 группы и QEMU boot/reset,
startup/weather waits, AP->STA setup, weather, field scroll, SNTP и UTF-8 обеих
прошивок. Идут региональные HTTP/NVS/cold-boot сценарии, затем natural calendar
matrix и complete scenes. Не выдавать эти промежуточные passes за весь suite.

Подробные исторические заметки JPEG-ветки (до объединения):

Новый permanent photo_qemu прошёл actual SDK HTTP/flash pipeline на app131ce792:
21 checks, valid gray/RGB, ten chunks, busy/premature/out-of-order/conflicting
requests, exact retries, download и четыре cold processes без debounce-пауз. Old app0d8b7585
в том же тесте публикует malformed Huffman JPEG363 (200/exists), candidate
rejects400/absent. Exact reports — `../qemu/parity/photo-http-checks.md`.
Общий byte producer вынесен в jpeg_test_fixtures; все 41 machine cases после
рефакторинга тоже pass. Production image не менялся, branch full suite ещё нужен.

Гипотеза о фоновом сохранении размера не подтвердилась: settings_photo_size()
уже вызывает settings_flush() синхронно. Firmware менять не нужно. Новый тест
останавливает VM сразу после finish и после start незавершённой замены: новая
длина/bytes сохраняются, незавершённый slot после cold boot скрыт, новая загрузка
доступна. Это границы HTTP-ответов, не произвольный power cut посреди flash write.
Фото-загрузка через браузер и actual completed photo/fade frames остаются gaps.

Huffman gap исправлен следующим child change: actual before принимал все 17
impossible prefix trees (DC1, AC1…16) в factory/native draw и native validation.
Новый uint32 prefix-space check отклоняет их до jd_decomp; 4 valid 1/16-bit
boundaries и прежние 8/12 cases проходят, всего 41. Public 107/35/7 и host
3,884 также pass. App 131ce792 / source f411bf0e / ELF 9184b08b сохранён в
firmware ветки, 1,176,272 bytes / free 359,728. Actual snippets/scoped evidence:
`../qemu/parity/huffman-checks.md`. Root full run 22926 не менялся, candidate
full suite ещё нужен. Следующий функциональный пробел — real HTTP photo
start/chunks/finish/download/reboot с valid/invalid JPEG, кроме уже проверенных
host adapters; затем интеграция ветки и общий повтор после terminal 22926.

Текущая отдельная ветка `codex/small-tv-jpeg-inputs`, worktree
`.worktree/small-tv-jpeg-inputs`, основана на main 41b972aa. Root full run 22926
продолжает проверять app 0d8b7585 неизменёнными source/test/helper bytes.
Здесь закреплены 8 synthetic JPEG / 12 invalid cases; исправлены factory/C
header bugs: DQT ID alias, ignored precision, SOF component length.
App a33788db / source 731815d5 / ELF c2c6ae3b, 1,176,256 bytes / free 359,744
сохранён в firmware. Новые 20 cases, 107 public JPEG / 35 errors / 7 placements
и 3,884 host checks pass. Exact instructions и scoped reports —
`../qemu/parity/jpeg-header-checks.md`. Branch gate обязателен; full suite ещё нужен.

Следующий подтверждённый дефект: synthetic 363-byte grayscale с тремя 1-bit
DC Huffman codes успешно проходит factory/native draw и native validation.
Первый random-entropy malformed case падал лишь позже; он не проверяет все
невозможные prefix trees. Probe/fixture/report в root
`.build/small-tv-parity/jpeg-extra-fixtures/oversubscribed-gray*` и
`.build/small-tv-parity/probe_oversubscribed_gray.py`. Добавить regression и
исправить построитель таблиц с сохранением literal factory observation.

Активный полный прогон: `.build/small-tv-functional/responsiveness-full-20261016`,
shell session `22926`. Запущен после commit `ad5b8c5d` на app `0d8b7585`,
ELF `97adeb91`, QEMU `fde38d53`. `inputs-before.json` фиксирует все test bytes
до старта. На этой записи handle действительно жив: пройдены native 3,884,
все 43 platform cases, frontend/integrity/TZ sources, basic machine/control,
classic и weather RV32; идёт machine_calendar. Не менять production/test/helper
bytes до terminal result; продолжать опрос того же handle, не перезапускать по
тайм-ауту наблюдения. Финального результата пока нет, старые positive reports
не перезаписывались. После завершения сверить start hashes с фактическими.

Отдельно, не меняя замороженный набор, проверены восемь дополнительных JPEG:
RGB 4:4:4/4:2:2/4:2:0, два restart-marker случая, grayscale и два odd-size.
Actual factory/native RV32 decoder дают 0 pixel differences во всех восьми.
Synthetic fixtures/probe/result находятся в `.build/small-tv-parity/jpeg-extra-fixtures/`,
генератор — `.build/small-tv-parity/generate_jpeg_fixtures.py`, probe —
`probe_jpeg_fixtures.py`. Encoder Pillow 12.3.0 из bundled runtime, MAXBLOCK=1MiB.
SDK read boundary подаёт generated bytes, firmware code и factory dump на диске
не меняются. После текущего full run перенести эти случаи в постоянный тест;
они ещё не часть его прохода. Malformed Huffman/restart и длительные/concurrent
сценарии по-прежнему требуют расширения.

Текущая интеграция main (2026-10-16): merge `12172b4d` принял все три
исправления offline/weather/startup и сохранил main calendar matrix. Установлен
QEMU main `962cda7a6f`, executable `fde38d53`; прежний c970591d и marker
сохранены в `.build/small-tv-parity/qemu-canonical-before-962cda7a/`.
Основная новая сборка: app `0d8b7585`, source `9d9c5c8c`, ELF `97adeb91`,
1,176,224 bytes / free 359,776. Различия с branch image identities не скрывать:
это root build и уточнённый комментарий factory_scroll_tick. Бинарники в firmware.
Exact compiled snippets девяти функций — `native-responsiveness-integrated.asm`.

Startup/weather observers включены в обязательный QEMU suite и publisher/verifier.
Общий WeatherFixture поддерживает явный hold/release внешнего ответа. Старое
требование frozen scroll в field_qemu заменено точными движущимися полями и
сохранением фазы. Preflight обеих прошивок прошёл: 110 native scroll frames,
offset 8..14 при RUNNING=1, после ответа 18 без reset. Scoped report —
`../qemu/parity/integrated-field-preflight.json`. Общий полный прогон ещё нужен;
ниже описаны исторические branch results, их не переименовывать в результаты main.

2026-10-16, software-delay audit: после app a2b6129b удалено также безусловное
ожидание startup при уже готовых Wi-Fi/SNTP. Кандидат app `743fa69f`, source
`2583ac4c`, ELF `7bda9d7d` сохранён в firmware; 43 platform cases / 1,182,204
checks и actual RV32 network regression прошли. Один и тот же QEMU observer
измерил ожидание после SNTP 13,353327 guest s на старом app и 0,040202 на новом;
полный первый кадр завершён за 0,101856. Дополнительный real HTTP weather-wait
regression тоже прошёл: RUNNING=1, новый кадр через .971445 guest s до ответа.
Точные инструкции, отдельные отчёты и оставшиеся delay —
`../qemu/parity/software-delays.md`. Общие published reports всё ещё старые;
startup/weather observers ещё требуется включить в полный gate, а frozen-scroll
ожидание в field_qemu обновить. Нельзя считать всю прошивку проверенной.

В QEMU candidate `962cda7a6f` / executable `fde38d53` добавлено отключение
внешнего AP через реальный 802.11 deauth, QOM station-ap-online. Все восемь
packet tests, 11 helper tests, SPI/I2C/SD, CYD/C3 legacy/modular boots и actual
HTTP AP->STA обеих прошивок прошли. Scoped real native app a2b6129b показывает
ход simple clock при connected=false и последующий reconnect; все три полных
кадра имеют 0 отличий от исправленной factory reference. Это graceful AP
shutdown, не внезапная RF-потеря. Canonical QEMU main/executable не заменён;
собственные ВМ закрыты. Более длинные outage/другие темы требуют отдельного gate.

Добиться функционального соответствия заводской прошивке. Подтверждённые ошибки
оригинала исправлять, как попросил пользователь. Намеренные исправления учитывать
отдельно от ошибок нашего переноса; полное совпадение пока не установлено.

Ветка `codex/small-tv-offline-clock` в `.worktree/small-tv-offline-clock`
восстанавливает активные часы/фото-fade и последний station IP при потере Wi-Fi.
Factory main `0x42008e56` и обработчик `0x4200c602` сравнены с настоящим compiled
C. Кандидат app `072135ee` / source `e10dd9f6` / ELF `eec972f2` собран и сохранён
в firmware этой ветки. Все 33 platform cases прошли; новый RV32 network gate
показывает fail старого app 9e4f856a и pass кандидата (четыре event traces,
16 factory dispatch states). Общие published reports ещё относятся к старому
app; candidate не объявлять прошедшим QEMU/full suite. Следующее: естественный
Wi-Fi disconnect/reconnect в QEMU, затем полный набор с обязательным
machine_network. Подробности/ограничения — `../qemu/parity/offline-clock-checks.md`.

Следующий child change удаляет software wait по weather_request_active в UI
по уточнению пользователя. App a2b6129b / source 246397dd / ELF 00ef2763 собран,
37 platform cases / 1,182,490 checks прошли. Actual external-HTTP QEMU test
before/after воспроизводит 6.735 guest s old wait и .932 guest s candidate
second-event frame при RUNNING=1. Результаты/точные compiled instructions —
`../qemu/parity/software-weather-wait-checks.md`. Старые reports 072135ee не
переименовывать. Нужны integration нового test в full gate, обновление прежнего
frozen-scroll ожидания field_qemu и full regression. Отдельный natural station
shutdown/recovery для app a2b6129b уже прошёл, как описано выше.

- Сопоставлять оригинальные инструкции с реально скомпилированным C ELF, а не
  только с псевдокодом Ghidra. Не менять исходный `Small_TV/full-flash.bin`.
- Если обнаружен интересный случай или пограничное состояние, добавлять тест:
  повторные вызовы, смена настроек/темы, ошибки SDK, незавершённые операции и
  сохранение состояния между шагами. По возможности показать сбой до исправления.
- Рефакторинг допустим в текущем участке работы: выделять повторяющийся алгоритм
  в общую функцию и проверять, что состояние и последовательность вызовов сохранены.
- По уточнению пользователя функции разделять по назначению и размещать в разных
  файлах и модулях: вывод на экран, сеть, настройки, хранение и другие подсистемы.
  Конвертеры форматов также держать в собственных модулях, отдельно от вывода,
  сети и хранения.
  Делать это по мере работы над соответствующим участком. Массовую
  переработку всего кода ради этого сейчас не проводить; сохранять поведение
  и проверять затронутые границы модулей.
- По уточнению пользователя ненужные программные паузы (`delay`, `vTaskDelay`,
  циклы ожидания) убирать, включая заводские:
  устанавливать их причину и влияние, устранять лишнее блокирование и отмечать
  намеренное исправление отдельно от parity. Проверять отзывчивость и работу
  таймеров после изменения; периоды часов и debounce не считать лишними без анализа.
- Выбирать осмысленные имена; объяснять назначение каждой функции и сложные места.
  Комментарии в C писать на английском. Исправленные функции маркировать по
  [CORRECTION_MARKERS.md](CORRECTION_MARKERS.md).
- OTA пока не добавлять. Обработка фотографий сохраняет удаление метаданных,
  изменяемую рамку кадрирования и масштабирование выбранного фрагмента до 240×240.
- Поля текста очищать и ограничивать собственными границами. Длинные город,
  описание и название погоды прокручивать туда и обратно с паузами; короткие
  оставлять неподвижными. Смена текста/темы сбрасывает фазу, обновление статуса
  сохраняет её. Прокрутка — запрошенное расширение, а не поведение оригинала.
- Сохранять сборки в `firmware/development/small-tv-esp32c2-reconstructed/`.
  Коммитить завершённые изменения отдельно, не включать посторонние правки,
  временные ВМ и журналы с пользовательскими данными.

## В работе: календарные переходы через SNTP

Последний завершённый участок (2026-10-16): в отдельной ветке
`codex/small-tv-offline-clock`, commit `b10ccf4c`, удалено startup-ожидание
после готовности station/SNTP; фото не ждёт SNTP. Сохранён тайм-аут 181 тик
для отсутствующих условий, остальные timer counters и task yield не менялись.
App `743fa69f` / source `2583ac4c` / ELF `7bda9d7d` сохранён в firmware ветки:
1,176,224 bytes / free 359,776. Все 43 platform cases / 1,182,204 checks,
RV32 network и повтор real external weather-wait test прошли. Один и тот же
startup observer на actual QEMU замерил 13.353327 guest s старого ожидания
против .040202 до нового renderer / .101856 до полного первого кадра.
Точные инструкции и отдельные отчёты — `Small_TV/qemu/parity/software-delays.md`
в этой ветке. Startup/weather gates ещё нужно включить в общий run-all;
field_qemu всё ещё содержит устаревшее ожидание frozen scroll. Main app/reports
пока прежние 9e4f856a; полного suite кандидата не было.

QEMU branch `codex/small-tv-wifi-link` отправлена до `962cda7a6f`, executable
`fde38d53`: runtime station-ap-online моделирует graceful external AP shutdown
настоящим 802.11 deauth. Восемь packet и 11 helper tests, modular SPI/I2C/SD,
CYD/C3 legacy/modular boots и actual AP->STA HTTP/persistence обеих app прошли.
Native app a2b6129b действительно продолжает simple clock при connected=false,
сохраняет station IP и восстанавливает HTTP; три полных кадра дают 0 отличий
от declared corrected reference. Это scoped проверка graceful AP shutdown,
а не длительных outage/RF/security. Canonical QEMU main/bin ещё 1c7e4c0512 /
c970591d; они не заменялись. Собственные ВМ закрыты, физических действий нет.

Ближайшее: объединить main calendar tests с app branch, добавить startup/weather
в полный gate, обновить field_qemu и повторить весь набор на новой QEMU. Ниже
сохранена история календарных attempts; разные запуски не склеивать в passed suite.

2026-10-16: новый `tests/calendar_qemu.py` готовит natural-transition matrix:
14 границ (Sunday/year/month/leap/noon, GB/US/AU DST, NP fractional offset,
post-2038), каждая в classic/simple/dial. Три date formats и оба hour modes
чередуются по случаям: все шесть сочетаний встречаются в каждой теме. Это
42 transitions / 84 completed frames на прошивку, не полный декартов продукт
всех параметров. Между before/after не разрешается новый NTP reply; ход часов
не подменяется. Наблюдаются реальные args/flags/calendar и все 57 600 пикселей.

Native календарь обязан совпасть с pinned IANA TZif; literal factory Newlib
исполняется отдельно и сохраняет implicit-DST ошибки. Чистый pixel reference
исполняет реальные factory renderers с ранее объявленными коррекциями; буквальный
factory replay сохраняет фактические flags/cache и entry background в отдельной
модели. Рабочая QEMU-прошивка не получает записей RAM/PC/регистров/инструкций.

Пробный Sunday прошёл во всех трёх темах отдельно для factory и native. Literal
factory replay даёт 0, native clean corrected reference даёт 0. В native один
POST занял 5.75 guest / 8.14 host seconds; H09/network latency этим не закрыт.
Новый helper измеряет обе длительности, не повторяет failed requests, ограничивает
ответ шестью гостевыми секундами и внешним wall guard 20 s. Old five-host-second
timeouts сохранены, не выданы за успехи или окончательно объяснённые product bugs.

Неверный NTP-log path и повторный breakpoint на прежнем PC исправлены в harness.
Native integer-Celsius field хранится как double: теперь проверяется точная
целочисленность и канонический Inputs использует int, как factory ABI. Поздний
city-triggered ответ не должен считаться ADV restart; перед ADV ждём реальные
initialized/sync flags. Stable factory наблюдение подтвердило saved host,
initialized client и отсутствие новой синхронизации в течение 3.01 guest seconds.

Full `calendar-final-20261016`, shell `97647`, завершился exit 1. Все 42 factory
перехода и первые пять reconstructed/classic прошли. Следующий `/SetTimeModeValue`
вернул 200 за 6.128 guest / 8.718 host s, превысив новый шестисекундный предел.
Это failed run, не общий passing checkpoint; native matrix не завершена.
Output `.build/small-tv-functional/calendar-final-20261016`; log
`.build/small-tv-calendar-full.log`. Новый полный результат не опубликован.
Приложение остаётся 9e4f856a, ELF 7e34a29b. Не повышать тайм-аут без изучения
транспорта; причина задержки пока не установлена.

Независимая ветка `codex/small-tv-offline-clock` в `.worktree/small-tv-offline-clock`
содержит исправление зависания активных часов/фото-fade без STA и подмены IP
адресом AP. App 072135ee / source e10dd9f6 / ELF eec972f2 собран и сохранён в
firmware ветки; 33 platform cases прошли. Новые реальные RV32 network traces
дают expected fail прежней сборки и pass кандидата: DHCP .15→.21, четыре retry,
сброс счётчика, сохранение IP; 16 factory main dispatch states продолжают темы
offline. Кандидат не прошёл полный QEMU и natural link-loss test, не в main.
Его scoped reports/ассемблер/описание находятся в worktree, не выдавать прежние
опубликованные общие результаты за подтверждение нового app.
Исправление/тесты/сборка сохранены и отправлены как `6f10bc46`; exact staged
50 production inputs, network/adapter bytes, 24 platform test/stub files,
LFS app и paired ELF сверены. Platform: 33 cases / 1,181,610 checks.

PCAP diagnostic `.build/small-tv-parity/http-latency-pcap-20261016-03` воспроизвёл
три медленных POST из 60: первый SYN не дал ответа, повтор через 5.82–5.94 guest s,
после прихода HTTP headers ответ через 42–49 ms. Это локализует фазу задержки,
но не доказывает RX DMA/SLIRP/SDK причину. Обезличенная сводка —
`../qemu/parity/http-latency-observation.json`; raw PCAP не публикуется.
Failed calendar summary — `calendar-transport-observation.json`.
Тестовая diagnostic VM закрыта. Создан отдельный QEMU worktree
`C:/Work/QEMU-ESP32/.worktree/small-tv-wifi-link`, ветка `codex/small-tv-wifi-link`,
от 1c7e4c0512. Diagnostics завершены: dedicated RX trace подтвердил no-descriptor
loss. Commits `6f3fa56a48` (trace), `9d4da15732` (C2 queue) отправлены в отдельную
ветку; remote SHA сверён. Candidate QEMU SHA e8122fe2, canonical по-прежнему
c970591d. C2 теперь удерживает head frame в существующей bounded queue до записи
RX_BASE_DESC, без poll/retry delay; C3 legacy path сохранён. Новый packet test
показывает fail только C2 на старом canonical и pass всех семи на candidate;
проверяет starvation 5 s, FIFO, queue limit и no duplicates. SPI/I2C/SD и
CYD/C3 legacy/modular boot прошли. 120 реальных HTTP POST: max .165376 guest s,
раньше trace-only QEMU давал 5.74/5.76 s. Scoped evidence
`../qemu/parity/rx-queue-candidate.json`. Это не полный firmware suite.

Native-only calendar shell 32961 завершился exit 1: все 42 transitions / 84
complete frames прошли, native везде совпал с IANA и corrected pixel reference.
Единственный отрицательный check — HTTP latency (max 6.195069 guest s), предел
не ослаблен. Scoped `../qemu/parity/calendar-native-observation.json` сохраняет
все samples и test hashes. Factory в этом attempt не запускалась; результаты
разных attempts не объединять в passing full suite. Freeze этого процесса снят.
Следующее: принять проверенный QEMU candidate и новый полный suite.
Для offline branch ещё нужна natural station disconnect/reconnect проверка.

По уточнению о программных паузах в offline branch убран отдельный software wait:
clock_task не пропускает active UI/fade пока weather worker pending/running;
cache защищён своим mutex. Media upload guard сохранён из-за частичного overwrite
photo slots. Новый negative platform case воспроизводит старую заморозку; после
изменения проходят все 37 cases, включая три clock themes и полный fade с pending
weather. Сборка app a2b6129b / source 246397dd / ELF 00ef2763 сохранена в firmware
ветки (1,176,144 bytes). Это новый candidate, старые offline scoped reports
072135ee не переименовывать. Actual-QEMU prototype before/after завершён:
прежний app ждал 6.535 guest s до следующего кадра и выходил только после weather
timeout; candidate дал кадр через .740 guest s при реальном REQUEST_RUNNING=1
и удержанном внешнем ответе. Prototype runs:
`.build/small-tv-parity/weather-wait-*-20261016-02`.
Переносимый постоянный test branch tests/weather_wait_qemu.py тоже прошёл:
candidate .932 guest s / RUNNING=1; old image 6.735 guest s / state=0, expected
negative. App/ELF/test/helper/code checks прошли, ВМ закрыты. Output
`.build/small-tv-parity/weather-wait-permanent-*-20261016`. Code/tests/build/
scoped evidence сохранены commit `e547d98a` в codex/small-tv-offline-clock.
Нужно включить test в full gate, обновить прежний frozen-scroll contract в
field_qemu под запрос отзывчивости и провести новый полный набор. Кандидат ещё
не в main; published general reports по-прежнему относятся к 9e4f856a.
Первый probe неверно считал RUNNING bit=2; исправленный читает реальный DWARF enum
REQUEST_RUNNING=1. Early failed harness attempts не являются доказательством bug.

Новый участок для последующего анализа: `settings.c` сохраняет через 1 s покоя;
factory dirty countdown начинает с 50 и сохраняет на 51-м eligible loop pass;
в loop передаётся delay 10 ticks. Реальный factory QEMU/GDB sample теперь
подтвердил около 100 ms для десяти ticks (98.5–109.5 ms, десять samples);
`../qemu/parity/factory-loop-delay-observation.json`. Эта задержка измерена,
а время body/render/weather в расчёт 51-pass модели отдельно не включено.
Игнорируемый persistence_probe использует явную модель 100 ms/eligible pass;
получает single 5.1 s против native 1 s, burst один save против трёх. Это
model timestamps, не измеренные RF/RTOS задержки. Счётчик
останавливается на blocking weather и не выполняется в setup branch. Адреса
`0x420090e2..0x420090f8`, save call `0x4200916a`, loop delay `0x42008fd2`;
bounded assembly в `.build/small-tv-save-delay-assembly`. Это установленная
разница алгоритмов, требующая отдельного теста/coalescing analysis, не закрыта
текущим календарным gate. Возможная связь с HTTP latency пока только гипотеза.

## Последний проверенный участок: завершённые кадры и яркость цифровой темы

2026-10-16: добавлен строгий gate полного кадра: реальные QEMU renderer entry/return
наблюдаются аппаратными GDB breakpoints без записи guest RAM/регистров/кода.
В отдельном Unicorn исполняются реальные RV32 renderers и JPEG/BMP. Все 57 600
пикселей сравниваются; поздний кадр после 40 virtual seconds строится с чистого
фона. Пройдены classic без/с погодой и dial, обе прошивки, по четыре кадра (24),
плюс 40 полных сцен с одинаковыми входами. См.
`../qemu/parity/completed-scene-checks.md`.

На прежнем app 446a5c3c первый цифровой кадр имел стартовую яркость 901/1000
при выбранной 1000. Read-only LEDC/GPIO observation отделил эту ошибку от
отрисовки: при фактической яркости отличалось 0 пикселей. Factory 0x42008e08
применяет backlight перед последующим digital render; наш объединённый init/render
передавал первый кадр раньше. В `clock_task` восстановлен этот порядок для
classic/simple. Новый платформенный тест проверяет duty во время передачи
цветных пикселей обеих тем, а не только после завершения кадра.

Новая сборка: app `9e4f856a45fb3526eb2032f08f948c1354e8ba80065d1b4b32242f2d0c94f03c`,
source `6ab9c80f0d245a4fdd977b6028a453d95a6156de6172ee959ced5284159db51b`,
ELF `7e34a29babbb85c1d9f8f5eac8f01ce48e7748952ed6d5c4dcb0e31bc91a7170`.
App 1,176,112 bytes, свободно 359,888; DIRAM 80,706. Full `scene-final-20261016`
прошёл из одного неизменяемого набора тестов: native 3,884, platform 29 /
1,180,724 checks, все RV32/QEMU groups и пять обычных scene pairs. Все 24
завершённых кадра совпали с replay. В 33 canonical classic scenes literal
factory/native difference равен 0; семь dial scenes совпали с явно исправленной
геометрией, буквальные отличия сохранены. Все 54 test inputs, 50 production
inputs, 106 TZif, font, LFS app и ELF проверены по staged bytes.

Код/тесты/сборка — `caad5d3c`. Current positive reports опубликованы для этого
app, включая `../qemu/completed-scenes-validation.json`; scoped negative
`../qemu/parity/first-digital-brightness-before.json` сохраняет старые app/ELF
и фактический duty 819. Запуск preflight с изменившимися test bytes не принят.
QEMU executable/source и физическая плата не изменены, созданные ВМ закрыты.
Полное соответствие всех путей не установлено: calendar/DST transport matrix,
дополнительные JPEG и concurrency/browser/physical/long-run остаются ниже.

## Предыдущий проверенный участок: региональные ключи и NVS v2

2026-10-16: восстановлены все 20 байт country slot, HTTP, raw import/export,
time/weather buffers и cache. NVS v2 = 364 bytes; v1 = 344 bytes мигрируется
по прежнему ABI с сохранением всех полей. Raw sector имеет прежние смещения
и приоритет. Нулевой legacy mode нормализуется только для v1; v2 mode 0
сохраняется. Неизвестный корректный ключ продолжает использовать GB fallback;
город не определяет часовой пояс. Details: `../qemu/parity/regional-settings-checks.md`.

Host проводит все 109 ключей через API/codec/persistence. Actual QEMU проверяет
все 15 regional keys (US/CA/AU/PT-AZ), clock/date pixels, weather cache, max
64-byte city + 19-byte region + full-width comma, rejected inputs и cold boot.
Настоящий SDK NVS fixture проверил все поля v1 migration и загрузку только из
NVS v2 после стирания raw sector в остановленной disposable VM.

`regional-final-20261016` полностью прошёл host/RV32/QEMU, все пять scene pairs:
native 3,884, platform 28 /
1,145,676 checks, timezones 109 / 36,404 comparisons,
JPEG 107, UTF-8 и transport gates. Сходство полных кадров не является критерием
parity; аппаратная плата, браузер и soak не проверены. Дамп не менялся.

App `446a5c3c5484c43a9f1645fd4e4487e62cf8443ccc4e76637c266ae4745d0bfb`; source `031eec92fad917e25cf7250e2427edb24524a7b29ae13cd90131101b0c766619`;
ELF `bde762ed5653506d3aadb65cb30c135dabef65f0b5da62cfa42b67375ac68da5`. App 1,176,096 bytes,
free 359,904; DIRAM 80,706.
Runtime heap/stack не измерены. Entry comments 157,
correction markers 50. Code/build commit `f27401af`.
QEMU main `1c7e4c0512`, compiled source `5e136b6eab`, executable c970591d unchanged.
Новые эмуляторные изменения и физическая прошивка не выполнялись.

Отрицательный `regional-before.json` относится к прежнему native app 2acdf34f:
AU-W обрезался до AU и показывал на три часа больше. `regional-factory-delay.json`
побитно подтверждает старую дату Jan 1 при обновлённом календаре Dec 31.
Оригинальная simple theme проверяется после штатного dial→simple re-entry,
наша — без него. AU-C/AU-E сохраняют объявленную factory implicit-DST разницу;
native обязан совпадать с IANA. Отрицательные результаты не переименованы в green.

Это предыдущий checkpoint; его app/source/ELF не переименовываются в новую
сборку. Перечень остающихся проверок расположен ниже.

## Предыдущий проверенный участок: новый сетевой профиль QEMU

Repo-owned `Small_TV/qemu/profiles/small-tv-c2.json` хранит schema 1 hardware,
factory SPI2/ST7789 wiring, network URLs/NTP hosts/SSID. `qemu/run.ps1` передаёт
его shared QEMU launcher; default state — `.build/small-tv-vm/<network>-<variant>`.
Standalone/full/comparator paths используют один профиль, weather/fields/text
fixture использует generic `service_port`. NTP/URL names остались factory;
profile не меняет compiled firmware endpoints и не содержит private keys.

QEMU kernel built from `5e136b6eab95345fa6889463dc5b0e3125d792ef`, source/helper main
`1c7e4c0512c68efd6e6d11276bfe7a13c070b7bd`, RISC-V executable
`c970591d626c7500cccd00121ba52667998ebeb091388acd2af46c22cc10bea6`. Установлен в canonical QEMU bin; прежний BF98..
и marker сохранены в `.cache/small-tv-profile-runtime-before`. Xtensa F6A.. прежний.
Own frozen worktree `C:/Work/QEMU-ESP32/.worktree/small-tv-service-profile`
(codex/small-tv-service-profile) оставить для следующих parity checks.

`service-profile-verified-20261014` объединяет реальные passing stages третьего
full attempt с fresh profile gate + пятью scene pairs после исправления seeder
signature. Успешные stages сохраняют точные unchanged input bytes. Все automatic
gates прошли на прежнем
app/source/ELF: host/native/platform/JS/integrity/timezone-source; RV32 renderer,
control/classic/weather/calendar/JPEG/timezones/time-state/text; profile 4;
реальный QEMU boot/reset/AP→STA/persistence/weather/fields/UDP SNTP/UTF-8 и пять
сцен. Source app не переписывалась. `qemu_profile` и publisher/verifier связывают
profile/launcher/comparator/compiler bytes; runtime guard проверяет стабильность.
Точные staged hashes проверяются перед коммитом. Source/app остаются ниже в
UTF-8 checkpoint; full functionality / physical RF/browser/soak ещё не доказаны.

Дополнительные evidence: packet DNS/NTP 6, shared helper 11, modular SPI/I2C/SD/CS
и CYD MMIO; legacy CYD + C3 legacy/modular boots. CYD boot LCD blank baseline,
LCD проверен отдельным MMIO; C3 OLED nonempty и legacy/modular hashes совпали.
Штатный wrapper/main runtime offline и clock boot/reset/SNTP passed. Public summary:
`../qemu/profile-compatibility-validation.json`; raw logs/flash не публиковались.

Неуспешные service-profile full runs сохранены: test-only old
weather-services property, затем service=weather trace. Generic service-hosts /
service=http expectations исправлены; target weather preflight прошёл обе apps.
Третий attempt дошёл до всех HTTP/time/UTF-8 passes, затем остановился на новом
optional SSID argument seeder. Исправлен comparator; scenes и profile gate
повторены отдельно и проверены точным unmodified validator из qemu_suite.py.
QEMU helper 1c7e4c исправляет ложное animation ожидание для static offline/setup;
clock animation остаётся обязательной. Main QEMU fix pushed; private user/source
images и physical devices не менялись. Owned VM/listeners закрыты после тестов.

## Последний проверенный участок: UTF-8 и поля текста

Строгий `app/text/text.c` decoder принимает Unicode scalars, а не произвольные
high-byte pairs. Известные A1E6/A848 и Unicode ℃/℉/°C/°F сохраняют factory
bitmaps. Неизвестный scalar без глифа -> '?'; malformed byte не поглощает ASCII.
452 bundled non-ASCII Spleen glyphs подготовлены в 16/24/32 cells, factory ASCII
сохранён. UTF-8 copy сохраняет прежний 15-byte бюджет погоды и полную границу
символа. Ширина/центрирование/прокрутка используют общий token decoder.
Новый URL escape явно ASCII-only, не зависит от locale.

`utf8-verified-20261014` объединяет прошедшие host/RV groups исходного full run
и полный повтор QEMU на pinned dependencies с теми же test/app/source bytes:
native 3,069, platform 26 /
1,145,647; JS/integrity, timezone_sources 9,
прежние renderer/control/classic/weather/calendar/JPEG/timezone/time-state.
Новый text RV32: 1,644 glyph comparisons,
195 full-panel cases, 219 scalar и
240 prefix/guard checks. Новый real HTTP gate прошёл
пять synthetic Unicode случаев, fragmented response, точные cache bytes,
все native field/guard pixels и полный scroll cycle. QEMU AP→STA/persistence,
weather/fields/actual SNTP и пять сцен тоже прошли. Сходство whole-frame остаётся
наблюдением; полного соответствия, physical/RF/browser/soak результата нет.

Factory UTF-8 `/updateCity` воспроизвёл NULL-client Load access fault в отдельной
VM: MEPC 4203e8f0, RA 4201098c, address c. `42010864` вставляет raw city bytes,
`42010988` вызывает perform без init guard. Native URL encoding/NULL-check
защищают этот путь; normal original flows использовали ASCII locations, чтобы
отдельно проверить Unicode JSON/cache. Source dump и физические платы не менялись.

Сборка: app 1,175,584, free 360,416,
DIRAM 80,650; app SHA
`2acdf34f68edccdfa9fd4753a22909598391ee23a6bc2e40e91737061a80f826`;
source `72ad106b1276f430f7f26b5e1a7fc6660f0174919f009d3591a70d660b64e1b5`;
ELF `570d62ad0547ae49a4bbe42b7deee586d319553f5565599d35635eaf5da6d2c5`.
Entry comments 155, markers
44. Public evidence:
`../qemu/parity/text-validation.json`, `../qemu/text-http-validation.json` и
`tests/functional-validation.json`. Старый negative text observation сохраняет
прежние app/ELF hashes. Native text/time-sync excerpts обновлены на точный ELF;
bounded factory temperature helper добавлен в existing assembly manifest.

Первый `utf8-final-20261014` дошёл до всех сцен, но runtime guard отклонил QEMU:
параллельное слияние изменило canonical HTTP-helper. Этот failed report сохранён.
Все QEMU checks повторены без overlay в собственном
`C:/Work/QEMU-ESP32/.worktree/small-tv-utf8-validation` на ветке
`codex/small-tv-utf8-validation`, pinned commit `5520fbb787` (parent b90e2131b8).
Использованы те же BF98.. executable и production app; fresh executable/profile/
helpers сохранились за повтор. Фактический client SHA
`222c3b17f3cf9fc4aed123fda4939678f7366076cd8f86373d3e59b630b22c94` записан в report.
Только реально прошедшая новая QEMU-группа заменяет rejected attempt; остальные
группы сохраняют исходные результаты и точные unchanged test hashes.
Чужие branches/worktrees не переключались. Worktree оставить для следующих
parity checks, пока параллельный main продолжает меняться; binaries в нём ignored.

## Завершённый участок: время и часовые пояса

`timezones.c`, `time_sync.c`, `clock_ui.c`, `timezone_oracle.py`. Настоящий
заводской `tzset`/`localtime_r` исполняется по адресам `0x420aa9c8`/`0x420aa5ce`;
новый C, Gregorian-переходы и `gmtime_r` исполняются из нашего ELF. Библиотеки
с прежними строками TZ совпадали, но дали 116 календарных отличий от IANA в
12 месячных выборках 2026 года для каждого из 109 ключей.

Добавлены закреплённые TZif IANA 2026e из wheel tzdata 2026.5, SHA и происхождение
в `resources/timezones/manifest.json`. Сохранён выбор по стране, fallback GB и
двухбуквенный интерфейс; длинные исходные ключи не добавляют выбор региона.
Генератор проверяет хеши/ключи, сохраняет полную историю и явные будущие правила,
дедуплицирует таблицы; TZif отмечены в Git как binary. Дисплей рассчитывает
календарь по текущему snapshot независимо от глобальной TZ; worker обновляет
фиксированное смещение libc при переходах, включая offline.

По запросу об открытом источнике добавлен `tools/update_timezones.py`:
`--check-latest` читает официальный IANA `tzdb/version`; download воспроизводит
закреплённый wheel tzdata либо требует все три новых version/SHA pins. Данные
пакета не устанавливаются и не исполняются. Кандидат сначала проверяется целиком;
`prepare_timezones.py --source ...` позволяет проверить его без замены текущей
базы. Обычная сборка остаётся офлайн. Проверены настоящая HTTPS-загрузка,
побайтовое воспроизведение 106 TZif/109 country keys и идентичный generated header,
девять офлайн-регрессий. IANA на 2026-10-14: 2026e, пакет 2026.5. В full suite
добавлен обязательный `timezone_sources`; старые опубликованные отчёты не
содержат эту группу и не являются доказательством нового полного прогона.

Текущий SNTP участок остаётся отдельным от обновлятора: atomic validity после
настоящего callback, pre-2025 и validity-change при том же epoch; пять literal /
восемь native RV32 случаев и две real clock-task темы. `time-network-ninth`
прошёл обе целые прошивки: отказ NTP 1/2 -> 3, reconfigure -> 2, 2024/2026,
backward leap day, post-2038 и reset/recovery. `0x42017ea0` вызывает restart,
enabled query находится в `0x4201bec6`, stop/init callback — `0x42017d34`.
Restart может прерывать 15-секундное ожидание следующего сервера. SDK сохраняет
server index при stop/init; тест не должен предполагать возврат на 0.
После reset использовать настоящие SYSTIMER ticks*5/52, RTC/HRT offset и system
correction; QEMU lifetime counter не равен SDK time-since-boot. Только QMP read /
stop/cont и внешние NTP packets; нельзя подменять guest clock/RAM/callback.

QEMU main `b90e2131b8` отправлен: service controls и документация; свежие CYD/C3/
модульные SPI/I2C/SD и пять network cases прошли. RISC-V SHA `bf98de89...33d44c`,
Xtensa `f6a5f293...3abc35`. Финальный app 1,115,104, SHA
`2a60eefcc480f96eced3e6318f91995f89b38475f93ce3551da1847c135f672c`, source
`9402fd83c7cef65222685deff3fbe6a98ad9cb197413da3d6af2b90536ace019`;
ELF `ee74d566d3d13a33c5d2ce767d8b7570efc853b6446d390b9d6646dc7793a394`.
Полный `sntp-final-20261014` прошёл и опубликован: native 3,021, 26 platform /
742,437, JS/integrity, timezone_sources 9, прежние machine/control/classic/
weather/calendar/JPEG, 36,404 timezone, 5+8 time-state и полный QEMU. В реальном
SNTP шесть UTC observations, максимум около 33 ms; все reset/date stages прошли.
151 production entry comments, 36 marker functions, DIRAM 80,650; 47 test inputs.
Код/сборка/тестовые инструменты — `6b7a52d3`; 48 production и 106 TZif совпали
с Git bytes. Результаты/журнал фиксируются отдельным коммитом.
Текущие отчёты связаны с этим архивом. Нижеследующий timezone baseline сохранён
как история; не переписывать старые negative/board identities. См.
`../qemu/parity/time-sync-checks.md`. Полное соответствие ещё не установлено.

Машинный gate прошёл 36,404 проверки: 109 ключей, все записанные переходы ±1 s,
будущие границы 2026/2038/2100/2400, дробные смещения, отрицательный DST,
fallback и пять ошибочных параметров. Ошибочный epoch сохраняет выходной календарь.
Прежний ABI-прототип ошибочно выравнивал named 64-bit argument; исправлен по
скомпилированным инструкциям: utc занимает a1/a2, output — a3.
Платформа прошла 24 случая, включая реальные worker и обе темы при изменении
страны/epoch с прежними секундами. Colon зависит от исходного timer event;
не подменять его фазу ожиданием нового полного кадра.

Сборка сохранена: app 1,115,008 байт, SHA
`4778377602bd3c596aba9640202fd40fb9420fb7a10b3da29c949a936a72585c`;
source `b1acb29646c238edda0018deac4e07042d5ff1187106bd4e9836fcdb4ffc875c`.
Полный `timezone-final` прошёл и опубликован: все host/machine/QEMU gates,
native 3,021; платформа 24 / 742,006; 36,404 timezone и прежние renderer/media
группы. В реальном HTTP field-потоке принято 110 native кадров прокрутки.
Архив и отчёты повторно проверены по хешам. App-раздел: свободно 420,992;
DIRAM 80,650; 148 entry comments, 34 функции с метками. Описание проверки —
`../qemu/parity/timezone-checks.md`. Порог валидности 2025, успешный SNTP callback,
transport retry/fallback и same-second gate оригинала — следующий отдельный
участок, этим исправлением не объявлены завершёнными. QEMU/платы не изменяются.
Текущие отчёты: `tests/functional-validation.json`, `validation.json`,
`../qemu/parity/timezone-validation.json`; scoped negative — `timezone-before.json`.
Исторические negative JPEG и CYD/C3 отчёты сохранены с прежними хешами.
Созданные для текущего прогона ВМ закрыты.
Код, тесты и сборка — `1e9fac91`; 48 production source files и 106 TZif
сверены с байтами Git index перед коммитом. В полном отчёте 44 test inputs.

Для следующего участка уже выполнен настоящий `0x42010b70` с синтетическими
epoch и SDK time/enabled/log boundaries. При 2025-01-01 18:14:07 публикуется
2025; скачок к 2026 с теми же h/m/s оставляет 2025. Настоящий callback
`0x420109de` выставляет sync flag, но корректное время 2024 всё равно игнорируется.
На 21-м обновлении сбрасывается retry counter; если SNTP stopped, очищается
initialized flag. Наблюдение — `../qemu/parity/time-cache-observation.json`,
это не passing gate и не транспортная проверка. Прототип пока в игнорируемом
`.build/small-tv-parity/time_state_probe.py`; перенести в воспроизводимый тест
вместе с будущим исправлением успешной SNTP-validity.

## Предыдущий проверенный участок: JPEG

`assets.c`, `tjpgdcnf.h`, `jpeg_oracle.py`. Исполняются настоящие RV32-декодеры,
callback и LCD blitter; подменяются только SDK flash/malloc/mutex и транспорт LCD.
Оригинал `0x42011624..0x420116c6` ограничивает IDCT-компоненты байтом до YCbCr.
Прежний `JD_FASTDECODE=1` давал отличия в четырёх status JPEG: 3/33/3/3 пикселя;
все 98 анимационных кадров и пять фото совпадали. `JD_FASTDECODE=0` восстанавливает
цвета. Код декодера third_party не переписан.

При ошибке после входа в `jd_decomp` известная область изображения очищается;
подготовка, недостаток malloc и discard-validation не изменяют экран. Старый
C сохранял смешанные полосы; оригинальный callback `0x4200c33e` вообще игнорирует
SDK-ошибку чтения. Метки и отдельный JPEG-документ объясняют причины.

Новый gate включает 107 изображений, 35 ошибок/повторов/валидаций и семь размещений,
включая отрицательные координаты и очистку при обрезанном выводе. Смещения кадров
native нужно читать из санитизированного GIF-контейнера; исходные смещения следующих
кадров отличаются. Ранний отрицательный midpoint подготовки с неверным ожиданием
очистки исключён: strengthened harness наблюдает реальный `jd_decomp` entry.

Текущая сборка: app SHA-256
`997769839e8a016cb1c86845410297cea4097b47580b820fe0a77492267e2ded`;
source `a754f79707a9f140c381c171101d5837ac9a7a62f9e6c8813c9a65491868434d`.
App 1,022,496 байт; свободно 513,504 в app-разделе. DIRAM 80,650;
runtime-память платы не измерялась. Entry comments у 142 функций, метки у 31.
Полный `jpeg-idct-final` прошёл: все host/machine/QEMU gates, 107 JPEG / 35 ошибок /
семь размещений. В реальном field HTTP-потоке принято 106 кадров прокрутки.
Отчёты опубликованы и проверены по хешам; все 46 production inputs совпадают с
байтами в Git. Код/сборка — `04f6438e`; JPEG-отчёты находятся в
`../qemu/parity/jpeg-validation.json`, `jpeg-before.json`. ВМ закрыты, QEMU и
физические платы не изменялись. Полное соответствие всех путей не установлено.

## Предыдущий проверенный участок

Дата и реальные HTTP-обновления: `ui_renderer.c`, `calendar_oracle.py`,
`field_qemu.py`. Оригинальные инструкции `0x4200b850`, `0x4200b0b2`,
`0x4200bd8c` проверены по сохранённому адресному ассемблеру.

Подтверждены два сбоя прежнего C: сравнение только `tm_yday` не замечало смену
года или календаря с теми же h/m/s и номером дня; простая тема оставляла края
длинной даты при выводе короткой. Отрицательный машинный тест — 48 сбоев из 96,
до 411 лишних пикселей; `../qemu/parity/calendar-before.json` и две картинки
относятся к прежнему app `d89542e62f823c0862c6e4d15b618ecc5e416ea5d87a9d21b7ae7d00cc591bd5`.

Общая `calendar_changed` сравнивает year/month/day/yday. Дата простой темы
очищается в x=0…239, y=180…203, не затрагивая weekday/IP. Новые 96 RV32
сценариев и два теста реального clock_task прошли. Исходная исправленная модель
объявляет только clock/minute event, Sunday и очистку даты; оригинальная ветвь
и её отличия сохранены. SNTP-транспорт при скачке epoch этим тестом не проверяется.

`field_qemu.py` проверяет настоящий `/updateCity` и ответы локального сервиса.
Город/название/иконка сравниваются с независимыми исходными bitmap и соседними
полосами. Прокрутка достигает обеих сторон и пауз; задержанный ответ удерживает
кадр/фазу. После нового поколения погоды нужно дождаться подтверждения рендерера
и сохранить фазу. Смена темы сбрасывает её. Проверены короткая строка, ошибка
сервиса, восстановление и неизвестная иконка. QMP только кратко останавливает
наблюдение и возобновляет ВМ; RAM/регистры/код не подменяются.

В реальном заводском HTTP-потоке короткие подписи могут очищаться полной
переинициализацией экрана: остатки текста в прямых incremental-вызовах не приписывать
каждому `/updateCity`. При неуспешной погоде старая иконка с ненулевым указателем
всё же остаётся — это подтверждено. Неизвестная иконка в отдельном HTTP-переходе
может дать пустую область; не обобщать этот результат на все пути декодера.

Код даты/сборка — `a3b35c8c`, network/общие проверки — `0c961908`.
Полный `.build/small-tv-functional/calendar-http-fields-final/report.json`
прошёл: native 3 021, платформа 21 сценарий / 741,961, JS, целостность,
машинные renderer/control/backlight/classic/weather/calendar и QEMU обеих
прошивок. В сетевой прокрутке наблюдались 107 корректных кадров,
новое weather generation подтверждено рендерером до проверки сохранения фазы.

App SHA-256 `5e12da8c5b20740316f17da954b7ce8bc250e06b04e2f1e4f1095ccf484acc44`;
source SHA-256 `fdaf71adcda5d52aa288989fa7872115c53c328c3219818272e36e4dc301246d`. App 1,022,416 байт,
свободно 513,584 в app-разделе. DIRAM 80,650;
runtime-память платы не измерялась. Entry comments у 142 функций, метки у 30.
Актуальные отчёты: `tests/functional-validation.json`,
`../qemu/parity/calendar-validation.json`, `../qemu/field-http-validation.json`.
Перед повторным использованием после новых правок проверять app/source/test
хеши. Полное соответствие всех путей остаётся неустановленным.

## Следующие участки для исследования

Остаются явно не проверенные или не восстановленные пути:

1. Расширить реальные UDP-проверки midnight/Sunday/country/DST/всех тем/форматов.
   SNTP validity/retries/same-second cache/reset уже проходят обязательные gates,
   IANA helper исполняет libc, но весь transport/locale путь ими не покрыт.
   Unicode gate охватывает bundled 452 scalars и '?' для остальных; это не все
   письменности, shaping/bidi/NFC или полный fuzz всех HTTP input strings.
2. JPEG: новый gate охватывает все публичные ресурсы и ограниченные ошибки/обрезку.
   Произвольные пользовательские JPEG, разные subsampling и malformed Huffman/
   restart marker требуют дополнительных фикстур. Старый classic oracle сохраняет
   media-вызовы как границу; новый complete-scene gate исполняет renderers и
   JPEG/BMP вместе, дополняя отдельные decoder gates.
3. Проверить более длительные сетевые/загрузочные сценарии и расход памяти во
   время работы. Аппаратные и браузерные сценарии описаны в `tests/README.md`;
   их нельзя объявлять выполненными по результату других тестов.

4. Расширить полные кадры на другие настройки, цвета/яркости, длинные поля и
   переходы тем. Canonical classic/dial и 24 actual completed frames уже проходят
   строгий gate без масок, но не исчерпывают все состояния. Известные factory
   corrections и разная фаза кадра не должны скрывать ещё не восстановленный
   путь. Scene similarity percentage остаётся наблюдением, не критерием parity.

## Проверки и репозитории

`tests/run-all.ps1` запускает C, платформенные/JS/артефактные проверки, машинные
сравнения и QEMU. После успешного полного запуска `tests/publish-report.py`
публикует компактный отчёт, а `tools/verify_artifacts.py` обновляет размеры и
счётчики в `validation.json`. Проверять соответствие отчётов текущему архиву.
Количество проверок и сходство снимков не являются процентом покрытия или
доказательством полной идентичности. Синтетическая погода не проверяет живой сервис.

QEMU находится в `C:\Work\QEMU-ESP32`. Исторические полные прогоны используют
`codex/flash-write-audit` (`0860e568`, RISC-V `20b133d9`). Новый host-forward
модуль находится отдельно в `codex/hostfwd-backlog` (`79badcba2b`, реализация
`b068387b7a`, RISC-V `d64f3013`, Xtensa `cd1163c3`). Его короткие сетевые,
NOR/SPI/I2C и C3 OLED тесты успешны, но CYD PHY/cache сравнение не принято;
новую ветку в main не сливать до расследования. Полный прогон 0592 на 20B
успешен (19 групп, 539 входов); это не полный прогон на новом QEMU. Сохранять
совместимость CYD и ESP32-C3 OLED. При изменении эмулятора выполнять их регрессии.
Закрывать созданные для проверки ненужные ВМ. Физические платы в текущих
проверках не прошиваются.

`tools/assist_c_port.py` теперь имеет рабочий review CLI и отдельные tests;
не считать его автоматическим генератором эквивалентной C-прошивки. Чужие
файлы `.karadio-*.patch`, `tmp/` и другие
посторонние изменения не относятся к этой задаче.

## Супервизор и незавершённые длительные проверки, 2026-10-18

BC68/20B H10 прерван после 336 циклов: host workload/supervisor исчезли без
footer. ENOSPC рядом по времени — наблюдение, не установленная причина.
Сохранены 31+11 исходных входов и все сырые материалы; после архивирования
осиротевшие VM/guard завершены по проверенным handles без новых QMP/RSP.
Документальная фиксация — `9696e433` в `codex/small-tv-h10-ap-services`.

Исправления Windows-супервизора выполняются в отдельной ветке
`codex/small-tv-runtime-supervision`. Очистка процессов/логов и атомарная запись
состояния разнесены по `runtime_cleanup.psm1` и `runtime_state_io.psm1`.
Обработка ошибок имеет метки `FIXED_TEST`; гостевой C-код, его таймеры, archive
app/ELF и factory dump не меняются. Проверки и границы их смысла описаны в
`tests/RUNTIME_SUPERVISION.md`; не заменять коротким preflight полный H10.

Не редактировать старые frozen деревья jpeg-uploads и h10-ap-services, их
WORK_LOG/WORKING_NOTES и 539/31+11 входов ради обновления контекста. Актуальные
добавления ведутся в этой незамороженной ветке и `Small_TV/qemu/parity`.
Следующие обязательные шаги: расследовать CYD-разницу, выполнить полный набор
на окончательной паре 0592/новый QEMU и затем полный H10 с проверкой живых
process handles, footer, UART и memory trend. Физическая плата не прошивалась.

## Актуальный контекст: отдельные reset-проверки, 2026-10-18

Рабочая ветка codex/small-tv-reset-display. Старые jpeg-uploads, H10 и
small-tv-runtime-supervision frozen; их src/SDK/archive/snapshot не редактировать.
Результат failed full553 сохранён bc9aff58; ложное условие объединяло
ROM reboot и мгновенный кадр после network-ready. Готовность сети и дисплея
теперь имеют независимые observers, tests и решения. См. tests/RESET_SUBSYSTEMS.md.
Наш app0592/ELFaea10675/sourceD338 и QEMU D64 неизменны. Новый helper лежит
в отдельном QEMU tools/small_tv_display.py; его fingerprint добавлен в связанные
input registries, чтобы публикация не принимала старые зависимости.
Native short: original +3 reconstructed pass. Требуются terminal полный suite,
продолжающийся H10 (его sole QMP/RSP принадлежит workload) и расследование CYD.
Следующие записи после freeze полного прогона вести только в qemu/parity.

## Текущая ветка JPEG headers, 2026-10-18

Активное изменение — codex/small-tv-jpeg-headers (sparse checkout Small_TV,
archive variant, .agents). Старые frozen src и snapshots полных561/557/553/539
и H10 не редактировать; их active identities см. в parity progress full561.
Новая сборка F1ADA8B4/91E26EB2/sourceF849F5BF исправляет подтверждённые factory
DRI/SOS/DQT/component-ID acceptance bugs. Изменены лишь tjpgd.c/tjpgd.h;
существующие JDEC offsets сохранены, размерRV32 увеличен на4bytes.
133native/107public/41oldInputs+128DHT/HTTP/host5531/artifact6 проходят;
before133 и before HTTP сохранены как отрицательные. Это не full/H10 F1.

Далее: сохранить exact evidence и focused commit, выполнить full наF1/D64,
подготовить длительный workload той же версии. Old0592 H10 не объявлять
доказательством новой версии. Наблюдать живые процессы, не делать повторный
запуск только из-за timeout наблюдения. Не добавлятьQMP/RSP клиентов к H10.
Отдельно остаётся classic ESP32 CYD PHY path0x60033c00; QEMU ветка не в main.


## 2026-10-20 — двусторонняя сверка переноса

Просмотрены все16 reference modules и26 app C modules. Явная карта
reference/correspondence.json:176 factory (120app/56SDK),168native app,
13TJpgd+116cJSON,11assembly-only codec entries.198direct factory callees
вне выбранного экспорта перечислены, а не объявлены автоматически перенесёнными.
Найдены HTTP-404 (Host/root/absolute redirect), CITY-REINIT (updateCity снимает
factory theme-init latch), HTTP lifetime multi-peer test gap, RESET/DC pulls
и устаревшая coarse navigation. Подробности reference/BIDIRECTIONAL_AUDIT.md.
Checker+10tests проверяют пропуски в обоих направлениях/опечатки/stale inputs,
не доказывают semantic equivalence. В native run добавлен обязательный gate.
Firmware C8FD пока не менялась. Frozen B50D full завершился exit0 в10:56UTC;
H10 всё ещё running, никаких новых QMP/RSP к нему не подключали.


## 2026-10-20 — terminal B50D full suite

Полный regression B50D/ELF85FCCF/sourceFC337C завершён:19automatic groups
passed, hardware_browser_soak not_run, controller exit0/terminal_passed
2026-10-20T10:56:30.2074153Z. Исходный report4.5MB иfooter сохранены без
изменения байтов (gzip) вqemu/parity/raw/b50d-full-20261020; certificate
qemu/parity/b50d-full-terminal-20261020.json. Это результат B50D, неC8FD/54F4
и не24h H10. Frozen tree/snapshot не редактировались. H10 supervisor11:56UTC
всё ещё running,396cycles,cleanup_errors[]; наблюдение только через его файлы.


## 2026-10-20 — исправлен найденный HTTP-404

Factory0x4200d4be: AP Host/нетHost ->root200, foreignHost ->absoluteAP302.
Наш unconditional relative redirect исправлен; factory substring bug с именем
192.168.43.1.example.invalid подтверждён в реальной factory VM и исправлен.
STA сохраняет local redirect, поскольку setup AP там не активна. Два старых
теста закрепляли неверное поведение, исправлены с FIXED_TEST. Новый тест
до изменения кода падает; после —5608native checks и10audit controls pass.
Новый network-only captive_qemu.py:factoryAP/nativeAP/nativeSTA,15HTTP cases,
59inputs unchanged, noLCD/noRSP, all3owned VMs stopped. Proof+before/failure/
after logs+matchingELF: qemu/parity/captive-portal-validation-20261020.json.
Production archive:app54f441af...,1170240bytes/free365760; ELF83ed2a7a...,
source9c16c56a...; DEBUGoff, oldTJpgd, libjpeg notlinked. Physical board,
full suite и24h новой54F4 не запускались. B50D full/H10 ей не приписывать.
Карта refreshed только для повторно просмотренного server.c; source-only
coverage не превращается вsemantic proof. Далее CITY-REINIT, AP multi-peer
HTTP lifetime и RESET/DC pulls; остальные оговорки вBIDIRECTIONAL_AUDIT.md.

Archive integrity:6tests pass; image checksums/partition MD5/current compiled sources/media/34routes/original dump unchanged. Report preserved with captive proof.


## 2026-10-20 — интеграция завершённых worktree

Объединены jpeg-library B3FC и боковые selector/header/H10/reset/flash-full
records; код54F4/source9C16 не меняется.277review inputs exact,5608native,
10inventory controls и6artifact checks pass в отдельнойintegration-worktree.
Единственный конфликт WORK_LOG разрешён сохранением актуального текста:
входящие непустые строки уже есть. Подробности Small_TV/WORKTREE_INTEGRATION_20261020.md.
Удаление7завершённыхworktree —после verified local archives иpush main;
active selector H10/CYD инезакоммиченные C3/ESP8266 сохраняются.

## 2026-10-20 — очистка после опубликованной интеграции

В main опубликован 678f6ac37 с проверенной интеграцией Small TV. Удалены семь
завершённых рабочих копий и временная integration-worktree; все ветки сохранены.
Полные локальные архивы семи копий проверены до удаления и повторно по SHA-256
после него: .build/worktree-retention/integration-20261020/. Shared SDK сохранён.
В реестре остаются основной checkout и семь активных/незавершённых worktree;
H10/CYD не прерывались. Пользовательские изменения root совпадают с начальным
inventory. Код и firmware не менялись; тесты повторно не запускались.
Подробности: Small_TV/WORKTREE_INTEGRATION_20261020.md и машинный отчёт.

## 2026-10-20 — актуальный checkpoint JPEG/NOR

Продолжение цели IMPROVEMENT_PLAN в `.worktree/small-tv-improvement-plan`, branch
`codex/small-tv-improvement-plan`. Root checkout с посторонними C3/ESP8266 изменениями
не трогать. Основная UI firmware3E03/ELF54293 всё ещё TJpgd,1170432bytes. Prepared
NOR/guard/journal/transport/espidf/scratch/coefficients/decoder modules не означают
включённый новый JPEG в UI. Завершённые progress commits идут послеccb29b1db.

Новый codec/jpeg_backing — actual adapter API→shared scratch/NOR, raw или packed
coefficients, noheap/globals; RV32handle600 +caller bitmap15 +NOR4352. IDs/constant
capacity сохраняются между jobs, first-use bitmap сбрасывается, dirty abort не
пишет. Весь запрос проверяется до sector preparation. Deadline/quota из callback
не маскируются generic I/O; owner читает transport.last_error после STATE.
Callback cause хранится в decoder diagnostic до cleanup, не брать его из
backing.last_error после успешного close.

Host61images/7limits/10negative/827physical faults/48stops/12transitions,
15273unit assertions/134partial+silent faults/6compiled mutants pass. Стандартный
stdio contract63/7/10/1197/12 также pass. Probe0F637039/ELF040300F8/source15AB27CD
с matching stamped assets сохранена отдельно в firmware/development/small-tv-jpeg-decoder-probe.
Полный decoder/NOR pipeline исполняется в собственном C2 QEMU:45576requested heap
peak,1988/4096stack free, без UI/Wi-Fi. FullCMYK12 занимает около39–45guest seconds;
это не hardware benchmark. Первый observer ошибочно требовал изменённые bytes на
повторной записи тех же данных; исправлен FIXED_TEST, сохраняются полные flash images.
Подробности tests/JPEG_BACKING.md и qemu/parity/jpeg-backing-validation-20261020.json.

Далее source/upload privacy + journal invalidation + physical source/frame SHA +
durable RGB565 cache и matching assets deployment с сохранением photos/settings.
Validation и cache generation — один decode; redraw готового кадра без повторного
multi-scan decode/flash writes. Затем UI link, реальный общий RAM/stack/time, HTTP/
reset/power-loss, независимые LCD/network/full/24h/hardware. Не закрывать цель.
Старые H10/frozen46payloads+manifest/SDK readonly; ни QMP/RSP, ни stop для oldH10.
Все новые процессы принадлежат только standalone probes; после tests reap owners.

## 2026-10-20 — следующий checkpoint persistent cache

Предыдущий goal turn69f138125 — progress; цель прежняя, не завершена. В этой же
clean worktree добавлены storage/jpeg_cache и tools/jpeg_cache_layout. Полный
source→decoder→rows→physical verify→journal→cold readonly cache workflow работает
на host с actual libjpeg, не только synthetic producer. Native UI3E03/TJpgd и
standalone target probe0F63 не менялись; новый cache на C2 ещё не исполнялся.

Cache handle5600RV32 включает journal1032+frameNOR4352; borrowed layout156/devices72,
scratchNOR/backing/decoder/SHA отдельно. All9roots cache+NOR+journal ET_REL9016code/
16rodata/static0, maxcacheframe336/maxjournal448. Не whole UI heap/task stack fit.
Source102400 limit — отдельный SOURCE_LIMIT с required/available, без decoder/
source reads. Code identity генерируется из actual archive SHA, patches, codec/
converter/storage sources и geometry. Codec change не требует изменения ownership
resources, но matching assets/deployment и сохранение user photos/settings ещё нужны.

Критическое: before/after source SHA не обнаруживала silent read внутри decoder.
Реальный fault378 публиковал wrong pixels, cold hit их повторял. Исправлено
FIXED_RECONSTRUCTION в jpeg_cache_read_source: fresh256byte readbacks до передачи
данных decoder. Все218actual input/readback points теперь отвергаются без READY;
before inputs/output и9runtime mutants сохранены. Cache readback SHA обязан читать
весь PHYSICAL frame после flush/reopen; test observer проверяет этот объём отдельно.

Final host:59JPEG240×240/5source refusals/6negative,268fault recoveries/18stops;
12120physical cuts+946SHAfailures+2424stops,9mutants,10generatorrejects и старые
sampling argc5 byte-identical8/12. FullCMYK12:1decode/2703104program/144erases;
cold hit0decode/0program/0erase, exact BE98FC78 pixels. Всё ещё host only.
Proof qemu/parity/jpeg-cache-pipeline-validation-20261020.json; tests/JPEG_CACHE_PIPELINE.md.

Следом native media owner/build/deployment/privacy/HTTP+target runtime. Не вставлять
40секундный decode под нынешний общий media_mutex: photo_upload_finish держит его,
UI вызывает media API. Нужен owner/worker protocol без нарушения source serialization
и отзывчивости UI/HTTP. После integration shared RAM/stack/time, reset/power-loss,
independent network/LCD/full/24h/hardware. Старые SDK/H10/frozen read-only, no QMP/RSP.


## 2026-10-20 — offline dependency/main build checkpoint

Текущая worktree/branch прежние. Goal active, предыдущий read-only ответ о
сокращении записей —no implementation progress; этот turn реализовал production
build. Не возвращаться к повторному исследованию vendor workflow: теперь есть
third_party/libjpeg-turbo/upstream.tar.gz +3qualified patches/licenses и tools/
build_jpeg_library.py. build.ps1 автоматически собирает dependency, app CMake
компилирует11codec/storage sources; API roots GC, UI/upload по-прежнему TJpgd.
Production .a D690BDF3 и configured headers побайтно одинаковы с old RV32 qualified
library; Os был и прежде в actual Ninja FLAGS, несмотря на O3 в CMakeCache.

Main archive app676C5EDF/ELF CB84E536/source2D1FB659,1170432bytes,365568free;
assetsBB4469E3 unchanged. Native5806/13dependency/12inventory/10generator/6artifact
checks pass. Explicit source inventory459/170app. No new VM, SDK tracked clean,
шесть protected H10 owners present. Локальные logs .build/jpeg-main-20261020;
доказательства qemu/parity/jpeg-dependency-build-validation-20261020.json.
Build helper refuses incomplete/corrupt cached output; use fresh dir on failure.
No source edits during build: post-link input recheck fails. Builds archive in
firmware/development; no push in this turn.

Next REAL integration: media owner/worker and privacy, not another decoder probe.
Source/journal invalidation before upload writes; one decoder+verified RGB565 cache,
source readback protections; no global media_mutex across slow decode. SDK async
HTTP begin/complete can retain legacy OK after actual finish; inspect server
lifetime and request/body ownership. Current UI has explicit upload_active pause,
remove with slot-scoped protection. Current privacy parser baseline-only: needs
strict metadata-only multi-scan scanner allowing only fixed JFIF/structural Adobe,
all EXIF/COM/etc rejected even between scans. Keep JS crop/resize/privacy.

Factory baseline photo pixel parity matters: compare TJpgd vs libjpeg output;
consider a purpose-specific baseline adapter/strip cache if needed rather than
silently changing factory pixels. UI has1920byte DMA buffer, NOT a115200byte full
framebuffer. Real combined heap/task stacks/time remain unverified. After owner
integration deploy matching guard/cache headers/assets without erasing user photo
slots/settings, then independent LCD/network/full/24h/hardware gates. Old H10/SDK/
frozen46payloads+manifest readonly, no extra QMP/RSP or stop for old H10.


## 2026-10-20 — live upload privacy gate checkpoint

Предыдущий goal turn b4b7834e9 —implementation progress. В этой же worktree
реальный photo_upload_finish теперь вызывает codec/jpeg_privacy. Старого
baseline-only marker scanner больше нет; entropy/dimensions всё ещё проверяет
TJpgd. Privacy module accepts fixed JFIF(no thumbnail)/canonical Adobe and scans
все SOS/entropy/inter-scan markers доexactEOI; rejects other APP/COM/trailing.
Domain statuses include I/O/stop/truncated/metadata separately. No private strings
in diagnostics. Cache CODEC_INPUTS includes policy. Don't reimplement this gate.

3727unit controls (45metadata positions/353truncations/2readfaults/343stops,
FF00crosses255/256),63actual qualifiedJPEG/5private+trailing rejections and
7compiled mutants pass. Ordinary tests/run.ps1 now also runs direct privacy gate;
old5806native checks and6artifact checks pass. Inventory469/172app,12controls.
Target module maxcompilerframe368,1224code+180rodata,0data/bss (not whole HTTP stack).
Main app733C006A/ELF C1F1D94B/source4C8C3878,1171136bytes,364864partitionfree,
DEBUGoff; assetsBB4469E3 unchanged. No new VM/runtime/hardware claim. Saved in
firmware/development; tests/JPEG_PRIVACY.md and qemu/parity/jpeg-privacy-validation-20261020.json.

Next: actual media owner/worker integration, not another standalone module/probe.
Reuse existing privacy/cache/guard/decoder. Current upload state+source serialization
must split short media_mutex from slow codec mutex. Need async HTTP begin/complete,
keep body/request lifetime, invalidate journal BEFORE source erase/write, persist
source length only after privacy+ONE decode+physicalcacheverify. Worker low priority
may use idle-priority time slicing to let idle/WDT run without arbitrary vTaskDelay;
verify scheduler settings, don't assume. UI should try codec mutex0 and keep clock/
immutable animations running, no blanket upload_active pause. Avoid read-modify-write
of selected source while UI reads; use owner state/short locks. Retry/failure/timeout
must release ownership and all async requests. Own all new VM handles; oldH10 untouched.

Baseline factory pixels still need comparison; consider TJpgd strip producer into
cache for supported8baseline rather than silent IDCT/color rounding drift. Include
producer/Tjpgd config/source in cache codec ID if used. UI has1920byte DMA, not full
framebuffer. Then matching assets/cache-header deployment preserving photos/settings,
combined heap/stack/time, independent LCD/network/full/24h/hardware. Goal active.
User asked about backdoor: existing static audit Small_TV/analysis/security/README.md
finds no confirmed malicious path but unauthenticated management/open AP/plaintext
weather/unsafe factory bounds. Don't claim whole-image absence; full audit pending.

## 2026-10-23 — current real main integration checkpoint

Do not repeat standalone integration work: UI/upload now call photo_codec/cache
through photo_worker, SDK async start/finish and matching stamped assets. Baseline
factory TJpgd pixels preserved via strip producer, extended modes via real libjpeg.
Source lengths/ready/failed results are rechecked under media/codec ownership.
Only stable input/fixed-capacity failures suppress background retries. Real
one-shot privacy-read fault and stale queued length both failed before their fixes.

Whole-app memory was the actual acceptance failure: successful fullCMYK12 alone
was misleading. Keep-alive probe alone and malloc-time reserve alone both failed.
Final policy preserves16KiB at allocation and checks the service floor during
buffered decode work; late pressure aborts, releases codec pools and reports
service-heap-reserve with measured required/free. Other allocations can happen
between checks: no claim of a hard reserved RAM bank. Heavy valid JPEG may be
refused; no broad target-format claims based on host/probe support.

6001native+privacy,176factory/212app/514total inventory,12controls,6artifact pass.
Main app4B7530CB/ELF6B233C4F/sourceC6B9D1AD,1464560bytes/71440free, DEBUGoff.
Final5HTTP cases: three heap-headroom refusals, one late service-reserve abort,
one progressive gray success;46concurrent GETs/max0.657host sec. Separate control
160GETs/max0.640sec. Two cold processes preserve source/protected bytes; all four
final workflow/control owners stopped/reaped. This is HTTP/storage, not LCD,
RF/weather, cold-hit0writes or power-loss proof. Final report/data in
qemu/parity/jpeg-main-integration-validation-20261023.json and tests/JPEG_MAIN_INTEGRATION.md.

NEXT: old unstamped-assets safe migration must verify matching immutable27payloads,
raw/SDK partition map and candidate ownership before any stamp/cache write; never
erase user photos/preferences to make the guard pass. Then exact whole-app
heap/stack/time/format/fault coverage and independent LCD frames/clock continuity.
Existing photo_frames_qemu assumes two clock delays/present31 before async cache
warm-up; adapt observer to real readiness, without guest RAM/PC changes or hiding
factory differences. Continue upload/decode power-cut, network reconnect/client/
connection-churn gates, whole-image indirect-call audit, full/24h/hardware.
No physical flashing/reset, no edits to frozen bundle or shared SDK. Goal active;
commit completed change, do not push without the user's next push instruction.

## 2026-10-23 — ordered legacy adoption checkpoint

Matching native unstamped assets migration implemented in jpeg_provision and
real ESP-IDF main, ordinary guard still read-only. Verify raw/SDK table/flags,
geometry,27 payloads, compiled stamp, every candidate byte twice, then ID32 FIRST
+ exact readback, header8 LAST + readback, final64 read + full physical guard and
deadline. One startup budget,40 program bytes max,0 erase, no photo/settings I/O.
Valid stamp skips vacancy scan and keeps used cache. Unknown/occupied stays intact.

Important regression: single-program prototype could adopt full foreign header
with wrong compatible ID; negative failed before correction. Nonerased header
NOW requires exact ID. Recover only torn subsets within supported phase ordering.
Historical failure preserved separately; never committed/pushed/deployed.

23409 host cases/8 provision +14 transport mutants/31 transport/5995 native/privacy/
12 inventory controls/6 artifact pass.527 total inventory,212 app unchanged.
12 actual main QEMU processes passed/stopped/reaped: fresh40, IDdone8, cold0,
foreign/occupied0, real retained old-main app update0. Full physical comparison
outside expected stamp/NVS, and NVS exact for cold/upgrade. This is bootstrap
storage acceptance, not general JPEG/LCD/network/RF/power-cut acceptance.
App034287C7 /ELFBB7FD7A1 /source1D1F52CE,1466576bytes/69424free,DEBUGoff.
Assets1032119B/layout44268211/codecB33BC0A1 unchanged. Firmware archive saved.
tests/JPEG_LEGACY_PROVISION.md + qemu/parity/jpeg-legacy-provision-validation-20261023.json;
lossless deduplicated sector evidence, independently reconstruct/verify fullSHA.

NEXT: separate full LCD and clock-continuity gate of CURRENT image. Existing
photo_frames_qemu assumes two clock delays/present31 before asynchronous warm-up;
observe genuine cache readiness, no RAM/PC patches or masks hiding differences.
Then complete target heap/stack/time/format/fault/refusal matrix; real upload/
decode/journal reset/power-cut; network clients/reconnect/churn; full-image
indirect-call audit/full/24h/hardware. Do not re-open solved standalone core work.
Frozen QEMU/SDK unchanged, no physical actions, no push. Goal active.

## 2026-10-23 — current photo LCD complete, startup regression measured

Do not rerun obsolete pre-worker photo_frames_qemu as a current-main acceptance:
it expects2delay calls/present31, whereas current coordinator has1yield and masked
async readiness. New photo_cache_frames_qemu +contract observes real ABI/states,
literal factory replay, full57600pixels, no RAM/PC/time writes or diff masks.
54frames/3110400pixels exact;13report rejects;3native owners reaped. Four masked
cycles exercise unsynced then actual SNTP night restoration. No production changes.
Proof qemu/parity/photo-cache-frames-validation-20261023.json; tests/PHOTO_CACHE_FRAMES.md.

IMPORTANT NEXT: startup timing DOES NOT match. Current first photo23.389901guest sec
(repeat23.559866), literal stock20.565822 in separate reaped VM, same seed/profile.
Slot0 ready~5.3sec, but photo_worker_idle gates fade until all5warm jobs complete.
Optimize initial/prefetch scheduling rather than inventing a delay or hiding
warm-up from measurement. Preserve invalid-slot skip, partial readiness ordering,
source cancellation/retry, fade timing. Add failing native/QEMU timing and cold
durable-cache0write tests. Existing source/app/ELF hashes remain034287/BB7FD7/1D1F52.
Then independent classic/simple/dial clock continuity under foreground decode,
full target RAM/stack/time/format/fault, reset/power-cut, lifecycle/churn,
whole-image/full/24h/hardware. Goal active; no physical actions, no push.

## 2026-10-23 — next-photo prefetch complete

Current source prepares only the next eligible round-robin slot at fade0/2;
no unrelated decode starts in phases1/3/4/5. Initial request only for photo theme.
Shared bounded next_photo helper preserves valid stock selection; stable failed
current lengths skip, transient I/O/memory/cancel retry. No new sleeps. Native
failure getter exposed through media; GUI waits for valid pending target rather
than jumping to a ready later source. Same-length upload still clears failure.

FINAL6077 native +privacy,12inventory controls,6unsafe compiled policy mutants,
13440literal factory/current RV32 fade/selection traces and6artifact pass.
Audit217app/532total. New target AppABF14143 /ELF896558F5 /source64EDEEF9,
1466800bytes/69200free,DEBUGoff; saved firmware/development archive. Assets1032119B,
layout44268211/codecB33BC0A1/libraryD690 unchanged. Old timing fails isolated new
criterion before correction (retained23.389901 >stock20.565822).

Five final owned cold QEMU processes stopped/reaped: all28frames, night22/4cycles,
none4, damaged-first22, true durable cold28.104frames/5990400pixels exact,
17report negative controls. First5.560901guest sec (pilot5.619954), present1;
cold2.251859,0JPEG program/erase attempts. Z1 traps actual unique flash_program/
flash_erase addresses, checked against exact ELF by machine model; whole4MiB
also unchanged in cold fixture. Cold before EXACT warm after, no NVS/settings
reseed. Damaged source0 SOI byte intentionally0, valid slots1..4 continue in order.
All warm runs preserve photos/boot/immutable/protected, only declared NVS/prefs/
generated candidates may differ. This is LCD/storage/timing, NOT network/RF gate.

Proof qemu/parity/photo-prefetch-validation-20261023.json, tests/PHOTO_PREFETCH.md;
verify_photo_prefetch_evidence.py reconstructs10full images and104RGB surfaces.
Only~0.8MB new compressed evidence,184old payloads reused. Source/app/ELF/QEMU/
raw hashes pinned. All exec handles55183/38683/1272/98601/28063/74933/61342 terminal0;
no owned VM remains. Production unchanged after successful target build.

NEXT: classic/simple/dial clock continuity during actual foreground decode,
complete CURRENT target JPEG memory/stack/format/fault/refusal matrix. Existing
photo_owner_qemu workflow can requalify current HTTP/resource policy, but its
simple WeatherHTTP1.0 fixture caused timeouts earlier: use actual persistent
weather_qemu WeatherFixture, keep network/display gates separate. Then real
upload/decode/journal reset/power-cut, clients/reconnect/churn, whole-image
indirect-call audit/full/24h/hardware. Earlier HTTP proofs belong to earlier app
hashes, do not relabel. SDK/frozen QEMU unchanged, no physical actions/no push.
Goal remains active. Finish focused commit of this checkpoint, then continue.

## 2026-10-23 — foreground clocks/HTTP/recovery completed scope

AppABF14143 /ELF896558F5 /source64EDEEF9 unchanged. New test-only checkpoint:
tests/JPEG_CLOCK_CONTINUITY.md and jpeg-clock-continuity-validation-20261023.json.
Classic/simple/dial actual foreground gray8 progressive:13wholeframes; separate
start/chunk-only control47.60frames/3456000pixels exact clean native/factory RV32,
real minute rollover,16+12report rejects, hardware breakpoints/no guest writes.
Actual main complete; only isolated native renderer skips non-pixel RTOS startup.

HTTP requalified current app with persistent WeatherFixture, not one-shot HTTP1.0.
First240host timeout retained; diagnostics show ongoing CMYK12 flash progress,
not mutex deadlock. Explicit900host run completed:CMYK12 305s, RGBprogressive146.438s,
gray37.25s.862GET/0errors/max.875; separate160GET/0errors/max.5. Two sampling44
precise resource refusals, GET10s/guest I/O-time budgets unchanged. Host icount
seconds NOT hardware timing. Actual cold source HTTP bytes exact.

Independent wire reader/newest journal/full physical frame matches unmodified
upstream gray RGB565A3EC07B0. Actual stopped first interrupted flash15F0392B,
NOT live failure-flash copy, ordinary new boot/replacement works journal1→2.
Before size0/notready, after full source/frame SHA correct, protected preserved.
This is not bit-level power-cut/brownout. All11accepted processes stopped/reaped.
No current firmware changes/new build. Coefficient packing and durable cache
remain enabled; prior cold-photo proof0program/erase remains separate evidence.

NEXT: current target format/RAM/stack/fault matrix; expand LCD load to accepted
fullCMYK12/richRGB progressive; publication/program/erase cuts, network lifecycle/
churn, whole-image/full/24h/hardware. Keep network/display acceptance separate.
SDK/frozen QEMU unchanged; no physical actions/no push. Goal remains active.

## Historical in-progress 2026-10-23 — configurable cumulative JPEG write budget

USER CHANGED POLICY: keep JPEG mode support, but cap cumulative physical program
bytes per image including coefficient scratch/RGB565/journal, default200KiB.
Original JPEG upload excluded. Configurable from0;0forbids decoder/cache erase
too. User explicitly selected cumulative traffic, NOT scratch capacity. Do not
silently disable all progressive. Live reductions must not reset usage; raising
cap enables a later retry. Cache invalidation before upload carries its program
usage into finish, preventing two full allowances for one image.

HEAD2e811f338 committed prior gray clock/HTTP/recovery checkpoint; active goal
unbounded. Current substantial edits UNCOMMITTED. Settings use separate NVS u32
key jpeg_write_kib (same small_tv namespace), default200read-only fallback;
legacy settings struct/version/raw ABI untouched. /get_jpeg_write_limit and
/set_jpeg_write_limit JSON limit_kib uint32, UI fragments photo_write_policy.*
injected by local_site/extract_pages.py. Generated pages/manifest refreshed.
Local-site server mirrors configuration only, NOT a NOR traffic model.

photo_codec shared transport program quota, zero erase quota; typed
flash-write-limit/flash-writes-disabled with next cumulative required/available.
transport program_required/program_limit_hit reset at begin; limit_program only
tightens and revokes before subtraction underflow. Separate global settings
short critical read each checkpoint, no new sleeps. Source upload stores prior
cache program bytes, prepare gets remaining allowance; returned diagnostic
program_bytes totals both phases. Background policy failures cached for current
length +budget; no repeated retries until a larger cap or changed source.

Native first failed only stale inventory expected217; updated219app/535total,
13correspondence controls. native-second.log passed6294checks +independent privacy
under .build/jpeg-write-budget-20261023; exec50041 TERMINAL0. transport-first gate
passed348557checks/34cases; actual tightening/zero/overflow safeguards. Need final
tests, production build/archive, actual QEMU byte-counter/zero cold/persistence,
browser setting/crop/privacy, mutants, proof/verifier, focused commit. No push.

Earlier heavy clock work superseded by this policy: current jpeg_clock_qemu.py
adds fixture choices and photo_runtime_metrics.py (passive DWARF/RAM SDK heap/
task fill diagnostics). .build/jpeg-clock-load-20261023/cmyk12/classic passed127
full frames, actual CMYK12 status0/finish200, pool40592/context4984/backing460800,
worker untouched stack4940/8192. RGB classic45frames exact, decode0/HTTP200,
pool37804/context4984/backing172800/stack5060, but gate correctly failed because
minute rollover happened before decoder entry. Need NTP phase45 instead of55
for that workload if reusing it. These are OLD ABF14143 partial runs, not new
policy acceptance or complete3theme matrices. CMYK continued to simple; explicit
supersede-intent saved, own QMP busy so verified PID/UUID/path VM terminated.
Exec81990 terminal1; RGB8038 terminal1; no owned VM remains. Old frozen47files/SDK
unchanged. old-app/ contains exact old firmware archive+app.elf BEFORE new build.
Preserve/label partial results and do not claim all themes passed. No physical
flashing/UART/reset. Full target fault/format, publication cuts, lifecycle/churn,
whole-image/full/24h/hardware remain open after policy qualification.

## CHECKPOINT 2026-10-23 — configurable JPEG budget qualified and saved

The user-selected cumulative write policy is implemented. Default200KiB,
0forbids decoder/cache PROGRAM AND ERASE, including startup provisioning.
Separate NVS u32 small_tv/jpeg_write_kib; settings legacy ABI unchanged.
Photos field and GET/POST API accept0..UINT32_MAX KiB, uint64 byte arithmetic.
Original JPEG save and ordinary NVS/settings remain separate as explicitly
agreed. Cache invalidation traffic carries into finish; no second allowance.
Live reductions tighten without counter reset/underflow, increases take effect
on next job. Background stable budget failures do not repeat writes; larger
budget or changed source allows retry. No new software sleeps.

FINAL app9C1A83BD/ELF76B5CE37/source7D95988C,1476432bytes/59568free,DEBUGoff.
Production firmware/development archive saved. Assets1032119B/layout44268211/
libraryD690 unchanged, codec6B537BBB. Native6298 +privacy3727,13inventory controls,
219app/535total, transport348557/34cases +18unsafe mutants,6integrated unsafe
mutants with compiled positive control, DOM16, artifact6 PASS.

Actual C2 JPEG callback trace: CMYK12 refused at204800programbytes, next205056
demand never issued. Gray progressive succeeds at115968 incl invalidation and
finish; diagnostic matches independent count. Persisted0 hot upload rejects
before program/erase, paused wholeflash same. Cold EXACT warm stoppedimage,
no reseed: true photo_worker_draw(slot4) succeeds, callbacks armed from reset,
0program/erase, entire4MiB same. Independent canonical journal/source/frame SHA.

Found genuine zero-startup loophole in first policy appF94C00B8: unmarked legacy
provision wrote32+8bytes stamp before HTTP. Retained actual failing report and
both images. Fixed photo_storage_authorize to strict readonly authorization at0.
Current legacy samecase:0callbacks/whole4MiB same, stamp/candidates FF, clocks/
HTTP boot. Without valid stamp photo storage remains unavailable; increasing
budget requires ordinary restart for safe startup adoption. No runtime erase.

Separate current LCD gray load: classic7/simple4/dial4 exactwholeframes,864000
pixels, actual foreground decode and minute rollover,16negative controls.
Worker untouched5012/8192; pool14099/context4984 observed. Passive exactELF DWARF
heap/task derivation, six256KiB RAM snapshots, heap minima explicitly lower
bound rather than simultaneous aggregate. Decoder diagnostic pointer not saved:
pool observation is runtime report, not independently reconstructable from RAM.
All6current owned processes stopped/reaped. Network timing not requalified here.

tests/JPEG_WRITE_BUDGET.md; qemu/parity/jpeg-write-budget-validation-20261023.json.
Lossless15physical images (13current+2old failing),15PNG,6RAM snapshots, mutant
source/compile/run logs; offline verifier recounts writes, reconstructs all
images/RGB/stack/heaps and checks source pins. Earlier wrongphoto-theme cold
observer, stale inventory/routes, equivalent mutant and compile-failed mutation
remain labelled historical failures, not accepted controls.

NEXT unchanged: full current target format/fault/RAM/stack matrix, publication
cuts, lifecycle/churn, whole-image/full/24h/hardware. Earlier unlimited heavy
JPEG passes are not new default-policy acceptance. Shared SDK/frozen QEMU
unchanged; no physical flashing/UART/reset, no push. Broader goal status is
controlled by the user; this checkpoint completes the requested budget feature.

## ACTIVE 2026-10-24 — current-image JPEG format/resource matrix

Previous goal turn made progress: production configurable budget committed
db738ea51, clean worktree. Goal explicitly resumed/active; do not shrink it to
this matrix. App9C1A83BD/ELF76B5CE37/source7D95988C unchanged, default200KiB.

New tests/photo_format_matrix_qemu.py reads committed old cache corpus70 via
verified fixture tar, uses actual HTTP async owner, full physical source/frame/
journal oracle and immediate gray recovery after every refusal.59host positives,
5source capacity,6negative/sampling cases. Extended expected SHA from original
upstream+Python conversion; rich baseline8 oracle recomputed literal factoryRV32
for preserved IDCT/clipping. No guest code/PC/RAM writes. Full diagnostic address
is now saved alongside entry/exit RAM, allowing independent nested field check.
photo_format_matrix_contract.py independently derives stored RAM fields, protected
bytes, physical pixels and precise failure reasons; union70 enforcement across
independent parts. No general network or LCD acceptance criterion.

Pilot .build/photo-format-matrix-20261024/pilot TERMINAL0 (exec38491), VM23772
SmallTV-6db847ce76bf stopped/reaped.6primary/9workflows:6accepted incl3recoveries,
2finish failures (write cap,unsupportedSOF5),1oversize source admission. Stack
untouched5012/8192; sum individual heap minima10548 is conservative lower bound,
NOT simultaneous aggregate/worst-case. Pilot contract passes, exact pixels good.

FULL RUN NOW LIVE, do not rebuild/apply source changes to pinned inputs or restart
because of an observation timeout. Four disjoint groups18/18/17/17, explicit names
in .build/photo-format-matrix-20261024/shards.json. Fresh owned VM per process.
exec handles part0=29480, part1=11839, part2=7249, part3=62925. Outputs
.build/photo-format-matrix-20261024/part-N, logs part-N.log; all four last polled
live by write_stdin. To continue poll the same handles; inspect session.json only
as locator, not liveness proof. No second debugger. Runtime uses Frozen QEMU
jpeg-selector-qemu-complete-20261019 and unchanged SDK; active processes retain
their exact input hashes. Contract/doc changes not consumed by these VM drivers.

NEXT: wait for all terminal; preserve failures truthfully, validate union70+
RAM/frame/protected data, capture raw reports/physical deltas and update status.
Then real target allocation/I/O failures, publication cuts and remaining broader
network/whole-image/full/24h/hardware. Do not claim this pilot completed the plan.
No push/physical actions. Whole-image/stale-navigation investigation was read-only
only: no new assertions or source fixes have been made in that category yet.

Pilot evidence saved as qemu/parity/jpeg-format-pilot-validation-20261024.json:
19lossless physical images,16RAM snapshots, raw diagnostic layouts/logs and
independent verify_photo_format_matrix_evidence.py. Full parts still excluded
from accepted evidence until they terminate; don't capture a live backing as
terminal output. Current owned VM locators: part0 PID4920 SmallTV-d66e31d2e749;
part1 PID21724 SmallTV-f83944d60067; part2 PID36888 SmallTV-fef47653c41e;
part3 PID28724 SmallTV-5f583294c6f3. Validate handles/process identity on resume.

## CHECKPOINT 2026-10-24 — stale reference navigation repaired

symbol-map native_module was still guessed from a broad category.74of176module
summaries were stale (e.g glyph ->SPI driver, classic ->dispatcher only). It now
contains exact native_targets and derives file summaries from reviewed factory
rows. All16reference headers link there. Organizer --refresh-navigation preserves
the decompiled function bodies/names/calls; default export also uses the reviewed
links, and newly discovered addresses stay explicitly unreviewed. Audit rejects
stale navigation and pins both tools. Before fails at0x4200826a native_module;
after passes, refresh idempotent,13existing omission controls pass. Library/app
source inventory176/219/535 unchanged. Header line numbers can shift; function
body SHA/name/calls are unchanged. Historical misleading aliases remain documented.

Only navigation and review metadata changed; app/ELF/codec/layout remain fixed.
The four JPEG VM inputs do not include these navigation files; do not restart
them. Earlier pilot proof e5d708b49 is bound to pre-refresh review metadata and
must be replayed at that revision (or with its archived source view), not claimed
to pin today's updated comments/map. The current app bytes are identical.
Whole-image xrefs/indirect callbacks/flags and other plan items remain open.
Proof qemu/parity/reference-navigation-validation-20261024.json retains old map,
old/new function SHA/call tables, actual rejection, current inventory and13-test log.

## CURRENT 2026-10-24 — full seventy-vector JPEG corpus finished

All four original handles have now returned TERMINAL0:29480/11839/7249/62925.
Their VM4920/21724/36888/28724 are stopped/reaped. Do NOT restart these completed
runs or treat earlier LIVE notes as current. Outputs part0..3 under
.build/photo-format-matrix-20261024. Independent aggregate.json proves disjoint
union70 with same app9C1A83BD/ELF76B5CE37/source7D95988C.92actual workflows:
48primary accepted,17finish refusals,5source admissions rejected,22immediate
successful gray recoveries. Primary reasons8write cap,5heap,1backing,1unsupported,
1truncated,1invalid,5source. Exact physical source/frame/journal +nested diagnostic
RAM, task/heap counters passed. Worker untouched minimum5012/8192; maximum
observed librarypool47983/context4984; sum individual heap minima lowerbound15468,
NOT simultaneous whole-app peak. No current owned VM remains from this matrix.

Full proof qemu/parity/jpeg-format-matrix-validation-20261024.json archives192
physical images and174RAM snapshots plus raw logs/layouts. Delta images can use
an earlier fully reconstructed SHA as parent, avoiding repeated immutable code
sector lists. Complete4MiB hash still checked for each image. Earlier pilot bound
to e5dmetadata remains historical; full proof uses updated navigation source view.

This closes the70-vector corpus gate, not all possible format/fault/RAM paths.
RGB6/CMYK6 lossless samples were source-slot refusals; smaller qualifying fixtures
needed to execute those precision/color paths on target. Next actual I/O/allocator
faults and publication cuts, then network lifecycle/churn/whole-image/full/24h/
hardware. Preserve fixed app/ELF during any newly launched run. No physical/push.
Archive schema2: only earlier full images may be delta parents; verifier also
recounts primary outcomes/recoveries/workflows from raw reports. Around12.3MBnew
compressed payloads,3574sector references, with old immutable/code payload reuse.

## CURRENT 2026-10-24 — six-bit RGB/CMYK lossless target paths closed

HEAD before this work05da1950f; prior goal turn progressed through full70 corpus
and74navigation fixes. New generated gradient source formula(x+2*y+3*c)&63 covers
all64samples/channel; files RGB27754/CMYK36999 fit102400slot at240×240,predictor4.
Unmodified upstream encoder library867C/exe referenceEC59, known original samples
exact after upstream decode; Python RGB565 independent. New host-only generator
tests/jpeg_decoder/generate_lossless6.c uses shared build-generator.ps1 optional
GeneratorSource; reproducible JPEG bytes verified. Old predictor1 rich experiment
still141194/188235 oversized, failed admission qualification, preserved separately.

Optional fixture-manifest adds the2JPEGs; base70 archive never replaced. Real
QEMU .build/jpeg-lossless6-20261024/qemu, exec80350 TERMINAL0, VM27340
SmallTV-414c845e6332 stopped/reaped. Both actual decoded, not cached/baseline,
processSOF3/precision6/components3&4/rows240 from saved RAM. Full source/frame/
journal exact;116736programbytes each incl invalidation/publication, limit200KiB
unchanged. Worker untouched5320/8192; pools12901/15198/context4984; heap-minima
sum lowerbound41044 NOT simultaneous whole-app peak. Independent-final.json pass.
No owned VM remains. Current production9C1A83BD/76B5CE37/7D95988C unchanged.
Proof qemu/parity/jpeg-lossless6-validation-20261024.json supplements the original
70-vectors on the same firmware; it is not a rerun of the old harness, whose
source pins require checkout05da. Both proofs jointly cover all45lossless
precision/color pairs, not every predictor/transform/entropy pattern.

NEXT actual target faults/publication boundary cuts, network lifecycle/churn,
whole-image audit/full/24h/hardware. Read-only QEMU inspection found main2a593f8d00
clean and flash-write-audit branch0860e568d4 (shared NOR/cache fixes, not merged
here). Frozen D64 help exposes operation-timing, no dedicated fault property.
Referenced79badcba source says functional contents/not electrical power failure;
program/erase storage changes immediately, WIP delay is tracked separately.
Do not claim partial in-page brownout from operation-timing. Need inspect/test
the newer shared-core revision before implementing model fault injection.
No QEMU/SDK files edited, no physical action/push. Goal remains broad/active.
Historical source replay now supported by verifier --source-revision. It reads
committed bytes/LFS identities with git cat-file, never resets files and never
skips hash verification. Base70 source357pins match05da, wrongE5D differs24files.
Supplement recursively rechecks all192base images/RAM +6additional images/4RAM,
then derives exact45modes from actual successful SOF3 diagnostics. This proves
joint coverage without pretending the old producer was today's changed harness.

## CURRENT 2026-10-24 — actual publication operation-boundary cuts

photo_publication_qemu.py исполнил8selected cuts на прежней9C1A83BD/76B5CE37/
7D95988C/frozenD64. Seed — stopped lossless6 VM flash с CMYK6ready slot5.
Replacement —27754-byte RGB6, recovery — known gray progressive. Clock seed
не включает photo prefetch; cold observations оставляют все4MiB unchanged.

Два4-case runs .build/photo-publication-20261024/part-0 иpart-1; exec88011/66603
terminal0, все16owned processes stopped/reaped. Warm process убивается через
TerminateProcess pinned own handle после selected completed SDK operation либо
обычного completed chunk/finish. Hardware RSP only, no memory/register/code writes.
Paused/stopped bytes exact; cold gets EXACT stopped flash без NVS/settings reseed,
actual initial image сохранён до первого CPUcontinue. No guest shutdown at cut.

Cuts: invalidation firstbody/footer => oldCMYK visible; source erased/firstchunk/
firstRGBpage/publication firstbody/footer => absent; fully completefinish => newRGB.
Последний footer уже имеет full ready physical cache, но photo_size0 не разрешает
видимость до settings publication. Каждый cold process затем успешно загружает
gray; source/frame/journal и protected bytes/остальные slots/cache entries exact.

Independent replay4+4pass,5unsafe report/image controls на каждую часть отвергнуты.
Trace last return/status/address и code prefix сверены с exact ELF. Archive
photo-publication-validation-20261024.json сохраняет complete physical identities
через lossless deltas, raw logs/trace/initial/cut/recovered и failed pilots.
57complete physical images/78raw items,60416new gzip bytes; each full SHA verified.
First pilot до cut: runner TypeError numeric getclocktype. Second cut/cold прошёл,
но recovery HTTP observer30s истёк; не counted. Final900s host observation как в
format harness; guest quotas/timeouts не менялись. Final обаrun success terminal.

Functional NOR/WIP timing не electrical partial-page power loss. Actual SDK I/O/
malloc faults, NVS-internal publication cuts, exhaustive timing, network lifecycle/
churn, whole-image/full/24h/hardware remain. No app/SDK/QEMU edits, physical/push нет.

## Checkpoint 2026-10-24 — network peers and QEMU DHCP (see newer CURRENT below)

Goal remains broad/active, no blocker, no new push request. Latest user explicitly
requests fixing QEMU emulation bugs when found. No app/SDK/physical changes.
Production9C1A83BD/ELF76B5CE37/source7D95988C and frozenD64 snapshot unchanged.

QEMU task worktree C:/Work/QEMU-ESP32/.worktree/small-tv-ap-clients,
branch codex/small-tv-ap-clients, base0860e568d4. Completed focused commits:
- fdb97bef73: native Windows trace generation fix (Meson fs.name + C filename
  escaping); actual C runtime12cases/6unsafe controls, full two-target build.
- 6324e5e152: independent3virtual AP clients, masks and packet queue identity;
  actual two-peer guest events, defaultone preserved. Ethernet initially primary.
- d49be39d77: bounded shared DHCP reply parser + acquisition state module;
  identity/server selection, ACK-before-ready, NAK restart. 349cases/905guard-page
  truncations/10000bad packets; factory/native integration pass; C3 default and
  modular60s boot checks pass. Xtensa unchanged821D9807 (not full CYD acceptance).
QEMU rootmain2a593f8d00, flash-write-audit0860, other worktrees untouched.

Build path taskworktree/build, local MSYS2 GCC16.1/Meson1.5/Python3.14.6,
DEBUGoff/staticSDL/slirp/internaldtc/downloads disabled. Preserve baseline
binaries; NEVER rerun resume-baseline.sh after model changes (overwrites control).
Baseline-riscv32 SHA4e283d9b197d3716bda77a4da54ec92da8e83b352b190ad546e7f1060559237e.
Baseline-xtensa821d98070aa131ccdc5c7ccd87336c90c13a7c205dfe991404ed242f9da0f0e1.
clients-v1-riscv32 SHA288478784db0281c33b605a781d70c6b18c6ce5ef17667d21f8b04049127df00.
clients-v2-riscv32 SHA128d0d75316eeb2a33e7c527ce3cb71cbf9158b9e3062fe1a23c7bcccbf610f5.
No active build/process remains. Old Windows trace verifier needs
--source-revision fdb97bef73 after model changes; no hash skips.

New Small_TV/src/tests/network_event_abi.py derives real RV32 SDK14/15/scan1,
connect8/MAC0/AID6, disconnect10/reason8size2 from separate ET_REL object using
exact production flags, original object/app/ELF unchanged. Probe under
.build/small-tv-ap-clients-20261024/event-abi-final. Do not edit this producer
without regenerating ABI report; it pins its own source. Factory old ABI only
first7bytes MAC/AID used, not unverified native reason layout.

network_clients_qemu.py uses immutable47file tools snapshot plus explicit
separately-pinned candidate. Read-only hardware RSP observes actual events and
httpd_start out-pointer/returns, handles tail-call/nested return ownership. No
register/memory/PC/code writes. Actual DHCP relay ready wait before first SYN.
Native wifi_event1107363056, WIFI_EVENT1007921672, httpd_start1107554060,
httpd_stop1107555256. Factory AP event handlerCORRECT0x4200c6e2 (STA C602 wrong),
base object0x3c0f1eb8, startwrapperC5EC/stopC578, globalhandle0x3fcc3a70.
3fcc3a78 is retry counter, NOTserver. Literal AP branch14start/15stop.

Eight C2 VMs (pilots included) all stopped/reaped; current process inventory no
QEMU. native-v1 failed initial observer status after HTTP before DHCP; factory-v2
wrong handler never collected AP events. Both not accepted. native-v1-relay and
native-v2 old prototypes passed but only final native-v3/factory-v3 and
native-dhcp-v2/factory-dhcp-v2 archived as4acceptedruns. Two C3 VMs also reaped.
Factory real nuance: second start overwrites first nonzero global handle with0
on listen112; subsequent stop cannot reach still-live listener. Returned client
repeats listen112. Final factory each3starts/2stopwrappers/handles[nonzero,0,0],
HTTP200atall4nonemptyphases. Native each1start/0stop, sameHTTP. Do not assert
that every factory disconnect necessarily kills HTTP in this sequence.

Proof Small_TV/qemu/parity/network-peer-validation-20261024.json:40raw/37gzip,
121065compressedbytes, source observers/ABIobject+exactQEMU Gitblobs. Full new
factory flash/RAM/UART not archived. Independent network_clients_contract.py +
verify_network_clients_evidence.py pass4runs,24unsafecontrols rejected. Native
exact ELF symbols/entry instructions/base object, factory exact ELF addresses,
raw SDK MAC/AID/reason, DHCP states/distinctIP and handles rechecked. Historical
--source-revision supported without resetting. See tests/NETWORK_CLIENTS.md.

NEXT: fix host Ethernet routing when primary virtual client leaves while the
secondary stays. Currently select_ethernet_interface always primary. Need actual
primary-departure HTTP proof (including ARP state), cannot call full lifecycle
from secondary-only case. Consider carrier selection or per-client NIC/backend,
then test any-one departure/zero->one, default mask/invalid masks/reset/APSTA,
scan/upload/weather/theme/churn. RF/WPA and full network acceptance distinct.
Do not overwrite clients-v1/v2 EXEs; new iterations unique names.
Known earlier CYD IDF6 esp_phy_enable assert is still open; identical Xtensa
binary only demonstrates these RISC-V Wi-Fi edits do not change it. No fresh
CYD run in this checkpoint, no complete hardware claim. Other whole-image,
SDK I/O/allocation/NVS-internal cuts/full regression/24h/H01-H09 remain.


## Checkpoint 2026-10-24 — either AP peer departure (newer CURRENT below)

Progress continues, broad goal active, no blockers/new push request. QEMU now
HEAD7a9764712b (Keep the AP Ethernet relay working across client departures),
preceded d49be39d77/6324e5e152/fdb97bef73 in same taskworktree/branch. Final
clients-v5-riscv32.exe SHA cce6b4717d4da21ca1871b817ab697346d428d803f733377dac74ba6e57e5aaa.
Xtensa still821D9807 byte-identical baseline. No build/liveVM remains.

Actual oldv2 primary departure repro native-primary-before failed HTTP Timeout
atmask2 while secondary actually SDK-associated/DHCPbound and native serverstill
onehandle/0stop. v3 selecting surviving peer alone stillfailed(native-primary-relay-v3).
v4 normal ARP probe via radio/DMA repaired guest neighbor, primary case passed
factory/native. One factory-secondary-relay-v4 stalled final association instate3;
explicitly stopped own QMP tosavefailedtrace/reap, notaccepted. v5 distinguishes
probe3/auth4/association8 waits and retries outstanding exchange after1virtualsec
onexistingbeacon (no guest busywait). ARP+selection and retransmit saved7a9764712b.

Final v5 all4native/factory x primary/secondary departures pass. Masks1,3,1,0,1
or1,3,2,0,2;16ordinaryHTTP200. Native1start0stop;factorysame losthandle defect.
C3 default/modular each60sboot pass also v4 and FINALv5, allstopped/reaped.
Including earlier pilots this phase19C2runs and6C3runs, noQEMUprocess now.
All sourceapp/SDK/frozenD64 unchanged, nophysicalactions/push.

Source observer network_clients_qemu.py now --departure primary|secondary
(defaultsecondary). DO NOT alter it without a fresh run: its exact hash pins all
v2before/v3/v4/v5 newreports. Independent contract now tracks AID perassociation:
finalsecondaryrejoin maygetAID1; former fixedMAC->AID assumption waswrongtest.
FIXED_TEST documentedCORRECTION_MARKERS. Native/factoryrawbytes otherwiseunchanged.

New schema2 proof network-relay-validation-20261024.json archives fourv5runs,
bothfailedprimarycontrols, excludedfactoryv4stall, exact7a9764712bGitblobs and
newproducerpins. Older payloads reused. Offline verifier terminal0: all4runs/24unsafecontrols andbothbeforecontrols pass.
36raw/35unique payloads; new gzip bytes=65978; old payloads reused.
Unused failed-capture AID-contract source preserved under ignored .build, not staged. Earlier
network-peer proof remains verified with --source-revision4f501d7af; do not
pretend previous producer source is today's changedharness.

NEXT after saving/replaying evidence: scan/upload/weather/theme during reconnect,
controlled management loss/retries, DHCP retransmission policy, APSTA/churn.
Per-peerhostendpoints are optional future capability, not requirement of current
AP/STA hostportseparation or twopeerHTTPgate. Do not expand goal unnecessarily.
Selected any-one departure cases pass; entire HTTP-LIFETIME/full/24h/hardware,
SDK I/O/allocation/NVSinternal faults and wholeimage audit remain open. Known
CYDIDF6 esp_phy_enable assert stillopen (not changedbyRISC-Vmodel). No freshCYD
run performed here. References tests/NETWORK_CLIENTS.md,QEMU docs/WIFI_AP_CLIENTS.md.


## Checkpoint 2026-10-24 — AP activity (newer CURRENT below)

Previous goal turn made progress (four focused QEMU commits + two yoRadio network
proof commits). This turn authoritatively inspected clean yoRadio HEADfc6e7750e
and QEMU7a9764712b, no new emulation bug or production change found.
Broad goal remains active; no blocker/new push request, no physical actions.

New tests/network_activity_qemu.py uses exact native9C1A83BD/ELF76B5CE37 with
unchanged clients-v5-riscv32 CCE6B471 and frozenD64 tools (47file pins). Reuses
Events observer/target SDK ABI, generic activity hook changes AP presence at real
SDK/photo/theme function entry while HTTP Future is stillpending. Records actual
return_event_index to distinguish nested callbacks from later events. No guest
code/PC/register/memory writes. Network gate has NO LCD acceptance criterion.

Initialpilot .build/network-activity-20261024/pilot exec54721 terminal0:
1cycle6ops, allpass. Saved exact older producer.py (before extra metadata),
matching reportinputhash. Final .build/network-activity-20261024/final exec91607
terminal0:2cycles12ops, 14SDKpeer events,6nestedinsideactualfunctioncalls,
2exact508byte sourceJPEG readbacks andthemeGET. BothVMsstopped/reaped.
Scan finds3APs yoRadio-QEMU/QEMU-2/QEMU-3. JPEG fixture flat-gray-progressive-8
SHA45263A1C; no realphotos/private dump data copied into new archive.

Sequenceeachcycle:scan mask3->2 atesp_wifi_scan_start(blocking1), uploadstart2->3,
chunk3->1, finish1->3, theme3->2, reselect2->3. FunctionreturnsESP_OK, mainHTTP200,
ordinary file/themeGETs match. Native onehttpd_start andzerohttpd_stop throughout.
PeerMAC/AID/reason bytes tracked by actual SDK layout, ready onlyafterDHCPACK.
This uses sharedhostbridge throughremainingpeer, not separateperpeerTCPbackends.

network_activity_contract.py independently validates records and8negativecontrols:
completedHTTP, wrongMACbytes, wrongreturnboundary, missingAP, alteredJPEG,
duplicateserver, notreaped, finish400. verify_network_activity_evidence.py
rechecks exactELFsymbols/code/base/SDKET_REL and modelGitblobs. Full proof
Small_TV/qemu/parity/network-activity-validation-20261024.json passedoffline,
29raw/29payloads,25531newgzipbytes, unchanged olderpayloads reused. No fullVM
flash/RAM/UART archive. OwnVMprocessinventory must remain empty beforecommit.
Documentation tests/NETWORK_ACTIVITY.md +IMPROVEMENT_PLAN updated.
Historical producer replay supported with --source-revision, nohashskips/reset.

NEXT: STA weather fetch during actual station disconnect/reconnect, then remaining
controlled managementloss/DHCP retransmission/APSTA/prolongedchurn. Existing
weather_qemu.WeatherFixture supports hold_response/release_response; snapshot()
reads identified cached_weather DWARF, separateLCDgates mustnotbeused for network.
Station profile(nativefirmware) hasnoAPnetif, APsetup usesAPSTAidleSTA so weather
cannot be checked from APclient-onlycase. Current network_activity is nativeonly;
factoryscan empty-result nullbug isalreadydocumented, nofactoryscan pass claimed.
Do not change currentproducer withoutfresh run (selfhashpinned). QEMU7a clean,
productionapp/SDK/frozenD64 unchanged. KnownCYDIDF6PHYassert, wholeimage audit,
SDKI/O/allocation/NVSinternalcuts/fullsuite/24h/H01-H09 stillopen.


## Checkpoint 2026-10-24 — station weather (newer CURRENT below)

Previous goal turn progress: committed3aedd9bb1 APactivity tests/actual12ops.
This turn inspected clean3aedd9bb1 and QEMU7a9764712b before work. Goal broad/active,
no blocker/new push request, no physical/app/SDK/QEMUsource changes. Exactnative
9C1A83BD/ELF76B5CE37/source7D95988C, candidateCCE6B471, frozenD64tools unchanged.

New station_event_layout.py extracts constants2/5/0 and IPevent20bytes/offset4
from ACTUAL ELF/DWARF. No target recompilation or new field assumptions. Native
objects:IP_EVENT3c13a984,connected3fcb6718,APactive3fcb6717,retries3fcb6708,
lastaddress3fcb6710. Existing weather.native_layout derives248byte cache/fields,
request_state3fcb6724 and cached_weather3fcafa78. Types/constants agreeacrossCUs.

New station_weather_qemu.py observes SDK callbackentry/return viahardwareRSP.
Initialpositive67/idle; realPOSTsamecity/fixtureheldresponse (200negative,503JSON).
At first SDKdisconnectentry restores ONLY externalAPproperty, lets nativebody
executeesp_wifi_connect and obtains realDHCP/GOT_IP. Actualconnected0/retries1 ->
connected1/retries0, addressretained10.0.2.15/APfalse. HeldworkerRUNNING1; initial
cacheunchanged. Bothrequests aborted beforefixture.release (before_releaseworker0),
oldrawcache retained. RecoveryPOST obtains distinct body/humidity78then79, raw
cachegeneration2->3->4. Do NOT claim full503received/rejected fromthisoutage:
actualTCPabort precedesrelease, HTTP503parserpolicy is separateoldweathergate.

Pilot .build/station-weather-20261024/pilot exec12222 terminal0; final /final
exec35690 terminal0. Pilot producer.py savedbeforeadding extra HTTP/beforerelease/
holdtiming metadata, matchesitsreporthash. Finaltwooutages,3GOTIP,2freshweather
publications,4refreshPOST+2themeGET200,1httpd_start0stop,1 ROM boot, no panic/watchdog.
Holdhostseconds1.563/1.610 (<30sfixturebound); firmwareHTTP10s unchanged. BothownVMs
stopped/reaped. ExpectedSDK socketabort errno113 recordedlocally, notapanic.

station_weather_contract.py independently reconstructs rawdouble/text/generation,
SDKIPbytes/baseIDs/nativeflagtransitions/HTTP records/bodySHAs and rejects9controls.
verify_station_weather_evidence.py rederivesstation+weatherDWARF fromexactELF,
checks entryinstructions andmodelGitblobs. Proof station-weather-validation-20261024.json passed offline:32raw/32payloads,30274newgzipbytes; unchanged old
payloads reused, nofullVMflash/RAM/UART. See tests/STATION_WEATHER.md; planupdated.
Do noteditpinnedproducer beforefresh rerun. Historic --source-revision available.

NEXT: controlled managementloss/retries, DHCP retransmission policy and prolonged
AP/STA churn/soak, then fullnetworkgate. Earlier AP any-one departure +2cycle
scan/photo/theme activity andnowSTAweather selectedrecovery covered. No complete
HTTP-LIFETIME/RF/24h acceptanceclaim. KnownCYDIDF6PHY, wholeimage audit, SDKI/O/
allocation/NVSinternalpublicationfaults/fullsuite/H01-H09 remainopen. NoQEMU
process should remain beforecommit. Goal notcomplete orblocked.


## Checkpoint 2026-10-24 — DHCP retry (newer CURRENT below)

Previous goal turn progressed: baf6969b3 committed real STA/weather recovery.
This turn started from clean baf6969b3 / QEMU7a9764712b and found an actual model
bug. The broad goal remains active. No blocker, push request or physical action.
Production app9C1A83BD / ELF76B5CE37 / source7D95988C and SDK/frozenD64 unchanged.

QEMU task worktree now HEAD b85483c98d (Retry virtual DHCP acquisition with
backoff and per-peer transactions), after focused commit287d95e1b1 (one-shot
virtual AP protocol packet loss controls). Before executable clients-v6-riscv32
SHA51b6746191d5dc910487ab1540b4279979f50a30eeec5da7fa74054f0674fb1a; final
clients-v7-riscv32 SHA6d9d82665330a6f567d04eac9563ed05d2d14bdb47329d78e9f306fce3761a90.
Xtensa v6/v7 still821D9807, byte-identical baseline. Both target builds terminal0.

New QMP softap-drop-next: 21bits = 3peers x7stages (probe/auth/assoc/discover/
request/offer/ACK). External one-shot loss at virtual client protocol boundary,
not physical RF/802.11 ACK. Counter/time getter softap-client-faults stores no
payload and formats only on query. Defaultmask0 exits before parsing/clockread;
STA excluded. Invalid mask bit21 rejected without mutation. Existing random
link loss remains separate. Fault policy/counters persist guest reset as external
harness state. Sources separated into esp32c3_wifi_fault.c/.h.

Before v6: three management losses recover (old1s retry), four DHCP losses remain
state6(discover/offer) or7(request/ack) for >=12guestseconds, while first peer
and HTTP200 work. New network_loss_qemu.py records before_control=true and
recovery_acceptance=false for these4; do not count them as recovery passes.
All seven v6 runs passed their intended oracle and reaped (including4failcontrols).

v7 adds per-peer acquisition deadline/backoff4/8/16/32/64s, uniform ms jitter
+-1s with rejection sampling, actual cap64s. Existing guestAPbeacon events check
deadline, no guest delay/busywait. ACK clears it; NAK/reassociation new transaction.
Fresh random per-peer XIDs (also distinct from existing peers), stable during
retry, parser matches lease.xid. Previous single constant XID removed. DHCP
constructors BOOTREQUEST/chaddr/clientID agree, also legacy model client mode.
Lease renewal/rebinding not implemented. Pure C lease struct now13bytes (adds
xid4); unit ctypes layout updated before execution. Unit351cases +905guard-page
prefixes +10000random non-DHCP +14007backoff/jitter combinations passed. Old9byte
lease reports remain historical, do not mix their ABI with new code.

All seven after runs pass. DHCP target has1retry, healthy peer0; both bound5,
nextdeadline/nominal cleared, two distinct stable XIDs. Native oneHTTPstart/0stop.
Factory primary-departure regression passed onv7 (known handle-loss remains).
C3 default/modular v7 each60s boot/console/panic/immutable-input check pass.
All15C2 +2C3 owned processes stopped/reaped; builds/sessions terminal. No liveQEMU.
Original worktrees/rootmain untouched. QEMU taskworktree clean after both commits.

Independent network_loss_contract.py replays14reports and112unsafecontrols.
verify_network_loss_evidence.py rechecks exactELF/APABI/modelGitblobs, Cunit
sources/report, factory typedevents and legacy boot reports. Proof
Small_TV/qemu/parity/network-loss-validation-20261024.json passed offline:
61raw/54payloads,116266newgzipbytes; oldpayloads reused, nofullVMflash/RAM/UART.
Docs tests/NETWORK_LOSS.md and IMPROVEMENT_PLAN updated. Newproducer source
network_loss_qemu.py is self-pinned across all14runs; do not edit without rerun.
Historical replay supports --source-revision. No push performed.

NEXT: remaining bridge liveness during a permanently stalled primary DHCP needs
an actual repro. Source select_ethernet_interface compares targetIP with only
s->softap.ipaddr. If slot0 never saw a DHCP reply, slot1 may have learned guestAP
IP while slot0 ipaddr iszero. Broadcast hostARP then may select STA wrongly.
This is a code observation, not yet runtime diagnosis. Use controlled repeated
DISCOVER loss on peer0, keep peer1 healthy, observe ordinary HTTP before allowing
peer0 recovery; fix if reproduced. Single-shot peer0 would recover in3..5s and
mask the demux issue. Could need a dedicated bounded rearm test, not a fake SDK
callback or PC/RAM mutation. Keep task worktree/model source isolated.
Then combined/repeated losses and prolonged churn/soak, full network gate.
Known CYDIDF6PHY gap, wholeimage audit, SDK I/O/allocation/NVSinternal faults,
fullsuite/24h/H01-H09 still open. Goal not complete/blocked/paused.

## Checkpoint 2026-10-24 — stalled bridge (newer CURRENT below)

Broad goal remains active, no blocker, physical action or new push request.
Previous checkpoint 98fedc62f qualified individual packet loss/DHCP retries.
Current production app9C1A83BD/ELF76B5CE37/source7D95988C, SDK and frozenD64
unchanged. QEMU task worktree HEAD21a8d6dd8c is clean; root/main untouched.

Actual v7 primary-probe failed AssertionError: peer0 held state6/no lease by
repeated Discover loss, peer1 bound5, HTTP still pending after >=10 guest s.
After release normal DHCP/pending+new HTTP200. Before secondary-control passes.
Bug: esp32_wifi_learn_guest_ip stored guest AP IP only in sending peer, but
Ethernet selector used primary.ipaddr. If primary never sends Discover it is
zero; host broadcast ARP goes to STA despite bound secondary. FIXED_EMULATION
shares learned AP interface IP across all AP peers, keeps leases independent;
STA/legacy path unchanged. QEMU marker policy docs/CORRECTION_MARKERS.md added.

v8 clients-v8-riscv32.exe SHA
a5be14c545fd2dffec145473429686b9a667735a8fb6f0226c5c60034ac3785f.
Before v7 SHA6d9d82665330a6f567d04eac9563ed05d2d14bdb47329d78e9f306fce3761a90.
Both targets build terminal0, Xtensa byte-identical821D9807. All original
baseline/v1-v7 executables preserved. New stalled producer self-pinned unchanged
across 4 runs; do not edit without rerun. After v8 peer0 and peer1 stalls both
serve HTTP200 through healthy neighbor while target still state6/no lease.

network_loss_qemu.py now supports --all-stages; two v8 runs target either peer,
seven actual losses each, target4DHCP retries/healthy0, distinct stable XIDs.
Healthy HTTP ready before target finishes, then post-recovery HTTP200. Producer
same exact hash in both. Generic contract retains single-case result keys;
old 14-run proof supports historical replay --source-revision98fedc62f.
Factory primary departure/zero-survivor regression passes, handle-loss still
observed. C3 default/modular each60s boot/console/panic/input checks pass; not
full OLED/RF acceptance. All7C2+2C3 owned VMs stopped/reaped, process inventory
empty. No firmware rebuild. No physical flashing/reset/serial or SDK writes.

New verify_network_stalled_peer_evidence.py checks exact ELF/AP ABI/symbols,
Git model blobs/source pins, real failed before run, recovery and combined
losses. 44 semantic negative controls rejected; hold mutations update matching
sample too so rejection does not rely on duplicated summary inconsistency.
Proof network-stalled-peer-validation-20261024.json:57raw/44payloads,
100050newgzipbytes, existing blobs reused; no fullVMflash/RAM/UART archived.
Docs NETWORK_STALLED_PEER.md, NETWORK_LOSS.md and plan updated. QEMU focused
commit21a8d6dd8c; yoRadio checkpoint commit follows this working note.

NEXT: qualify prolonged AP/STA churn and current-image runtime/soak. Existing
runtime_qemu.py supports --duration-seconds/--cycles and actual ROM heap/stack,
but executable is hardcoded to frozenRoot/bin/qemu-system-riscv32.exe. Add an
explicit candidate --qemu option preserving default and separate binary pins;
do not overwrite frozenD64. Inspect code first, run bounded qualification
before H10. Whole-image xref audit, SDK I/O/allocation/NVS-internal/electrical
publication faults, full current regression, known CYD IDF6 PHY assert and
hardware H01-H09 remain open. Goal not complete/blocked/paused.

## Checkpoint 2026-10-24 — runtime qualification (newer CURRENT below)

Goal remains active and unbounded, no blocker or physical actions/push. Prior
turn progress677defd qualified stalled-peer/combined loss and QEMU21a8d6dd8c.
Feature commit00096f882 adds --qemu to runtime and -QemuExecutable to both PS
launchers, preserving default/frozen D64. Schema5 binds exact candidate path
and pinned SHA; auditor retains schemas3/4 and all weather requirements.
25audit/16memory/4ROM/6state/8weather tests passed (59). Sandbox TEMP ACL
initially blocked fixtures; a task TEMP fixed the environment, no weakened tests.

Current native app9C1A83BD/ELF76B5CE37/source7D95988C, SDK, production files and
frozen47/D64 unchanged. QEMU v8 A5BE14C5 after21a8d6dd8c; Xtensa821D unchanged.
No new build, SDK writes, physical flash/reset/serial or push. QEMU tree clean.
Runtime source/test helpers below are now pinned by a live H10; do not edit them,
rebuild/replace its executable or connect a second debugger/QMP observer.

Completed two runtime qualification VMs: preflight4cycles/2outages/32HTTP/
22.569796guest s; detached churn40cycles/20outages/320HTTP/200.910826guest s.
Churn exercises all4themes/5GIF, real city/weather, concurrent settings requests,
10ordinary JPEG uploads, external AP offline/recovery. MaxHTTP4.084654s<6;
minimum sampled free54688B, sum of SDK per-heap minima23180B (not simultaneous
whole-app minimum), stack-fill minimum332B. All positive, no ROM reset/panic;
not proof of no possible leak. Both workload/guard/supervisor terminal0, pinned
inputs unchanged. Host CIM explicitly found all8 qualification PIDs absent.
Do not infer host liveness from sandbox Get-Process or qemu-system-* name: this
candidate is named clients-v8-riscv32.exe and sandbox may hide detached workers.

verify_runtime_candidate_evidence.py replays numeric journals/ROM counts,
SDK heap arithmetic/task headroom/HTTP/outages/weather/UART summaries and guards,
checks app/ELF/source pins, early40cycle start record captured atcycle0, link to
exact archived network-model proof. The archived model JSON bytes carry its SHA;
working checkout JSON is compared as parsed data to tolerate Git line endings.
16actual-report negative controls rejected. Proof runtime-candidate-validation-
20261024.json:34raw/34payloads,114908newgzipbytes, no fullVMflash/RAM/UART.25unit
log included; other34unit results recorded in worklog. Earlier draft payloads
preserved in ignored .build/runtime-candidate-20261024/replaced-evidence, unstaged.
Docs RUNTIME_MEMORY.md/plan/worklog updated; evidence commit follows this note.

ONE NEW H10 LIVE, launched24Oct10:41:38UTC after qualification, pending:
run .build/runtime-h10-current-20261024
supervisor34280, workload34996, guard13180, VM1512 / SmallTV-dc56f2b7a572.
Windows CIM checked exact commands/creation times after launch; supervisor
CREATE_BREAKAWAY_FROM_JOB verified outside caller Job. Early start identities
captured atcycle0 in .build/runtime-h10-current-20261024-start.json. Requested
86400guestseconds, interval15, externalSTA outageEvery60, 1guestsecond outage.
Report/JSONL/UART guard are in that run, supervisor heartbeat in sibling
runtime-h10-current-20261024-supervisor/supervisor.json. Initial guard reports
oneROMboot/noerrors. Only read status files/OS identities; do NOT pause/reset,
restart it on observation timeouts or open another debugger. Preserve original
older H10 evidence. A started/pending flag is not 24h acceptance.

After terminal H10, run tools/analyze_runtime.py with --run that directory,
--repository-root current worktree, --start-record early-start JSON, allow roots
C:/Work/yoRadio and C:/Work/QEMU-ESP32/.worktree/small-tv-ap-clients, output OUTSIDE
run. Auditor schema5 accepts explicit filename. It requires actual86400guest s,
terminal guard/start/source match, weather throughout, phase-complete trend
windows; do not shorten the goal or claim H10 passed from 40cycles.

NEXT independent work while H10 runs: whole-image xrefs/callback/task/timer audit
outside176selected exports (NETWORK/SLOW/browser_time/clickCount/JPEG flash-output),
CYD IDF6 PHY assert in existing tools/test_esp_legacy.py (docs/ESP_FLASH_WRITE.md
records phy_module_has_clock_bits(PHY_INIT_MODEM_CLOCK_REQUIRED_BITS), phy_init.c332).
Current candidate Xtensa is byte-identical, not CYD acceptance. Full current
network/display/regression suite still needs separate gates and candidate/deps
selection: qemu_suite.py and several older scripts hardcode frozenRoot/bin and
root SDK. Do not overwrite frozenD64 or edit live-H10 pinned weather/time/runtime
helpers; use an appropriate isolated snapshot or defer changes until it ends.
Actual SDK I/O/allocation/NVS-internal/electrical publication faults and hardware
H01-H09 still open. Goal not complete, blocked or paused.

## Checkpoint 2026-10-24 — xref inventory (newer CURRENT below)

Previous goal turn was PROGRESS: deda58625 qualified current-image runtime,
00096f882 candidate selection,677defd99 stalled-peer tests/QEMU21a8d6dd8c.
This turn is PROGRESS, no blocker; broad goal remains active/unbounded.
New independent reverse tools/typed evidence, no native firmware/SDK/QEMU
source changes and no physical actions or push. Root/main untouched.

New files tools/reverse/ExportFactoryXrefs.java, tools/audit_factory_xrefs.py,
tests/factory_xrefs_test.py. Java reads existing Ghidra12.0.4 project SmallTV
(.build/small-tv-reverse/ghidra-project on dependency root), -readOnly -noanalysis.
5140 analysed functions,286384 instructions; full GNU executable-section stream
287952 records. Actual immutable factory ELF SHA8C9FD166; all5 initialized payload
blocks/ELF metadata and17215 code references checked. Also475literal data pointers and3metadata refs
match actual four-byte values; the synthetic Entry Point matches ELF entry. GNU canonical map SHA
67f4f41f9e2e5f398e7dcee65f4ca854d810e6ad4ed3efe010c5dff05fb7b81f.

GP startup AUIPC/ADDI4038046c/40380470 derives3fcb49c0. Existing Ghidra refsTo
browser active3fcb41f0(gp-2000) empty, but four actual memory instructions exist:
4200ee60 WRITE1,4200ee6c READ1,4200eef8 WRITE1,4200efd2 WRITE1. Owners GETsettings
4200ee02/POSTsettings4200ef62. Stored browser3fcb7d14 has2READ+3WRITE. NETWORK
3fcc39f0 onlyknownWRITE42008356; SLOW3fcc39f4 onlyknownWRITE42008382; click3fcc3a90
onlyknownWRITE4200ec0c. JPEG flag3fcc3a6c READ4200c432/zeroWRITE4200c54c. Do not
infer whole-program deadness or add/remove app behavior based only on this.
Bulk settings I/O/computed aliases still open. Timer callback pointer42008468,
JPEG output callback param4200c50c, app_main caller420b1e70 in420b1e4e recorded.

393 Ghidra GP integer memory instructions vs396GNU. Real omitted sites:
42058280 READ32 3fcb4858;420662da READ32 same;420757d2 READ8 3fcb4b0c. These are
explicit database_gp_gaps, gp_coverage_agrees=false, not suppressed mismatches.
Crosschecker intentionally rejects any NEW gap until reviewed; known gaps are
profile facts, not completeness acceptance. Current Ghidra DB has 4964RAM
functions outside selected export;1162pointer candidate edges/772targets outside
export. No new found pointer targets in review window4200826a..42011040 outside
176, but window is not a proven whole-application boundary.3327computed-call
EDGES (not necessarily distinct call instructions) remain for reachability audit.

Proof full-image-xrefs-validation-20261024.json:7gzip payloads/361910bytes. Raw
Ghidra address graph +audit+Java/Python/test/symbol-map snapshots and sessionmeta.
No full dump/ELF/DROM data/VMflash/RAM/UART. GNU14MB text stays ignored at
.build/factory-all-executable-20261024.asm, can regenerate via local objdump.
Replay factory_xrefs_test.py --proof ... --elf C:/Work/yoRadio/.build/small-tv-
reverse/factory-analysis.elf --assembly .build/factory-all-executable-20261024.asm
passed,9actual-report negative controls rejected. All three semantic/full-image/
physical claims false. Source revision replay currently needs matching source
checkout/snapshots; no --source-revision option in this new tool yet.

Local .build/full-image-xrefs-20261024: initialghidra-refs.json had0xram: format;
v2 script failed on EXTERNAL refs despite headless exit0; v3 repaired namespaces;
v4 adds GP instruction export and is acceptance. Preserve prototypes, do not
mix them with v4. audit-final4.json is final core report, controls-final2.json
records final positive/9controls; committed archive replay reruns
all9 with final sources. archive.py regenerates proof; replaced draft payloads
are ignored under replaced-evidence. Ghidra native jobs all terminal, no GUI.
Docs reference/FULL_IMAGE_XREFS.md +BIDIRECTIONAL_AUDIT/plan/markers/worklog updated.

ONE H10 STILL LIVE: see preceding runtime checkpoint for full preservation rules.
Run .build/runtime-h10-current-20261024, supervisor34280/workload34996/guard13180/
VM1512 SmallTV-dc56f2b7a572. Host CIM verified same creation times twice this turn;
last observed42cycles, oneROMboot/no guarderrors. Requested86400guestseconds,
interval15,outageEvery60. Pending, not terminal. Never restart it on polling
failure, never open second QMP/RSP, and do not edit its pinned runtime/weather/
time helpers or rebuild/overwrite app/QEMU. Early start record is sibling
.build/runtime-h10-current-20261024-start.json. After terminal use analyze_runtime
with start record and allowed dependency/QEMU roots, as previous checkpoint.
Sandbox Get-Process and qemu-system-* name filters cannot establish its liveness.

NEXT independent work: inspect three GNU-only sites and their function boundaries/
callers; classify SDK vs application callback/task/timer targets, then follow
computed aliases. Could extend read-only Ghidra observation or use an isolated
analysis copy, never edit original factory bytes or claim5140equalsall functions.
Known CYD IDF6 PHY issue still open; separate full current network/display/suite,
SDK I/O/allocation/NVS internal/electrical cuts and hardwareH01-H09 remain open.
All full plan requirements persist; goal not complete/blocked/paused.

## CURRENT 2026-10-24 — three SDK gaps identified/recovered; H10 live

Previous goal turn PROGRESS36adbd6f7, current turn also PROGRESS. No blocker,
physical action or new push request. Full objective remains active/unbounded.
Native9C1A83BD/ELF76B5CE37/source7D95988C, SDK installations and QEMU21a8d6dd8c
unchanged. Work stays in .worktree/small-tv-improvement-plan branch; main/root
untouched. New work is static reverse tooling/evidence, not a firmware rebuild.

Three GP-only missing sites belong to complete known SDK functions:
* ieee80211_tx_mgt_cb:420581b6..4205838a, source516/linked468,27localbranches.
* wifi_connect_process:420662da..4206632e, source100/linked84,1localbranch.
* pm_coex_slice_timeout_process:420756f0..4207581e,source318/linked302,15branches.
SDK source tagv5.5.4/commit735507283d5b2f9fb363a1901172dbd9e847945d, gitlink
b87cce81803b85c3639fb14bac6c24cff6d0fbad in espressif/esp32-wifi-lib. Local old
SDK submodule absent, fetched only3officialC2archives to .build/factory-gaps-
20261024/sdk-wifi-b87cce8, verified Git blob+SHA via exact commit tree. NO SDK
writes. Whole934SDKbytes/854factorybytes matched, only17authorizedCALL relaxations
and3GP LUI elisions.43localCFdestinations/repeatedsymbol/shared g_wifi_nvs,g_ic,
g_osi_funcs_p,wifi_log bindings verified. This is SDK code identity, not semantic
or timing equivalence across SDK versions.

New modules tools/reverse/elf_archive.py (bounded ar reader, no extraction),
rv32_link_match.py (relocation-aware instruction/CF match), xref_delta.py,
native_sdk_links.py; tools/match_factory_sdk.py; tests/factory_sdk_match_test.py;
tests/verify_factory_sdk_evidence.py; Java InspectFactoryGaps/RecoverFactoryGaps.
Classify raw whole source bodies with only supported relocations; no prefix-only
identity. Direct semantic branch controls are checked after legitimate immediate
masking. Unsupported/ambiguous alignments fail, no generic all-SDK acceptance.
Existing audit_factory_xrefs.audit adds expected_gaps, default old3 unchanged;
new recovery requires empty. factory_xrefs_test supports historical source SHA
via --source-revision, old36ad proof+9controls replay passed. Do not overwrite old
source snapshots/reports as though they used the new graph.

Ghidra source copied to .build/factory-gaps-20261024/project-copy (10files hashed),
then -readOnly -noanalysis RecoverFactoryGaps + ExportFactoryXrefs. Only analysis
instructions/function definitions changed transiently, every initialized block
SHA unchanged. Both source project and copied project disk hashes identical to
before afterwards, source factory ELF8C9FD166 unchanged. Script session terminal0.
Result5143enumeratedfunctions (was5140),286671instructions (was286384), all396GP
instructions match GNU. Manager count5145→5148 differs from enumeration but both
increase3. After-audit verified17233code references,475literal pointers/3metadata/
syntheticentry still checked. Newgraph stored as14function-row replacements/
additions,3GP rows,instructioncount over immutable ancestor; actualbefore/after
full files stay ignored. This closes these THREE gaps, not whole image.

Sourcecaller ownership: first materialization4206fd6a belongs4206fd54..4206fd71;
second42068f1e belongs42068eec..42068f43. Caller4207b120 still has NO containing
function. pm original SDK match ends7581e, not nextGhidrafunction75896: intervening
code still needs classification, do not infer boundary from next known symbol.
Some bound SDK log anchors lie outside loaded DROM; identity matching alone
must not turn that into a firmware/backdoor/error claim or proof of reachability.

Native ELF already includes ieee80211_tx_mgt_cb4205b482/452B,
wifi_connect_process4206a534/836B, pm_coex_slice_timeout_process4207ab2c/6B. Last
is c.li a0,1 +tailJALto4207a9f0 pm_coex_go_to_sleep316B, not an absent body.
Native symbol existence/link target are verified, old-vs-new SDK behavior NOT
proved equivalent. No app functions added/removed or manual SDK duplication.

Proof factory-sdk-gaps-validation-20261024.json:24payload references,
50296newgzipbytes, ancestor gzip/source reused.15SDK+5analysis negative cases
rejected, replay matched actual libraries/ELF/ancestor+delta/native ELF/app and
source pins. NO full library .a/firmwareELF/dump/DROMdata/VMflash/RAM/UART added.
Need exact local libs to replay: net80211 SHA8f989ecd..., ppb460bb30..., core85394ad5...
(complete values in reference/SDK_GAP_RECOVERY.md and loader constants). Raw caches
SDKobjects, SDKmatches-final.json, before.json, recovery.json, after-graph.json,
after-audit.json, graph-delta.json, native-links.json, sdk-controls.json,
project-integrity.json and archive.py are under .build/factory-gaps-20261024.
Producer SDK match input still same exact helpers as sdk-matches-final.json;
avoid changing them without preserving/rerunning. New verifier supports
--source-revision for future compatible source changes. Oldfull-image proof
command now documents --source-revision36ad +PYTHONPATH for shared oracle deps.

ONE H10 STILL LIVE: .build/runtime-h10-current-20261024, supervisor34280,
workload34996,guard13180,VM1512/SmallTV-dc56f2b7a572, created24Oct10:41UTC.
Host CIM verified same live processes this turn; last145cycles/2STAoutages,
oneROMboot/noerrors. Duration86400guestseconds/interval15/outageEvery60 remains
PENDING. Never restart on observation timeout, never open second debugger/QMP,
never edit its pinned runtime/weather/time/source helpers or overwrite V8 exe.
Earlystart .build/runtime-h10-current-20261024-start.json. After terminal use
analyze_runtime with exact start record and allowed dependency/QEMU roots; do
not claim24h from short runs. Prior checkpoint has full command/preservation rules.

NEXT: caller4207b120 +undefinedregion7581e..75896, callback registration parents
and wider SDK/application xrefs/reachability. The matcher can help classify SDK
boundaries; keep all unclassified nodes explicit and no whole-image claims.
Also resolve known CYD IDF6 PHY assertion (QEMU docs/ESP_FLASH_WRITE.md), possibly
independent of C2. Preserve H10's clients-v8 exe if making/building new QEMU;
build a DISTINCT candidate filename and separate CYD/C3/C2 regression. Full
current network/display/suite, SDK I/O/allocation/NVSinternal/electrical faults,
H10 and hardwareH01-H09 remain open. Hardware requires identified intended board,
no unsolicited serial resets/flashes. Goal not complete/blocked/paused.

## CURRENT 2026-10-25 — H10 interrupted; main qualification live

Previous turn PROGRESS: QEMU main9135fc89ce merged/pushed. Current turn also
PROGRESS. Older LIVE notes above are historical: CIM now confirms all old IDs
34280/34996/13180/1512 absent and no same-run/V8 processes. Stale running JSON
stopped24Oct19:57:54UTC. Termination cause unknown; no matching app crash events
in checked20-minute window, host last boot14Oct. Do not invent a clean finish or
firmware failure. Original run/pinned sources remain intact.

Old .build/runtime-h10-current-20261024 audited read-only. Strict rejects missing
footer; diagnostic replays1488cycles (saved counter1487 lags),4pendingevents,
25560.689541guest s,11909HTTP incl partialcycle,24outages,1ROMboot/noUARTerrors,
minsampledfree55116B,1482validweathergenerations/maxfreshgap68.579137s. Seven
flags remain: phases1/13/25/33/37/49/59 losses16/18/16/20/12/12/220B. Investigate;
no leak/no-leak conclusion or weakened thresholds. Diagnostic pending means a
prefix, not liveness. H10 unaccepted. New proof runtime-interrupted-validation-
20261025.json:24raw/refs,167082newgzipbytes,12rejected controls; no rawUART/RAM/flash.
Replay supports --source-revision and needs matching app/ELF. Details RUNTIME_MEMORY.

App9C1A83BD/ELF76B5CE37/source7D95988C/SDK unchanged. Current QEMU main9135fc89ce,
compiled modelcb9deafd83, SHA2df903276e66afe0095ad19afd6d8b7201bcca3fbda073f3edb958934aef0001.
Separate pin C:/Work/QEMU-ESP32/.worktree/small-tv-ap-clients/build/main-9135-riscv32.exe;
preserve it, old V8 and frozen47-file tools. Preflight4/2outages/22.790034guest s
passed terminalguard/supervisor0. ONE40-cycle/outageEvery2 qualification RUNNING:
.build/runtime-main-20261025/churn-40, supervisor30164 created25Oct11:15:03.325607Z,
workload37400/guard24956; live viaCIM, last2cycles. Cycle0 captured at sibling
churn-40-start.json. No new H10 yet. Never restart from a polling timeout.
Next: finish candidate qualification/preserve evidence, investigate retained loss,
then caller4207b120/undefined7581e..75896/fullsuite/fault matrix/hardware as planned.
No physical reset/flash, no OTA; full goal active, not complete/blocked/paused.

## CURRENT 2026-10-25 — main qualified; ONE new H10 live

This turn is PROGRESS (committed interrupted soak, qualified current app on QEMU
main, launched a fresh full H10). Old interrupted run/V8 and all original raw
files are intact. No physical action or push in this continuation. Goal active.

40-cycle main qualification is now TERMINAL SUCCESS, not live: all workload/
guard/supervisor0,4+40cycles/22outages/352HTTP;40-cycle run201.050119guest s,
10JPEGuploads, maxHTTP4.043722<6, minsampledfree54816B, SDKsummin20348B,
minstackfill332B. All8savedowner IDs absent viaCIM. Proof runtime-main-validation-
20261025.json:34raw/refs,30741newgzipbytes,20negative controls. Current reader
supports explicit schema2 main manifest identity and old schema1; old proof replay
--source-revisiondeda58625/16controls pass.25audit/trend units pass. Model source
pins equal actual QEMU main9135 files. This does NOT explain the old memory flags.

ONE H10 RUNNING:
* run .build/runtime-h10-main-20261025, VM SmallTV-530edfe0517b.
* supervisor19884 created2026-10-25T11:23:20.860023Z.
* workload8080 created2026-10-25T11:23:22.225068Z.
* guard18380 created2026-10-25T11:24:04.818320Z.
* VM18652/main-9135-riscv32.exe created2026-10-25T11:23:29.720127Z.
Host CIM confirms all four exact processes; last1cycle/oneROMboot/noerrors.
Requested86400guest s/interval15/outageEvery60, app9C1A83BD/ELF76B5CE37/source7D95988C,
QEMU2df903276e66afe0095ad19afd6d8b7201bcca3fbda073f3edb958934aef0001.
Pin C:/Work/QEMU-ESP32/.worktree/small-tv-ap-clients/build/main-9135-riscv32.exe.
Frozen bundle remains C:/Work/yoRadio/.worktree/small-tv-jpeg-selectors/.build/
jpeg-selector-qemu-complete-20261019. Do not overwrite binary/app/ELF/assets or
edit pinned runtime/weather/time helpers/SDK. No second QMP/RSP connection.

Early cycle0 .build/runtime-h10-main-20261025-start.json. Actual all-positive CIM
identities in sibling -processes.json. -processes-initial-incomplete.json is an
EXCLUDED early probe: guard PID not published yet, null converted to zero and
System Idle appeared; never use that as an owner. Corrected observation keeps
four positive PIDs and creation times, first record itself remains genuine0.
Never restart on a polling timeout; check current CIM identities against above.
After actual terminal, analyze_runtime with new run/start record, --allow-root
C:/Work/yoRadio and C:/Work/QEMU-ESP32/.worktree/small-tv-ap-clients; output outside
run. No24h or memory-trend acceptance yet. Old7h never combines with the new run.

NEXT: investigate retained losses12..220B without weakening thresholds. Consider
read-only allocator block/free-fragment metadata in a SEPARATE owned control VM;
do not attach another observer to H10 or infer leak/no-leak from free-size alone.
New firmware builds must use an independent worktree/artifact location while H10
pins the current app. Broader SDK/application reachability (4207b120 and7581e..
75896), target actual I/O/allocation/NVS/electrical faults, independent current
network/display/fullsuite and hardwareH01-H09 remain open. QEMU main fixed earlier
classic SPI/clock issues; full CYD RF still unqualified at MMIO60033c00 (main docs),
so do not keep treating the old PHY assertion as the current proven fault.
No OTA, no serial reset/flash; full objective not complete/blocked/paused.

Latest H10 identity recheck: all4savedPID+creationUTC pairs match, last11cycles,
oneROMboot/noUARTerrors, request86400 unchanged. IMPORTANT for pwsh7.5 probes:
read -processes.json with ConvertFrom-Json -DateKind String before exact ISO
comparisons. Default JSON date conversion produced one false string/DateTime
mismatch even though supervisor19884 was alive. Immediate re-query of the SAME
four IDs with string timestamps confirmed all identities; no restart occurred.
This does not explain the OLD interrupted run: its four PIDs and same-run/V8
scan were truly absent, independently of timestamp comparison. Pinned runtime
helper sources use held process handles/command identities, not this ad-hoc
timestamp comparison. Do not edit them for a probe-only formatting mistake.

## CURRENT 2026-10-25 — TCP median diagnostics; producers remain frozen

Worktree small-tv-memory-retention, producer23b641680, prior docs67556af2b.
This turn is PROGRESS: read-only QEMU branch audit/push verified main9135fc89ce,
then new offline attribution, host tests and real saved-journal CLI checks.
No producer, firmware, SDK, frozen helper or live VM input changed.

At resume CIM matched all12 original PID/name/creationUTC identities. Main H10
had410 cycles; main/V8 controls61/57. Later offline prefix replays verified67/62
cycles and68/63 snapshots,1167.278640/1069.220519 guest seconds. These remain
pending prefixes before3600s warmup, never terminal8h/24h qualification.

runtime_tcp_trend annotates the UNCHANGED original runtime_trend: same3600s
warmup/windows, lcm(20,outage cadence), phase coverage and dynamic initial
variation criteria. Use the SAME one/two central free-heap observations for
both components. Equal-free ties retain ranges; even centers are distinct.
Busy central candidates mean unknown attribution and remain in original free
statistics. Signed TCP release can coexist with positive unclassified growth.
No component ownership automatically excuses a retained-loss flag.

22 math +8 CLI preservation/rejection tests passed. New CLI fully verified
preflight4/churn40,5+41 snapshots; both correctly insufficient for steady-state
trend. See tests/TCP_TREND_ATTRIBUTION.md and tcp-trend-validation-20261025.json:
26 refs,14newgzip/24760bytes,12reused payloads. Reader replays original76controls
and16new controls. Live prefixes are deliberately excluded from immutable proof.

Do not modify live producer sources in this tree or the original H10 tree.
Producer fixes need another task worktree. Remaining: full matched controls,
old7loss flags12..220B, real queued guest buffers, already-dead VM cleanup,
whole-image caller4207b120/undefined7581e..75896, final full suite and physical
gates. No goal completion, no physical reset/flash and no automatic OTA addition.

## CURRENT 2026-10-25 — selected timer gaps identified in factory and native

After e572291ef, added separate match_factory_timers and reverse/native_timer_match.
Actual call4207b120 belongs to pp_timer_coex_slice4207b11a..4207b12c.
Four PM bodies4207581e..42075896 now matched by complete SDK models, plus five
timer wrappers:9 bodies/238SDKbytes/210factorybytes/4localbranches. All9 native
counterparts also matched the same full models and real ELF symbol targets.
The32/28byte sleep-delay difference is permitted call relaxation, not omitted code.

IMPORTANT: the shape matcher alone accepts a REAL neighboring timer wrapper.
Require bound callee/global anchors, and local anchors scoped to object/section.
Eight factory and two native controls rejected. See reference/SDK_TIMER_GAPS.md;
two small evidence gzip files under parity/factory-timers-20261025 total6438bytes.
No ELF/SDK/project/VM/producer modifications. Existing PM coexistence callees
can differ across SDKs; no transitive/whole-image semantic equivalence claimed.

Remaining immediate whole-image step: transient Ghidra metadata recovery for
these bodies, timer dispatch callback registration/reachability, then other gaps.
Main H10 and matched schema7 controls continue protected; old memory findings,
cleanup fix, final suite and physical gates remain open. Keep full goal active.

Latest authoritative CIM recheck25Oct14:24:02UTC: all12original identities match;
mainH10=454cycles, schema7main/V8=105/100. All supervisors/guards running,
oneROMboot/noUARTerrors each. Saved ignored owners-after-static-checks.json.
No terminal result yet, and no durations are combined.

## CURRENT 2026-10-25 — dispatch recovered; vendor invalid-ID defect to fix next

Previous turn PROGRESS:e572291ef/c473d3caa. At resume all12CIM original identities
matched; H10=457cycles, metadata main/V8=107/103, all guards running/oneboot/noerrors.
No producer/firmware/SDK/frozen helper/live VM input changed this turn.

audit_timer_dispatch links initial120B table14events+sentinel and17complete bodies
per image. Factory table3FCB52F8/postslot3FCC3100/dispatcher420ACC28; native
table3FCAC978/postslot3FCB5D98/dispatcher420D1486. Four register-shaped candidates
reduced to one by the shared post slot. Native ID11 has explicit version names
pp_timer_keep_alive/pm_keep_alive_timeout_process vs old max_idle names. A direct
probe rejected old100B callee model against native128B body; review remains open.

Transient Ghidra RecoverFactoryTimers +old3gap recovery, readOnly/noanalysis:
21 qualified bodies,18created/3renamed,14callbackowners,global/local instruction
delta143. Enumerable5143→5161,manager5148→5166. Both persistent projects'10files
unchanged. v2 adds before-range counts; initial successful observation retained.

New private CPU fixtures execute exact178B dispatcher bodies with declared
callback/log/free stubs:1002cases, all256IDs+poison15..255/null/fallback/nullcb/ret0.
REPRODUCED VENDOR DEFECT, NOT FIXED: table[id].id read precedes bounds checking;
15..255 read one byte outside120B table at PCs420ACC62/420D14C0, then correctly
reject/free. No out-of-table reads for0..14 (14 accesses the in-table sentinel).
Do not preserve this known error in our final firmware. Tests are characterization.

NEXT: new task worktree for a pre-dispatch ID guard preserving Wi-Fi message ABI
and free ownership. Verify both ppTask direct reference and wdev_funcs_init
function-pointer registration actually enter the guard after linking; a wrap flag
alone is insufficient. Keep active app/ELF and producer trees frozen. Then review
ID11 callee semantics and continue other computed aliases/callback/event sources.

Evidence timer-dispatch-validation-20261025.json:28refs,15newgzip47112bytes,
13reused payloads. Actual consumer replay:20ancestor+15newcontrols/1002cases,
396GP/no gaps,5161enumerated. See tests/WIFI_TIMER_DISPATCH.md. Full goal stays
active; retained-loss flags, H10/matched controls, cleanup/fullsuite/hardware open.

LatestCIM25Oct14:47:09UTC: all12original owners live, H10=511cycles,
schema7main/V8=162/158; guardsrunning/oneROMboot/noerrors. Ignored
factory-timer-dispatch-20261025/owners-after-audit.json retains observation.

## CURRENT 2026-10-25 — active tree is small-tv-timer-bounds

Continuing turn PROGRESS:cdd3646f9 audit committed in small-tv-memory-retention,
then new branch codex/small-tv-timer-bounds at repo/.worktree/small-tv-timer-bounds.
Do not edit the original H10 or matched-control producer trees. All three old
VMs/app9C1A83BD/ELF76B5CE37 remain protected; their runs do not qualify a new image.

Implemented network/wifi_timer.c FIXED_FACTORY: reject ID14..255 before vendor
table read, free once through the same g_osi_funcs_p adapter, delegate valid/null.
Pinned target6.1/C2/ABI compile assertions; wrap+undefined ensures archive extraction.
ROM complication was real: native ppTask at40001C44 is a trampoline to40046EEC,
not its archive522B body. Actual ROM554B/event8 jumps through pp_wdev_funcs+356;
full current SDK wdev_funcs_init writes the guard to that slot. Three archive
refs are catalogued, but the ppTask archive body is not a linked ingress.

Build V3 COMPLETE SUCCESS, DEBUGoff, saved production development files:
app c91294fca6acb16283605eef8aedcf98102d7a8ad42076c09b058594a5c97e93
ELF 9e4ec88d6e85ae58fa3e164362f1b10491f9edef0feaa4af8c52c9fa88446e24
source04b19378061ef5cdad4fd56f27477cafb4d454f58b0767df30eba66384333bcd
App1476480bytes,+48;guard46B. Exact ELF under this tree's .build/small-tv-esp32c2.
Post-link ROM/table/library verification mandatory in build.ps1; source ledger
includes checker modules. Do not rebuild/change compiled inputs while a new VM
qualification is using them. Current prototype/unit artifact names listed below.

Final unit .build/wifi-timer-guard-tests-v2-20261025.json:518cases=258direct+
256exactROMblock+4complete successful-allocation initializer tails. Actual final
slot remains guarded through SDK return. Earlier tail fixture missed a beacon
callback data precondition supplied by wdev_data_init; it failed on0x10, never
silently zero-filled. Now initialized ELF data +declared opaque beacon stubs;
these callbacks and earlier APIs/scheduler remain outside this host fixture.
All242invalid IDs avoid vendor/table/OOB and free1; valid/null preserved.
Bare vendor control reproduces OOB. No software delays/Flash writes/allocations
added by guard. tests/WIFI_TIMER_GUARD.md documents exact scope and replay.

Proof wifi-timer-guard-validation-20261025.json,1902B packed transcript,12source
pins; consumer fully replays source ledger/link/ROM/518cases and rechecks sources.
Two early build failures were extraction and incorrect ROM assumption, not passed
qualifications. Final artifacts/static/probe SHA all agree. No physical actions.

NEXT: commit complete guard change, run ONE schema5 preflight4/current-main and
guard/supervisor; then40cycle qualification and independent network/display/final
gates. Never use TcpTopology yet: its ABI policy is pinned to OLD76B5 and needs
separate qualification for a new ELF, not a weakened SHA check.
Also new CODEC-REPRO plan item: same JPEG code got BUILD20261020→20261025,
archive d690..→9c009.. and codecID6b537..→2a6d6... Normalize reproducible recipe
inputs/date with cross-path/date tests; do not remove library SHA ownership guard.
This is separate from timer fix and not yet implemented. ID11 max_idle/keep_alive
callee review, old retained losses, three long runs, cleanup/fullsuite/hardware open.

## CURRENT 2026-10-25 — timer guard qualified in short QEMU workloads

Active tree small-tv-timer-bounds, producer2b036586e; appC91294FC/ELF9E4EC88D
unchanged. Last turn QEMU merge/push audit confirmed all useful branches already
in main9135fc89ce. This continuation PROGRESS: actual completed preflight inspected,
then ONE separate churn40 launched, genuine cycle-zero/owners captured, both ended.
Do not rerun either run due to the earlier truncated launcher output.

Runtime schema5 preflight4/churn40: 32/320HTTP,2/20outages,17.959790/161.595062
guest seconds. Workload/guard exit0, supervisors complete/inputs unchanged, UART
one ROM boot/no reset or panic. All8 original PID/name/creationUTC owners exited;
their live and terminal records are archived. No TCP topology allowlist change.
Reader schema4 validates exact producer prefix, actual UART bytes, both early
captures and original-owner exit (PID reuse is not an original owner). New proof
wifi-timer-runtime-validation-20261025.json:47refs,37241new gzip bytes,28rejections.
Actual consumer replay and old main schema2 replay pass (old20controls);25analysis
tests pass. See tests/WIFI_TIMER_GUARD.md. This is NOT H10/fullsuite/hardware.

IMPORTANT: original H10/main9135 OLDapp9C1A is now AUTHORITATIVELY FAILED, not live.
Supervisor terminal at2026-10-25T14:53:49.5005313Z/workloadexit1/guardexit0, all4
original PIDs absent. 526cycles/4207HTTP/8outages, last guest9066.078574,
9040.980895observed seconds from start,4pending HTTP events. Timeout during
/start_upload response. Journal aggregates+2108ROM crosschecks agree; no panic.
QEMU log has535 WSAEventSelect invalid-socket warnings. Cause NOT established;
do not call a firmware bug or excuse the failure, and do not accept as24h.
Supervisor cleanup also reported connection refused after workload closed VM:
known separate cleanup issue. Preserve complete failure before a diagnostic run.
Two schema7 OLDapp controls remain active; revalidate identities before using.

NEXT: archive failed H10 and investigate Windows slirp socket lifecycle/HTTP
timeout, with a separate QEMU task worktree/build and owned diagnostic VM. Current
long controls and pinned executables must remain untouched. Then cleanup helper,
CODEC-REPRO, ID11 callee/full-image reachability, new-image independent gates and
hardware remain open. Full goal active; do not combine old/new run durations.

Failure archive now saved: runtime-main-failure-validation-20261025.json,
19 payload references, 64787 new compressed bytes. Actual consumer replay with
--recheck-inputs passed and rejected seven false-success/ownership controls.
The first reader prototype expected an explicit null elapsed field; the real
terminal failure omits it. Fixed the reader to accept absence or null while still
rejecting any invented elapsed/end time. No producer or report was changed.
See tests/RUNTIME_MAIN_FAILURE.md. Next priority is bounded pre-cleanup failure
state capture and an owned diagnostic reproduction. Invalid-socket warnings may
come from callback registration or unregistration; causation remains unknown.

## CURRENT 2026-10-25 — idempotent host VM cleanup fixed and qualified

Active branch codex/small-tv-timer-bounds. Previous progress committed as
d7dccb92f (short timer-guard runtime) and 421291ab5 (failed H10 preservation).
Firmware app C91294FC / ELF 9E4EC88D remains unchanged; no rebuild or flashing.

runtime_cleanup.psm1 now checks production session PID, executable and launch
timestamp before a redundant helper call. The session time is an upper bound
on original creation, not the exact creation timestamp. Absent/exited originals
or a demonstrably later/different process need no stop. For a matching live
process, hold its kernel handle through helper completion. A helper error is
benign only if that original has exited; keep its actual nonzero code and logs.
Unknown liveness never excuses failure. Inspection errors are recorded but do
not bypass the existing nonce-checking helper. No new PID-based kill operation.

Final module SHA 86cec17ca752b01dd4f5ba447856fbdb8934b2f01df4a43c3f1391a62cb9cf2a.
13 real Windows canary cases, 10 old supervisor cases and a real main-QEMU
filesystem-fault run passed. Native workload/guard/VM stopped by the supervisor;
test fallback cleanup was unnecessary. Replay against the retained closed H10
session chose absent/original-already-exited, no new cleanup error, passed=false.
Four final reports saved, 8314 compressed bytes, seven source pins:
runtime-cleanup-validation-20261025.json; tests/RUNTIME_CLEANUP.md explains scope.

Initial test harness hit an actual Windows sharing race in vm-ready.json; the
remaining owned canary was stopped by verified nonce and confirmed gone before
rerun. Added bounded same-file read retry and cached identity. V2 had 12 cases;
final V3 has 13 after strengthening inspection-error cleanup continuation. Only
final reports are accepted. All test sessions have finished; none needs polling.

Historical timer runtime replay now needs --source-revision d7dccb92f because
the cleanup producer file changed after its qualification. That replay passed;
the original archives were not rewritten. Two metadata-control producer trees
and their pinned executables are still protected and must be revalidated.

NEXT: implement bounded failure-state capture before runtime_qemu finally closes
its RSP/QMP and VM, then an owned diagnostic reproduction of the HTTP timeout.
Do not increase the timeout or infer causation from WSAEventSelect warnings.
Afterward CODEC-REPRO, ID11 callee review, real queued TCP buffers, full-image
reachability, final independent network/display/full suite, H10 and hardware
gates remain open. The broad goal remains active, with no duration aggregation.

Latest authoritative observation, 25 Oct 16:08:50/51 UTC: all eight original
metadata-control owner identities still match. Main/V8 have 357/352 cycles,
running guards, one ROM boot each, no guard errors. No cleanup-test processes
remain. Saved ignored remaining-controls-after-cleanup-20261025.json. These are
pending prefixes, not 8-hour or H10 acceptance.

## CURRENT 2026-10-25 — bounded failure capture implemented and native-tested

Active tree/branch remains small-tv-timer-bounds, last prior commit 6da615e3c.
This goal turn is PROGRESS. Firmware remains C91294FC / 9E4EC88D, source 04B19378;
no firmware rebuild, SDK/frozen-helper change or physical device operation.
User asked what remains: answered with H10/retained memory, actual JPEG I/O and
power faults/CODEC-REPRO, remaining whole-image/ID11 paths, final independent
network/display/full regression, and hardware H01-H09. Broad scope stays active.

Added runtime_failure_capture + separate DWARF layout module. Context captures
before existing QMP __exit__ and outer RSP/VM cleanup. Actual arbitrary-PC stop,
no advance to SDK entry, no guest writes/calls. Read CPU PC/SP/RA, heap/task
metadata, upload/worker flags and queue/mutex counters/owners only, never payload
or used stack bytes. Partial components remain explicitly diagnostic, not quiet
TCP/allocator qualification. TCP topology allowlist for the new ELF unchanged.

RSP has a shared deadline; QMP uses the existing bounded stream. Five seconds,
192 requests, 32768 requested SRAM bytes, 4096 per read, metadata file 64 KiB.
Usernet serialized component <=16 KiB so a large connection inventory cannot
crowd out CPU/photo data. Normal context exit performs no diagnostic I/O.

Final native test .build/runtime-failure-capture-qemu-v2-20261025 completed:
intentional host TimeoutError after real /start_upload HTTP200, original error
object preserved. File SHA observed before actual stop, original kernel VM
object exited, no fallback cleanup. Complete snapshot 0.047000 seconds,
96 requests / 2230 bytes, errors empty. Two prior cycles/four pending events;
this is NOT a reproduction or explanation of the historical H10 timeout.
Earlier first native probe passed at 0.016 s; final adds usernet size protection.

10 deadline +10 capture/error/budget tests pass. First socketpair fixture hung
during Windows local setup; inspected real processes and TCP bound/listen state,
stopped only the verified own Python PID45000/creation16:15:43.253067UTC, then
confirmed the same exec session ended. Replaced that unbounded startup with
explicit bounded IPv4 connect/accept and used the normal approved local-network
execution context. No live QEMU was restarted from an observation timeout.

Proof runtime-failure-capture-validation-20261025.json: 31 references,22 source
pins,17 new gzip/37969 bytes. Actual consumer replay recomputes journal/UART/
native DWARF and rejects11 controls. An unused reader prototype blob was moved
into ignored .build after confirming no JSON proof referenced it. All unit,
native and archive replay sessions are terminal; none needs more polling.

NEXT: commit the complete feature, then ONE ordinary schema5 preflight4 using
the committed producer and one separate diagnostic duration86400/interval15/
outage60 run with genuine cycle-zero and four original owner observations.
Do not overwrite failed H10 or protected old controls; their durations never
combine. Current tree must stay frozen once a new diagnostic run uses it.
Independent CODEC-REPRO/new source changes then need another task worktree.

## CURRENT 2026-10-25 16:45 UTC — producer frozen for the diagnostic duration run

Feature committed as 70cd3e5bef443c772a714a826ab6a72ea69e38de. The ordinary
schema5 preflight finished: 4 cycles,32 HTTP,2 outages,18.816259 guest seconds.
Workload/guard exit0, supervisor complete, all inputs rehashed, original owners
exited. No failure file/field on success. Journal/UART and 8 workload +4 owner
controls independently verified. Nine raw records /10446 gzip bytes saved in
runtime-failure-capture-preflight-20261025.json, including genuine start0.

ONE diagnostic-main run was launched after that pass. Preserve exactly this run:
root .build/failure-capture-runtime-20261025/diagnostic-main
request86400 guest seconds, interval15, outage60, schema5, no TCP topology.
VM name SmallTV-ee01f5c96c24; appC91294FC/ELF9E4EC88D; main QEMU2DF90327.
Producer70cd3e5be. Genuine cycle-zero and all four original owners captured.

Original owner identities (name, PID, exact creation UTC):
- supervisor pwsh.exe,31368,2026-10-25T16:42:18.2230720Z
- workload python.exe,16156,2026-10-25T16:42:18.6920630Z
- guard python.exe,19100,2026-10-25T16:42:55.3108110Z
- VM main-9135-riscv32.exe,20424,2026-10-25T16:42:24.5192390Z

Last CIM16:45:03UTC matched all four,3 cycles, guards/supervisor running, one ROM
boot/no UART guard errors. Old metadata main/V8 controls also still match all8
original owners,444/437 cycles at16:45:04UTC, guards running. Saved ignored
failure-capture-final-owner-observation-20261025.json. All three are pending;
never call them H10/8h pass or combine their durations with earlier failed runs.
Both launcher execs22039/15764 are terminal; their detached owners are live.

DO NOT change producer/runtime/helper/profile/compiled inputs in this tree or
the old metadata-control tree. Documentation/offline analysis may be updated.
For CODEC-REPRO or firmware/producer fixes, create a separate branch/worktree
under repo/.worktree from this completed source state. Shared SDK/ROM, frozen
helper bundle and both pinned main/V8 executables remain read-only.
NEXT: revalidate owners/status, inspect any genuine failure-state snapshot;
meanwhile advance CODEC-REPRO or selected whole-image/ID11 analysis independently.
HTTP timeout cause, long acceptance, retained loss, actual I/O/power fault matrix,
queued guest TCP samples, final independent gates and hardware remain open.

## CURRENT 2026-10-25 — factory comparison takes priority; event 11 characterized

User explicitly requested continuing item4 (factory firmware), then returning to
items1–3. Do not advance CODEC-REPRO/JPEG fault/retained-memory fixes ahead of this
factory audit. Existing three duration/control VMs remain protected and running.
Created a clean worktree from d0c82d127, then renamed its unused initial CODEC
branch/path to `.worktree/small-tv-factory-audit`, `codex/small-tv-factory-audit`.
This tree is the active editable analysis tree. Frozen timer-bounds and memory-
retention producer trees, SDK/ROM/helpers/QEMU executables stay read-only.

Progress: timer_event11_match + independent model/instruction/test/consumer
modules. Factory8C9F/native9E4E and exact old/new libpp archives pinned. Six event
bodies plus two parameter setters matched completely, boundaries/data/calls bound
to actual bytes. Factory setter starts74c12 after the intervening getter74c08;
its encoding of the period differs from native. Finding raw delay formulas alone
was insufficient. OSI480-byte tables are ABI8/9, not one shared ABI; three slots
and whole forwarding wrappers checked. Legacy timer bodies are linked IRAM code,
not ROM. Runtime OSI binding/complete timer backend still unqualified.

9776 private RV32 executions pass:4632 event states per image plus128 setter+
event states per image. All186 instruction starts in8 selected bodies visited.
Caller-saved poison, preserved ABI/stack, exact SRAM writes/call arguments/order
checked against independent models. 11 static and5 evidence mutations rejected.
Raw-state pairs4344different/288equal are synthetic coverage, NOT a compatibility
percentage. Native adds pending-action suppression, byte15-zero flag writes and
fallback/changed rearm. Factory setter10 stores12 and later arms slot224 with6144;
native stores10/adjustment2000000 and arms slot240 with8240000. Timer units differ.
Documented wrap edges as observations, not desired behavior or a proven bug in a
reachable clock path. Do not copy SDK bugs or revert modern SDK without evidence.

Proof factory-event11-validation-20261025.json pins9 sources and7630-byte result
gzip. Consumer reexecutes exact original code; final replay passed all5 controls.
See tests/WIFI_TIMER_EVENT11.md. No firmware rebuild/change, VM launch, physical
flashing, QEMU edit, long-run acceptance or whole-image equivalence in this step.

Read-only CIM17:11:26–28UTC matched all12 original owner PID/name/creation times.
Diagnostic-main64cycles; old metadata main/V8 controls505/498. Supervisors/guards
running, no workload error. Diagnostic UART guard last observation one ROM boot,
no errors. Details ignored `.build/factory-event11-20261025/live-observation.json`.
These are pending prefixes, never H10/8h pass; do not combine durations.

NEXT factory work: verify actual OSI pointer binding; match timer initialization/
post11 and follow pm_set_bss_max_idle inputs, flag producers and valid protocol
period ranges (including overflow boundaries). Then compare corresponding clock
behavior, preserving improvements and correcting confirmed defects. Remaining
whole-image computed aliases/function boundaries/SDK-application transitions are
open. User-deferred items1–3 and final independent gates/hardware still remain.
Broad goal remains active; this is a progress checkpoint, not completion.

## CURRENT 2026-10-25 — event-11 registration and actual OSI binding verified

Previous turn classified PROGRESS:7d8b50d88. Continue factory item4 first. Active
editable tree remains small-tv-factory-audit. Producer trees/QEMU/SDK/helpers
unchanged; appC912/ELF9E4E retained. This turn is another progress checkpoint.

New static registration qualifier pins old/new libnet80211 and prior libpp;
six complete SDK bodies per image (init, OSI register, pm_attach, timeout11,
post, post-register) matched, plus actual timer_setfn forwarding adapters.
Factory attach76792..76978, init68a9a..68bbc, register6819e..68206.
Setfn is in flash962d0 / native9378c, forwarding to ets_timer_setfn; do not guess
an IRAM wrapper. Actual old/new local cfg anchor names differ; bind addresses
and object context, not identical .LANCHOR names across SDK versions.

96 registration/gateway cases pass, including bad ABI/magic/null, already-bound
pointer idempotence and real init error propagation. All five other selected
SDK bodies plus setfn adapters covered completely. Init gateway intentionally
exits at a stubbed API-lock error:26/99old,25/98new instructions only. Its later
branches are statically matched but NOT dynamically covered in this checkpoint.
pm_attach direct stores match independent model and registers ten timers;492
is timeout11 with null arg. Invoke captured callback through real post body:
outer8/{11,0}; absent callback returnsffffffff, installed callback status
0/1/fffffffb propagated, remove/reset exercised. Backend helpers explicit stubs.

Ran owned factory/native station VM pair twice: first observation passed; final
pair adds retained raw typed reads so offline replay is independent of decoded
passed fields. Final session98016 terminal0. FactoryPID43028/SmallTV-50e01a6c9d49,
nativePID6280/SmallTV-b44080cb0c48; both absent by CIM17:27:06UTC after owned quit.
Initial pair20828/22872 likewise absent. No leftover short VM or restarted long VM.

Actual OSI global selects factoryABI8/nativeABI9 table, all480bytes match known
SHA. One UART boot/no errors each. Connected PM bytes1/14/15/16/488=0/1/1/0/0,
word36=1, configenable52=0 both, fallback28=10000000. Factorystoredperiod60 /
adjustment0, native30/500000. These fields are inactive here; do not label them
an observed timing regression. Timer word4=12121212 and word16 SRAM handle read;
backend callback/queue delivery/RF still not proven. Source/firmware pins unchanged.

Proof factory-timer-registration-validation-20261025.json:14 source pins,5gzip/
27614bytes, no complete RAM/credentials/stack/payload. First consumer exposed
JSON int-address keys vs serialized string keys; fixed canonical comparison,
kept previous prototype proof in ignored scratch. Final consumer session10021
ended0: all96 cases and both native observations replayed, four static mutations
and six raw-runtime/owner/UART mutation controls rejected. Archive session71047
ended1 for the diagnosed JSON comparison issue; no live process from either.

Latest CIM17:28:21–27UTC matched all12 protected original process identities.
Diagnostic-main99cycles, metadata main/V8 controls540/533; all supervisors/guards
running, one ROM boot each/no UART errors, no workload error. Ignored snapshot:
.build/factory-event11-registration-20261025/long-owners-after-short-tests.json.
Not H10/8h acceptance and no duration aggregation. No launcher/poll timeout was
treated as completion: sessions51918/78286/95000/98016/43387 inspected to terminal.

NEXT: follow pm_start/stop and pending-flag writers, old separate pm_keep_alive /
pm_reset_keep_alive path versus native unified fallback, then protocol period
range validation and timer cancellation. Real post callback/backend ownership
also open. Continue remaining full-image computed aliases/functions/SDK boundary
audit. User-deferred1–3, final independent gates/H10 and physical gates remain;
the broad goal remains ACTIVE. Do not edit frozen long-run producer inputs.

## CURRENT 2026-10-25 — old keep-alive path and TX/pending boundaries characterized

Previous turn PROGRESS:dfb452cce. Factory item4 remains first; no return to the
user-deferred1–3. Active editable tree small-tv-factory-audit, current firmware
C912/9E4E and frozen producers/SDK/QEMU/helpers unchanged. No new VM this turn.

New timer_keep_alive qualifier matches12 full bodies/4502linkedbytes from exact
old/new pm.o. Factory predicate40390590..4039061c, reset42074c5c/82B, TXdata
42075896/196B, TIM4039061c/488B, start420763d8/580B, stop4207661c/374B,
TXnull420759cc/514B. Native equivalents except absent predicate/reset:
TXdata4207ad48/218B,TIM420d1b6a/356B,start4207b93e/568B,stop4207bb76/352B,
TXnull4207ae8c/634B. Shared globals/calls and pm.o-scoped local anchors cross-
checked against previous PM/configuration bodies. This prevents relocated data
lookalikes from silently binding another configuration struct.

Predicate is boolean elapsed-time check, called by real factory pm_process_tim;
factory instructions4207a020/24 materialize/store its pointer in another table
(full initializer/indirect caller table still to qualify).
It compares fallback28 vs timestamp88, or sign-extended wrapped BSS product vs
timestamp480. Document overflow as observed code, not a requirement to copy it.
TXdata modern path coalesces rearm at elapsed>100000us; exactly100000 skips,
100001 rearms. This is a comparison, not an explicit sleep/delay. Old reset and
new rearm paths tested with actual child bodies, OSI clock paira0/a1 stub only.

12108 executions:2664 oldpredicate,36 oldreset,4608 TXdata perimage and96 selected
TXnull perimage. Four whole dynamic bodies cover213instruction starts; partial
null61/174old,92/213new. TIM/start/stop statically matched only,0dynamic visits.
No claim of full lifecycle/reachability/RF. New pending clear checks g_ic+16,
second pointer+228 and byte820; ifbyte820 nonzero, nonzero third argument permits
the clear. A first model inverted that last branch; literal CPU mismatch exposed
it, fixed against actual beqz at4207af54, final matrix then passed. Missing first
object logs/returns, missing second skips clear. Older clear additionally gates
on BSS enabled. Selected fixtures do not establish these states as reachable.

Proof factory-keep-alive-validation-20261025.json pins12 sources and33297byte gzip.
Six static mutations reject wrongSDK, truncation, neighbor, PM/config anchors,
100-msconstant. Consumer session37767 ended0: all12108 cases recomputed and five
evidence mutations rejected. Main test sessions45970/96044/96167/63506 terminal0;
49901 terminal1 for corrected reference-model branch, not a firmware failure.
Readonly assembly session47608 and owner session93137 terminal0. Preserve
intermediate results in ignored .build/factory-keep-alive-20261025.

Latest CIM17:39:06–12UTC matched all12 protected original PID/name/creation UTC
identities. Diagnostic-main118cycles, metadata main/V8 controls559/552; all
supervisors/guards running, one ROM boot/no UART errors, no workload errors.
Ignored long-owner-observation.json retains readings. Pending prefixes only;
not H10/8h pass and never aggregate their durations with failed/interrupted runs.

NEXT factory scope: TIM/start/stop dynamic state/cancellation paths, remaining
null-failure branches, station object+820 lifetime; trace setter callers and
negotiated BSS period bounds before deciding overflow fixes. Then remaining
whole-image computed aliases/functions/SDK-application boundaries. Independent
network/display/final/H10/hardware and deferred1–3 stay open. Broad goal ACTIVE.

## CURRENT 2026-10-25 — full start/stop bodies tested; cancellation question retained

Previous turn PROGRESS:7a9b2f830. Continue factory item4 first. Active worktree
small-tv-factory-audit, firmwareC912/ELF9E4E unchanged, no SDK/QEMU/physical change
or new VM. New source modules separate static qualification, reference model,
private instruction probe, case matrix and archive consumer by purpose.

5224 executions pass:1440start+1152stop perimage,40retained-state invocations in
8 chains(start,start,stop,stop,start). All319old/309new instruction starts visited
across main bodies/selected SDK helpers/shared ROM helper. Full PM/configuration
bytes and direct writes/global writes/call order/log numeric arguments match
independent models. Read-only callback data, saved registers/stack and caller-
saved poison verified. Cases include optional beacon callbacks, all local branch
choices, integer narrowing/shift wrap and 32/64-bit clock boundaries.

New qualifier reuses exact prior bodies and adds active-cancel22B perSDK and
factorymaxidle-cancel22B. Active object is PM+200, not guessed220. The actual
ROM4Bentry40001b74→40043cae/30B executes: clearbyte440,disarm260. Synthetic
g_pm_ptr at3fcdfd7c explicitly bound to corresponding private PM object; actual
guest binding still open. Existing external platform calls remain declared
stubs; complete transitive platform or RF effects are NOT claimed.

First fixture needed missing numeric word reader; added locally. Then actual
callback incominga5 was its JALR target, not original argument5 (already saved
in s4). Corrected model from actual instruction order; this is no firmware bug.
Final v3/final producers terminal0, earlier v1/v2 terminal1 fixture/model issues.
Proof factory-pm-lifecycle-validation-20261025.json pins15 sources,39281byte gzip.
Consumer recomputed all5224 cases and rejected5evidence controls;5staticcontrols
also pass. No need to rerun absent a new source change or unresolved concern.

Direct stop disarm sequence with declared platform boundaries:
factory260/200/180/492, native260/200/180. Configenable52 cleared in both; native
has no direct keep-alive disable call in this body. Need real runtime ownership/
cancel evidence before any vendor patch. Inspected shared ROMconnectionless
body40045d68/374B behind40001f70: directly disarms316/336, conditional ROM-table
calls still external here. Native ELF's entry symbol size388 is not actual ROM
body extent. pm_disable_sleep_delay uses actual ROM g_pm_ptr rather than ELF
g_pm address; don't equate a synthetic pointer assignment with runtime proof.

Runtime follow-up preparation: native SDK esp_timer struct has alarmu64 at0 and
timer_armed returnsalarm>0; must derive actual ELF/DWARF layout before backend
metadata reads. Linked esp_timer_is_active/timer_armed symbols were absent in
current ELF; do NOT invent/call those guest APIs. Factory needs independent
layout qualification. Natural QEMU station loss with read-only metadata is
next, using new owned VM copies and pinned helper/QEMU, not protected runs.

Latest authoritative CIM18:06:16–17UTC matches all12 original protected owners.
Diagnostic-main177cycles; old metadata main/V8 controls617/609. All supervisor/
guard states running, one ROM boot/no UART errors, no workload error. Ignored
.build/factory-pm-lifecycle-20261025/long-owner-observation.json. These remain
pending prefixes, never H10/8h acceptance, and durations must not combine.

NEXT: real ROM binding/backend timer state around natural disconnect and
reconnect, then TIM/full null-failure branches, station+820lifetime, negotiated
BSS period validation/overflow and remaining whole-image aliases/gaps. Deferred
1–3 and final independent network/display/full/H10/hardware gates remain open.
Broad goal stays ACTIVE. Preserve all frozen producer/helper/QEMU inputs.

## CURRENT 2026-10-25 — native cancellation resolved; factory recovery still fails

Previous checkpoint1007938ae. Continue factory item4; deferred1–3 untouched.
Editable tree small-tv-factory-audit. NativeC912/ELF9E4E, SDK/ROM/QEMU and all
protected long-run producer inputs unchanged. No firmware build or board I/O.

New modules separate qualification, bounded decoder, literal predicate tests,
live observer and offline evidence verifier. Native DWARF: esp_timer32B/alarmu64
at0, legacy20B/marker4/handle16. Factory independently qualified14B/18B predicates
and handle load; only8B backendprefix claimed. Eight literal predicate cases,
eight metadata cases, ten rejection cases and four uninitialized/ROM-unbound
cases pass. Follow handle only if real ROMg_pm_ptr equals SDKPM and marker valid.
Metadata only/max32requests/256bytes; no stack/payload/credentials.

Final qemu-v4 session7708 terminal1, deliberately MIXED OUTCOME. FactoryPID6112/
SmallTV-252af7b44bc1, nativePID28832/SmallTV-9f08cc5692fa. CIM18:36:25UTC confirms
both absent; oneROMboot/no panic each. FactoryHTTP did not recover within30host
seconds after APonline; PMactive0/apphint2 persisted. Factory baseline alarm0
cannot prove armed cancellation. Actual handler4200c652 callsconnect before
state1 store4200c66a; GOT_IP doesn't directlywrite2. Hint isn't a live link bit.
No blocked callbackPC/stack captured; idlePC doesn't establish cause/app/QEMU.

Native PMstop epilogue4207bcca still hasalarm17535664. Natural cancelhelper
4207a0e6 enters atguest7791516us withsamealarm, returns7791544us/alarm0 BEFORE
deadline. RA42070ad4 identifies cnx_sta_leave42070aac/628B. ELFcheckedcalls:
42070acc->pm_stop,42070ad0->pm_disable_keep_alive_timer. Same initializedbackend
1070352264, realROM/OSI bindings throughout. Then appflag0; APreturn restores
actualHTTP/PMactive/flag1, newalarm20137076. No missing-cancellation patch needed
on this leave path; other callers/lifecycle/RF/hardware remain open.

Proof factory-pm-runtime-validation-20261025.json: fivegzip9956B/13sourcepins.
Consumer terminal0 repeats predicates/rawreads, callerJALs, preserves factory
passedfalse and rejects9evidence mutations. See tests/WIFI_PM_RUNTIME.md.
qemu-v1 failed obsolete apphint assumption, v2 factoryHTTP, v3nativeonly passed;
all remain ignored scratch, not paired acceptance. Finalhostunits terminal0.
Original24209 handle absent, but persistedv2failure/ownerexit inspected before
new run. No restart based solely on observing a timeout or missing output.

CIM18:37:44UTC matches all12original PID/name/creationUTC. Diagnostic243cycles,
oldmatchedmain/V8=682/674; allguardsrunning, oneROMboot/noUART/workloaderrors.
Snapshot long-owner-observation-final.json. Concurrent reportwrite truncated
an earlier read; bounded retry succeeded, earlier stalePS variable not evidence.
Pending prefixes only, not8h/H10. No secondQMP/RSP or protectedinput changes.

NEXT item4: actual factory callback/SDK boundaries at reconnect stall; other
cnx_sta_leave callers, TIM/null-failure, station+820lifetime, negotiated BSS
validation/overflow and remaining whole-image computed aliases/gaps. Otherplan
items and final independent network/display/full/H10/physical gates stay open.

## CURRENT 2026-10-25 — factory event-post returns; application callback not observed

Previous checkpoint1599acede. Continue item4. New factory_disconnect_qemu.py
uses explicit immutable CLI inputs, one owned RSP connection and one QMP owner
thread. One-shot breakpoints are removed before resume. Initial ignoredv1
forgot removal and repeatedly hitret, preventing guesttime/APrestore; invalid
observer control, NOT firmware evidence. V2–6 exploratory; finalv7 is archived.

Final originalexec42947 terminal0, PID37708/SmallTV-5671e7f01262 absent by actual
CIM18:55:01UTC. OneROMboot/no panic, owned stop/controller join/input rehash pass.
Ten observed boundaries: PMret42076790→4206c1d2; leave-tail4206c438→4206dfa4;
ROM crypto call4206dfb2/return4206dfba (40001e68 is hal_crypto_enable entry,
not coexistence as an exploratory label guessed); SDKcallback at42085452
returns via4206dfd8; event-postcall4206e03e→42067b46 id5,length41 returns0 at
4206e042. Actual payload/stack neverread. Appentry4200c602 and connect-return
4200c656 armed but nothit in10hostsecond inactivity window. Controller restored
AP afterguest1.007137seconds; lastguest snapshot later, hint2/PM0/alarm0.
No claim of lost event/blocked thread/app-or-QEMU cause from idlePC or timeout.

New station_leave_match requalifies old/new libnet80211 SHA and complete
wl_cnx.o::cnx_sta_leave, factory4206c1ae..4206c444/662linkedB and native
42070aac..42070d20/628B. PMstop binding checked; not parent state-machine or
all branch/lifetime semantics. Initial ignoredqualifier guessed cnx.o name;
actual archive is wl_cnx.o, corrected before final match. No SDK input changes.

Proof factory-disconnect-validation-20261025.json: fourgzip12414B/14sourcepins.
Reader repeats completebodymatches, checks realcallerJALs/metadata and rejects
9 alterations. Event-postreturn0 is observed; actual event queue/delivery not
yet qualified. Final observer additionally bounds diagnostic interrupt and
exits nonzero on controller/transport/cleanup/UART/hash errors; v6 archive kept
in ignored archive-v6 rather than relabelled as final. Consumer finalsession
terminal0; all10boundaries and9controls replay. NEXT inspect real default event-loop dispatch and netif/other
handlers preceding the factory appcallback, then remaining TIM/null/lifetime/
negotiated-period/whole-image gaps. Preserve both failed recovery and native
cancellation resolution. No firmware rebuild, protectedinput change or boardI/O.

## CURRENT 2026-10-26 — factory reconnect cause proved: startup unregisters app handlers

Previous goal turn PROGRESS:1599acede/b15a01a73; current branch unchanged on entry.
Continue user-priority item4/factory audit; do not return to deferred1–3 yet.
New evidence resolves the previously open appcallback absence. Original reference
wifi_dns.c already shows successful startup teardown; actual assembly/live calls
now confirm it. No SDK/QEMU fault was established by the older idlePC/timeouts.

Factory initialize_wifi_station success path cd90 sets hint2, cdae unregisters
IP_EVENT/0/c602, cdc0 unregisters WIFI_EVENT/ffffffff/c602. Both real APIreturn0.
Then startup event group is deleted. Keeping that original group-using callback
without preserving its group would be unsafe. Native network_init retains its
atomic-state callbacks; added FIXED_RECONSTRUCTION explanation only, no executable
change/new firmware build. AppC912/ELF9E4E/ROM289C/QEMU2DF9 remain unchanged.

Factory finalexec12743 terminal0, PID1388/SmallTV-da2f4da0c1ba. Startup4breakpoints
plus5 runtime boundaries observed. Samequeue: postentrycount0, queue-sendresult1/
count1, driverpostreturn0/count1; sys_evt dequeues/count0 and invokes actual SDK
callback420456ea for WIFI_EVENT5/41B, then returns, queueempty/runningtask0.
CurrentTCB matches the defaultloop task at both callback boundaries; task/global
and queue offsets qualified from exactfactory instructions. PM0/hint2 persists.
No payload or stack reads; nine4B eventmetadata words plus priorboundedPMdecoder.
Early helper probe65916 and startup probe94930 terminal0 and cleaned; excluded
from final proof. First host test lacked valid instructions at private stub
entry addresses, fixed with ret boundary bytes; not a firmware CPU exception.

Native finalexec91502 terminal0, PID40996/SmallTV-685dea4f9739, actual connected→
disconnected→reconnected and HTTP ready, same backend cancelled after pm_stop by
cnx_sta_leave and then rearmed. CIM10:24:42UTC confirms finalfactory absent;
native and prototypes42984/9700 already absent10:14:55UTC. OneROMboot/no panic
each; no physical flashing/serial/reset.

New test modules separated by role: static event_delivery_layout, numeric
event_delivery_metadata, literal event_lifetime_test, live event_lifetime_qemu,
offline verify_event_lifetime_evidence. Private test passes24 cases/all21starts
of full50B dispatcher;9 selected144B startup-tail/error paths with explicit SDK
stubs;9 realnativecallback events;6metadata cases and15 rejection controls.
Not full startup or registry implementation. Native reconnect tested in actual
fresh QEMU as well, not inferred only from direct callback unit invocations.

Proof event-lifetime-validation-20261026.json pins20sources/sixrawgzip15223B.
Reader terminal0 recomputes algorithms and both exact typed read streams;
11 runtime mutations reject wrong unregister/return, queue/count/task forgery,
stale native connected state, extra read, live owner, reset/full-lifecycle claim.
Document tests/WIFI_EVENT_LIFETIME.md supersedes the historical unresolved cause.
Initial11984factory proof is retained in ignored archive-before-lf. Final observer
normalized to Git eol=lf before capture, avoiding post-checkout source SHA drift.
Helper comments completed; finalhostunits replay passes. Read unitJSON in
PowerShell with -AsHashtable: wifi_event/WIFI_EVENT are distinct keys.
Factory failed recovery remains a known application defect; native retention is
an intentional correction, not a requirement to copy factory teardown.

IMPORTANT long runs: actual CIM09:50 and10:14UTC finds all12original owners
ABSENT, despite stale running guard/supervisor files. Last report prefixes:
diagnostic654cycles, matchedmain1091/V8=1081, passedfalse/errornull, last diagnostic
supervisor observation21:23:55UTC25Oct. No terminal success/exit evidence; do not
call them8h/H10 passes or combine durations. Cause of disappearance unknown.
No restart or source mutation. Read-only snapshot:
.build/factory-event-delivery-20261026/long-owners-absent.json. Frozen inputs should
still be preserved for later interrupted-run analysis under deferred1–3.

NEXT item4: remaining TIM/null-completion branches, station+820 lifetime, BSS
negotiated-period callers/range-overflow, remaining whole-image computed aliases
and startup/error lifecycle branches. New tool-quality lead: GNU wrapper
objdump-xespv2p2 decodes actual RV32 bytes712b at420aeb6e as addiw even with -m
riscv:rv32. Prepared ELF is ELF32/RVC, no archattribute. Literal RV32 Unicorn
control proves JAL: target420af10a,RA420aeb70,s6unchanged17. Investigate decoder
selection before trusting GNU mnemonic-based whole-image searches. Raw-byte
qualifiers/private RV32 tests remain independent. Ignored cjal-control.json
and cjal_control.py retain the control. Other plan points and final independent
network/display/full/duration/hardware acceptance remain open. Goal stays ACTIVE.

## CURRENT 2026-10-26 — ISA-qualified factory disassembly and five call candidates

Previous goal turn PROGRESS25b8ef015. Active user priority remains factory item4,
not deferred1–3. No new physical I/O, firmware build, QEMU/SDK/ROM mutation or VM.
Native appC912/ELF9E4E remain unchanged. Do not restart absent duration owners or
call stale prefixes acceptance. Frozen prior inputs remain available for replay.

GNU main and both dispatcher variants misdecode ISA-less ELF/raw16bit712b at
420aeb6e even with -m riscv:rv32. Real RV32 proves C.JAL/target420af10a/RA420aeb70/
s6unchanged17. New reverse/rv32_disassembly standard ISA metadata view preserves
codebytes/addresses, no loadsegments/DROM/data; actualGNUcanary before export and
toolpinsbefore/after. Verified unique temp child paths before recursive cleanup.
disassemble_factory.py gains optional verified --dump; fullELFexport and pureaudit
are separate tools. Assistant repairs old C.JAL encodings with visible warnings,
rejects otherRV64 and retains compressed/numericSPframehints. Original ELF intact.

New fullzero export .build/factory-decoder-20261026/full-rv32-zeroes/factory-rv32.asm
contains813936bytes/288036rows, all287952oldrows identical. Added84zerohalfwords/
168bytes (128vectors/40flash) via-z.453C.JALcandidates:old443c.addiw/10.insn;
all396GPaccesses unchanged. Canonical rawmapold67f4f41f..,newd2d264eb..;
oldGNUtextSHA d82e4db7a45a128554f7da5abf92a0be0190f5fdd238899ad9f332fe3d16feb9.

Audit uses frozenSDKgap graph5143functions, not later5161. Ancestor+delta reused
by hashes, canonicalgraph36a65f46edcab37281fd079b2295ab0ff20fad7f520db9cefa0c769dea4b30f9.
448refs agree/452targets known. Five unmatched:40380180→40380584,
4038018e→40380566,420a3a12→420a3d32,420a3a14→420a3da2,420a3e32→420a3fd4.
Don't declare missingfunctions/bugs or all453reachable: code sections can contain
inline data/unreached regions. Need boundary/caller/SDK qualification next.

Final evidence rv32-disassembly-validation-20261026.json:3newgzip11468B/10sourcepins.
All29tests no skips:21assistant+8ISAview. Every2048C.JAL encoding runs literalRV32
and realGNU; PC/RA/s6 and parsedcalltarget checked. IndependentELFreader, wrongISA,
tempcleanup/range and realcapture publicIROMCLI tested. Reader reconstructsgraph,
recomputes fullbyte/call/GP audit, reruns29tests, rejects8report+1realGNUtargetmutant.
Finalconsumer exec0c42ea terminal0; first output lost to compaction, actualCIM
found no originalconsumer, archive already complete, so onlyconsumer rerun.
Do not rerun archive.py into an existing output. All source inputs LF before pins.
Docs tests/RV32_DISASSEMBLY.md include commands and claims. Whole-image completeness,
candidate reachability, semantic equivalence and physical flags remain false.

NEXT item4: qualify five remaining call candidates, revisit GNU mnemonic-dependent
searches, then TIM/null-completion/station+820 lifetime/BSS negotiated ranges and
other aliases/startup error branches. Retaining Wi-Fi callbacks remains verified
intentional factory-bug correction. All broader goal and acceptance gates persist.

## CURRENT 2026-10-26 — five runtime gaps identified; FIX NTH-ALLOC-FAIL NEXT

Previous goal turn PROGRESS79fc5c424. Factory item4 priority persists. New
runtime_call_gaps module qualifies19completebodies/1004linkedB:10factory508B,
9native496B. Seven pinned objects (vectors, C++stubs, GCC15new_op/new_opv/
new_opvnt/eh_globals/eh_catch) and named bindings, not guessed function labels.
Factory compiler version not established. Persistent Ghidra projects untouched.

Five sites:40380180/18e→xt_unhandled_exception/panicHandler in fullpanic214B;
420a3a12/14→begin/endcatch in20Barraynothrownew;420a3e32→UnwindDeleteException
in48Behglobalsdtor. Scalar/array similar-byte trap resolved via actual_Znaj
veneer→_Znwj and native symbols. Native arraynothrow DOES exist at420a413e;
only_Unwind_Resume absent. Do not repeat the exploratory scalar absence claim.

Confirmed actual bug in BOTH factory/native frozen images: new[](nothrow)→new[]
→scalarnew→cxaAllocateException abortstub when mallocNULL/no new-handler. Does
NOT returnnullptr or enter landingpad. Caller42040efc requests512B and checks
NULL at42040f02→42040f80. Name/fullbody not yet SDK-qualified; likely-NVS source
similarity is not proof. NEXT fix native nothrow failure paths safely, including
zero-size/newhandler/ownership, fail-before/pass-after/source+target tests, new
production app under firmware/development and actual NVS/network workflow.
Don't patch shared SDK or any frozen old ELF/build/helper. Ordinary throwing new
and all exception semantics are not implicitly fixed by nothrow-only wrappers.

176privateRV32 cases pass as observation:132panic fullframes/return/mret,
allocsizes0/1/512/ffffffff, handlerretry, cleanupnull/empty/one/two, nothrow
success/abort/directlandingpad in BOTH images. Desired nothrowOOM contractfalse
is explicitly retained. Panic callbackreturn/directEHentry synthetic; full
endcatch internals/naturalEHdelivery unproved. Valid ret at external private
stub entries required before Unicorn codehooks, fixed before final capture.

Proof runtime-call-gaps-validation-20261026.json:10gzip62267B/12sourcepins;
consumer redoes19bodymatches,176cases,13input/7reportmutations (forgedfix too).
Source modules separate qualification/instructions/controls/consumer. Original
images/library/selectedbuildobjects rehashed; no app/SDK/QEMU/sourceproducer
mutation, VM or physicalI/O. Broad compilerarchive exploratory scan90076 stopped
via verifiedownedhandle, terminal1; narrowed EH/new members completed normally.
All12old durationowners remain historicallyabsent/unaccepted; don'trestart
or accept stale statuses. GoalACTIVE, full original scope/points1–3 deferred.
After NTHfix: transient Ghidra ranges, actualcaller matching, remaining TIM/null/
station+820 lifetime/BSS negotiated period/aliases and final acceptance gates.
Final consumer exec3a80d5 terminal0 repeats176cases and13+7controls after adding
the exact512-byte caller input. Desired OOM contract staysfalse, not accepted.

## CURRENT 2026-10-26 — NTH-ALLOC-FAIL fixed, production app and independent gates

Previous goal turn PROGRESS cfd5cb9f3. User-priority item4 continues; points1–3
remain deferred. App/platform/nothrow_new.cpp shares malloc/get_new_handler loop
between scalar/array CABI wrappers, marked FIXED_FACTORY. Size0→1, null failure,
retry and changing/removing/nonreturning handler preserved. C2/RV32/IDF6.1,
no C++exceptions and no heap-abort profile enforced; no SDK patch, no FlashI/O,
no new endpoint/delay. Throwing/aligned new unchanged; unsupported linked aligned
nothrow symbol rejects checker. Upper app_main NVSinit ESP_ERROR_CHECK stillfatal;
this is not full boot-under-global-OOM recovery.

Final build .build/small-tv-nothrow-20261026, production DEBUGoff archived under
firmware/development/small-tv-esp32c2-reconstructed. AppSHA4f2cfd9837fff0143098eb32f3a2ec6f59170d23902f17f2b2e9fff857165195,
ELF eb20fb1309d1a5f28229d2ca846924cd18b311da229d34a1319a324d621ee2e6,
source5b6252cec1006fc3b4e5a6fc2dc2f72ca4a396a2a8c6bac521f45be0bf07d161.
App1475840B (-640 vsC912),60160free. Helper50B+two4B wrappers=58B.
Strengthened post-link checker validates local helper calls too; real NVSPage::load
328sourceB matched to linked body and its allocation selects wrapper. Existing
Wi-Fi guard post-link/ROM check stillpasses. Final buildexec50378 terminal0;
ELF/app identical to firstbuild46239, only source/validator metadata updated.

26host source cases,26actual RV32 cases (incl4NVS outcomes), actual old9E NVS→
abort before vs EB20 NVS→NO_MEM after. Private partition/ROMmemset/malloc/handler/
free boundaries explicit. No wholeVM OOM fault injection. New-handler nonreturn
is retained, not converted to success.13semantic input controls including wrong
localhelper/NVScallee and oldunwrappedbuild pass. Main native gate6300checks (initial6298; conditional async-wait CHECK count varies),
3727privacy;16inventorytests/223appdefs and6artifact checks pass. CPP/noexcept
simple definitions included, missing prior Wi-Fi guard support row restored.
HostCPP26 now mandatory in tests/run.ps1; final exec33184 terminal0.
Protected production inputs unchanged.

Finalnetwork exec93791 terminal0: configreboot/cold/reset, HTTP settings2,
connectedSTA192.168.43.15/time_synced and fresh NTP1/1/2, ROMboots2/1/2.
Network-only copiedprofile has noLCD; weather loopback503 not weatheracceptance.
Finaldisplay exec3351 terminal0: factory and native setupframes all57600pixels
each exact acc588ab.., onecoldcycle each, network not used as LCDgate.
4finalowners34392/21584/21168/35764 absent byCIM12:24:26UTC, nativeheldhandlesexit0.
No physicalserial/reset/flash. Earlier network2/display1 also passed, notfinalpins.
Network1 failed only stale helper expected10.0.2.15; actualSDK192.168.43.15 proven
in successfulfinalrecords. Scoped newpredicate derives configuredaddress, frozen47
helperfiles/QEMU unchanged. Preserve prototypes in ignored scratch, don'tcallpass.

Proof nothrow-fix-validation-20261026.json:14gzip124101B, reused legacyqualification,
sourcepins plus optionalmandatory-test-entrypoint pin. Readerexec7eb452 terminal0
replayed before/after/static+13controls and recomputed clocks/2wholeframes;
5runtime mutations rejected. Need final replay after context/docs/sourcepin refresh.
Consumer requires exact current ELF/object/NVSarchive and frozen old9E ELF/app;
these build dirs must remain for replay. Original whole-image completeness and
physical/full/24h flags false. CODEC-REPRO fresh library/cache identity remains
deferred. Don't widen old9E-specific observer pins to acceptEB20: qualify layouts
and budgets first when returning to old network/heap/soak gates.

NEXT item4 after focused commit: qualified transient Ghidra ranges for the five
runtime sites; full identity of factorycaller42040efc (nativePage::load known,
factory identity stillunqualified); TIM/null-completion/station+820 lifetime,
BSS periods/range-overflow and computed aliases. Broad plan stillACTIVE.

Final native count6300 vs initial6298 is an observed check count; dispatch has conditional async-wait CHECKs. Do not rerun to seek an exact old count or relax functional assertions. Final proof has14gzip124100B/30sourcepins.

Final reader session22193/output8f0061 terminal0 after30pins/native6300 refresh. Getter `_GLOBAL__sub_I__ZSt7nothrow` at420a416a is registered in init_array and tail-calls pthread_mutex_init(3fcb6920,0). SDK valid-mutex lock skips lazy allocation. This is static/source review, not full pthread/RTOS OOM execution. Final prototype owners all absent; no pending sessions. Ready for focused commit.

## Latest checkpoint — runtime metadata, 26 October 2026

RecoverFactoryRuntime.java executed only in a copied read-only Ghidra project;
ten object-qualified bodies / 508 B recovered, three functions created and 116
instructions added. Full graph changes exactly match instructions and scoped
ownership: enumerated5140→5143 (API5145→5148), 19 changed function records,
GP accesses unchanged. All453 C.JAL now have exact references/target functions.
Detached return420a3e08..3e0a and abort-forwarder420a3fe0..3fe8 stay decoded and
unowned: no guessed SDK names. Original/copy ten project hashes unchanged;
both headless sessions terminal0/read-only discarded. Production4F2C/EB20,
SDK/QEMU unchanged; no VM or physical action.

Proof runtime-metadata-validation-20261026.json reuses original full graph and
seven runtime objects; six new gzip11097B/17pins. Consumer61b949 terminal0,
20 actual altered-input controls rejected. Historical runtime consumer1b9dd6
also terminal0 with176literal cases/13input/7report controls. Do not call the
old OOM-failing-before flag a regression; current correction is the separate
nothrow proof. Details: tests/RUNTIME_METADATA.md.

NEXT user item4: factory512B allocation caller42040efc belongs to Ghidra body
42040e56..42040f8e/312B. This is metadata ownership, not full source identity.
Factory descriptor says IDFv5.5.4 (already documented), currentSDK6.1 NVSPage::load
is328sourceB and calls Header constructor out of line; factory has an inline19B
fill loop. Check pinned SDK5.5.4/compiler/options before requiring full-body
matching. Existing14compiler not found in inspected tool directories;
SDK5.5.4 tools.json selects esp-14.2.0_20260121. No toolchain downloaded yet;
no compiler version proved and no strict relocation matcher weakened.
Then TIM/null-completion, station+820 lifetime, BSS periods/range-overflow and
computed aliases. Deferred points1–3 and full/24h/physical gates remain open.
No active exec/VM from this checkpoint. Broad goal ACTIVE; no push performed.

Final staged-source check aacd3a confirms all17 source pins equal Git index bytes
and production app4F2C SHA is unchanged. Final consumer2ef9bb terminal0 repeats
the scoped validation and all20 rejection controls. Ready for focused commit.

## Latest checkpoint — factory NVS caller, 26 October 2026

Factory call42040efc fully identified as Page::load42040e56..42040f8e/312B.
Four complete factory bodies1442B, four native1158B matched strict unchanged
objects. Clean SDK5.5.4/735507283d5b + officialGCC14 esp-14.2.0_20260121,
RV32IMC/Newlib/Og/no-shrink-wrap is a sufficient matching profile; factory
compiler/config identity still unproved. Toolchain isolated under this worktree
.build/factory-nvs-20261026/idf-tools; archiveSHAc2734714… verified from SDKmanifest.
No sharedSDK/QEMU/production changes or physical action.

Public tools/compile_factory_nvs_fixture.py produces source object and an
analysis-only DWARF carrier. Qualified and qualified-replay are byte-identical
object9ed443fe…/carrier314324a8…/provenance258dependencies(34SDK), bothexec0.
Newlib fixture config is derived from the existing native profile with libc
selection changed; it is not a recovered factory sdkconfig. Original mixed
Picolibc/Newlib failures and rejected optimization prototypes remain ignored.
Current/factory sourcePage::load and CRC exactly equal; entry-table source differs.
page_layout sees Page84B/offsets8,12,16,20,64,66,80/read_raw-vslot12 in both ELFs.

197caller cases pervariant(394) reached every120/118caller instruction starts,
checked all84pagebytes/return/ABI/read sequence/ownership.442directfind cases
reach all51starts, including all tails and length0 bounds. Normal allocator,
partitionI/O, ROMCRC arithmetic and entry-table are explicit boundaries;
NULL-return factorycase is synthetic. Two separate actual allocator cases
follow factoryNVS→abort vs currentNVS→NO_MEM through real runtime instructions.
Do not call the factory fixed. Upper app_main NVSinit error stillfatal.

Proof factory-nvs-validation-20261026.json:11gzip185441B/20pins, oldruntime and
currentwrapper qualifications reused. Consumer83649/bf8c31 terminal0 recomputes
394+442+2cases and13input+5report controls. SDKs remain clean and production4F2C/
EB20unchanged; no current VM or exec session from these finished runs.

NEXT user item4: actual mLoadEntryTable execution for corrupt/incomplete/duplicate
records and read/write/erase faults. Its bodies are statically matched970Bfactory/
822Bnative, but SDK6.1 DEFAULT_PURGE_AFTER_ERASE=true adds purgeEntry and extra
purge arguments vs5.5.4. This is a real unverified repair/write policy difference,
not covered by caller delegation tests. Do not automatically disable purge to
match old bytes. Then TIM/null-completion/station+820 lifetime/BSSoverflow/aliases.
Deferred1–3, H10/currentABI observer qualification, CODEC-REPRO, full/24h/physical
remain open. Goal ACTIVE. No push requested/performed this checkpoint.

Final replay78978/e4246d terminal0 after source-pin refresh; metadata replay852092
also terminal0 with20controls. Staged check99e25a: all20pins equal Git index bytes,
production appSHA unchanged. No pending exec/VM. Ready for focused NVS commit.

## Latest checkpoint — partial-record repair, 26 October 2026

Actual TABLE/bitmap/purge instructions tested, factory3bodies1106B/native6bodies
1108B. New files: reverse/nvs_repair_linkage.py, nvs_partition_fixture.py,
nvs_partial_repair.py, nvs_repair_controls.py, verify_nvs_partial_repair_evidence.py.
No changes to previous source pins, production4F2C/EB20, SDK or QEMU.

All126slots eachvariant: factory4Bbitmap, native additional32Bzero payload.
Sector bytes/other records/reserved bits checked.252reopen+12clean baselines
issue no writes/erases.68faults (4boundaryslots/everyactualAPIordinal/before or
half-transfer) retain actual physical prefixes;68new Page instances recover.
Total652CPU executions, ABI/fields/counters/error checked. This is private
PartitionAPI byte fixture, not live flash/SPI/WIP/fullVM power cut acceptance.

10native failure/retry cases retain16..32nonzero payload bytes because bitmap
alreadyERASED: includes partial bitmap and purge failures. Original operation
returns0x104; no invented secureerase guarantee, no automatic purge disabling.
Last-slot RAM sentinel depends on retained bitmap: in-flightrepair126 vs fresh
allnonEMPTY INVALID_ENTRY. Old simplistic oracle corrected, not widened.
Initial missing outlined nativeGET/SET helpers now fully qualified; prototypes
preserved ignored. JALR mutant corrected to change bit1, since bit0 is ignored.

Scratch .build/factory-nvs-repair-20261026; target-final-v6 cbd9d2 terminal0,
11input controls4fcf20 pass. Proof nvs-partial-repair-validation-20261026.json:
3gzip44243B/25pins; initial reader57870/596e0b terminal0 with652CPU+11+7controls.
Prior factory object/basequalification reused, no new full dumps. Update source
pins/final replay after last report-control edit before commit.

NEXT item4: other actual entry-table branches (ILLEGAL/WRITTEN/corrupt headers,
variable spans/duplicates, HashList allocations, eraseEntryAndSpan/purge ranges),
including return/error and physical writes. Factory page object already contains
several full helpers (diagnostic repair-factory-probe.json in oldfactory-NVS
scratch), but HashList/Item need their own SDK5.5.4 objects and strict bindings.
Do not stub these algorithms and call the whole loader tested. Then pending
TIM/null/station+820/BSSoverflow/aliases. Old1–3/full/24h/physical remain open.
GoalACTIVE. No VM, board, serial/reset/flash or push from this checkpoint.

Final reader20605/226540 terminal0 after refined actual-rollback/purge-error report
controls:652executions/11input/7report controls pass. Staged27baf6 confirms25pins
equal Git index bytes/appSHA unchanged. No pending exec/VM; ready for focused commit.

## 26 October 2026 — inherited NVS record defects before correction

Full Page/Item/HashList direct-call closure qualified: 19 factory functions /3368B,
20 native /3062B. Item/HashList unchanged SDK5.5.4 objects and canonical provenance
are byte-identical across two analytical builds. Actual official C2 ROM CRC code
and table executed; 192 cases reach all60 instruction starts/all256 table indices.
528 real header cases reach all109factory/85native starts, including bad CRC,
span/type/bounds. 23 records+11malloc failures eachvariant, full bitmap/lookup/
ABI/cache ownership checks. Seven actual input controls and six report controls.

Both factory and app4F2C/ELFEB20 have three real inherited defects: wrong erased
counts for ILLEGAL/alreadyERASED children, destructive 24-bit hash-collision
candidate handling, final duplicate lookup ignoring BLOB chunk/generation.
The published-index scenario retains a valid old index while mistakenly deleting
its old data chunk. Full Storage.init/powercut is still untested. These are
explicitly failing desired native contracts, not a parity success or a QEMU bug.
No shared SDK, production app, VM/board/serial/reset/flash or push changed.

New proof nvs-records-before-validation-20261026.json:9gzip/202203B/33sourcepins.
Scratch .build/factory-nvs-records-20261026, source objects replay identical.
NEXT local, exact-SHA-guarded SDK source corrections with FIXED_FACTORY marks;
keep before app/ELF and source pins immutable, preferably use a separate task
worktree for production changes. Fix counters, verify real namespace/key/chunk
identity for hash candidates, pass exact chunk to final findItem. Retain type
replacement semantics. Then fault/reopen tests, build/archive app, independent
network/display checks. Other factory/TIM/lifetime/BSS/aliases and deferred1–3,
full/24h/hardware remain open. Goal ACTIVE.

Final reader99701/e31951 terminal0; staged33pins match, no sensitive findings across22files/9expanded gzip. Ready for baseline commit; then local NVS corrections in new task worktree.

## 26 October 2026 — correct inherited NVS recovery in a local component copy

Previous checkpoint7ebe96846 preserved failing-before records. Created task
worktree .worktree/small-tv-nvs-fixes / codex/small-tv-nvs-fixes from it, leaving
factory-audit old source/4F2C/EB20 inputs immutable. Common SDK6.1 stays clean.
Exact source SHA patcher + CMake replace only our NVS Page translation unit;
FIXED_FACTORY comments describe count, identity and I/O corrections. New build
postlink guard qualifies all20current direct-call closure bodies/3184B against
source objects and validates generated source; factory19bodies/3368B preserved.

Fixed ERASED/ILLEGAL span accounting, full namespace/key/chunk comparison for
24-bit cache hash candidates, exact chunk for last duplicate search, and missing
recovery I/O error propagation. Native-before136faults reproduce50hidden errors;
factory108faults reproduce32. Selected current130faults surface0x104/INVALID,
stop immediately, preserve physical prefixes, and fresh Page reopens retain keys
and correct counts. A second reopen is stable/no programs. No secureerase claim.
Additional damaged-tail probe reproduced count3 for twoERASEDslots in firstfixed
candidate; corrected adjacent tail accounting too and added permanent vector.

Build prototype initially failed configure because IDF_PATH used Windows
backslashes while target SOURCES used forward slashes. Normalize declared path,
require exactly one replacement; no broad basename fallback. First successful
candidate89E8/0464 retained ignored with its passing checkpoint; final34CB/73BE
includes the tail correction and mandatory NVS linkage guard. App1475968B,
128Bmore than4F2C,60032Bpartition free. Source aggregatee3a1e0b5….
Final build89297/b5a19d terminal0; app/bootloader/assets/metadata archived normally.

Final machine check8105/f5ff8d terminal0:192actualROMCRC+528headers,23records and
11OOM eachvariant;27native extra records+27reopens+12FULL/FREEING;130faults each
with recovery/stable retries;652previous partial cases. Seven actual input and
five source/link guards pass/reject. New counter/key/error contracts pass.
Native gate first stopped on changed build inventory; reviewed changed files,
added10NVS tool inputs, updated explicit hashes/disposition, did not bypass gate.
Second native79334/946dd8 terminal0:6298checks,3727privacy,26nothrow,16map controls.
Six artifact checks848adc terminal0 using new explicit --resources argument.

Independent network58264/9f97ba terminal0: Wi-Fi setup/HTTP/settings persistence,
reboot/coldboot/reset and threefresh SNTP phases, no LCD device. Independent
LCD84889/71e571 terminal0: onefactory+onenative coldboot,57600pixels exact.
All4ownedVMs exited; initial non-escalated CIM call was inaccessible and its
absence inference discarded. Final fail-fast escalated CIM51acc3 verified all4
matching owners absent. No foreign processes, physical board/serial/reset/flash,
QEMU source, push or global SDK changed.

Proof nvs-recovery-validation-20261026.json:23gzip/250808B/51sourcepins. Final
reader62193 is collecting/replaying; obtain terminal0 before committing. Next
full Storage.init/multisector repair/power cuts and TIM/null/station+820/BSS/
aliases. Deferred1–3/full/24h/hardware remain open, goal ACTIVE.

Final reader62193/e7059c terminal0; all phases reproduced,51pins,7+5+6controls. No pending exec or ownedVM at this checkpoint. Stage/scan/commit current fix; factory-audit baseline remains7ebe96846.

Precommit scan1686ee checks52staged files/23expandedgzip/2LFS data/51pins; no unresolved sensitive findings. Four generic PEM parser constants classified against official SDK header. No push; currentapp34CB/73BE remains frozen.

## 26 October 2026 — full Storage init/read and multi-sector before evidence

Previous goal turn made concrete progress in c95e3674b. Verified clean HEAD and
continued user factory item4 in small-tv-nvs-fixes without changing production
34CB/73BE or any existing proof/build/network/LCD input. Added only analysis
sources/tests/docs, source SDK5.5.4/6.1 and QEMU remain unchanged.

Compiled unchanged SDK5.5.4 PageManager/Storage twice with the same qualified
GCC14 profile; objects5bcb5625/aed3fbcf, canonical provenance and resolved DWARF
carrier ELF are byte-identical. The full factory Storage.init is42041d38/314B,
PageManager.load42043314/620B, Storage.readItem42041740. New strict qualification
follows every named direct call from init/read,71factory bodies8750B and53native
7630B; no unqualified NVS algorithm/relaxed identity. Standard array new/delete,
allocator/string copies and synthetic Partition API are explicit boundaries;
actual C2 ROM CRC code/table executed. Factory array OOM abort is not replaced
by a claimed real NULL path; this fixture boundary is explicitly synthetic.

Resolved DWARF independently verifies Storage104B/PageManager40B/Page84B/
NamespaceEntry28B/BlobIndexNode40B and all used offsets/virtualslots. First CPU
prototype used get_readonly slot36, reached PC0, and was corrected to real slot40
before accepted runs; actual slot guards and offset mutants prevent recurrence.
No QEMU emulation defect or production SDK fix was inferred from that fixture bug.

Full literal CPU baseline:9wire images pervariant plus fresh stable reopens,
ordering/duplicates/FREEING before and after target activation/BLOB publication/
two-chunk reads. Real Storage.readItem returns factoryNOT_FOUND for old valid
BLOB + uncommitted new generation in the same page; current returns oldA.
Cross-page uncommitted generation retainsA, published new index returnsB,
two-chunk returnsAB. Thus prior Page fix now has a complete Storage witness.
Six additional cases use sixactualNVS sectors24576B:5used+reserve,6writable
NO_FREE_PAGES,6readonly successful unchanged reads. No fabricated sector size.

460actual faults (224factory/236native) cover every observed non-512-byte I/O
ordinal on4new inter-sector paths, each before/half-transfer. Retained media
is independently replayed from issued physical program/erase prefixes. All460
fresh Storage retries retain expected values. However higher layers hide130
factory and134native errors: error contract false. PageManager ignores some
search/erase returns; Storage lookup loops and private void cleanup helpers lose
I/O errors, init can become ACTIVE despite an underlying failure. This is new
unfinished corrective work, not a pass waived by successful fresh retry.

8actual source/frame/call/ABI mutations are rejected. Repeated analysis builds
13e573 and public strict closure90cd77 completed0. Producer24173/0c164f completed0;
geometry29546/bb5f43 completed0. Proof nvs-storage-before-validation-20261026.json
archives9newgzip536773B/60sourcepins and reuses prior3objects/config/ROM witness.
Consumer53022 is replaying; require terminal0 including5report controls before
staging/committing. No new firmware build, VM, board/serial/reset/flash or push.

NEXT exact I/O propagation through PageManager/Storage, no subsequent I/O,
INVALID storage, preserve normal NOT_FOUND. Return status from private cleanup
helpers with consistent declarations/definitions. Use exact-SHA guarded local
NVS component source/header copy; do not patch shared SDK, invent global error
state, misuse enum fields, or leave inconsistent class declarations across TUs.
Preserve all34CB/73BE before inputs in this worktree; create separate task
worktree for the production correction. Then rerun before/after fault matrix,
archive new app, independent native/network/LCD checks. Remaining TIM/null/
station+820/BSS/aliases and deferred1–3/full/24h/hardware remain open. Goal ACTIVE.

OOM checkpoint:4custom malloc failures reproduce40Btemporary leak at second BlobIndex allocation, both factory/native. Proof10gzip539365B/61pins; finalreader47042 pending. Add cleanup-on-all-exits to next correction. Firstreader53022 failed only numeric-key vsJSON string-key equality, canonicalized without changing archived bytes.

Final reader47042/2a9a74 terminal0, all18+18+460+460+6+4cases and8+6controls reproduced. Native upper-error and temporary-cleanup false; data preserved in selected retries. No pending exec/VM. Stage scan26files/10gzip/61pins clean; ready for focused baseline commit, then production fix in a separate worktree preserving this snapshot.

## 26 October 2026 — fix upper Storage recovery errors and temporary ownership

Previous goal turn made progress in a3ebb45d0 with a complete failing-before
Storage witness. Verified clean HEAD; created .worktree/small-tv-storage-fixes /
codex/small-tv-storage-fixes from a3ebb45d0. Old small-tv-nvs-fixes remains frozen
with34CB/73BE, source pins and full before proofs. No shared SDK/QEMU mutation.

Five C++ fragments in storage/nvs correct PageManager.load, Storage index
collection/mismatch/orphan cleanup and init. PageManager consolidates predecessor
erase with preserved FREEING skip, first match, TYPE_MISMATCH miss and legacy
BLOB fallback. All failed scans/erases return the original status. Storage stays
INVALID until all recovery succeeds. Cleanup helpers return esp_err_t; local
scope guard frees every temporary index even after a later OOM/I/O failure.
No global error slot or overloaded enum state is used. FIXED_FACTORY comments
mark the corrected functions and explain ownership/nontrivial cases.

prepare_nvs_component checks45source/header SHA and exactly5fragments, copies35
src files locally, patches the private header consistently, retains the oldPage
patch/report, and redirects all17component TUs. Postlink guard verifies allinput
bytes, compile commands and56native bodies7776B; factory71bodies8750B. No private
header disagreement across TUs or vendor checkout edits. Unsafe source/report
outputs are rejected. Full normal I/O sequences in9native baselines remain
byte-identical to before (1bbe8e), so no added flash operations in those paths.

First patch application was rejected atomically for duplicate CMake patch
operations; corrected before any generator write. First build33896 failed
configure because3target_sources paths were relative; resolve them against the
pinned component directory, retain strict source containment. Build15955/0d74c2
completed0. Added output-path/fragment-inventory guards, then final build97551/
e9a7e4 completed0 and archived app8758BD09/ELFDA1ED0CE/sourceF2699B39. App1476112B,
144Bmore than34CB,59888Bpartition free. Existing WARN/DEBUGoff/JPEG policy remains.
JPEG long try-compile path warnings did not cause a failed dependency build.

Producer19839/bacb08 completed0: all236native I/O failures now0x104/INVALID with
no further I/O; all retained-media retries preserve values. Before replay still
reproduces134native false successes. Four customOOM failures leave0temporary
bytes native; two replacement cases + two same-object retries pass. Sixgeometry
cases and previousPage records/652partial executions pass. Standard arrayOOM is
an explicit nullable fixture boundary, not a new full-VM OOM claim.

Native40197/710c8d completed0:6300checks/3727privacy/26nothrow, mapping controls.
Artifact681d8c completed0 with7tests including component metadata consistency.
Overlay62988/3b14e6 completed0: unchanged private copied fixture passes,8real
vendor/header/TU/app/archive/output mutations reject, original SDK/overlay intact.
Network45257/972668 completed0: setup/HTTP/NVS persistence/reboot/coldboot/reset/
3fresh SNTP phases, no LCD. Display48754/a34d42 completed0:1factory+1native cold
frame exact. CIM a73edb verified all4matching owners absent. No physical board,
serial/reset/flash or outside process touched. No push.

Inspected raw-settings witnesses locally without printing suspected values:
password empty, SSID synthetic, country/city compiled defaults, unused bytes only
zero/erased. Weather field is the fixed8B test token at offset0x11c/width65 in
pinned small_tv_network.seed_network, not a user key; NTP is private VM service
address. Initial empty-key/zero-tail assumptions rejected and were replaced by
exact fixture comparison plus padding check; all3phases pass d6980d. No user
credential values were printed or exported by this inspection.

Proof nvs-storage-fix-validation-20261026.json:23newgzip405247B/74sourcepins.
Final reader59401/fd6be3 terminal0: complete before/after CPU rerun, Page652,
8input+8overlay+5report/runtime controls, full production source/resource hashes,
6300native/3727privacy and independent3network/2LCD witnesses. Allthree native
contracts pass; physical/full-VM powercut/whole-image flags remain false.

NEXT factory TIM/null-completion/station+820/BSSoverflow/aliases and remaining
whole-image gaps; fullpublicNVS/API/arbitrary physical cuts and deferred1–3,
fullsuite/24h/hardware acceptance remain open. Preserve allold/new proof inputs;
no long VM is pending. Goal ACTIVE. Stage exact focused fix, inspect archives/
LFS/metadata locally and commit after clean staged checks; do not push implicitly.

Staged57files/23expandedgzip/2LFS/74pins checked clean (dd2404), plus decoded synthetic settings check d6980d. Finalreader59401/fd6be3 terminal0, no pending exec or ownedVM. Ready for focused commit; next factory TIM/null/lifetime/BSS/aliases.

## 26 October 2026 — complete TIM instruction comparison

Previous goal turn made progress in671ecdf59: Storage propagation and temporary
index cleanup fixed, archived current app8758BD09/ELFDA1ED0CE, clean HEAD verified.
Continued factory priority with TIM; no production/source-overlay/sharedSDK/QEMU
or physical device changes. Existing production proof source pins are preserved.

New reverse/timer_tim requalifies the old reference9E4EC88D without relaxing its
guards, then independently matches9complete native SDK bodies to the saved
current app/ELF. Checks data geometry/local anchors/public callees, actual OSI
wrappers and event11 entry. Absolute g_osi_funcs_p is intentionally resolved by
the existing unique-symbol reader; LinkedRuntime.symbol excludes SHN_ABS and
was unsuitable for that ROM-global lookup. No existing helper was weakened.

New separate tim_model/tim_instructions/tim_test cover2404cases per image,
4808executions, full TIM168/168factory and128/128native instruction starts.
Exact PM/counter stores, whole remaining buffers/config, stack/callee-saved ABI,
caller-register poisoning,64-bit clock/deadline, capped/lowword OSI408delay,
32-bitcounterwrap, truthy flags and originalpredicate boundaries all pass.
Real old predicate executes; RF/slice/sleep/dream/wake/platform helpers remain
explicit boundaries. Complete instruction coverage is not all RF paths.

Factory computes predicate even before unrelated early returns and can set488/
request null instead of sleep; native TIM relies on separateevent11 keepalive.
No production bug found in these cases. Do not restore factory requests into
modern TIM based only on this difference. BSS negotiated ranges still unproven.

Producerfa341c terminal0; independent readercb431f terminal0.9staticcontrols
including4actual body mutations below whole-image hash guard,6reportcontrols.
Prooffactory-tim-validation-20261026.json:16pins,1gzip33240B /458146Bexpanded.
No pending exec/VM; no push. NEXT remaining null/failure completions, actual
station/peer+820 lifetime, BSS producers/overflow, aliases/whole-image gaps.
Deferred1–3/fullsuite/24h/hardware stay open. Goal ACTIVE.

## 28 October 2026 — complete null-completion comparison

Previous goal work made progress: c8e672cf0 completed TIM instruction comparison;
the user-requested push sent all 34 unpublished commits through that HEAD to
origin/codex/small-tv-storage-fixes. Revalidated a clean, synchronized worktree.
No historical proof, production source, app/ELF, shared SDK or QEMU was changed.

New reverse/tx_null extends the strict TIM qualifier and matches complete
quick-wake/state-setter helpers from each SDK, with parent target, scoped local,
shared/public/absolute symbol, data and counter checks. Initial helper target
check incorrectly assumed a global namespace; the quick helper is object-local.
Corrected this new guard to use exact matched caller bindings. No old guard was
weakened and no library/ELF was patched. The first CPU run then passed.

Separate tx_null_model/instructions/test modules perform 8331 cases per image,
16662 executions. Every instruction in parents (174 factory / 213 native),
quick-wake (40/38) and state setters (27/27) is visited: 519 starts / 1524 B.
Real old reset and both rearm functions also execute. Exact writes/calls,
remaining PM/config/counter buffers, ABI and guarded station read sequences
match the independent model. Explicit external RF/slice/scheduler/hardware,
beacon, GPIO and off-channel boundaries remain; no concurrent lifetime proof.

Newly checked differences: native pending byte 488 changes the ready/retry
selection compared with factory byte15/16 rules; native byte543/deadline568/572
can choose sleep instead of the delay timer. Null station returns before peer
reads, null peer skips byte820. Quick-wake can return synthetic byte19 unchanged;
do not normalize it in tests. Retry/counter boundary effects are retained.
Actual callback argument/status meaning remains a producer-tracing requirement.
No production defect was established by these selected synthetic fixtures.

Producer 6244 / 3ee096 and independent consumer 19325 / caeea6 are terminal 0.
Nine static controls reject wrong SDK/reference/helper/body fields, including
four parent mutations below the image hash guard; eight evidence controls reject
changed effects, pointers, counters, coverage and an unsupported lifetime claim.
Proof factory-null-completion-validation-20261028.json: 17 source pins, one gzip
36734 B / 538755 B expanded. No VM or physical device test was started.

NEXT: actual callback producers/status and station/peer lifetime (+820), BSS
setters/ranges/overflow, computed aliases and whole-image reachability. Deferred
points 1–3, full regression, 24-hour and physical acceptance remain open. Goal
ACTIVE. No running exec from this checkpoint; no implicit push of this new work.
