# Opus ASM: N3 finite differences, четыре шага

2026-09-19. Независимый кандидат `esp8266-opus-pvq-n3-unroll4-{control,candidate}-v1`
над принятой eBands-final базой. Предыдущий N3-diff отклонён и не становится
production parent. Развёртывание проверяется против принятой прошивки.

## Изменение

Начальная проба U(K), первый fast return и site43B0x40253329 такие же, как
в скалярном N3-diff. Другие N сохраняют линейный поиск. Только helper в94B
decoder-dead storage0x40251024 заменён на23 инструкции/66B вместо8/21B.

При входе в группу p=U(3,K), delta=4*(K-1). Первые три стадии выполняют
p-=delta и проверяют результат до следующей стадии. При раннем выходе K
уменьшается на1/2/3 соответственно. Четвёртая стадия уменьшает K сразу на4
и либо возвращает результат, либо начинает следующую группу. Нельзя выполнять
все четыре вычитания без промежуточных проверок: это нарушило бы границу13.

Используются те же a2(index),a8(p),a12(K),a6(delta),a13(N). Перед возвратом
a6=N-1. CALL0/RET и48B исходного frame остаются; a0 мёртв до старого epilogue.
Нет новой таблицы, stores/SAR, scratch или дополнительных stack slots.
C fallback production не меняется, bitrate cap не вводится.

Для d=начальная_K-конечная_K,q=floor(d/4),r=d%4 предполагается
4+13*q+(r?3*(r-1)+4:0) инструкций helper вместо4+4*d, если d>0.
Это нужно сверить с actual linked кодом. Число чтений U остаётся таким же,
как у N3-diff; больший код может ухудшить кэш. CPU измерять, не выводить из
числа инструкций. Историческая скалярная серия не заменяет свежий контроль.

## Протокол

- [x] 303906 linked случая всех U-интервалов, точные K/p/GPR, границы и ABI;
  static RAM/frame/app size без роста.4392 первых fast returns неизменны.
- [x] 24 host exact PCM/state/ASan/UBSan случая, в том числе320/510, mixed,
 120мс/48 frames. Это semantic mirror, не выполнение LX106 на компьютере.
- [x] 11 регрессий PASS: branch/phase/delta, все23 helper-инструкции покрыты,
  неизменный site относительно скалярного опыта и проверка decoder-dead storage.
- [x] Linked instruction census совпадает с независимой host-моделью:
  на192 инструкции119961→122440, U-reads24259→18357; на12860732→63195,
  U-reads11682→9798. На320/20мс292130→277220 инструкций; это не CPU.
- [ ] 10A/10B/10A2: CPU160/runtime QIO40, RAM packets, без output/function/stage
 profiler; все попытки/timeout/минимумы RAM сохранять.
- [ ] Оба high-bitrate gate и память; только затем решение о принятии.
- [ ] Восстановление ordinary radio и HTTP/WS/playlist. Цель75% raw CPU
 и20s live I2S PDM/WebUI требует отдельного подтверждения.

Рецепты в `tools/esp8266_opus_asm/`:
`pvq_n3_unroll4.cjs`, `check_bands.cjs pvq-n3-unroll4`,
`analyze_pvq_n3_unroll4_instructions.cjs`, `report_pvq_n3_unroll4.cjs`.
Тесты `tests/esp8266-opus-pvq-n3-unroll4*.test.js`.
[Предыдущая модель](ESP8266_OPUS_PVQ_SEARCH_NEXT.md) и
[отклонённый скалярный опыт](ESP8266_OPUS_PVQ_N3_DIFF_ASM.md).

App903216B. Candidate SHA256:
`ce4647efde438926d1aa3b628ce88dd959c103cadc5f9eabb4924cfe1f63b77d`.
Скалярный N3 helper заменён с8 на23 инструкции/21→66B. RAM и48B frame прежние.
Физические10A/10B/10A2 ещё выполняются; CPU-ускорение не установлено.
