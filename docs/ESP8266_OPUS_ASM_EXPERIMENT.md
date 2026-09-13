# ESP8266: отдельная Opus ASM-библиотека

## Что реализовано

Ветка `codex/esp8266-opus-asm`. По уточнённому запросу за основу взят **реальный
ассемблер GCC**, а не переписанный заново алгоритм. Snapshot: LX106/call0,
GCC 8.4.0 / O3 / fixed-point, исходная C-база `c470f55`.

- 110 translation units, 229 сгенерированных функций. ASM хранится в
  `esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/gcc/`.
- Каждая единица повторно собрана ассемблером и сравнена с независимой
  C -> object сборкой: инструкции, relocations **и содержимое секций** точные.
- `libopus-gcc-asm.a` — отдельная исходная библиотека;
  `libopus-optimized-asm.a` — та же библиотека с проверяемым изменением ASM.
  Они находятся в `firmware/development/esp8266-opus-asm-library/`.
- Функции снабжены комментариями: модуль/назначение, C-контекст, ABI, аргументы,
  оговорки для IPA-клонов GCC и ограничения доступа к IRAM. `-fverbose-asm`
  дополнительно сохраняет соответствие инструкций строкам C и переменным.
- Служебные `native_opus.c`, Ogg demux и allocator остаются на C. **Весь код
  собственно библиотеки upstream собирается из ASM** при выборе ASM backend.
  Это не утверждение, что 229 функций написаны вручную или уже оптимизированы.

Архив `.a` — промежуточный link artifact, не прошивка. Его размер не равен
расходу flash: linker удаляет неиспользуемые функции/данные. Для встраивания
нужны существующие YoRadio allocator hooks (`opus_memory.c`), libgcc/libc и
совместимый fixed-point ABI. Лицензия Xiph сохранена рядом с архивами.

## Выбор при сборке

`-OpusBackend c` (по умолчанию), `gcc-asm` или `optimized-asm`.
CMake: `YORADIO_OPUS_BACKEND` с теми же значениями. Production default не менялся.
ASM-варианты требуют `-Diagnostic -EnableOpus` и точного набора flags снимка:

```powershell
tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 `
  -Variant esp8266-opus-optimized-asm-v1 `
  -Diagnostic -EnableOpus -OpusBackend optimized-asm `
  -OpusWordAsm -OpusIcdfFlashWord -OpusFirFlashWord `
  -NoSpiffsCache -Pdm32Iram -Pdm32Batch
```

Для raw CPU A/B добавить `-OpusBenchmark -OpusBenchmarkFixtures <directory>`.
Собранные здесь два образа — **raw benchmark**, не обычное радио и не тест
физического PDM: аудиовывод в измеряемом интервале выключен, WebUI/OTA сохранены.
Ничего на плату в этой задаче не прошивалось.

В worktree Windows можно указать `-RuntimeRoot C:/Work/yoRadio/.build` и
абсолютный `-SdkPath`, чтобы использовать установленный toolchain без слишком
длинного пути к его C++ include-файлам. Нужен свежий Variant при смене runtime.
Для ASM явно передаётся `-mlongcalls`: SDK по умолчанию задаёт его только C/C++,
без этого flash -> ROM/IRAM вызовы не линкуются.

Снимок содержит hashes 203 локальных C/header dependencies. Сборка отклоняет
изменённые исходники, подменённый ASM, другой набор файлов и несовместимые
low-RAM/leases/rotation/div/stage flags. Нельзя просто включить low-RAM поверх
старого ASM: сначала нужно экспортировать и квалифицировать отдельный снимок.
Это сознательная защита ABI, а не новый лимит битрейта.

## Первая оптимизация: ec_dec_update

Исходный GCC-код делает часть вычислений `val` заранее для случая нулевого
дополнения и повторяет их после чтения реального байта. Кроме того, в цикле
повторно загружается указатель пакета, а для временных значений сохраняются
четыре callee-saved регистра.

В `tools/esp8266_opus_asm/ec_dec_update.inc.s`:

1. Обе ветви сходятся до вычисления нового `val`; лишнее вычисление удалено.
2. Указатель пакета читается перед циклом.
3. Состояние остаётся в регистрах и записывается на выходе.
4. Используются только a2..a11: нет stack frame и save/restore a12..a15.

Сохранены unsigned32 wrap, маска31, точное округление/извлечение битов и
нулевое дополнение после конца пакета без увеличения `offs`. Пакет не должен
перекрываться с `ec_dec`: это выполняется в native decoder. Нет malloc,
новых таблиц, перемещения кода в IRAM или маскирования прерываний.

| Измерение | GCC ASM | Оптимизированный ASM |
| --- | ---: | ---: |
| Код ec_dec_update | 171 байт | 107 байт |
| Локальный frame функции | 16 байт | 0 байт |
| Размер проверочного app.bin | 902 992 байта | 902 912 байт |
| Дополнительная static RAM относительно исходного | — | 0 байт |

Это не экономия 16 байт heap: выделенные стеки задач **не уменьшались**.
Пики codec scratch и persistent state в host-регрессиях не изменились.
Глобальное уменьшение RAM или CPU пока не заявляется.

## Проверки и ограничения результата

- 100 000 состояний: 49 360 без refill, 50 640 с refill, 1 549 с zero padding.
  Сравниваются все поля состояния и неизменность входных данных, ASan/UBSan.
- Модель построена **из текста фактических ASM-инструкций**, а не отдельного
  придуманного C-алгоритма; неизвестные инструкции останавливают генератор.
- Полный decoder с этой моделью: свои 12/24/64/128/192-kbit/s фрагменты,
  SILK/Hybrid/CELT, 57 600 PCM samples — побитное совпадение, max error=0,
  SNR относительно исходного PCM=Infinity. Reset/OOM/guards также проверяются.
- Смена SILK/Hybrid/CELT с PLC проходит отдельным последовательным тестом.
- Обе реальные ESP8266 прошивки полностью собраны/слинкованы; RAM/IRAM секции
  одинаковы. Полные отчёты сохранены рядом с отдельными библиотеками.
- Модель инструкций **не исполняет машинный код на LX106 и не измеряет CPU**.
  Сокращение команд ещё не доказывает ускорения: ранее rotation ASM ухудшал
  результаты из-за факторов, не видимых по числу инструкций.

## Воспроизведение

```powershell
node tools/esp8266_opus_asm/export.cjs --compile-commands <C-build>/compile_commands.json
node tools/esp8266_opus_asm/optimize.cjs --compiler <toolchain>/xtensa-lx106-elf-gcc.exe
node tools/esp8266_opus_asm/verify.cjs optimized-asm
node tools/esp8266_opus_asm/check.cjs <own-opuspkt-fixtures>
node --test tests/esp8266-opus-asm-backend.test.js
node tools/esp8266_opus_asm/compare_builds.cjs <toolchain-bin-directory>
```

Baseline immutable: исправления вносятся в reviewable recipe/overlay, не в
исходный GCC snapshot. После regeneration обновляются hashes и оба архива.
Экспорт сейчас намеренно привязан к проверенному feature set выше; другой
профиль требует обновления compatibility guard и независимого A/B.

## Следующие шаги

- [x] Экспорт полной библиотеки и round-trip машинного кода/данных.
- [x] Комментарии функций, provenance, отдельные архивы и build-time выбор.
- [x] Первая оптимизация непосредственно ASM, точность и локальный стек.
- [x] Полная линковка двух raw benchmark образов, сравнение static RAM/flash.
- [ ] На плате: interleaved A/B не менее десяти попыток каждого варианта,
  исходные пакеты из flash/RAM, task CPU, max call, free/min/largest heap/stack.
- [ ] Подтвердить PCM реальным LX106, затем радио/WebUI и >=20 с без underrun.
- [ ] При отсутствии воспроизводимого выигрыша не включать overlay в default.
- [ ] Следующие ASM-функции выбирать по physical stage profile (bands, IMDCT,
  SILK synthesis), а не переписывать весь листинг без измерений.
- [ ] Отдельно исследовать сокращение lifetime/переиспользование scratch:
  механическая замена C на ASM сама по себе буферы не уменьшает.
