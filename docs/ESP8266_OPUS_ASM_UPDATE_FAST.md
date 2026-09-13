# Opus ASM: no-normalize fast path ec_dec_update

2026-09-13. Отдельный diagnostic backend bands-update-fast-asm.
Цель ≤70% CPU ещё не достигнута. Кандидат проверен на плате и отклонён
по критерию high-bitrate-first; default не меняется. C fallback и защищённый
GCC snapshot не изменяются.

## Изменение

Два decoder call site в quant_partition/quant_all_bands заменены GAS-макросом.
Он вычисляет будущий rng в регистрах. Если rng > 2^23, записывает rng/val
без вызова и без стека. При rng <= 2^23 вызывает оригинальный ec_dec_update:
до вызова состояние и a2..a5 не изменены. Равенство порогу тоже нормализуется.
Не заменяются laplace, другие встроенные entropy-пути и общая функция.

Это не прежняя перепись всего ec_dec_update: нормализация остаётся исходной.
Цена холодного пути — повторное вычисление guard перед обычной функцией.
Комментарии описывают ABI, a6..a9 scratch, SAR, uint32 и отсутствие новых
литералов/буферов/stack slots. Сохранения caller не удаляются.

## Проверки перед платой

- Интерпретация реальных инструкций макроса: 100000 состояний и пороги.
  Проверяются uint32 через независимую BigInt-арифметику, регистры,
  неизменность состояния/аргументов при переходе к исходному вызову.
- 100000 сравнений host C-зеркала с исходным ec_dec_update:
  49360 без refill, 50640 с refill, 1549 с zero-padding; состояние и вход
  совпадают, ASAN/UBSAN включены.
- Полный PCM/PLC/reset/OOM пяти fixtures проверяет check_bands.cjs update-fast.
  Все случаи прошли, результаты в host-correctness.json.
- LX106 object сгенерирован; семантика остальных функций и данные совпадают.
  Изменение padding соседних функций GAS допускается только вне fall-through;
  linked addresses/размеры и RAM проверены после полной сборки, см. ниже.

## Динамические пути, не скорость

Host C, один проход по каждому 12-пакетному fixture, без self-test в счётчиках.
Полный PCM соответствует контролю. Это частоты двух bands-мест, не всех
вызовов ec_dec_update и не профиль тактов LX106.

| Поток | Вызовов | Без нормализации |
|---|---:|---:|
| mono12 | 0 | 0 |
| mono24 | 51 | 29 |
| stereo64 | 320 | 187 |
| stereo128 | 821 | 436 |
| stereo192 | 1318 | 580 |

На 192 кбит/с guard успешен в 44,01% случаев; в остальных вызов сохраняется.
Выигрыш по сокращению пролога нельзя автоматически перенести на весь декодер.

## Воспроизведение

- node tools/esp8266_opus_asm/update_fast.cjs <gcc.exe>
- node --test tests/esp8266-opus-update-fast-asm.test.js
- node tools/esp8266_opus_asm/check_update_fast.cjs
- node tools/esp8266_opus_asm/check_bands.cjs update-fast
- build_i2s_pdm_production.ps1: Diagnostic, EnableOpus,
  OpusBackend=bands-update-fast-asm, OpusWordAsm/IcdfFlashWord/FirFlashWord,
  NoSpiffsCache, Pdm32Iram/Pdm32Batch, OpusBenchmark и те же fixtures.
- По 10 fresh A/B/A через OTA, run_raw_series.ps1 IntervalMs=15000;
  сохранять все попытки, затем вернуть обычное радио.

Рецепт/manifest: components/opus_decoder/asm/lx106/bands-update-fast.json.
Проверки пути и unit: .build/opus-bands-update-fast/paths.json.
В production не включать без принятия измеренного результата и live-проверки.

## Физический результат: 10 A + 10 B + 10 повторных A

CPU160, профиль QIO40/кэш16, пакеты заранее в RAM. Без audio network,
demux, нормализации/PDM и function/stage profiler. Wi-Fi/WebUI включены.
Медиана task CPU / длительность исходного аудио; ISR, начисленные задаче,
и измерительные издержки не вычитаются. 120 пакетов / 2,4 секунды аудио
в каждом из пяти случаев каждого запуска; не непрерывное воспроизведение.

| Поток | Контроль CPU % | Кандидат CPU % | Повторный контроль CPU % |
|---|---:|---:|---:|
| mono12 | 22,775 | 23,196 | 22,770 |
| mono24 | 54,689 | 54,798 | 54,702 |
| stereo64 | 65,551 | 65,160 | 65,538 |
| stereo128 | 80,728 | 78,694 | 80,720 |
| stereo192 | 92,911 | 91,878 | 92,844 |

Относительная экономия времени на 128: 2,519% к первому контролю,
2,509% к повторному. На 192: 1,112% / 1,040%, но mono12 медленнее
на 1,849% / 1,871%. Выигрыш высоких не превосходит проигрыш низких
по принятому критерию обоих 128/192, поэтому вариант НЕ принят.
Ранее измеренный tell-inline с 88,136% CPU192 остаётся лучшим.
Независимая текущая серия не является прямым A/B против tell-inline.

Все 30 попыток сохранены, без HTTP observation errors, с точными PCM hashes,
packets/samples и scratch peaks. Максимальный отдельный wall-вызов на 192:
22547 мкс контроль, 24331 мкс кандидат, 23185 мкс повторный контроль.
Это wall с вытеснением, не exclusive CPU; предел 20 мс не гарантируется.

## Память и фактические инструкции после линковки

- App 903120 B против 902992 B, +128 B flash.
- Flash text 637122 B (+116); flash rodata 241228 B (+4).
- DRAM data/bss 1652/18752 B; IRAM vectors/text/bss 128/22900/4044 B:
  без изменений. Арена 16384 B, пик 15600; scratch 6144 B, пик 5488.
- Audio stack 5120 B, минимальный lifetime остаток 1660 B во всех сериях.
- Минимум sampled DRAM всех случаев: A 8028, B 7160, повтор A 5172 B.
  Разные динамические значения не доказывают экономию памяти или утечку.
  Минимум heap после cleanup: 26432 / 26568 / 26432 B.
- quant_partition 2170→2222 B; quant_all_bands 9416→9468 B.
  ec_dec_update остаётся 171 B, адрес 0x402469d8→0x402469dc.
  Полная карта с ELF hashes — link-proof.json.

Важный результат аудита: 1162 нормализованные инструкции/relocations/граф
ветвлений static_handler в исходных .obj совпадают, но linker выдаёт разные
вызовы close(fd). В контроле по адресу 0x40222302 — CALL0; у кандидата —
L32R a0,0x40210490 и CALLX0. Литерал действительно содержит адрес close
0x40295ab4. Тело static_handler увеличилось с 3159 до 3163 B без правки
его C-кода. Проверка воспроизводится audit_update_link.cjs; данные —
link-relaxation.json. Это не обнаруженная ошибка HTTP и не измеренная
причина CPU-разницы, а доказательство изменения инструкций при линковке.

Таким образом, эффект всего кандидата нельзя приписать только guard/call
или только cache misses. Следующий отдельный опыт — контролируемое
размещение неизменённого горячего кода с аудитом linker relaxation.
На mono12 два изменённых call site вообще не посещались в host census,
хотя CPU изменился: прямое ускорение этого fast path не объясняет эту строку.

## Сохранённые доказательства и восстановление

firmware/development/esp8266-opus-bands-update-fast-v1 содержит app,
manifest/sdkconfig/CHANGELOG, comparison.json, 10 runs, host correctness/path
counts, 17 PASS регрессий, link proof и все четыре OTA-отчёта.
20 контролей — esp8266-opus-bands-control-v1/update-fast-20260913 и
update-fast-repeat-20260913. Ссылки и hashes всех 30 входов есть в comparison.

Обычная esp8266-opus-live512-idle3s-20260913 восстановлена через OTA,
app0x10000, stopped, Wi-Fi подключён, RSSI −58 dBm, heap 27448 B,
error пустой. Главная HTML и status получили HTTP200; два последовательных
запроса заняли суммарно около159 мс. Это HTTP smoke, не полная browser QA
и не проверка 20 секунд звука. UART, разметка, Wi-Fi/плейлист/SPIFFS не менялись.
