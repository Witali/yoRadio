# Холодные старты: отдельная проверка дисплея

`display_cold_boot_qemu.py` выполняет20холодных процессов QEMU на каждую
прошивку. Factory и reconstructed работают на собственных persistent raw images.
Каждый процесс должен сам вывести полный статичный setup frame240×240; ни UART,
ни HTTP, ни SDK flags Wi-Fi/DHCP/SNTP не являются признаком готовности дисплея.
Host forwarding отключён. Это проверка QEMU cold process, а не физического питания.

RGB эталон взят из фактической заводской ВМ5321A6B9 на QEMUD64, завершившей
самостоятельный AP services subtest внутри текущего полного прогона. Его setup
frame визуально проверен. `fixtures/display/factory-setup-provenance.json`
связывает full-flash, QEMU, исходный AP report, PPM и сжатый fixture. SHA RGB:
`acc588ab852b81d9e034b64eb489c0f6a8057a3bf49477046c17071e414fffcd`.
Эталон не строится из реконструированного renderer и не берётся с первого
произвольного кадра нового теста. Сам parent full этим fixture не объявляется успешным.

`display_boot_observer.py` сравнивает все172800RGB bytes с эталоном. Чёрные,
частично нарисованные и любые другие кадры остаются pending только в пределах
10guest/90host seconds. Ровно на deadline готовность уже не принимается.
Перед каждой командой screendump старый файл удаляется: отсутствие нового кадра
не может пройти по старым bytes. Читается только read-only elapsed counter;
отложенные guest tasks не вызываются, RAM/PC/время не меняются, guest sleeps
не добавляются. Это отдельный более строгий cold/setup gate; он не меняет
порог существующего reset smoke observer5guest/30host seconds.

Результат каждой итерации содержит независимые boot/display/source_integrity
решения, а network явно помечен not_run. Дисплей может пройти независимо от
ROM результата. Boot отдельно требует работающую ВМ, один новый ROM boot,
bootloader entry и отсутствие panic/watchdog. Source integrity проверяет direct
writable raw backing и неизменность executable/media вне NVS/raw settings.
Для каждого процесса сохраняются frame и UART gzip; VM name должен быть новым.
Сеть выбирается setup только как воспроизводимый начальный сценарий прошивки,
не как проверяемый критерий её сетевого стека.

Короткая предварительная проверка1цикл/variant прошла на F1/ELF91E2/D64:
factory exact frame за5.371089guest/8.344host seconds, native за0.410494guest/
0.625host seconds после начала наблюдения. Это измерение конкретного QEMU run,
не физический benchmark. Все62наблюдаемых inputs совпали.

Запуск использует полный frozen snapshot (с `frozen-inputs.json`):

```powershell
python -X utf8 -B Small_TV/src/tests/display_boot_observer_test.py `
  --temp-root C:/Work/yoRadio/.build/display-unit-temp `
  --output C:/Work/yoRadio/.build/display-unit-new.json
python -X utf8 -B Small_TV/src/tests/display_cold_boot_qemu.py `
  --qemu-root C:/Work/yoRadio/.worktree/small-tv-jpeg-headers/.build/jpeg-header-qemu-complete-20261018 `
  --dependency-root C:/Work/yoRadio --cycles 20 `
  --output C:/Work/yoRadio/.build/display-cold-new
```

12unit cases проверяют exact pixels, transient clears, полностью белый неверный
кадр, один неверный цвет, постоянный black, stalled time, оба deadlines, wrap,
усечённый raster и stale screenshot. Нужен actual matching native ELF рядом с
archived app; физическая плата не используется. Сравнение всех тем, динамических
сцен, GPIO/PWM, RF, HTTP, software reset и H10 остаётся в отдельных проверках.
20циклов не добавляются задним числом в frozen full/H10.

Полный самостоятельный прогон20+20 завершён успешно: все40отдельных процессов
нарисовали побайтно точный эталон, boot/source-integrity также прошли в каждой
итерации. Все62inputs совпали; сетевой результат везде not_run. Максимальное
время после начала наблюдения: factory5.496407guest/9.547host seconds,
native0.460610guest/1.391host seconds. Это не сравнение физической скорости.
Proof: `../../qemu/parity/display-cold-20-validation-20261018.json`.
