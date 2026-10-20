# Независимые таблицы Хаффмана в JPEG

Заводской parser `0x42011eae..0x42011efa` принимает только пары00/11,
проверяя наличие таблиц по классу компонента. В `mcu_load` по адресу
`0x42011a9a` выполняется `snez s3,s0`: Y получает таблицу0, Cb/Cr —1,
независимо от SOS. Восстановленный C сохранил это поведение.

[ITU-T T.81, B.2.3 и Table B.3](https://www.w3.org/Graphics/JPEG/itu-t81.pdf)
задают отдельные DC/AC destinations для каждого компонента; для baseline
каждый может быть0 или1. Отсюда допустимы00/01/10/11, совместное использование
и перестановка таблиц. Выбранная таблица должна существовать до начала scan.

`jpeg_selector_fixtures.py` строит136корректных8×8изображений: все64комбинации
RGB и4grayscale, с полным и минимальным набором таблиц. Table0 кодирует нули
кодом0, table1 —кодом10: игнорирование selector меняет разбор entropy.
Все изображения должны быть сплошным RGB128/128/128, RGB565=0x8410.
Независимый Pillow12.3.0 подтвердил каждый пиксель всех136fixtures.
Ещё32повреждённых случая проверяют отсутствующие выбранные таблицы и выход
DC/AC destination за диапазон baseline.

`jpeg_selector_oracle.py` исполняет неизменённые RV32 instructions обеих прошивок.
Синтетические bytes поступают только через SDK flash-read callbacks; проверяются
все240×240pixels с защитой вне области8×8. Validation не должна рисовать вообще.
Factory результат сохраняется как наблюдение; известная ошибка не становится
критерием приёмки исправленной прошивки. Отдельный consumer contract проверяет
все168cases, fixture hashes, executable identity и8negative evidence controls.
Parent JPEG inputs, publisher и artifact validator требуют этот gate.

Первоначальная F1/ELF91E2 прошла лишь34из168сценариев:4из136valid и30из32invalid.
Два missing-gray-table1 случая доходят до entropy и очистки области изображения;
они должны завершаться уже на подготовке. Before reports сохраняются отдельно,
не переименовываются в успешные. Последующее сравнение использует те же fixtures
и тот же harness, а различия source hashes записываются явно.

Исправление `FIXED_FACTORY` сохраняет packed SOS selectors в хвосте `JDEC`,
проверяет наличие выбранных DC/AC и использует их при загрузке MCU. Прежние
поля структуры, IDCT, преобразование цвета и вывод не переписываются.
На appB50D15A1/ELF85FCCF00 проходят все168случаев и8consumer rejection controls.
Actual DWARF подтвердил прежние member offsets и размер124→128bytes,
selector field начинается в бывшем padding по offset123. Native `mcu_load`
встроен компилятором в `jd_decomp`, поэтому сравнивается его реальный листинг,
а не пустой вывод objdump по отсутствующему standalone symbol.
Прежние107JPEG/35error/7placement и41additional inputs/128DHT/133headers,
5531host checks и6artifact checks прошли. Это адресная приёмка декодера.

В `photo_qemu.py` отдельно проверяется реальный HTTP upload240×240: grayscale
table1, RGB со shared0 и смешанными01/10/11, а также два отсутствующих table1.
Для valid требуются200, metadata и byte-exact download; для invalid400/absent.
Это интеграция HTTP/storage/decoder, не критерий готовности дисплея или сети.
НаB50D/85FC/D64 все26HTTP/storage checks прошли, включая cold/interrupted
persistence. На исходнойF1 те же3valid selector uploads получили400; далее
cold-stage `/start_upload` завершился timeout с предупреждением QEMU
WSAEventSelect. Этот дополнительный failure не скрыт и не объявляется
следствием JPEG: причина требует отдельного расследования сети/host socket.
Все tested sources/helpers и fixture hashes совпали между HTTP runs.
Пять отрицательных мутаций HTTP evidence consumer отклоняет.

Raw before/after,136Pillow+3upload checks,168small+5upload fixture bytes,
native/host/artifact reports и RV32/DWARF proof сохранены в
`../../qemu/parity/jpeg-selector-correction-20261018.json` и42gzip artifacts.

```powershell
python -X utf8 -B Small_TV/src/tests/jpeg_selector_oracle.py `
  --output C:/Work/yoRadio/.build/jpeg-selectors-new.json
```

`--dependency-root` указывает дерево с factory-analysis.elf и oracle-deps.
Native ELF/BIN должны соответствовать archived app. Сценарий входит в
`jpeg_inputs_oracle.py`. Запуск standalone не заменяет полный набор,24h/H10,
проверку LCD/PWM или физическую плату. Входы текущих F1 full/H10 не меняются.
