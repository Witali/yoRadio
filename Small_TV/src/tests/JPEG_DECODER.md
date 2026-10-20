# Переносимый JPEG decoder API и точные причины отказа

Checkpoint2026-10-20. `codec/jpeg_decoder.c/.h` и `codec/jpeg_memory.c` — реальный
модуль, вызывающий pinned libjpeg-turbo3.2.0, с RGB565 converter. Это уже не часть
CLI `probe.c`. Public API не раскрывает libjpeg network/LCD коду. Host execution
и relocatable RV32 link выполнены; **target execution и UI integration ещё нет**.
Рабочая app3E03 остаётся TJpgd. Предыдущая transport probe6cb29771… не менялась.

## Владение и поток данных

Конфигурация задаёт allocator, library pool cap, backing callbacks/capacity и
native image dimensions до240×240. Instance/context создаётся один раз; источник,
RGB565 row callback и mandatory checkpoint передаются на один decode. Callbacks
обязаны возвращать точный результат или ошибку; источник читается блоками до1024.
Синтетический EOI не добавляется, metadata skips проходят тот же bounded reader.
Checks выполняются до/после I/O, на строках и при preflight. Вызовы instance
сериализуются, mutable longjmp/state/buffers хранятся в context, не globals.

Строки RGB565 до успеха **provisional**. API не публикует cache metadata: будущий
владелец upload/journal должен делать publish только после OK. Ошибка после
записи части строки, финального EOI или cleanup не может становиться successful
decode. Это контракт для интеграции, не доказанный HTTP/persistent cache workflow.

После успешно созданного JPEG object ошибка обрабатывается через abort/reuse;
ошибка самого создания допускает destroy/recreate. Context освобождается отдельно,
destroy также освобождает permanent pools. Backing close должен освобождать handle
без budgeted flush даже после ошибки/отмены. Особое окно: post-open deadline может
сработать до установки `b_s_open` внутри jmemmgr. После обычного library abort
модуль закрывает такие orphan handles, не разыменовывая уже освобождённый owner.

## Preflight и диагностика

Wrapped request_virt_sarray/barray учитывают **actual padded requests** библиотеки.
При min-window policy (`jpeg_mem_available` возвращает0) backing нужен массивам,
у которых rows>maxaccess. В realize wrapper проверяется вся сумма до первого
open. Нехватка последнему компоненту не должна обнаруживаться после открытия
предыдущих. Sample precision и sizeof(JBLOCK) учтены; жёсткого предположения
«каждый240×240JPEG требует не больше460800» в модуле нет.

| Причина | Возвращаемый status и поля |
|---|---|
| Не хватает заданного временного хранилища | `backing-capacity`, полные required/available, available_known=true |
| Превышен cap library pools | `library-pool-limit`, actual allocation demand/limit |
| Allocator отказал в пределах cap | `allocation-failed`, requested bytes; free heap неизвестен, available_known=false |
| Размер изображения превышает policy | `image-dimensions`, width/height detail и actual/allowed |
| Неподдерживаемый process/precision/arithmetic/sampling/color | `unsupported-jpeg`, detail и значимый numeric parameter |
| Неправильная структура или corrupt warning | `invalid-jpeg` |
| Источник закончился раньше обязательных данных | `truncated-jpeg` |
| Источник, строка output или backing I/O | Отдельные `input-io`/`output-io`/`backing-io`, callback_error |
| Отмена, deadline, I/O quota | `cancelled`/`time-limit`/`io-budget` |

Library error codes сохраняются отдельно. Parameter не заполняется устаревшим
содержимым msg_parm для сообщений без параметра. Declared width65535 ограничен
размером устройства, не помечен damaged JPEG из-за IJG maximum65500. Height0/DNL
не поддерживается, но width0 классифицируется invalid. Unsupported SOF5 и
fractional sampling — отдельные причины. Некоторые negative fixtures изменяют
только header declaration; они не выдаются за valid complete JPEG entropy.

Пример: CMYK12 требует460800, при capacity460799 возврат сразу содержит оба
числа; opened/read/write/output0, прочитано1024input bytes для заголовков.
Реальный legal4x4 CMYK с noninterleaved DC/AC scans требует524288 из-за округления
coefficient arrays до32×32blocks каждого компонента. При capacity460800 отказ
до backing I/O. Positive4x4 oracle выполнялся на host с **262144pool/1048576backing**:
его успех не является fit proof для native64KiB/460800. Для device конфигурации
отказ должен сохранять реальную причину, как просил пользователь.

## Доказательства

-63positive RGB565 cases: baseline/progressive, gray/RGB/CMYK/YCCK, arithmetic,
  все2–16lossless precisions, full240×240CMYK12,411/440/410/4x4 sampling8/12bit.
  Samples получены unmodified upstream, RGB565 — independent Python arithmetic.
-7resource limit cases: backing0/1/460799, pool1, dimensions239, два padded4x4.
-10invalid/truncated/unsupported header cases и12format transitions.
-1197injected callbacks: allocation15,input2,output17,open4,read72,write72,close4,
  cancel337,time337,budget337. Partial stdio transfers действительно выполняются.
  После ошибки exact recovery pixels, все handles закрыты, final requested heap0.
  Created object повторно используется; при failure до успешного создания — recreate.
-6compiled mutants rejected: skipped whole preflight, wrong padded accounting,
  allocation/oversize misdiagnosed as corrupt JPEG, orphan leak, stale job state.
  Compiler/loader errors и crashes не считаются caught mutants.
-Host context5232bytes отдельно от pools. FullCMYK12 pool peak42275 +context =
  47507requested allocator bytes; это не malloc metadata/stdio/whole process RAM.
-Strict C11/RV32IMC ILP32: context4984; decoder2384code+311rodata, memory1870code,
  color586code. Module writable static0. Binding largest individual frame144,
  color96; полная call chain/library/SDK stack не измерена.
-Relocatable decoder+RGB565+full pinned JPEG retains148672code+120581rodata.
  JPEG symbols разрешены; libc/libgcc/SDK/startup остаются внешними. Это не финальный
  firmware link, app delta или доказательство app/heap/stack/time fit.
-6artifact/10correspondence controls; SDK и oldH10/frozen files readonly checks.

First generator compile использовал неверный signedness J12SAMPROW; исправлен
test generator через настоящий J12SAMPLE. Первый strict C11 build обнаружил
лишний private jinclude/setenv и ambiguous indentation; использованы нужные
standard headers, formatting исправлен без подавления warnings. Failed inputs/
logs и промежуточные успешные этапы сохранены отдельно от final closure.

Proof: [jpeg-decoder-validation-20261020.json](../../qemu/parity/jpeg-decoder-validation-20261020.json).

```powershell
pwsh -NoProfile -File Small_TV/src/tests/jpeg_decoder/build.ps1 -LibraryBuild QUALIFIED_HOST_LIB -OutputDirectory NEW_DECODER
pwsh -NoProfile -File Small_TV/src/tests/jpeg_decoder/build-generator.ps1 -LibraryBuild UPSTREAM_HOST_LIB -OutputDirectory NEW_GENERATOR
python -B Small_TV/src/tests/jpeg_decoder/contract.py --build NEW_DECODER --reference-build UPSTREAM_HOST_LIB --generator-build NEW_GENERATOR --output NEW_CONTRACT
python -B Small_TV/src/tests/jpeg_decoder/mutation_contract.py --build NEW_DECODER --contract NEW_CONTRACT --output NEW_MUTANTS
```

Следующий checkpoint: portable NOR/packed backing и standalone C2 target execution
реализованы отдельно — [JPEG_BACKING.md](JPEG_BACKING.md). Исторические RV32
link-only цифры выше относятся к первоначальному checkpoint этого API.
Далее source/upload/journal/physical hashes и RGB565 cache workflow,
matching assets build/deployment с сохранением photos/settings. Затем UI link,
total RAM/task stack/time, HTTP/reset, independent LCD/network/full/24h/hardware.
Error strings/HTTP mapping и privacy validation интегрировать с настоящим WebUI;
структурированная host диагностика пока не является готовым ответом WebUI.
