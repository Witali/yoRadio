# Контекст работы над восстановленной Small TV

Актуальные решения и рекомендации для продолжения сравнения заводской прошивки
ESP32-C2 с собираемым C-проектом в `Small_TV/src`. История действий и результатов
сохраняется отдельно в [рабочем журнале](WORK_LOG.md). Обновлять этот контекст после
завершённых исправлений; при продолжении читать оба файла и проверять Git-статус.

## Работа возобновлена пользователем — 2026-10-17

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

Новый единственный run link-timing-integrated-full-20261017 запущен, handle11075,
initialHEADaf7c8c17, QEMU30F/source0d27a7ca98. Pins:75 tests/88 extras,
appDD41/source96A/ELFB4. Все18 pre-QEMU groups passed; текущий QEMU stage прошёл
boot/reset/SNTP, startup/weather_wait/advanced/photo, photo_frames/brightness/
controls/reinit/settings, initial setup, weather/fields/time/text и regional
обеих firmware, NVS migration. Следующий/текущий stage — calendar. Общего
результата пока нет.
Не запускать дубль по timeout наблюдения. До terminal report не менять frozen
inputs и не публиковать новый pass. Контекстные Markdown не входят в pins.

Независимая ветка codex/small-tv-runtime-observer /9adf0fb0 сохранена и отправлена,
worktree .worktree/small-tv-runtime-observer. В ней standalone read-only observer
и19 parser/ROM tests; main/test pins не менялись, merge до terminal full не делать.
Новый40-cycle runtime-workload-20261017-02 завершён:121.076406 guest s,
41 samples всех12tasks,10 uploads,240 recorded HTTP +80 concurrent GET,
max.405659s, inputs unchanged/no panic/ВМclosed. SDK heap minima sum47 028,
lowest task stack480bytes(settings); last free heap86 268. ROMcrosschecks164.
Scoped doc/JSON runtime-memory-* находятся в ветке; они не объявляют H09/H10,
24h leak-free/physical/ISR stack или factory memory equivalence выполненными.
Ошибки прежних попыток harness сохранены отдельно. Root app/source/ELF прежние.
Следующая работа с observer: объединить после сохранения immutable full result,
затем расширять duration/reconnect/concurrent writes/restart/ISR observation.

Вторая независимая ветка codex/small-tv-http-body-deadline /79445774 (основной
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

QEMU находится в `C:\Work\QEMU-ESP32`; изменения ESP32-C2, модульных SPI/I2C и
виртуальной сети объединены и отправлены в `main` до `962cda7a6f`; установленный
RISC-V executable `fde38d53`, Xtensa binary не менялся. Сохранять
совместимость CYD и ESP32-C3 OLED. При изменении эмулятора выполнять их регрессии.
Закрывать созданные для проверки ненужные ВМ. Физические платы в текущих
проверках не прошиваются.

Отдельные незавершённые черновики, например `tools/assist_c_port.py`, не считать
готовыми инструментами. Чужие файлы `.karadio-*.patch`, `tmp/` и другие
посторонние изменения не относятся к этой задаче.
