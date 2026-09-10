# ESP8266 Opus: FIR word-pairs — результат A/B

2026-09-10, исходники `3f72f25`. Wemos D1 mini, CPU160, QIO40,
fixed-point libopus1.5.2, WordASM и ICDF-word включены. Прошивка через OTA,
Wi-Fi/SPIFFS/плейлист не изменены. Основной профиль автоматически не менялся.

## Что изменено

Во внутреннем SILK FIR восемь signed16 чтений коэффициентов из flash заменены
четырьмя aligned32 чтениями пар. Порядок восьми MAC, округление и насыщение
сохранены. Таблица остаётся во flash, явно выровнена на4 байта; нет копии в RAM.
Опция `-OpusFirFlashWord`, CMake `YORADIO_OPUS_FIR_FLASH_WORD`, default OFF.

## Чистый декодер: 10 + 10 прогонов

Собственные tone/noise Opus-пакеты,5 режимов,12 разных20-мс пакетов на режим.
В каждом прогоне10 повторов после прогрева:120 пакетов/115200 PCM-отсчётов,
2.4 секунды звука на режим. Пакет перед decode находится в RAM; отсутствуют
скачивание аудио, Ogg/ICY, нормализация и PDM. Wi-Fi/WebUI остаются включены.
Task CPU исключает другие задачи, но включает отнесённые к задаче ISR и
измерительные накладные расходы. Это не идеальный CPU-only запуск без Wi-Fi.

| Режим | CPU-бюджет OFF, медиана | ON, медиана | Уменьшение времени |
|---|---:|---:|---:|
| SILK mono12 | 59.416% | 23.401% | 60.62% |
| Hybrid mono24 | 94.477% | 58.484% | 38.10% |
| CELT stereo64 → mono | 75.996% | 74.100% | 2.49% |
| CELT stereo128 → mono | 101.739% | 99.246% | 2.45% |
| CELT stereo510 → mono | 196.425% | 199.795% | **ухудшение1.72%** |

CPU-бюджет = время задачи / длительность PCM.100% не оставляет времени на
вывод/сеть; это не процент загрузки компьютера или исключительно Wi-Fi.
Ни один прогон не исключён, ошибок наблюдения нет. Серии последовательные,
не рандомизированные/interleaved. Первые предварительные OFF-замеры не
использованы: после фиксации исходников бинарник пересобран и все10 повторены.

Для SILK/Hybrid ускоряется реальный горячий FIR. Чистый CELT этот FIR не
вызывает: его небольшие изменения **нельзя приписывать алгоритму FIR**.
Сдвиг flash text/rodata и cache placement — вероятное объяснение, не измерение
cache misses. Максимальный wall-вызов CELT64 всё ещё достигал70.410мс.
На10 значениях nearest-rank p95 равен максимуму; это не оценка редкого хвоста.

SILK CPU OFF59.354–59.491%, ON23.375–23.417%; Hybrid OFF94.433–94.540%,
ON58.456–58.531%. Максимальные wall-вызовы SILK15.309→7.053мс,
Hybrid71.298→16.059мс; wall включает прерывания/вытеснение.

## Корректность и память

- Все контрольные суммы PCM совпали между всеми20 прогонами и обоими профилями.
- Host full PCM:5 фикстур + смешанный SILK mono/stereo/Hybrid/CELT/PLC,
  reset/OOM recovery — exact, максимальная ошибка0, SNR=∞.
- ASan/UBSan внутреннего FIR:357590 отсчётов,35 случаев, все12 строк таблицы,
  все дробные фазы, насыщение и границы выходного массива — exact.
- Scratch по режимам прежний:1808/2904/5488B DRAM и14112/15600B word arena.
- Стек FIR80B в обоих Xtensa-объектах. Остаток полного аудиостека в raw-серии
  не является размером стека FIR; его значения сохранены в исходных отчётах.
- `.dram0.data`1652B, `.dram0.bss`18768B, `.iram0.text`22900B,
  `.iram0.bss`4044B — одинаковы в обоих ELF. Это только статические секции,
  не общий расход SDK/кучи/стеков.
- ON flash text меньше20B, rodata больше4B; app911776→911760B.
- Минимум свободной DRAM во всех raw-случаях: OFF7808B, ON6980B.
  После cleanup: OFF26168–26988B, ON26316–26924B. Различия динамической
  Wi-Fi/HTTP памяти не означают изменение размера кодековой арены или утечку.

## Воспроизведение

Оба артефакта в `firmware/development/esp8266-opus-fir-{off,on}-raw/`:
app.bin,manifest.json,sdkconfig,OTA-отчёт иrun1..run10.json.
Все поля manifest, кроме FIR-флага, времени сборки и размера/хэша app, совпадают.

```powershell
node tools/esp8266_opus_profile/compare_raw.cjs --reference firmware/development/esp8266-opus-fir-off-raw --candidate firmware/development/esp8266-opus-fir-on-raw --output .build/opus-fir-comparison.json
node --test tests/esp8266-opus-fir-word.test.js tests/esp8266-opus-raw-comparison.test.js
```

[Машиночитаемый A/B](../firmware/development/esp8266-opus-fir-on-raw/comparison-results.json)
проверяет app SHA256, настройки, завершение всех прогонов, PCM и scratch.
Выбросы/timeout не удаляются; незавершённый прогон не превращается в успех.

## Физический вывод: отрицательный тест непрерывности

Отдельная сборка `esp8266-opus-fir-on-output`, app912496B. Raw-пакеты берутся
из flash; нормализация, PDM32 и реальный GPIO3/I2S/DMA включены.100 повторов,
24 секунды PCM на режим. Один диагностический прогон, не повторный A/B скорости.

| Режим | Весь pipeline, CPU-бюджет | DMA misses | PCM / wall | Min free DRAM |
|---|---:|---:|---:|---:|
| SILK12 | 36.32% | 56 | 0.99985 | 320B |
| Hybrid24 | 71.39% | 556 | 0.97292 | 720B |
| CELT64 | 87.74% | 1221 | 0.93927 | 1208B |
| CELT128 | 111.49% | 6582 | 0.73443 | 712B |
| CELT510 | 180.33% | 16623 | 0.52144 | 2260B |

**Ни один режим не прошёл строгий zero-underrun gate.** Малый средний CPU
SILK не исключает редких задержек. Кроме того, запас RAM этой тяжёлой
диагностической сборки небезопасен. В4 наблюдениях HTTP был timeout/reset;
они сохранены. После cleanup свободно26852B. Нулевой FIFO-empty не отменяет
DMA misses: резервный буфер поддерживает аппаратный поток ценой пауз звука.
Нельзя выдавать pipeline CPU за время исключительно декодера или вычитать
его из raw серии для точного измерения PDM.

[Исходный отчёт](../firmware/development/esp8266-opus-fir-on-output/run1.json).
Следующий тест проводится на `esp8266-opus-fir-on-live` без raw fixtures,
benchmark task и FreeRTOS runtime stats; app884848B.

## Проверка реального HTTP-потока

В live-сборке DLF24 прошёл HTTP redirect, но остановлен существующим лимитом:
`Opus packet exceeds 20 ms`. Это не ошибка FIR; PCM не сформирован. Добавлен
пунктA8/P7 в общий план для bounded block-output длинных пакетов.

`http://secure.live-streams.nl/opus.opus`: первый snapshot подтвердил48кГц
PCM,207004 frames и free_heap7288B. Во втором snapshot через27 секунд —
HTTP timeout. Поэтому **нет валидного двухточечного измерения непрерывности**,
нет доказательства25 секунд без пропусков и нет корректного stage CPU-профиля.
Не подменять пропущенную точку последующим успешным ответом после stop.

Явный `stop=1` выполнен успешно: playing=false, RSSI−59dBm,
free_heap27324B, lifetime min_heap3604B. На плате оставлена live-сборка,
проигрывание остановлено; Wi-Fi и плейлист не изменены. UART/reset не применялись.

[DLF24](../firmware/development/esp8266-opus-fir-on-live/dlf24-result.json),
[Opus56](../firmware/development/esp8266-opus-fir-on-live/celt56-result.json),
[подтверждение stop](../firmware/development/esp8266-opus-fir-on-live/stop-result.json).

Итог: FIR-оптимизацию стоит сохранить для SILK/Hybrid. Она сама по себе не
решает непрерывность CELT и не доказывает отсутствие пауз у реального радио.
Следующий приоритет — CELT pulse-cache/energy/eBands и точные операции
деления из [общего аудита](ESP8266_OPUS_DECODER_SPEED_OPTIMIZATION_PLAN.md).
