"""Exercise actual diagnostic wrappers with destructive lwIP platform doubles."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    main = ROOT / 'idf/esp32c3-oled-native/main'
    files = [main/'web_tcp_probe.h', main/'web_tcp_probe.c',
             ROOT/'tests/native/web_tcp_probe_test.c', Path(__file__).resolve()]
    for path in files:
        saved = a.output/'sources'/path.relative_to(ROOT)
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(path.read_bytes())
    strip = lambda path: re.sub(r'^#(?:include|pragma once)[^\n]*\n', '', path.read_text(), flags=re.M)
    text = files[2].read_text().replace('/* PRODUCTION_HEADER */', strip(files[0])).replace('/* PRODUCTION_SOURCE */', strip(files[1]))
    unit = a.output/'test.c'
    unit.write_text(text)
    for backlog in (0, 1):
        binary = a.output/f'backlog-{backlog}'
        (a.output/f'build-{backlog}.log').write_bytes(run([
            'gcc', '-std=c11', '-O2', '-g', '-Wall', '-Wextra', '-Werror',
            f'-DTCP_LISTEN_BACKLOG={backlog}', '-fsanitize=address,undefined',
            '-fno-pie', '-no-pie', host(unit), '-o', host(binary)]))
        output = run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                      'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
        (a.output/f'run-{backlog}.log').write_bytes(output)
        assert output.startswith(b'PASS TCP probe:')
        print(output.decode().strip())
    (a.output/'report.json').write_text(json.dumps(dict(passed=True, backlog_variants=[0,1],
        scope='Actual wrappers; platform doubles, not real TCP or physical timing.',
        sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}),indent=2)+'\n')


if __name__ == '__main__':
    main()
