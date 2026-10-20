# Слияние проверенных worktree, 2026-10-20

В `main` объединены и опубликованы последние проверенные изменения Small TV и завершённые
боковые ветки с результатами тестов. Отдельная integration-worktree основана
на `origin/main` (`42bc7bd4`); остальные платы и их исходники не изменены.

## Включённые ветки

| Ветка | Проверенный head | Содержание |
|---|---|---|
| `codex/small-tv-jpeg-library` | `b3fc801a0` | JPEG corrections, color helpers, двусторонняя карта, исправленный captive portal, host/RV32/QEMU evidence и подготовка будущей libjpeg |
| `codex/small-tv-jpeg-selectors` | `c8e56f932` | Прерванные/возобновлённые B50D прогоны и точные start records |
| `codex/small-tv-jpeg-headers` | `018a4b72d` | Проверки неизменности замороженных входов после независимых display/network gates |
| `codex/small-tv-h10-ap-services` | `9696e4338` | Исторический прерванный H10 и сохранённые сырые результаты |
| `codex/small-tv-reset-display` | `6d8816d90` | Завершённый отдельный reset/subsystem full regression |
| `codex/small-tv-flash-full` | `4d7888165` | Завершённый исторический BC68/shared-flash full regression |

Ветки browser-controls, jpeg-uploads и runtime-supervision уже входят в историю
перечисленных heads. Их изменения не переносились повторно через cherry-pick.
Все local/remote topic refs сохраняются.

Конфликт возник только в `src/WORK_LOG.md`: старый снимок не содержал поздние
записи. Проверка входящего текста не нашла ни одной уникальной непустой строки,
которой не было бы в актуальном журнале; актуальный журнал сохранён полностью.

## Проверка объединённого результата

- Все 277 входов двусторонней карты совпали с просмотренным snapshot.
- 5608 native checks, 10 negative/inventory controls и 6 artifact tests прошли
  в integration-worktree. Сохранённые образы, исходники, generated media,
  partition table, ESP checksums и 34 original routes согласованы.
- Производственная app сохранена без изменения байтов: SHA-256
  `54f441afa6294236f2ac711df56a5558ac5830eb5e6f80779fe046b333559137`,
  source SHA-256
  `9c16c56a5ec25a533fe4e93b0add2fb819c794b68fd7c4f803fdb91c9473b36d`.
  Это та же app, для которой отдельный network-only gate проверил 15 реальных
  HTTP случаев в factory AP/native AP/native STA. Этот gate повторно не
  объявляется запущенным при слиянии.
- B50D full regression принят только для B50D. H10 ещё выполняется в
  `small-tv-jpeg-selectors`; его исходники, SDK/snapshot и processes не изменялись.
- Новая libjpeg остаётся подготовленным компонентом и не включена в firmware.
  CITY-REINIT, AP multi-peer и RESET/DC pull-up вопросы остаются в
  [двустороннем аудите](src/reference/BIDIRECTIONAL_AUDIT.md).

Машинный отчёт и точные сырые результаты текущей проверки:
[`qemu/parity/worktree-integration-20261020.json`](qemu/parity/worktree-integration-20261020.json).

## Рабочие копии и восстановление

Перед удалением семи завершённых Small TV worktree сохранены полные локальные архивы
в `C:/Work/yoRadio/.build/worktree-retention/integration-20261020/`.
Включены hidden/ignored файлы, результаты сборок и локальные исходники;
SHA-256 каждого файла проверяется чтением архива. Общая ссылка `.idf` записана
в manifest и не обходится; сам SDK остаётся в `C:/Work/yoRadio/.idf`.
Архивы не отправляются в Git. Для восстановления можно создать worktree на
сохранённом head и распаковать соответствующий архив в неё.

`main` опубликован на `origin` (`678f6ac37`). После проверки полных архивов,
HEAD/index/status/processes удалены семь завершённых рабочих копий:

- `small-tv-browser-controls-verify`;
- `small-tv-h10-ap-services`;
- `small-tv-jpeg-headers`;
- `small-tv-jpeg-library`;
- `small-tv-jpeg-uploads`;
- `small-tv-reset-display`;
- `small-tv-runtime-supervision`.

Также удалена временная `integrate-verified-worktrees-20261020`: в ней остались
только 33 производных файла тестовой сборки и Python cache; сырые результаты
проверок уже сохранены в Git. Все ветки сохранены, heads семи рабочих копий
входят в опубликованный `main`. Контрольные суммы архивов повторно проверены
после удаления. Общий SDK не удалялся; активные процессы не останавливались.
В реестре остаются основной checkout и семь рабочих копий ниже. Локальные
пользовательские изменения основного checkout совпадают с начальным inventory.
Точный список удалённых heads, архивов и SHA-256 добавлен в машинный отчёт.

Сохраняются:

- `small-tv-jpeg-selectors`: активный H10 и его sole QMP/RSP владельцы;
- `esp32-cyd-c3-review`: продолжающийся перенос Vorbis/FLAC/MPI;
- `esp32c3-stream-format`: незакоммиченные AAC owner/reclamation изменения;
- `esp8266-native-port`: смешанные staged/unstaged изменения, включая заголовки;
- `esp8266-output-baseline` и `esp8266-stage-profile`: локальные изменения;
- `esp8266-opus-asm`: опубликованные эксперименты и локальные firmware/probes;
- основной checkout: пользовательские patches/attachments/tmp остаются на месте.

Старые AAC storage/DAC и recovery refs остаются опубликованными или локальными
архивными ветками; они не считаются новыми исправлениями Small TV.
Навык [git-repo-cleanup](C:/Users/rudol/.codex/skills/git-repo-cleanup/SKILL.md)
требует: “Do not modify active or locked worktrees, or worktrees with unfinished
Git operations, during general cleanup.” Это ограничивает удаление активных
каталогов; оценка незавершённых экспериментов дополнительно основана на их
diff, статусах и продолжающейся работе.
