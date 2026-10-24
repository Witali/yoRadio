# Прерывания публикации фото в production QEMU

Отдельный storage gate проверяет реальные HTTP upload/codec/cache/settings пути
app `9c1a83bd…`, ELF `76b5ce37…`, source `7d95988c…`. Сборка, лимит200КиБ,
SDK и frozen QEMU D64 не меняются. LCD и network acceptance сюда не входят.

## Сценарий и ожидаемая видимость

Начальный образ — фактически остановленный4МиБ backing предыдущего lossless6
прогона с готовым CMYK6 фото в slot5. Проверяются полные исходник/RGB565/journal,
а также точные app/ELF/source/frozen inputs. Для замены используется RGB6 fixture;
оба файла240×240 и имеют независимо вычисленные samples/pixels.

| После какой завершённой операции остановлен процесс | Фото после холодного запуска |
|---|---|
| Первая body page инвалидации | Старое CMYK6; прежняя полная journal bank |
| Commit footer инвалидации | Старое CMYK6; источник ещё цел, кэш отозван |
| Erase всего исходного slot | Фото отсутствует |
| Первый4096-byte HTTP chunk | Фото отсутствует |
| Первая256-byte RGB565 page | Фото отсутствует |
| Первая body page нового journal | Фото отсутствует |
| Commit footer нового journal, до settings publication | Фото отсутствует; полный кэш уже подтверждён |
| Полностью завершённый finish/upload/settings | Новое RGB6 |

Используются только аппаратные GDB breakpoints и чтение регистров/памяти.
Вызовы выполняются штатно до реального return; PC, code и return values не
подменяются. Сохраняются адреса/размеры/status completed callbacks и наблюдённые
инструкции. `TerminateProcess` применяется только к собственному process handle;
QMP quit/guest shutdown при cut не вызываются. Paused/stopped backing обязаны
совпасть полностью. Новому процессу передаются ровно эти bytes без NVS/settings
reseeding. Сохраняется и его actual initial backing до первого CPU continue.

После холодной проверки каждый сценарий выполняет обычную загрузку известного
gray progressive JPEG. Проверяются полный source/frame/journal, чужие photo
slots/cache entries и protected bytes. Готовность HTTP только запускает storage
сценарий; это не проверка RF, Wi-Fi reconnect/churn или LCD.

`photo_publication_contract.py` повторно вычисляет authority и полные hashes из
физических образов, проверяет trace последней операции, cold visibility,
producer identities и остановку владельцев. Negative controls должны отвергать
ложную видимость, running owner, failed callback return, cold reseed и повреждение
recovery pixels. Архивный verifier восстанавливает каждый полный4МиБ image.

## Границы модели и статус

Проверяются восемь выбранных границ **между завершёнными операциями**. NOR модель
обновляет functional contents и отдельно моделирует WIP timing. Это не обрыв
питания внутри отдельного program/erase и не электрическая brownout модель.
Настоящие SDK I/O/allocation failures, промежуточные NVS/settings операции и
физические отключения питания остаются отдельными пунктами плана.

Полный восьмиточечный прогон завершён двумя независимыми частями4+4: оба exec0,
все16owned процессов stopped/reaped. Восемь cold boots и восемь немедленных
successful recovery uploads прошли. В двух сценариях старое фото видно до source erase,
пять промежуточных состояний невидимы, завершённый upload публикует RGB6.
Состояние publication-footer с готовым физическим кэшем остаётся невидимым до
settings commit. Оба independent replays pass; по5negative controls на часть.
Предел200КиБ не менялся. App/ELF/SDK/frozen QEMU прежние, физическая плата не
затрагивалась. Это закрывает выбранные operation boundaries, не все power cuts.

Proof: [photo-publication-validation-20261024.json](../../qemu/parity/photo-publication-validation-20261024.json).
Архив сохраняет actual initial/paused/stopped/recovered flash, prepared/session
и UART, full callback traces и failed pilot reports. Verifier дополнительно
сверяет observed instruction bytes/addresses с точным production ELF; каждый
cold initial совпадает с stopped cut, каждый warm initial — с общим seed.
57полных physical image identities и78raw items сохранены через проверяемые
lossless deltas; добавлено60416bytes gzip payloads с повторным использованием
ранее сохранённых точных секторов. JSON index и прежние зависимости считаются отдельно.

Первый pilot неверно разобрал numeric getclocktype как object и завершился до
cut. Второй выполнил cut/cold checks, но recovery observer имел лишь30s host timeout.
Эти pilot результаты не засчитываются как успешные сценарии. Runner исправлен:
штатный numeric ответ; явный900s host bound как у format harness. Guest budgets,
предел200КиБ и firmware timeouts не менялись. Это не скорость физического C2.

## Воспроизведение

```powershell
python -B Small_TV/src/tests/photo_publication_qemu.py --qemu-root FROZEN_QEMU --seed STOPPED_CMYK6_FLASH --output NEW_PUBLICATION
python -B Small_TV/src/tests/photo_publication_contract.py --run NEW_PUBLICATION
python -B Small_TV/src/tests/verify_photo_publication_evidence.py --proof Small_TV/qemu/parity/photo-publication-validation-20261024.json
```

`--cases` выбирает явный subset. Он не даёт полного восьмиточечного pass.
После последующих изменений source pins можно проверить с
`--source-revision PRODUCER_COMMIT`: Git blobs/LFS OIDs читаются без checkout/reset.
Физическая плата не затрагивается; оригинальный seed остаётся неизменным.
