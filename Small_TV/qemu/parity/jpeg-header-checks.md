# Дополнительные JPEG и ошибки заголовков

Ветка `codex/small-tv-jpeg-inputs` закрепляет восемь synthetic JPEG: RGB
4:4:4/4:2:2/4:2:0, два restart-варианта, grayscale 240×240, RGB 123×117 и
grayscale 23×29. Actual RV32 decoder обеих прошивок сравнивается по всем
57 600 пикселям, включая guards. Подставляются только данные SDK flash read;
инструкции заводской программы и dump на диске не меняются.

Двенадцать malformed cases выявили три ошибки, которые принимают оба decoder:

| Вход | Factory/C до исправления | Новый C |
|---|---|---|
| DQT ID = 4 | `0x420110c4` выполняет `& 3`: таблица превращается в 0, draw/validation возвращают 0 | Проверять reserved ID/precision bits |
| SOF0 precision = 12 | `0x42011c48` игнорирует точность, 8-битный decoder возвращает 0 | Требовать precision 8 |
| Лишний байт SOF0 | Длина component payload не проверяется, draw/validation успешны | Требовать минимум и `6 + 3 * ncomp` bytes |

Ошибки отмечены `FIXED_FACTORY` в `create_qt_tbl` и `jd_prepare`. IDCT, цвет и
output callbacks не менялись. До изменения все три случая действительно рисовали
кадр в factory/native. Теперь C отклоняет их при подготовке без изменения экрана.
При ошибке entropy/restart очищается известный прямоугольник; discard validation
не рисует. Прежний `photo_headers_safe` уже отклонял precision != 8 при upload;
этот случай не является обходом той HTTP-проверки.

Before — app `0d8b7585`, ELF `97adeb91`, три ожидаемых сбоя с literal factory
observations: `jpeg-headers-before.json`. Candidate — app `a33788db`, source
`731815d5`, ELF `c2c6ae3b`: все 8 valid / 12 invalid pass в
`jpeg-headers-candidate.json`. Observer/fixture bytes совпадают до/после.
Все 107 public JPEG дают 0 pixel differences; 35 error/validation и 7 placement
cases проходят (`jpeg-headers-public-candidate.json`). Host C — 3,884 checks
(`jpeg-headers-native-candidate.json`). Полные SHA-256 сохранены в отчётах.

Сборка 1,176,256 bytes / free 359,744 сохранена в firmware ветки. Actual native
instructions — `native-jpeg-headers.asm` и manifest; compiler включил quantizer
builder в `jd_prepare`. Bounded factory snippets добавлены в reference/assembly.
Новый `machine_jpeg_inputs` обязателен в branch run-all/publisher/verifier.
Candidate QEMU/full suite ещё не запускался; работающий main run 22926 продолжает
проверять неизменённый app `0d8b7585`. Физических действий нет.

Следующий отдельный дефект: synthetic 363-byte grayscale JPEG с тремя 1-bit
DC Huffman codes принимается обоими decoder и native validation. Такое prefix
tree невозможно; entropy использует лишь первый код. Первый malformed mutation
падал позже на entropy и не доказывал проверку самой таблицы. Нужны отдельные
case и исправление; этот scoped результат не закрывает arbitrary JPEG fuzz.
Последующее исправление и точные boundary/depth tests описаны в
[huffman-checks.md](huffman-checks.md); header-only results выше остаются историческими.
