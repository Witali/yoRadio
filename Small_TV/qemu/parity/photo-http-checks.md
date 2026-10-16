# Фотографии через реальный HTTP и flash

`tests/photo_qemu.py` передаёт настоящему ESP-IDF HTTP-серверу прошивки JSON и
binary multipart. Guest RAM/PC/время/инструкции не подменяются; клиент ограничен
собственным localhost listener ВМ. Проверены valid grayscale и RGB 240×240
(38,488 bytes, десять chunks), полное скачивание bytes, запрет второй сессии,
раннего finish и out-of-order chunk, точный retry и отклонение изменённого retry.

Четыре последовательных процесса с тем же собственным flash-файлом проверяют:
обычный cold boot, замену RGB на gray другой длины и остановку сразу после finish,
затем start новой загрузки без chunks и немедленную остановку. Без debounce-пауз
завершённый файл сохраняет длину и все bytes, незавершённый slot скрыт и следующая
загрузка работает. settings_photo_size() уже вызывает settings_flush() синхронно;
изменение firmware для этого не требовалось. Panic/watchdog проверены до повторного
использования каждого UART log. Меняется owned copy flash; source archive прежний.

Один и тот же permanent observer/fixture/helper набор получил:

| Сборка | Malformed Huffman finish | Metadata | Остальные проверки |
|---|---:|---|---|
| Прежняя app `0d8b7585`, ELF `97adeb91` | 200 | exists=true, size=363 | Pass |
| Candidate app `131ce792`, ELF `9184b08b` | 400 | exists=false, size=0 | Pass |

Before — ожидаемый отрицательный результат только для malformed Huffman. После
исправления проходят все 21 checks; maximum observed request .298990 guest s.
Finish→stop: 0 guest s, start→stop: .143098 guest s (обе границы < .5 s).
`photo-http-before.json` и
`photo-http-candidate.json` сохраняют app/source/ELF/QEMU/profile/helper/test
hashes и HTTP stages. Использованы только synthetic images без личных данных,
два разных owned state directories и настоящий guest flash driver. ВМ закрыты.
Первоначальный 11-check observer с debounce-паузой заменён усиленным; архивные
before/after имеют одинаковые финальные test/helper hashes.

Производитель минимальных JPEG выделен в `jpeg_test_fixtures.py`. После
рефакторинга все 41 machine cases повторно проходят; свежий результат —
`jpeg-shared-fixtures-candidate.json`. Production code/image не менялись;
старые header/Huffman reports сохраняют прежние observer identities.

Photo gate обязателен в branch QEMU suite/publisher/verifier; он пока не часть
живого root run 22926. Не проверены browser cropper, полный photo/fade LCD frame,
реальные одновременные клиенты и внезапное питание посреди flash write. QMP stop/quit
после HTTP-ответа проверяет durable metadata на этих границах, а не любой момент
внутри операции. Гипотеза о фоновом сохранении photo_size была опровергнута чтением
реального settings_photo_size() и новым тестом; лишних задержек не добавлено.
