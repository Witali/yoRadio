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
sys.path.insert(0, str(ROOT / 'tools/esp32c3_tests'))
from web_tcp import parse


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    main = ROOT / 'idf/esp32c3-oled-native/main'
    files = [main/'web_tcp_probe.h', main/'web_tcp_probe.c',
             ROOT/'tests/native/web_tcp_probe_test.c', Path(__file__).resolve(),
             ROOT/'tools/esp32c3_tests/web_tcp.py']
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
        lines = output.decode().splitlines()
        assert lines[-1].startswith('PASS TCP probe:')
        frames = [parse(dict(at=i,line=line)) for i,line in enumerate(lines[:-1])]
        assert len(frames) == 70 and all(frames)
        assert frames[0]['kind']=='event' and frames[0]['dir']==1 and frames[0]['flags']==18
        assert frames[1]['before']==255 and frames[1]['after']==3 and frames[1]['port']==32000
        assert frames[2]['before']==3 and frames[2]['after']==4
        assert frames[3]['result']==-7 and frames[3]['pending']==(2 if backlog else 255)
        assert frames[4]['kind']=='watermark' and frames[4]['emitted']==4 and frames[4]['queued']==0
        assert [f['port'] for f in frames[5:69]]==list(range(64))
        assert all(f['dropped']==5 for f in frames[5:69])
        assert frames[-1]['kind']=='listener' and frames[-1]['seq']==0x10203040
        assert frames[-1]['backlog']==5 and frames[-1]['pending']==2
        print(lines[-1],'; 70 firmware frames independently decoded and CRC checked')
    (a.output/'report.json').write_text(json.dumps(dict(passed=True, backlog_variants=[0,1],
        scope='Actual wrappers; platform doubles, not real TCP or physical timing.',
        sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}),indent=2)+'\n')


if __name__ == '__main__':
    main()
