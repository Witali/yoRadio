# JPEG: безопасное размещение временных данных и пяти кадров

`tools/jpeg_storage_layout.py` рассчитывает erase-aligned области **нашего
санитизированного assets.bin**, не меняя образ, partition table или устройство.
Это подготовка NOR backend, а не его реализация. Заводской dump этим планом
не размечается. App C8FD и её компилируемые source inputs остаются прежними.

Задача — одновременно разместить measured temporary backing460800bytes и
пять готовых RGB565 кадров240×240×2. Один backing без cache заставил бы повторно
декодировать progressive JPEG и перезаписывать flash при каждом проходе slideshow.
План оставляет отдельное место каждому из пяти кадров; будущий backend должен
перестраивать их при upload/invalidation, а показывать без новых scratch writes.

## Проверенные свободные области

Все диапазоны полуоткрытые; sector4096bytes. Внутри assets свободны только
полные сектора после подтверждённого container payload. Сам поискFF не является
основанием считать сектор свободным.

| Начало | Конец | Секторов | Основание |
|---|---|---:|---|
|0x187000|0x200000|121|Промежуток после всей app partition и до assets|
|0x290000|0x2af000|31|Неиспользуемый хвост animation0|
|0x2c9000|0x2e1000|24|Неиспользуемый хвост animation1|
|0x2fb000|0x313000|24|Неиспользуемый хвост animation2|
|0x340000|0x345000|5|Неиспользуемый хвост animation3|
|0x35b000|0x377000|28|Неиспользуемый хвост animation4|
|0x3ca000|0x3e7000|29|После всех полных weather/status slots|
|Всего||262||

Пять container lengths:75543,102902,104999,181090,88148bytes. Последний частичный
erase sector каждого container остаётся защищённым. Полностью защищены все пять
upload slots0x200000…0x27d000, независимо от длины default photos, полные18weather+
4status slots, boot/NVS/вся app partition и настройки/хвост0x3e7000…0x400000.

| Назначение | Logical bytes | Reserved sectors |
|---|---:|---:|
|Measured temporary backing|460800|113|
|Две metadata области|8192|2|
|Пять кадров по115200bytes|576000|145|
|Всего занято||260|
|Остаётся|8192|2|

Backing0x187000…0x1f8000получился непрерывным. Metadata занимает
0x1f8000…0x1fa000. Cache stores состоят из2–3physical extents каждый: нельзя
заменять их одной непрерывной erase_range. Полная точная карта находится в
`plan.json` внутри raw proof; layout ID
`4508149b7701de9fbd945b6f9fe7145b5f2dbe93de9760e56fe2437f51ad9ca6`.

## Отказ при изменении ресурсов

Planner проверяет partition ownership, base/size/hash образа, все32resource
records и их hashes, GIF header/container length и126frame descriptors. Он
отклоняет неизвестные/отсутствующие/дублированные records, payload за пределами
банка, данные в планируемом свободном хвосте и пересечение с другой partition.
JSON создаётся только после успешного расчёта; существующий output не заменяется.

`tests/jpeg_storage_layout_contract.py` подтвердил:

- Разделение всех1024секторов4MiB на protected и candidate; ни одно выделение
  не пересекается с другим, protected или spare sector.
-30unsafe cases отклонены, в том числе согласованный новый global hash при
  данных в хвосте, frame/header overflow и чужая partition в промежутке.
- Увеличение animation0на2сектора пересчитывает план и использует весь запас;
  рост на3сектора уже отвергается. Старые offsets не применяются автоматически.
- Изменение padding внутри upload slot сохраняет его защищённым. Повторный
  output не перезаписывается, при нехватке места output не создаётся. Всего
 4positive/CLI controls. Исходные assets.bin/manifest остались побайтово прежними.

Первая версия positive padding control записывала5bytes с последнего byte
photo0и в памяти задевала payload соседней photo1. Правильный payload-hash guard
остановил тест. `FIXED_TEST` ограничивает mutation одним byte; неудачный log
сохранён, production image никогда не менялся.

```text
python Small_TV/src/tools/jpeg_storage_layout.py --assets-dir firmware/development/small-tv-esp32c2-reconstructed --output .build/jpeg-plan.json
python Small_TV/src/tests/jpeg_storage_layout_contract.py --assets-dir firmware/development/small-tv-esp32c2-reconstructed --output .build/jpeg-plan-contract
```

Proof: `Small_TV/qemu/parity/jpeg-storage-layout-validation-20261020.json`.

## Что остаётся реализовать

460800—максимум текущей measured matrix, не доказанный предел всех JPEG/T.81
subsampling/scan arrangements. Дополнительная matrix должна подтвердить этот cap
либо planner должен отказать для большего backing. Запас8KiB нельзя объявлять
достаточным для произвольного будущего роста resources или всей JPEG library.

Нужны sparse block I/O, настоящий NOR read/modify/erase/program, ограниченный RAM
sector cache и измерение физических erase/write counts. Ещё нужны atomic metadata,
invalidation/source/codec/layout keys, отказ/cleanup, cold recovery и interrupted
upload tests. Две metadata области сами по себе не доказывают atomic publication.

Перед первой записью runtime должен проверять именно неизменяемые resource
ranges против matching build: app-only update не гарантирует matching assets.
Полный assets hash после пользовательских uploads/cache writes для этого
не подходит. Все photo slots и settings должны сохраняться. Integrity tests
должны разрешать только точные принадлежащие cache/scratch extents; исключать
целиком assets partition из проверок нельзя. После backend/codec integration
требуются полный link, total heap/stack, privacy/HTTP/LCD/full/soak и hardware
acceptance. В этом этапе NOR и эмулятор не менялись, прошивка не перешивалась.
