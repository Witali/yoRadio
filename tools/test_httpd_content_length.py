"""Check actual pinned SDK guards at 32/64-bit boundaries under ASan/UBSan.

On Windows this uses WSL gcc. No board or network endpoint is contacted.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from patch_httpd_content_length import GUARD, OLD, patch


HARNESS = r'''
#include <stdint.h>
#include <stddef.h>
#include <limits.h>
#include <stdio.h>
#include <inttypes.h>
#define ESP_LOGW(...) ((void)0)
#define HTTPD_413_CONTENT_TOO_LARGE 413
#define PARSING_FAILED 7
#define ESP_FAIL -1
struct parser { uint64_t content_length; };
/* Simulate the target's 32-bit size_t even on a 64-bit host. */
struct request { uint32_t content_len; };
struct state { int error, status; };
static int convert(struct parser *parser, struct request *r, struct state *parser_data) {
@BODY@
return 0;
}
int main(void) {
    const uint64_t lengths[] = {0, 1, 1024, INT32_MAX, (uint64_t)INT32_MAX+1,
        (uint64_t)UINT32_MAX-1, UINT32_MAX, (uint64_t)UINT32_MAX+1,
        (uint64_t)UINT32_MAX+1025, UINT64_MAX-1, UINT64_MAX};
    int failures = 0;
    for (unsigned i = 0; i < sizeof(lengths)/sizeof(lengths[0]); ++i) {
        struct parser parser = { lengths[i] };
        struct request request = { 12345 };
        struct state state = { 0, 0 };
        int result = convert(&parser, &request, &state);
        int reject = lengths[i] > UINT32_MAX && lengths[i] != UINT64_MAX;
        int valid = reject ? result == ESP_FAIL && state.error == 413 &&
            state.status == PARSING_FAILED && request.content_len == 12345 :
            result == 0 && state.error == 0 && state.status == 0 &&
            request.content_len == (lengths[i] == UINT64_MAX ? 0 : lengths[i]);
        printf("length=%" PRIu64 " result=%s\n", lengths[i], valid ? "PASS" : "FAIL");
        failures += !valid;
    }
    return failures;
}
'''


def host_path(path):
    path = path.resolve().as_posix()
    if sys.platform == 'win32':
        if len(path) < 3 or path[1:3] != ':/':
            raise ValueError('WSL tests require a local drive path')
        return '/mnt/' + path[0].lower() + path[2:]
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--idf-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    prefix = ['wsl.exe', '--exec'] if sys.platform == 'win32' else []
    results = []
    for version in ('6.0.2', '6.0.3', '6.1'):
        original = (a.idf_root/('v'+version)/'components/esp_http_server/src/httpd_parse.c').read_bytes()
        fixed = patch(original)
        lf = original.replace(b'\r\n', b'\n')
        assert patch(lf).replace(b'\r\n', b'\n') == fixed.replace(b'\r\n', b'\n')
        assert patch(lf.replace(b'\n', b'\r\n')).replace(b'\r\n', b'\n') == fixed.replace(b'\r\n', b'\n')
        assert fixed.decode().replace('\r\n', '\n').count(GUARD) == 1
        if version == '6.0.3':
            assert fixed == original, 'Already-fixed SDK must remain byte-identical'
        try:
            patch(original + b'\n')
        except ValueError:
            pass
        else:
            raise AssertionError('Changed SDK source was accepted without review')
        for control in (False, True) if version != '6.0.3' else (False,):
            body = OLD if control else GUARD
            assert body in (original if control else fixed).decode().replace('\r\n', '\n')
            name = version + ('-unpatched' if control else '-guarded')
            source = a.output/(name+'.c')
            binary = a.output/name
            source.write_text(HARNESS.replace('@BODY@', body), encoding='utf-8')
            command = prefix + ['gcc', '-std=c11', '-Wall', '-Wextra', '-Wno-unused-parameter',
                '-Werror', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                host_path(source), '-o', host_path(binary)]
            subprocess.run(command, check=True, capture_output=True, timeout=60)
            run = subprocess.run(prefix+[host_path(binary)], capture_output=True, text=True, timeout=30)
            (a.output/(name+'.log')).write_text(run.stdout+run.stderr, encoding='utf-8')
            expected = 4 if control else 0
            assert run.returncode == expected, (name, run.returncode, run.stdout, run.stderr)
            assert not run.stderr, (name, run.stderr)
            results.append(dict(sdk=version, control=control, boundary_cases=11,
                rejected_behavior_cases=run.returncode, expected_failures=expected,
                original_sha256=hashlib.sha256(original).hexdigest(),
                generated_sha256=hashlib.sha256(fixed).hexdigest(),
                unknown_source_rejected=True, sanitizer_passed=True))
    (a.output/'report.json').write_text(json.dumps(dict(passed=True, results=results), indent=2)+'\n')
    print('PASS: 33 guarded boundaries; each legacy control fails four; unknown sources rejected')


if __name__ == '__main__':
    main()
