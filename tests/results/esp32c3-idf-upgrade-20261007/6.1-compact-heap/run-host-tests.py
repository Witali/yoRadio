import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import time

p = argparse.ArgumentParser()
p.add_argument('--version', required=True)
p.add_argument('--label', help='Separate result directory for another configuration of this SDK')
args = p.parse_args()
out = Path('.build/idf-upgrade') / ('python-' + (args.label or args.version))
out.mkdir(parents=True, exist_ok=True)
tools = Path('C:/Work/yoRadio/.idf') / ('tools-v' + args.version)
compilers = list(tools.glob('tools/riscv32-esp-elf/*/riscv32-esp-elf/bin/riscv32-esp-elf-gcc.exe'))
assert len(compilers) == 1
results = []
for test in sorted(Path('tests').glob('test-*.py')):
    cmd = [sys.executable, '-X', 'utf8', str(test)]
    source = test.read_text(encoding='utf-8')
    if re.search(r"add_argument\(['\"]--compiler['\"]", source):
        cmd += ['--compiler', str(compilers[0])]
    if re.search(r"add_argument\(['\"]--toolchain['\"]", source):
        cmd += ['--toolchain', str(compilers[0].parent)]
    started = time.monotonic()
    with (out / (test.name + '.log')).open('wb') as log:
        try:
            run = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=300)
            code = run.returncode
        except subprocess.TimeoutExpired:
            code = 'TIMEOUT'
    text = (out / (test.name + '.log')).read_text(encoding='utf-8', errors='replace')
    count = re.search(r'Ran (\d+) tests?', text)
    skipped = re.search(r'skipped=(\d+)', text)
    results.append({'test': test.name, 'command': cmd, 'exit_code': code,
                    'cases': int(count[1]) if count else None,
                    'skipped': int(skipped[1]) if skipped else 0,
                    'seconds': round(time.monotonic() - started, 2)})
    (out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    print(test.name, code, flush=True)
sys.exit(0 if all(r['exit_code'] == 0 for r in results) else 1)
