from pathlib import Path
root=Path(__file__).resolve().parent
source=Path('.build/c3-quiet-tls-records-20261010/freeze.py').read_text().replace('esp32c3-quiet-tls-records-20261010','esp32c3-tls-renegotiation-20261010')
source=source.replace("allowed={'.py','.json','.jsonl','.log','.md','.pem'}", "allowed={'.py','.json','.jsonl','.log','.md','.pem','.txt'}")
source=source.replace("    if not source.is_file()", "    if source.relative_to(ROOT).parts[0]=='packages':continue\n    if not source.is_file()")
source=source.replace("('test-quiet-tls-records.py','test-tls-record-server.py','test-sustained-output.py')", "('test-quiet-tls-records.py','test-tls-record-server.py','test-tls-renegotiation-server.py')")
(root/'freeze.py').write_text(source)
verify=Path('.build/c3-quiet-tls-records-20261010/verify_commit.py').read_text().replace('esp32c3-quiet-tls-records-20261010','esp32c3-tls-renegotiation-20261010')
(root/'verify_commit.py').write_text(verify)
