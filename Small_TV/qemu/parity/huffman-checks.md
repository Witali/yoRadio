# Проверка переполненных деревьев Хаффмана

Первый malformed DHT test падал на последующем entropy и не доказывал проверку
самой таблицы. Новый минимальный grayscale JPEG использует только первый DC/EOB
код. Остальные, невозможные ветви не используются: три кода длиной один бит
не помещаются в два доступных префикса, но заводская программа и прежний C
успешно рисовали изображение и возвращали 0 при validation.

`jpeg_inputs_oracle.py` теперь строит без image library:

- Четыре корректных варианта: one-bit, 16-bit DC, 16-bit AC и оба 16-bit.
- 17 некорректных таблиц: DC depth 1 и AC depths 1…16. На каждом раннем уровне
  остаётся один свободный префикс; следующий уровень имеет два, но требует три.
  Неиспользуемые AC symbols допустимы и различны; entropy использует первый EOB.

Весь JPEG, включая размеры, таблицы, entropy и EOI, задаётся явно. SDK flash-read
boundary подаёт эти bytes реальному factory/native RV32 коду. Original dump и
инструкции не меняются. Before на app `a33788db`, ELF `c2c6ae3b` показывает
успешный native draw/validation и factory draw для всех 17 impossible trees.
Все четыре корректных boundary cases уже проходили.

`create_huffman_tbl` отмечен `FIXED_FACTORY`: перед построением codewords
проверяется число свободных префиксов. Каждый уровень удваивает доступные
ветви и вычитает число кодов; превышение возвращает format error. Используется
`uint32_t`: для разреженной таблицы на длине 16 доступно до 65536 префиксов.
Incomplete trees сохраняются. IDCT, цвет и output callbacks не менялись.

После исправления все 17 invalid cases отклоняются до `jd_decomp`, экран не
трогается и validation ничего не рисует. Все четыре boundary cases и прежние
8 valid / 12 invalid cases проходят: всего 41. Дополнительно 107 public JPEG
дают 0 отличающихся пикселей, прежние 35 errors / 7 placements и 3,884 host
checks проходят. Это отдельные scoped runs, не общий QEMU/physical acceptance.

Candidate app `131ce792670349e81cba3d3c16288ad6472502bcf1fe16908d885d406b5e2701`,
source `f411bf0e7af2230294e25f1bf9da5a15eecb85e7d1961f375bdc305f3e5edebc`,
ELF `9184b08b4cd29b855d962209baaa70bff56c98863c6d06c1fd4f55fec7274575`.
App 1,176,272 bytes / free 359,728 сохранён в firmware ветки. Отчёты:
`huffman-before.json`, `huffman-candidate.json`, `huffman-public-candidate.json`,
`huffman-native-candidate.json`. Observer/fixture hashes до/после одинаковы.
Точные compiled instructions — `native-huffman.asm` и manifest; builder включён
compiler в `jd_prepare`. Factory 0x42011100..0x42011244 сохранён отдельно.

Branch publisher/verifier требуют все глубины и boundary cases. Root main full
run 22926 по-прежнему использует свой frozen app 0d8b7585 и не объявляется
проверкой этого candidate. После завершения нужны integration и новый полный
прогон, включая фактическую загрузку фото по HTTP.
