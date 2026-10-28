# Historical improvement-plan checkpoint, 25 October 2026

Retained during chronological smart-tv integration. These are historical
observations from the original improvement-plan worktree, not current
process status or instructions for the integration checkout. Source commits:
983313540c4d648803afddb7973366a854cfe76c and
c23365db395327a2e0e50422a71b6500f242e6db. Current journals retain the later
memory-retention content and subsequent updates. Both original commits remain
ancestors of smart-tv.

## WORKING_NOTES additions

## Продолжение в отдельной рабочей копии — 2026-10-25

Текущая разработка: `.worktree/small-tv-memory-retention`, ветка
`codex/small-tv-memory-retention`, commits `135e61860` (exact TLSF metadata replay)
и `82d901e2d` (TCP/IP mailbox gate), затем `23b641680` (typed TCP inventory и
live-allocation attribution). Там обновлены полный IMPROVEMENT_PLAN,
WORK_LOG и tests/HEAP_TOPOLOGY.md / tests/TCP_HEAP_ATTRIBUTION.md. 4+40-cycle
heap qualification,46snapshots/92inventories и38negative controls pass;
TCP prerequisite15host tests/real4cycles/5quiet samples/12controls pass.
TCP PCB/segment/pbuf attribution готов:33real-ROM hosttests+25baseline,
4+40actualcycles/46observed snapshots/76negativecontrols. Actualguest samples
далиLISTEN/FIN_WAIT_2 PCB80..504B; queuedbuffer targetprobe и старые7warnings
не закрыты. Там запущеныsoak-main/soak-v8 по28800guest seconds/15s/outageEvery60,
25Oct13:40/13:42UTC,early0 и4positiveowneridentities каждый. Теперь runtime inputs
обеих рабочих копий pinned; дальнейшие producer изменения — новая task worktree.

Эту рабочую копию пока сохранять как pinned input основного
`.build/runtime-h10-main-20261025`. Не cherry-pick/merge сюда новые runtime
helpers, не менять app/ELF/SDK/ROM/profile/assets/frozen47files и не присоединять
второй observer. При последней CIM-проверке362cycles,4originalowners и точные
creationUTC совпали; oneROMboot/noUARTerrors, H10 ещё running. Дополнительные
короткие ВМ завершены. После настоящего terminal H10 выполнять полный audit,
а не принимать старый JSON status за liveness или дополнять24h прежними7часами.


## WORK_LOG additions


## 2026-10-25 — разработка перенесена без изменения H10 inputs

В отдельной codex/small-tv-memory-retention завершены commits135e61860 и82d901e2d.
Первый квалифицирует exact ROM/linked TLSF metadata walk:11+8новыхhost tests,
16+25baseline,4+40actualcycles/22outages/352HTTP,46snapshots/92inventories и
38semanticnegativecontrols. Второй добавляет prerequisite безопасного TCP walk:
15hosttests,actual4cycles/2outages/32HTTP,5blocked-empty-mailbox samples и
12archivecontrols. Подробные proof/docs/log/полныйплан находятся в новой копии.
Прошивка и QEMU source не менялись; physical device не тронут.

Retained-loss12..220B прежнего прерванногоH10 не объяснён. ROMfixture доказывает
возможность12Bpadding при тех жеlive requests, но не его участие в старыхflags.
Следом nativeTCP PCB/pbuf attribution с gate, длинный контроль обычногоcadence,
idempotentalready-stoppedVMcleanup и остальные пункты полного плана.

ОсновнойmainH10 остаётся здесь:4ownerPID/creationUTC повторно подтверждены,
203cycles/lastsample3535.629206guest s/start25.097679,oneROMboot/noerrors,
guardrunning. Эти runtime inputs не изменялись; новыхhelpers сюда не сливать до
terminal result. Здесь обновлены только notes/log pointers, goalactive.

## 2026-10-25 — typed TCP checkpoint и protected matched controls

В новой копии codex/small-tv-memory-retention сохранён коммит23b641680:
обход TCP lists/segments/pbuf metadata и точные allocation capacities. Прошли
33real-ROM host tests,25baseline,4+40actual cycles/22outages/352HTTP,
46observed snapshots и76semantic negative controls. Старые heap/gate checkpoints
повторно прошли38+12controls. В target snapshots были LISTEN/FIN_WAIT_2;
queued pbuf/segments пока проверены только host fixtures. Старые7memoryflags
остаются открытыми, thresholds прежние.

В ней запущены matched8h controls main/V8:soak-main25Oct13:40:41UTC и
soak-v8=13:42:23UTC,28800guest seconds/interval15/outageEvery60/schema7.
Start0 и4positive original owners/creationUTC сохранены для каждого; runtime inputs
новой копии теперь тоже pinned. Последняя CIM13:47:42UTC подтвердила все12owners
трёх runs: здешний mainH10 —362cycles/guest6272.078252, metadata-main13,
metadata-v8=9, oneROMboot/noerrors каждый. Это pending prefixes, не8h/24hpass.
Подробные identities, команды и следующие gates — в новых WORKING_NOTES/WORK_LOG.

Код/SDK/app/ELF/ROM/frozen47files и живые VM в этой копии не менялись; здесь
обновляются только notes/log pointers. Новые producer changes — другая task worktree;
read-only offline analysis допустим без изменения pinned inputs. Полная цель active.
