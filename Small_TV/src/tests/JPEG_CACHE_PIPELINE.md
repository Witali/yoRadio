# Persistent JPEG → RGB565 cache

`storage/jpeg_cache.c/.h` соединяет физический JPEG source, streaming RGB565 rows,
existing NOR и двухбанковый journal. Это подготовленный модуль реконструкции;
**в основную UI firmware3E03 и target probe0F63 он ещё не включён**. Здесь проверены
host execution и RV32 relocatable link, не новый ESP-IDF cache runtime или HTTP.

## Порядок работы

Owner сериализует изменение source/resources и все cache операции. Guard заранее
проверяет карту/stamp/resources; source readonly, frames и metadata используют
отдельные scoped ports **одного** budget/epoch. Конфигурация и callback contexts
заимствованы до abort. Перед переиспользованием port освобождаются все borrowers.

1. `open` валидирует всю карту пяти slots до readonly metadata reads. Журнал
   восстанавливается из фактических bytes; новые записи ещё не выполняются.
2. `lookup` хеширует текущий persistent JPEG по длине из committed settings или
   завершённой загрузки. Сверяет source identity, затем **весь физический frame**.
   Старый dirty/read cache не может заменить physical verification.
3. На miss: `begin` сначала durably invalidate через journal, затем хеширует source
   и принимает последовательные полные RGB565 rows. Они одновременно записываются
   в NOR и поступают в output SHA; отдельный validation-only decode не нужен.
4. Только после decoder OK: `commit` заканчивает output SHA, повторно хеширует
   source, flush/reopen frame и проверяет его целиком с flash. Ready metadata
   публикуются последними. Decoder failure, даже после emitted rows, не разрешает commit.
5. `read_row` разрешён после verified lookup/commit. Повторный показ не вызывает
   JPEG decoder и не пишет/стирает flash. Abort освобождает SHA и dirty RAM без I/O.

`invalidate` — отдельный обязательный шаг **до source erase/write** при upload.
Новый модуль сам source не пишет и не восстанавливает незавершённую загрузку из
cache metadata. Settings publication и server privacy validation остаются обязанностью
media/upload owner. При failed job нужен abort/reopen, не повтор со stale RAM.

Source length >102400 возвращает `JPEG_CACHE_SOURCE_LIMIT`, actual required/available,
без source reads/decoder/frame writes. Missing/invalid arguments отличаются от
capacity refusal. Cache integrity, source change, SHA, journal и physical I/O
имеют отдельные причины; это не ошибка формата JPEG. Детали JPEG сохраняет decoder.
Причину deadline/quota владелец берёт из общего transport, включая после STATE.

## Найденная ошибка и исправление

До исправления однократное тихое повреждение read callback378 меняло JPEG
quantization/entropy bytes, прочитанные decoder. Обе physical source SHA до/после
совпадали с оригиналом; decoder возвращал OK, неправильные pixels публиковались и
затем успешно выдавались из cold cache. Это воспроизведено, старые source/binary
hashes и raw результаты сохранены. Основная прошивка этим кодом не пользовалась.

`jpeg_cache_read_source` помечен `FIXED_RECONSTRUCTION`: возвращаемые данные сначала
сравниваются со fresh256byte physical readbacks, затем передаются decoder. Source
hash до/после остаётся проверкой изменения persistent файла. Это покрывает
испытанные одиночные transient read errors, не все возможные аппаратные сбои.
Дополнительный read traffic на full fixture —44402bytes; новой heap allocation нет.

## Build identity и память

`tools/jpeg_cache_layout.py` выдаёт guard header, cache maps, prepared assets и
codec identity. `codec_id` включает actual qualified archive SHA, три adaptation
patches и исходники decoder/конвертера/storage, RGB565 LE policy и geometry.
Изменение codec не меняет ownership stamp/immutable assets, но запрещает старые
cache hits. Это не инструмент автоматического переписывания assets на устройстве.
Production deployment ещё должен сохранить все пользовательские photos/settings.

В RV32 cache handle5600bytes, включая journal1032 и frame NOR4352. Layout156 и
devices72bytes; scratch NOR/adapter, decoder pools/context, SHA provider и tasks
считаются отдельно. Модуль не содержит heap allocation или mutable globals.
Все9public roots cache+нужные NOR/journal связаны в ET_REL:9016code/16rodata,
static writable0. Largest cache frame336, read_source/read_row/write_row304;
largest combined individual frame448 в journal.open. Это не суммарный call-chain
stack, whole UI/Wi-Fi heap fit или target execution.

## Доказательства

-12120physical fault/cut cases: каждый2424callback update × partial error,
  silent partial/corrupt read, full/half/before-operation power cut. Реальные
  bytes сохраняются; при cold recovery допускается только целый old/new frame
  или отсутствие разрешения на показ. Все остальные photos/caches/settings/
  protected sectors сравниваются byte-exact.
-946SHA callback failures и2424global stops; cleanup не вызывает flash.
  Dangerous old-ready fallback после повреждённого invalid snapshot отвергается
  physical hash. Наблюдатель отдельно считает physical reads внутри frame SHA,
  поэтому RAM cache не выдаётся за проверку физического кадра.
-59реальных240×240JPEG: baseline/progressive,8/12lossy,gray/RGB/CMYK/YCCK,
  arithmetic8,2–16lossless predictor4. Пять source-slot refusals и шесть negative/
  resource cases. Flat4x4 сохраняет524288backing requirement даже при маленьком
  compressed source; rich4x4 может раньше не поместиться в source slot. Эти
  отказы не маскируются как unsupported format или damaged JPEG.
-268real-JPEG fault recoveries:43physical errors,7SHA и218silent source reads/
  readbacks. Все44actual input callbacks и их свежие readbacks проверены.
  Ещё18time/quota/cancel stops. Final requested allocator heap0, exact independent
  upstream samples +Python RGB565 oracle; после любой ошибки cold recovery
  выдаёт правильный кадр, без публикации промежуточных строк.
-9compiled mutants отвергнуты runtime assertions или independent pixel oracle,
  не ошибкой compiler/loader. В том числе source-read bug воспроизводится при
  удалении readback, а пропуск physical reopen обнаруживается observer coverage.
-10generator rejects, deterministic identity/dependency change; новые flat
  fixtures не изменили bytes старых argc5 outputs8/12bit.6artifact/10map checks pass.

FullCMYK12 source44402bytes, exact RGB565 SHA `be98fc78…e4c8cf46`:

| Job | Decode calls | Program bytes | Erases | Read bytes |
|---|---:|---:|---:|---:|
| Первая подготовка и показ | 1 | 2703104 | 144 | 14471482 |
| Cold verified lookup и показ | 0 | 0 | 0 | 276338 |

Первая запись включает2582784scratch +118784frame/padding +1536metadata.
Исходные model sectors неFF; это counts issued callbacks, не chip endurance или
hardware timing. Host decoder requested peak47507 отдельно от cache/storage/OS.

Proof: [jpeg-cache-pipeline-validation-20261020.json](../../qemu/parity/jpeg-cache-pipeline-validation-20261020.json).

```powershell
pwsh -NoProfile -File Small_TV/src/tests/jpeg_cache/run.ps1 -LibraryBuild QUALIFIED_HOST_LIB -OutputDirectory NEW_UNIT
pwsh -NoProfile -File Small_TV/src/tests/jpeg_cache/build-decoder.ps1 -LibraryBuild QUALIFIED_HOST_LIB -OutputDirectory NEW_DECODER_CACHE
pwsh -NoProfile -File Small_TV/src/tests/jpeg_decoder/build-generator.ps1 -LibraryBuild UPSTREAM_HOST_LIB -OutputDirectory NEW_SAMPLING_GENERATOR
python -B Small_TV/src/tests/jpeg_cache/decoder_contract.py --build NEW_DECODER_CACHE --reference-build UPSTREAM_HOST_LIB --traffic QUALIFIED_TRAFFIC --decoder-oracle QUALIFIED_DECODER_CONTRACT --generator-build NEW_SAMPLING_GENERATOR --output NEW_CONTRACT
python -B Small_TV/src/tests/jpeg_cache/mutation_contract.py --build NEW_DECODER_CACHE --contract NEW_CONTRACT --library-build QUALIFIED_HOST_LIB --output NEW_MUTANTS
```

Следом — native media owner, matching assets/codec build, privacy/HTTP/error mapping,
target execution/shared RAM/stack/time и reset/power-loss workflow. Медленный decode
нельзя просто вставить под текущий общий media mutex: `photo_upload_finish` держит
его во время validation, а UI вызывает media API. Нужен owner/worker protocol,
сохраняющий корректность source и отзывчивость UI/других HTTP clients. Затем
независимые LCD/network/full/24h/hardware gates для точного итогового app/ELF.
