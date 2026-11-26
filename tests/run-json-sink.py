"""Differential shared JSON buffer/sink contracts against the pinned original encoder."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'idf/components/native_stream'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run

ORIGINAL_SHA = '0bb4f88346019a5d319f2264c4bc3132d8ab87d8c644699d43814b4cfa82aa30'

def sha(body):
    return hashlib.sha256(body).hexdigest()

def logged(command, path):
    try:
        body, code = run(command), 0
    except subprocess.CalledProcessError as error:
        body, code = error.output, error.returncode
    path.write_bytes(body)
    return code, body

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert not output.exists()
    output.mkdir(parents=True)
    sources = output / 'sources'; sources.mkdir()
    files = [ROOT/'tests/native/json_sink_test.c', Path(__file__),
             *[BASE/'include'/name for name in ('json_string_span.h','json_buffer.h','json_sink.h')]]
    original = subprocess.check_output(['git','-c','core.longpaths=true','show',
        'f7dee344fb30ce109f2d30a01f0325d353e3b2eb:idf/components/native_stream/include/json_buffer.h'],cwd=ROOT)
    assert sha(original) == ORIGINAL_SHA
    for path in files:
        destination = sources/path.relative_to(ROOT)
        destination.parent.mkdir(parents=True,exist_ok=True); destination.write_bytes(path.read_bytes())
    report = dict(scope='Private portable representation only; exact original f7 JSON header is the differential oracle. No target frames, network framing, timing or hardware qualification.',
                  source_commit_reference='f7dee344fb30ce109f2d30a01f0325d353e3b2eb', physical_tested=False,
                  original_header_sha256=ORIGINAL_SHA,
                  source_pins={p.relative_to(ROOT).as_posix(): sha((sources / p.relative_to(ROOT)).read_bytes()) for p in files},
                  variants={}, passed=False)
    path = output / 'report.json'
    def save():
        path.write_text(json.dumps(report, indent=2) + '\n')
    save()
    code, _ = logged(['gcc', '--version'], output / 'compiler-version.log')
    if code:
        report['reason'] = 'Host compiler unavailable; original version log retained'; save(); return 1
    mutations = [
        ('candidate', None, None, None, 0, b'PASS 6 JSON sink groups;'),
        ('replacement-codepoint-negative', 'json_string_span.h', b"scratch[5] = 'd';", b"scratch[5] = 'c';", 42, b'FAIL span encoding'),
        ('capacity-off-by-one-negative', 'json_sink.h', b'size >= out->capacity - out->length', b'size > out->capacity - out->length', 42, b'FAIL sink state equivalence'),
        ('ignore-writer-failure-negative', 'json_sink.h', b'!out->write(out->context, data, size)', b'(out->write(out->context, data, size), false)', 42, b'FAIL writer failure propagated'),
        ('unchecked-overflow-negative', 'json_sink.h',
         b'out->length >= out->capacity || size >= out->capacity - out->length',
         b'out->length + size >= out->capacity', 42, b'FAIL checked overflow rejected'),
    ]
    for name, filename, before, after, expected, marker in mutations:
        work = output / name; work.mkdir()
        for header in ('json_string_span.h', 'json_buffer.h', 'json_sink.h'):
            body = (sources / 'idf/components/native_stream/include' / header).read_bytes().replace(b'\r\n', b'\n')
            if header == filename:
                assert body.count(before) == 1; body = body.replace(before, after)
            (work / header).write_bytes(body)
        (work / 'original_json_buffer.h').write_bytes(original)
        (work / 'test_json_sink.c').write_bytes((sources / 'tests/native/json_sink_test.c').read_bytes())
        binary = work / 'test'
        command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                   '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                   '-fstack-usage', '-I' + host(work), host(work / 'test_json_sink.c'), '-o', host(binary)]
        item = dict(build_command=command, compiled_header_pins={p.name: sha(p.read_bytes()) for p in work.glob('*.h')})
        code, _ = logged(command, work / 'build.log'); item['build_returncode'] = code
        report['variants'][name] = item; save()
        if code:
            report['reason'] = name + ' host compilation failed; raw log retained'; save(); return 1
        command = ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                   'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', host(binary)]
        code, body = logged(command, work / 'test.log')
        item.update(test_command=command, returncode=code, expected_returncode=expected,
                    passed=code == expected and marker in body,
                    host_stack_usage=[dict(file=p.name, sha256=sha(p.read_bytes())) for p in work.glob('*.su')])
        if expected == 0 and item['passed']:
            match = re.search(rb'differential_cases=(\d+); buffer_layout=(\d+)', body)
            assert match and int(match[1]) == 81501
            item.update(differential_cases=int(match[1]), host_buffer_layout_bytes=int(match[2]))
        save()
        if not item['passed']:
            report['reason'] = name + ' unexpected outcome; raw logs retained'; save(); return 1
        print(name + ': ' + ('PASS six groups' if expected == 0 else 'defective control rejected'), flush=True)
    for source in files:
        assert source.read_bytes() == (sources / source.relative_to(ROOT)).read_bytes(), 'Draft input changed during qualification'
    report.update(passed=True, groups=6, differential_cases=81501, rejected_controls=4)
    save(); return 0

if __name__ == '__main__':
    raise SystemExit(main())
