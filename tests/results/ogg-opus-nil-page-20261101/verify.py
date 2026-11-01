"""Check original host evidence as data; never execute archived code or tools."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parents[2]
HEADER = 'idf/components/native_stream/include/ogg_opus_timeline.h'


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def verify(require_current=False):
    manifest = json.loads((FOLDER / 'manifest.json').read_bytes())
    need(manifest['metadata_only'] and not manifest['playback_trim_implemented'] and
         not manifest['native_mcu_executed'] and not manifest['physical_hardware'], 'honest qualification scope')
    pin = manifest['archive']
    archive_path = FOLDER / pin['path']
    need(archive_path.name == 'captures.zip' and archive_path.parent == FOLDER and
         archive_path.stat().st_size == pin['bytes'] and sha(archive_path.read_bytes()) == pin['sha256'], 'exact archive')
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == manifest['physical_blobs'], 'unique physical blob inventory')
        physical = {}
        for name in names:
            body = archive.read(name)
            need(name == 'blobs/' + sha(body) and not body.startswith(b'\x7fELF'), 'complete public bytes, no executable')
            physical[name] = body
    files = {}
    for row in manifest['files']:
        path = PurePosixPath(row['path'])
        need(not path.is_absolute() and '..' not in path.parts and path.as_posix() == row['path'] and
             row['path'] not in files, 'unique contained logical path')
        body = physical[row['blob']]
        need(len(body) == row['bytes'] and sha(body) == row['sha256'], 'every logical size/hash')
        files[row['path']] = body
    need(len(files) == manifest['logical_files'] and
         set(physical) == {row['blob'] for row in manifest['files']}, 'complete manifests')
    omitted = {row['path']: row for row in manifest['executable_bytes_omitted']}
    need(len(omitted) == 5 and all(path not in files and row['original_retained_locally'] and
         row['byte_payload_published'] is False for path, row in omitted.items()), 'explicit local executable omissions')
    reports = {}
    for label, pin in manifest['campaigns'].items():
        prefix = label + '/'
        body = files[prefix + 'report.json']
        need(sha(body) == pin['original_report_sha256'], 'original report bytes')
        report = json.loads(body)
        reports[label] = report
        need(report['passed'] == pin['original_passed'] and report['state'] == pin['original_state'] and
             report['all_source_bindings_unchanged'], 'unchanged original outcomes and source bindings')
        for source in report['sources']:
            frozen = files[prefix + source['snapshot']]
            need(sha(frozen) == source['sha256'] and len(frozen) == source['bytes'], 'all frozen sources')
        for command in report['commands']:
            need(command['state'] == 'complete' and command['pid'] > 0 and not command.get('timed_out'), 'actual terminal native command')
            for key in ('stdout', 'stderr'):
                stream = command[key]
                raw = files[prefix + stream['path']]
                need(sha(raw) == stream['sha256'] and len(raw) == stream['bytes'], 'all original command logs')
            need(command['exit_status'] == (1 if label == 'baseline01' and command['name'] == 'test' else 0), 'actual native terminal status')
        command_names = [row['name'] for row in report['commands']]
        need(len(set(command_names)) == len(command_names) and 'build' in command_names and
             'test' in command_names, 'unique actual build and test commands')
        binary = report['binary']
        omission = omitted[prefix + binary['path']]
        need(omission['sha256'] == binary['sha256'] and omission['bytes'] == binary['bytes'] and binary['local_only'], 'original executable identity without byte claim')
        rows = [json.loads(line) for line in files[prefix + 'test.stdout.log'].decode().splitlines()]
        need(rows == report['test_records'] and not files[prefix + 'test.stderr.log'], 'original complete native transcript and no sanitizer diagnostic')
        summary = rows[-1]
        if label != 'regression04':
            need(len(rows) == 141 and summary['cases'] == 24 and summary['negative_cases'] == 4 and
                 summary['schedules'] == 140 and summary['state_bytes'] == 512, 'complete nil differential inventory')
            valid = [row for row in rows[:-1] if 'case' in row]
            negatives = [row for row in rows[:-1] if 'negative' in row]
            need(len(valid) == 120 and len(negatives) == 20 and
                 {(row['placement'], row['nil_continued'], row['nil_count'], row['tail'], row['schedule']) for row in valid} ==
                 {(p, c, n, t, s) for p in range(3) for c in range(2) for n in (1, 2) for t in (0, 7) for s in range(5)}, 'every valid matrix case actually observed')
            need(all(row['libogg_packets'] == 1 and row['libogg_pages'] == 4 + row['nil_count'] for row in valid), 'real reference reconstructs every complete packet')
            need(all(row['expected_status'] == 2 and row['passed'] == (row['observer_status'] == 2)
                     for row in valid), 'valid stream statuses independently interpreted')
            need(all(row['libogg_packets'] == 0 and row['libogg_holes'] == 1 and
                     row['libogg_sync_errors'] == int(row['negative'] == 2) for row in negatives), 'real reference rejects lost/corrupt pieces')
            need({(row['negative'], row['nil_continued'], row['schedule']) for row in negatives} ==
                 {(n, c, s) for n in (1, 2) for c in range(2) for s in range(5)}, 'complete negative schedule matrix')
            need(all(row['expected_status'] == (-3 if row['negative'] == 1 else -1) and
                     row['passed'] == (row['observer_status'] == row['expected_status']) for row in negatives), 'negative statuses independently interpreted')
            mismatches = sum(not row['passed'] for row in rows[:-1])
            need(mismatches == summary['mismatches'] == (65 if label == 'baseline01' else 0), 'independently recounted mismatch inventory')
            need(sum(not row['passed'] for row in valid) == (60 if label == 'baseline01' else 0), 'confirmed original valid-stream rejection')
        else:
            need(summary['passed'] and summary['cases'] == 525 and summary['semantic_negatives'] == 159 and
                 summary['reset_positions'] == 403 and summary['fixture_runs'] == 10 and
                 rows[-2]['duration_comparisons'] == 219, 'unchanged full timeline/fixtures/libopus regression')
    need(not reports['baseline01']['passed'] and reports['baseline01']['state'] == 'nonpass' and
         reports['reader-failure02']['passed'] and reports['reader-failure02']['state'] == 'nonpass' and
         reports['reader-failure02']['failure']['type'] == 'TypeError' and
         reports['authoritative03']['passed'] and reports['regression04']['passed'] and
         reports['authoritative05']['passed'], 'preserved contradictory failed-reader record distinct from fresh successes')
    old = files['baseline01/sources/' + HEADER]
    new = files['authoritative05/sources/' + HEADER]
    need(sha(old) == manifest['baseline_header_sha256'] and sha(new) == manifest['fixed_header_sha256'] and old != new, 'original and fixed header identities')
    before = b'        if (seq != s->next_sequence || continued != s->packet_open)\n'
    after = b'''        /* A nil page has no first segment for the continuation bit to
         * describe. Preserve the previous packet's state across it; RFC 7845
         * section 3 compares the previous/next pages with packet data.
         * Sequence checking still includes every page, including nil pages.
         */
        if (seq != s->next_sequence ||
            (h[26] && continued != s->packet_open))
'''
    old_normal = old.replace(b'\r\n', b'\n')
    need(old_normal.count(before) == 1 and old_normal.replace(before, after) == new.replace(b'\r\n', b'\n'), 'only targeted nil continuation guard/comment changes')
    need(files['reader-failure02/sources/' + HEADER] == new == files['regression04/sources/' + HEADER] ==
         files['authoritative03/sources/' + HEADER], 'same fixed observer in all successes and regression')
    if require_current:
        for row in reports['authoritative05']['sources']:
            need(sha((ROOT / row['path']).read_bytes()) == row['sha256'], 'explicit current source binding')
    return dict(passed=True, logical_files=len(files), physical_blobs=len(physical),
                original_valid_rejections=60, final_schedules=140, regression_cases=525,
                current_sources_compared=require_current, archived_code_executed=False,
                omitted_executable_bytes_read=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-current', action='store_true')
    print(json.dumps(verify(parser.parse_args().require_current)))
