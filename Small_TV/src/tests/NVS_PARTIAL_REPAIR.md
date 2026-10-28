# Восстановление незавершённой записи NVS

26 октября 2026 проверен следующий реальный путь после
[идентификации NVS caller](FACTORY_NVS.md): `mLoadEntryTable` обнаруживает
непустые данные в записи, bitmap которой ещё обозначает EMPTY. Исполняются
настоящие инструкции таблицы, изменения bitmap и native purge.

Восстановлены полные helper bodies из прежних неизменённых объектов:
factory — три функции /1106байт; native — шесть /1108байт. В native отдельно
исполняются get/set compressed table, alterEntryState, purgeEntry и purgeEntryRange.
ROM memset только готовит32нулевых байта; он остаётся явной внешней границей.

## Фактическая запись

На каждой из126позиций подтверждено:

| Действие | Factory | Native |
|---|---:|---:|
| Программирование bitmap | 4байта | 4байта |
| Обнуление данных незавершённой записи | Нет | 32байта |
| Erase сектора | Нет | Нет |
| Новые программы при повторном открытии восстановленной страницы | 0 | 0 |

Сравниваются все4096байт синтетического сектора. За пределами bitmap word и
выбранной32-byte записи байты должны совпасть с исходными. Ранее ERASED записи
не очищаются повторно. Отдельные ACTIVE/FULL/FREEING страницы с EMPTY/ERASED
таблицами также не порождают writes.

После восстановления последнего слота текущий проход имеет next_free=126.
Новый проход по полностью занятой таблице сохраняет INVALID_ENTRY=0xffffffff.
Оба значения означают отсутствие места; проверки сохраняют фактическое различие
и не подменяют один sentinel другим.

## Ошибки и повторное восстановление

252 основных исполнения и252повторных открытия,12чистых baseline cases,
68I/O failures и68новых восстановлений: всего652CPU executions. Ошибки вводятся
на каждом наблюдённом API call для слотов0/15/16/125. Проверяются отказ до
передачи и передача половины read/program с возвратом0x104. При повторе сохраняются
реальные изменившиеся байты, а volatile Page создаётся заново.

Проверены счётчики used/erased, first_used/next_free, INVALID state после ошибки,
возвращаемый код, сохранение ABI и неизменность посторонних полей Page. Введённая
ошибка не превращается в успех. Успешный повтор восстанавливает логическую
ёмкость, включая границы bitmap words и последний слот.

В десяти native cases после ошибки программирования bitmap или purge остаются
16..32 ненулевых байта данных выбранной записи. Bitmap уже ERASED, поэтому
повторный scan их пропускает. Это наблюдение о текущем SDK, а не гарантия secure
erase. Путь возвращает ошибку исходной операции; firmware здесь не менялась.
Вопрос дальнейшего усиления удаления данных хранится отдельно от совместимости
и допустимого количества flash writes. Автоматически отключать purge не нужно.

Backend — частный fixture интерфейса Partition, не новое ядро SPI flash.
Он проверяет границы, фактические4/32-byte запросы и программирование только1→0,
сохраняет частично изменённые байты и записывает каждую операцию. Порядок SPI,
WIP, произвольные bit-level power cuts, шифрование, полный boot/NVS manager и
физическая плата этим не симулируются. Все данные искусственные.

11 реальных изменённых входов отвергаются: helper frame/instruction/call targets,
запрос0→1, выход из сектора и недопустимые запросы fixture. Ещё семь report controls
отвергают выдуманное отсутствие32-byte purge, потерю повторного открытия,
откат уже записанных байтов, успешный ответ на purge failure, гарантированную
повторную очистку и ложные whole-table/full-VM заявления.

## Воспроизведение и следующий шаг

[Proof](../../qemu/parity/nvs-partial-repair-validation-20261026.json): три новых
gzip /44243байта /25source pins. Factory object и исходная полная NVS qualification
переиспользуются по хешированным ссылкам. Consumer заново исполняет весь этот
набор и проверяет физические snapshots по сохранённым synthetic operations.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
$taskBuild='C:/Work/yoRadio/.worktree/small-tv-factory-audit/.build/small-tv-nothrow-20261026'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_nvs_partial_repair_evidence.py `
  --proof Small_TV/qemu/parity/nvs-partial-repair-validation-20261026.json `
  --factory C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --native "$taskBuild/small_tv_reconstructed.elf" `
  --app firmware/development/small-tv-esp32c2-reconstructed/app.bin `
  --nvs "$taskBuild/esp-idf/nvs_flash/libnvs_flash.a"
```

Открыты остальные ветки entry-table repair: ILLEGAL/WRITTEN records, плохие
заголовки/CRC, variable-length spans, duplicates, HashList/allocations и реальные
eraseEntryAndSpan/purge ranges с их ошибками. Затем TIM/null/station/BSS/aliases.
Этот этап не закрывает весь NVS, full VM/hardware, whole-image или финальные gates.
