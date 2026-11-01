"""Verify original host page-owner/PCM-span evidence; execute no archived code."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

HERE = Path(__file__).resolve().parent


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def main():
    manifest = json.loads((HERE / 'manifest.json').read_bytes())
    need(manifest['schema'] == 1 and manifest['production_integrated'] is False and
         manifest['physical_hardware'] is False, 'scope')
    archive = (HERE / 'captures.zip').read_bytes()
    need(len(archive) == manifest['archive']['bytes'] and sha(archive) == manifest['archive']['sha256'],
         'complete archive identity')
    with zipfile.ZipFile(HERE / 'captures.zip') as z:
        names = z.namelist()
        need(len(names) == len(set(names)) == manifest['physical_blobs'], 'unique physical inventory')
        blobs = {name: z.read(name) for name in names}
    need(set(blobs) == {row['blob'] for row in manifest['files']}, 'exact physical inventory')
    files = {}
    for row in manifest['files']:
        path = PurePosixPath(row['path'])
        need(not path.is_absolute() and '..' not in path.parts and row['path'] not in files,
             'unique contained logical path')
        body = blobs[row['blob']]
        need(not body.startswith(b'\x7fELF') and len(body) == row['bytes'] and sha(body) == row['sha256'] and
             row['blob'] == 'blobs/' + row['sha256'], 'exact published bytes, no executable')
        files[row['path']] = body
    need(len(files) == manifest['logical_files'], 'complete logical inventory')
    commands = ['compiler-version', 'compiler-path', 'compiler-sha256', 'libopus-path',
                'libopus-sha256', 'build', 'test', 'libopus-post-sha256']
    for suffix, expected_pages in (('01', 263), ('02', 276)):
        prefix = 'campaign-' + suffix + '/'
        report = json.loads(files[prefix + 'report.json'])
        need(report['passed'] and report['state'] == 'complete' and report['all_source_bindings_unchanged'] and
             report['production_integrated'] is False and report['physical_hardware'] is False, 'genuine host scope')
        need([row['name'] for row in report['commands']] == commands, 'complete command inventory')
        for source in report['sources']:
            body = files[prefix + source['snapshot']]
            need(sha(body) == source['sha256'] and len(body) == source['bytes'], 'frozen source identity')
        for command in report['commands']:
            need(command['pid'] > 0 and command['state'] == 'complete' and command['exit_status'] == 0 and
                 not command.get('timed_out'), 'actual terminal zero')
            for channel in ('stdout', 'stderr'):
                log = command[channel]
                body = files[prefix + log['path']]
                need(len(body) == log['bytes'] and sha(body) == log['sha256'], 'original unmodified log')
        build = next(row for row in report['commands'] if row['name'] == 'build')
        test = next(row for row in report['commands'] if row['name'] == 'test')
        need({'-Werror', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'} <= set(build['argv']),
             'actual instrumentation')
        need({'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1', 'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1'}
             <= set(test['argv']), 'actual sanitizer settings')
        need(not files[prefix + test['stderr']['path']], 'no sanitizer diagnostics')
        records = [json.loads(line) for line in files[prefix + test['stdout']['path']].splitlines()]
        need(records == report['test_records'] and len(records) == 15 and
             all(row.get('passed') is True for row in records), 'all original test records')
        need(records[-1] == dict(suite='ogg-page-input-host', passed=True, page_cases=expected_pages,
             trim_cases=204, allocation_refusals=12, max_page_bytes=65307, production_integrated=False),
             'required page/PCM/allocation inventory')
        need(records[-4]['suite'] == 'ogg-opus-timeline-host' and records[-4]['cases'] == 525 and
             records[-5]['reference'] == 'libopus' and records[-5]['duration_comparisons'] == 219,
             'unchanged original regression also executed')
        need([row['bytes'] for row in records[-3:-1]] == [706319, 707097] and
             all(row['allocation_ordinals'] == 6 for row in records[-3:-1]), 'both complete fixture owners')
        omitted = [row for row in manifest['local_only_executables'] if row['campaign'] == suffix]
        need(len(omitted) == 1 and omitted[0]['sha256'] == report['binary']['sha256'] and
             omitted[0]['bytes'] == report['binary']['bytes'] and omitted[0]['original_retained_locally'] and
             omitted[0]['byte_payload_published'] is False and prefix + report['binary']['path'] not in files,
             'explicit local-only executable identity')
    print(json.dumps(dict(passed=True, logical_files=len(files), physical_blobs=len(blobs),
        page_cases=276, trim_cases=204, production_integrated=False, archived_code_executed=False)))


if __name__ == '__main__':
    main()
