# JPEG DHT: зарезервированные коды и AC-символы

В `create_huffman_tbl` исправлены ещё две ошибки заводского декодера, которые
сохранялись в нашей прошивке BC68. По [ITU-T T.81](https://www.w3.org/Graphics/JPEG/itu-t81.pdf#page=54),
Annex C, код из одних единиц должен оставаться свободным на каждой длине.
В baseline AC допустимы категории размера 1…10; нулевой размер имеет смысл
только для EOB (`00`) и ZRL (`f0`), см. F.1.2.2.1 и Table F.2.

Заводские инструкции `0x42011194..0x420111c8` строят codewords без резервирования
all-one prefix. В `0x42011208` ненулевой класс AC сразу переходит к сохранению
символа; ограничение размера применяется только к DC. Прежний C уже отклонял
переполненное дерево, но разрешал полностью заполненное и любые AC-символы.
В старом `jd_prepare` ветвь `0x4201320c` проверяла строгое превышение доступных
префиксов. Новая `0x4201320a` проверяет также равенство; `0x420132aa..0x420132c6`
проверяет AC-категорию и два исключения. Точные три disassembly сохранены gzip.

`jpeg_dht_oracle.py` исполняет исходные factory/native RV32 функции. Подменяются
только SDK flash/read, allocation/mutex и LCD transport; код JPEG остаётся
настоящим. Синтетический серый JPEG8×8 использует только DC0/EOB, поэтому
неиспользуемая ошибочная ветвь должна отсеиваться именно при подготовке DHT.
Все 57,600 пикселей панели сверяются, включая guard вне8×8; discard validation
не имеет права рисовать. Корректные изображения дают независимый RGB565 `8410`.

128 случаев включают четыре корректных контроля, 94 запрещённых AC-символа,
три уже запрещённых DC-символа и 27 полностью заполненных деревьев: DC на
длинах1…11, AC на1…16. В корректной таблице могут находиться все12DC/162AC
символа; отдельно проверены sparse16-bit и последний разрешённый код `fffe`.
Эти контроли используют DC0/EOB в entropy и не объявляют все162AC execution paths
исчерпывающе проверенными. Старый и новый прогоны имеют одинаковые fixture hashes
и точные байты самого DHT harness/его общих helpers.

BC68 и factory принимали121новый malformed вариант; три DC случая уже
отклонялись. Candidate0592 отклоняет все124 до `jd_decomp`; четыре valid case
совпадают с factory. Прежние41input cases,107public JPEG/35errors/7placements,
5,531host C checks и6artifact checks прошли. Семь mutation controls требуют
отказа publisher при пропуске case, другом ELF, изменённых inputs, принятии
malformed, запуске entropy, рисовании validation или изменении guard pixels.
Расширение включено в обязательный `machine_jpeg_inputs` и оба publication tools.

Тот же `photo_qemu.py` на BC68 получил200/exists для трёх362-byte JPEG:
reserved AC size, reserved zero-size AC и all-one word. На0592 каждый получает
400/absent. Все22HTTP/storage checks кандидата прошли: valid gray/RGB, retries,
download, finish→cold boot, interrupted replacement→cold boot и новая загрузка.
Изначальный failed report сохранён как failed; он отличается только новым
`reserved_dht_rejected` check. Это не эмуляция отключения питания внутри записи.

Candidate app `0592b51036117b81b98d7b7f615bbc7cce7e52e88635627c9f2c48afbed422ec`,
ELF `aea10675caa2cb7c6f817eb4d517998e4b1023a2fa845e0d66badbfbc2dba6c6`,
source `d338a294e3f95f911d1526b8cdf5986691f4e77fcc14d4765c0a3b938848a404`.
Из59production inputs изменён только `third_party/tjpgd/tjpgd.c`. App1,169,936bytes,
прирост32bytes; в app partition свободно366,064bytes. DEBUG выключен; успешная
сборка сохранена в development archive. Иной bootloader hash после новой сборки
не объявляется доказательством изменения его алгоритма.

Точные результаты и raw hashes: [jpeg-dht-validation-20261018.json](jpeg-dht-validation-20261018.json).
Это scoped проверка исправления. Продолжающиеся full533/H10 используют BC68/20B
и не подтверждают candidate0592. Полный прогон, длительная работа и физическая
приёмка этой сборки ещё не выполнены; их результаты нельзя выводить из JPEG gate.
