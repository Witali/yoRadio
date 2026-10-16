# Яркость в паузе фотослайд-шоу

Подтверждено расхождение нашего coordinator. Factory handlers `0x4200d5ac` и
`0x4200d66a` записывают новый уровень и ставят `0x3fcc39f2`; основной цикл
`0x42009128..0x42009140` применяет schedule на ближайшем проходе. В C эта операция
находилась только в `action.finished`, поэтому изменение между fade ожидало
следующей фотографии. По исходному C пауза могла достигать настроенных 60 секунд.

Одинаковый `photo_brightness_qemu.py` использовал настоящий HTTP form
`ledBrightness=50` после первого завершённого fade, при interval60 и mask1:

| Программа | GET brightness | Наблюдаемый duty | Результат |
|---|---:|---:|---|
| Factory | 50 | 4095 | Pass |
| Старый C, app `ad7a9009` / ELF `6d7b586f` | 50 | 819 | Expected negative |
| Исправленный C, app `e3902939` / ELF `d73c9146` | 50 | 4095 | Pass |

Это bounded negative observation после ответа, а не эмпирическое ожидание всех
60 секунд. Candidate HTTP занял .167458 guest s; правильный duty проверен через
.141715 guest s после ответа (эта граница включает GET metadata). Все57,600 pixels
исходной фотографии и прозрачного IP footer совпали с real factory JPEG/glyph
replay при QEMU brightness501/1000. Новая fade не начиналась, RAM/PC/код/время не
записывались, code/media hashes не менялись, panic отсутствует, ВМ закрыты.

Теперь `clock_task` обновляет schedule при `!action.set_duty || action.finished`.
Активные fade-уровни сохраняются, idle реагирует на настройки/смену дня и ночи;
cached setter не делает лишних LEDC writes. В entry comment стоит
`FIXED_RECONSTRUCTION` согласно `src/CORRECTION_MARKERS.md`.

Новый C-case `clock_photo_idle_brightness` воспроизвёл fail старого кода на
`duty == 4095`. После исправления все44 cases /1,182,252 checks проходят:
дневная яркость, включение ночной, смена календаря без settings write, full
brightness, отсутствие новых SPI draws и повторных LEDC writes. Реальные
factory/native instructions сохранены в reference assembly и native-photo-idle.

Candidate source `b9787790`, app1,176,288 bytes/free359,712 архивирован в firmware
ветки. Before/after HTTP reports сохраняют одинаковые observer/helper hashes.
Дополнительный полный photo/fade regression новой сборки прошёл:84 exact frames,
девять canonical scenes и10 проверок отклонения неполного evidence. Результат —
`photo-frames-candidate.json`; baseline84 сохраняет свою прежнюю сборку.
Root run92411 продолжает старый ad7a9009,
новому candidate этот full result не приписывается. Физическая панель и browser
acceptance остаются отдельными проверками.
