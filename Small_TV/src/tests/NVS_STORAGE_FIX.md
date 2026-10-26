# Исправление восстановления Storage и временных индексов

26 октября 2026 исправлены ошибки из [full Storage before](NVS_STORAGE.md).
Новая production app `8758BD09`, ELF `DA1ED0CE`, source aggregate `F2699B39`.
Прежние app34CB/ELF73BE и результаты с 134 скрытыми ошибками сохранены в
`.worktree/small-tv-nvs-fixes`; новые изменения находятся отдельно в
`.worktree/small-tv-storage-fixes`.

## Изменение поведения

`PageManager::load` различает завершение поиска и I/O failure, возвращает ошибки
удаления предшествующей записи и прекращает дальнейшие операции. Общий поиск
предшественника вынесен в одну локальную функцию: сохранены пропуск FREEING,
первая подходящая запись, TYPE_MISMATCH как обычный пропуск и fallback для
legacy BLOB при публикации нового индекса.

`Storage::populateBlobIndices` возвращает точную причину сбоя. Два private cleanup
helpers теперь возвращают `esp_err_t`; объявления и определения согласованы во
всех файлах компонента. Ошибки чтения/удаления больше не превращаются в окончание
списка. `Storage::init` устанавливает INVALID в начале и ACTIVE только после
успеха всех этапов, включая повторную инициализацию ранее активного объекта.

Временный список BLOB indices принадлежит локальной области видимости. Его
scope cleanup освобождает узлы при успехе, I/O failure и частичном OOM. Подмена
глобальной переменной ошибки или специальных значений enum не используется.
Функции и сложные места снабжены комментариями `FIXED_FACTORY`.

## Локальный компонент SDK

Исправления оформлены пятью C++ fragments в `storage/nvs/`, отдельно от Python
генератора. `prepare_nvs_component.py` проверяет SHA всех 45 исходников/заголовков
из pinned SDK6.1 и точный набор fragments. В build directory копируются 35 файлов
`src`, включая согласованный private header. CMake направляет все 17 translation
units компонента в эту копию. Общий SDK не меняется. Существующий Page patch
применяется тем же прежним генератором и сохраняет свою отдельную квалификацию.

Перед архивированием проверяются каждый generated file, compile commands и
полное замыкание init/read по source objects: 56 native функций / 7776 байт.
Заводская сторона по-прежнему полностью matched: 71 функция / 8750 байт.
App занимает 1476112 байт, на 144 больше app34CB; свободно 59888 байт app partition.
В девяти нормальных native baseline сценариях последовательности Partition I/O
побайтно совпадают с before; исправление не добавляет flash операций в этих путях.

## Проверки

- Полный before/after replay: 18 baseline images, стабильные reopens, 224 factory
  и 236 native fault/recovery cases. Все 236 native failures возвращают исходный
  0x104, оставляют Storage INVALID и останавливают I/O на ошибочном ordinal.
  Сохранённые реальные program/erase prefixes дают успешное восстановление ключей.
  Before повторно воспроизводит 134 native ошибки, возвращавшие ложный успех.
- Четыре отказа custom allocator: native больше не оставляет временный40B узел
  после второго OOM. Factory/before leak сохранён и исполняется отдельно.
- Шесть случаев с реальными шестью секторами NVS: reserve/no-free-pages/readonly.
  Два сценария type/legacy-BLOB replacement и два retry на том же Storage после
  header failure и page-array OOM. ABI, реальные destructors и владение malloc
  проверяются в CPU fixture; nullable array allocation — явная граница теста.
- Повторены прежние Page record/HashList cases и 652 partial-repair executions.
  Private DWARF layouts прежние; восемь frame/callee/object/ABI mutations отвергаются.
- Ещё восемь overlay controls: изменённый vendor header, добавленный source,
  несовместимый private return type, смешанные TUs, неверная app/ELF pair, старый
  archive и два опасных output paths. Сначала проходит неизменённая private copy;
  тесты не меняют общий SDK или production overlay.
- Native regression: 6300 проверок, отдельно 3727 privacy и 26 nothrow cases;
  correspondence controls и семь artifact tests проходят. Новый artifact test
  связывает overlay/linkage metadata с app, ELF и actual fragments.
- Отдельная network-only QEMU без LCD: setup Wi-Fi, HTTP, сохранение настроек,
  reboot/cold boot/reset, три свежих SNTP observations. Отдельный display run:
  factory/native cold boot, точное совпадение57600пикселей кадра настройки.
  Четыре matching QEMU owner отсутствуют по fail-fast CIM check.

Эти результаты закрывают найденные ошибки init/recovery, а не весь public NVS
API и не произвольные физические power cuts. Старые H10 warnings этой утечке
не приписываются. Whole-image/TIM/lifetime/BSS/aliases, deferred1–3, полный suite,
длительная и аппаратная приёмка остаются открытыми. QEMU source не менялся.

## Воспроизведение

[Proof](../../qemu/parity/nvs-storage-fix-validation-20261026.json): 23 новых gzip /
405247 байт, 74 source pins. `verify_nvs_storage_fix_evidence.py` заново выполняет
`check_nvs_storage_fix.py`, полную before matrix, after matrix, ABI/guard checks,
проверки Page и overlay mutations, затем сверяет каждую сохранённую phase и
независимо проверяет network/SNTP/settings/LCD witnesses. Производственные
source/resource hashes сверяются по полному source-manifest.

Передаются явно before/current ELF/app/NVS archive, factory/ROM, old-root,
component/overlay/overlay-report/compile commands и новая папка diagnostics.
Дополнительный `--evidence` выбирает этот proof. Новые ВМ и компиляция при offline
replay не запускаются. Все три native contracts (I/O, temporary cleanup, key
preservation) должны быть true; physical/whole-image flags остаются false.
