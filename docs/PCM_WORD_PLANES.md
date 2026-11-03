# PCM в памяти с 32-битным доступом

[Общий helper](../idf/components/native_stream/include/pcm_word_plane.h)
хранит исходные 16-битные PCM bit patterns парами в `uint32_t`: чётный sample
занимает младшие 16 бит, нечётный — старшие. Загрузка и запись памяти выполняются
через выровненные `volatile uint32_t`. Упаковка сохраняет все биты, включая
`0x8000` и `0xffff`; арифметика звука здесь не выполняется.

Это требуется для classic ESP32: публичный allocator с
`MALLOC_CAP_INTERNAL | MALLOC_CAP_32BIT` может вернуть IRAM, к которой допустимы
только выровненные целочисленные 32-битные обращения. Byte/halfword и FP-доступ,
`memcpy` и `memset` через такой указатель недопустимы. Ограничение и возможность
выделения IRAM описаны в [ESP-IDF 6.0.2: 32-bit accessible
memory](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-reference/system/mem_alloc.html#bit-accessible-memory).
Сам capability flag не гарантирует отдельную IRAM: allocator может использовать
DRAM или D/IRAM. D/IRAM имеет два адресных представления одной физической памяти;
его aliases нельзя складывать как независимый запас RAM.

Контракт вызывающего кода:

- Выделить не менее `((samples * 2 + 3) & ~3)` байт с выравниванием 4.
- Очистить каждый выделенный word через `pcm_word_plane_clear` до первой
  частичной записи: store читает word и сохраняет соседний sample.
- Проверять границы, владеть временем жизни и исключать конкурентную запись
  двух samples одного word. `volatile` задаёт обращения, но не синхронизацию.
- Упаковывать входной S16LE и собирать выходные байты только в обычной DRAM.
  Сам helper принимает и возвращает `uint16_t` bit patterns.

В [CYD family1 playback](../idf/esp32-cyd2usb-native/main/opus_family1_playback.h)
это хранение используется для рабочих наборов больше 23040 B.
Каждый уникальный используемый канал получает отдельную plane до 11520 B;
дублирующие speaker mappings используют ту же plane, silence не требует plane.
Малые наборы, включая C1/C2, сначала используют прежний byte-DRAM путь. При
отказе его realloc classic ESP32 пробует тот же word allocator, сохраняя старый
byte buffer до успешного выделения всех кандидатов. Ошибка памяти возвращается
только при отказе обоих путей. Успешный обычный byte путь не меняется. Подключение через
public heap capabilities ограничено classic ESP32; профиль ESP32-C3 не меняется.

Замена storage должна происходить только после успешного выделения всех новых
planes. При отказе освобождаются только кандидаты. Реальный close refusal
сохраняет действующие planes до успешного закрытия decoder handles. Полный
packet и все нужные streams по-прежнему декодируются до публикации PCM;
частота, точность, trim, gain, порядок каналов и decoder packet cadence
не меняются. Полный actual-task и ресурсный gate этого подключения остаётся
открытым до отдельного завершённого SDK/QEMU прогона.

[Интеграционный HOST-корпус](../tests/results/cyd-ogg-family1-word-fallback-host-20261103/README.md)
проходит с обоими видами хранения: по 43 schedules/12 controls и 12983296
точных creator PCM samples. Ещё 23 проверки покрывают отказ первого/среднего/
последнего кандидата, сохранение byte/word storage при отказе роста, нечётный
trim, duplicate/silence maps и удержание planes при close refusal. Полный C8/20ms
поток после отказа byte allocation проходит через восемь word planes по 1920 B;
при отказе small-growth fallback старые pointer/capacity/bytes сохраняются. Это
ASan/UBSan HOST evidence, отдельно от настоящих ESP32 allocations.

Проверки helper воспроизводятся отдельно:

```text
python tests/run-pcm-word-plane-host.py --output .build/pcm-word-plane-host-fresh
python tests/check-pcm-word-plane-xtensa.py --output .build/pcm-word-plane-xtensa-fresh
```

[Checkpoint helper](../tests/results/pcm-word-plane-20261103/README.md)
использует ASan/UBSan на HOST: 127 групп, все 65536 bit patterns, 468228 exact
sample checks, нечётные размеры/смещения, partial writes, reuse, canaries и
неизменность входной DRAM. Это не проверка ограничений физической IRAM.
Отдельный Xtensa checker компилирует тот же helper при O2/O3, проверяет реальные
word instructions и отклоняет реальные byte, halfword и FP-memory controls;
он не линкует и не исполняет объекты. Допустимые 32-битные stack/literal reads
не считаются обращениями к plane. Из этих проверок не следуют доступный heap,
успех выделения или производительность полного приложения.
