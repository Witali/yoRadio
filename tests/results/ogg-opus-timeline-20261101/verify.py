"""Verify saved metadata-only host evidence without executing archived code."""
import hashlib
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ORIGINAL_HEADER = 'idf/components/native_stream/include/ogg_opus_timeline.h'
ORIGINAL_HEADER_SHA = 'b5a5c60e8015efdcbe8339abb37ad6067967d227b09d8e81c074947f53e8a531'


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def main():
    manifest = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
    need(manifest['schema'] == 1 and manifest['metadata_only'] is True, 'scope')
    archive = (HERE / 'captures.zip').read_bytes()
    need(len(archive) == manifest['archive']['bytes'] and
         sha(archive) == manifest['archive']['sha256'], 'archive identity')
    with zipfile.ZipFile(HERE / 'captures.zip') as z:
        need(len(z.namelist()) == len(set(z.namelist())), 'unique archive members')
        bodies = {name: z.read(name) for name in z.namelist()}
    rows = manifest['files']
    need(len(rows) == len({row['path'] for row in rows}), 'unique logical paths')
    need(set(bodies) == {row['blob'] for row in rows}, 'complete blob inventory')
    by_path = {}
    for row in rows:
        body = bodies[row['blob']]
        need(len(body) == row['bytes'] and sha(body) == row['sha256'] and
             row['blob'] == 'blobs/' + row['sha256'], 'exact saved bytes')
        need(not body.startswith(b'\x7fELF'), 'executable images must stay local')
        by_path[row['path']] = body

    expected_commands = {
        '01': ['compiler-version'],
        '02': ['compiler-version', 'compiler-realpath', 'compiler-sha256',
               'compiler-target', 'build', 'test'],
        '03': ['compiler-version', 'compiler-realpath', 'compiler-sha256',
               'compiler-target', 'libopus-path', 'libopus-realpath',
               'libopus-sha256', 'build', 'test', 'libopus-post-sha256'],
    }
    for campaign in ('01', '02', '03'):
        prefix = 'campaign-' + campaign + '/'
        report = json.loads(by_path[prefix + 'report.json'])
        need([row['name'] for row in report['commands']] == expected_commands[campaign],
             'actual command inventory: ' + campaign)
        need(report['physical_hardware'] is False and
             report['decoder_executed'] is False and
             report['playback_trim_implemented'] is False, 'bounded metadata scope')
        for source in report['sources']:
            body = by_path[prefix + source['snapshot']]
            need(sha(body) == source['sha256'] and len(body) == source['bytes'],
                 'original frozen source binding')
            if campaign == '03':
                if source['path'] == ORIGINAL_HEADER:
                    # A later nil-page fix legitimately changes production
                    # sources. This historical gate authenticates the exact
                    # earlier source, without qualifying the later revision.
                    need(sha(body) == ORIGINAL_HEADER_SHA,
                         'exact original qualified observer revision')
                else:
                    need((ROOT / source['path']).read_bytes() == body,
                         'unchanged original harness/fixture/runner binding')
        for command in report['commands']:
            need(command['state'] == 'complete' and command['pid'] > 0 and
                 isinstance(command['exit_status'], int), 'actual terminal native command')
            for channel in ('stdout', 'stderr'):
                row = command[channel]
                body = by_path[prefix + row['path']]
                need(sha(body) == row['sha256'] and len(body) == row['bytes'], 'raw command log')
        if campaign == '01':
            need(report['passed'] is False and report['state'] == 'nonpass' and
                 report['commands'][0]['exit_status'] != 0 and 'binary' not in report,
                 'original sandbox denial must remain a pre-build nonpass')
            continue
        need(report['passed'] is True and report['state'] == 'complete' and
             report['all_source_bindings_unchanged'] is True and
             all(row['exit_status'] == 0 and not row.get('timed_out')
                 for row in report['commands']), 'genuine successful native run')
        omitted = [row for row in manifest['local_only_executables'] if row['campaign'] == campaign]
        need(len(omitted) == 1 and omitted[0]['bytes'] == report['binary']['bytes'] and
             omitted[0]['sha256'] == report['binary']['sha256'] and
             report['binary']['local_only'] is True and
             prefix + report['binary']['path'] not in by_path, 'explicit executable omission')
        test = next(row for row in report['commands'] if row['name'] == 'test')
        need(not by_path[prefix + test['stderr']['path']], 'no sanitizer diagnostics')
        records = [json.loads(line) for line in by_path[prefix + test['stdout']['path']].splitlines()]
        need(records == report['test_records'] and all(row.get('passed') is True for row in records),
             'actual stdout equals unaltered report records')
        need(records[-1] == {
            'suite': 'ogg-opus-timeline-host', 'passed': True, 'cases': 525,
            'semantic_negatives': 159, 'reset_positions': 403, 'fixture_runs': 10,
            'state_bytes': 512, 'physical_hardware': False, 'playback_trim_implemented': False,
        }, 'complete test inventory')
        for name, size, raw, pages in (('20ms', 706319, 528960, 15),
                                       ('120ms', 707097, 529920, 14)):
            fixtures = [row for row in records if row.get('fixture') == name]
            need(len(fixtures) == 5 and {row['split'] for row in fixtures} ==
                 {'whole', '4096', '257', '1', 'seeded'}, 'all original byte splits')
            need(len({row['digest'] for row in fixtures}) == 1 and all(
                row['bytes'] == size and row['raw_frames'] == raw and row['pages'] == pages and
                row['pre_skip'] == 312 and row['raw_end'] == 528312 for row in fixtures),
                'split invariant real-fixture metadata')
        build = next(row for row in report['commands'] if row['name'] == 'build')
        need({'-Werror', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'} <=
             set(build['argv']), 'actual compiler instrumentation')
        need({'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
              'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1'} <= set(test['argv']),
             'actual sanitizer/leak options')
        if campaign == '03':
            need(len(records) == 12 and records[-2] == {
                'reference': 'libopus', 'version': 'libopus 1.4',
                'duration_comparisons': 219, 'passed': True,
            } and '-l:libopus.so.0' in build['argv'], 'independent public reference duration calls')
            before = next(row for row in report['commands'] if row['name'] == 'libopus-sha256')
            after = next(row for row in report['commands'] if row['name'] == 'libopus-post-sha256')
            need(by_path[prefix + before['stdout']['path']] ==
                 by_path[prefix + after['stdout']['path']] and
                 report['libopus_binary'] == by_path[prefix + before['stdout']['path']].decode().strip(),
                 'unchanged reference binary identity')
        else:
            need(len(records) == 11, 'original pre-reference run stays distinct')
    print(json.dumps({'passed': True, 'logical_files': len(rows), 'physical_blobs': len(bodies),
                      'executables_omitted': len(manifest['local_only_executables']),
                      'metadata_only': True, 'playback_trim_implemented': False,
                      'current_header_matches_historical_revision':
                          sha((ROOT / ORIGINAL_HEADER).read_bytes()) == ORIGINAL_HEADER_SHA}))


if __name__ == '__main__':
    main()
