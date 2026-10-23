from pathlib import Path

root = Path.cwd()
path = root / 'docs/ESP32_CYD_C3_TRANSFER_PLAN.md'
text = path.read_text(encoding='utf-8')
old = '[Аудит TLS reserve/MPI](../tests/results/cyd-tls-reserve-mpi-audit-20261020/README.md) завершён; реализация этих кандидатов, IRAM/stack и физические измерения CYD остаются.'
new = '[Аудит TLS reserve/MPI](../tests/results/cyd-tls-reserve-mpi-audit-20261020/README.md) завершён. [Ранняя MPI](CYD_EARLY_MPI_DESIGN.md) подключена default-off в `959f35486`: canonical startup, реальные SDK locks/heap, оба ядра и exact controls проходят; [архив проверок](../tests/results/cyd-early-mpi-20261020/README.md) сохранён. Её полные application exports и radio/board квалификация, TLS reserve, IRAM/stack и физические измерения CYD остаются.'
assert text.count(old) == 1
path.write_text(text.replace(old, new), encoding='utf-8', newline='\n')
print('Updated MPI row without closing stage 13')
