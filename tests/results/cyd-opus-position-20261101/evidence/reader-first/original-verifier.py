"""Verify preserved public comparison evidence; execute no archived/native code.

Full PCM/hex streams and executable images are omitted. This reader checks their
recorded identities and the original process/result witnesses; it does not claim
to recompute sample errors without those local payloads.
"""
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import math

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parents[2]


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def valid_metrics(row, raw_frames, packets):
    need(row['reference'].startswith('libopus ') and row['packets'] == packets and
         row['raw_frames'] == raw_frames and row['logical_frames'] == 528000 and
         row['channels'] == 2 and row['preskip'] == 312 and row['eos_granule'] == 528312,
         'all original packets and actual complete raw/logical span')
    need(row['candidate_windows'] == raw_frames-528000+1 and row['samples_per_candidate'] == 1056000 and
         row['best_offset'] == 312 and row['best_ties'] == 1 and row['second_offset'] != 312 and
         row['second_squared_error'] > row['best_squared_error'] >= 0,
         'exhaustive unique complete-length sample-position observation')
    need(row['unique_sample_position_observed'] is True and row['numeric_conformance_claim'] is False,
         'observed alignment is distinct from numeric conformance')
    need(0 <= row['aligned_exact_samples'] <= row['aligned_within1_samples'] <= 1056000 and
         0 <= row['aligned_max_abs'] <= 65535 and row['raw_same_position_squared_error'] >= row['best_squared_error'],
         'complete aligned sample/error accounting')
    need(math.isclose(row['aligned_rmse'], math.sqrt(row['best_squared_error']/1056000), rel_tol=1e-10, abs_tol=1e-12),
         'RMSE agrees with integer squared error and full sample count')


def verify():
    manifest = json.loads((FOLDER / 'manifest.json').read_bytes())
    files = {}
    for row in manifest['files']:
        relative = PurePosixPath(row['path'])
        need(relative.as_posix() == row['path'] and not relative.is_absolute() and '..' not in relative.parts and
             ':' not in row['path'] and '\\' not in row['path'], 'contained canonical publication path')
        body = (FOLDER / row['path']).read_bytes()
        need(row['path'] not in files and sha(body) == row['sha256'] and len(body) == row['bytes'], 'every original published byte')
        need(not body.startswith(b'\x7fELF') and relative.suffix.lower() not in ('.pcm', '.bin', '.elf'), 'no local payload copy published')
        files[row['path']] = body
    need(manifest['logical_files'] == len(files) and manifest['metadata_only'] is False and
         manifest['production_trim_implemented'] is False and manifest['numeric_conformance_claim'] is False,
         'precise checkpoint scope')
    actual = {p.relative_to(FOLDER).as_posix() for p in FOLDER.rglob('*') if p.is_file() and p.name != 'manifest.json'}
    need(actual == set(files), 'no unmanifested public payload')
    for canonical, pin in manifest['canonical_sources'].items():
        body = (ROOT / canonical).read_bytes()
        need(sha(body) == pin['sha256'] and len(body) == pin['bytes'], 'current canonical source identity')
    omitted = {row['path']: row for row in manifest['omitted_local_payloads']}
    need(len(omitted) == len(manifest['omitted_local_payloads']) and all(row['original_retained_locally'] and
         row['byte_payload_published'] is False and row['bytes'] > 0 and re.fullmatch(r'[0-9a-f]{64}', row['sha256'])
         for row in omitted.values()), 'explicit whole-payload omission identities')
    report = json.loads(files['evidence/oracle/report.json'])
    native = json.loads(files['evidence/native/report.json'])
    failed_native = json.loads(files['evidence/native-failed/report.json'])
    need(not failed_native['passed'] and not failed_native['completed'] and failed_native['target_executed'] and
         failed_native['failure'] == 'no native runtime fault', 'original actual watchdog campaign stays nonpassing')
    inserted = (b'            // Diagnostic UART output is much slower than normal PCM delivery.\n'
                b'            // Give IDLE1 time after each observed frame without touching codec\n'
                b'            // state or weakening the real watchdog configuration.\n'
                b'            vTaskDelay(1);\n')
    old_source = files['evidence/native-failed/project/main/main.c']
    new_source = files['evidence/native/project/main/main.c']
    need(new_source.count(inserted) == 1 and new_source.replace(inserted, b'') == old_source and
         files['evidence/native-failed/sources/controller.py'] == files['evidence/native/sources/controller.py'],
         'exact diagnostic-only observer scheduling change, native controller unchanged')
    for prefix in ('evidence/native/','evidence/native-failed/'):
        config = files[prefix+'sdkconfig'].decode()
        for setting in ('CONFIG_ESP_TASK_WDT_EN=y','CONFIG_ESP_TASK_WDT_INIT=y',
                        'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0=y','CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1=y'):
            need(re.search(r'^'+re.escape(setting)+r'$', config, re.M), 'real original idle watchdog settings preserved')
    failed_child = json.loads(files['evidence/native-failed/sdk-child.json'].decode('utf-8-sig'))
    need(failed_child['pid'] > 0 and failed_child['exit_status'] == 0, 'failed original native gate followed successful SDK build')
    need(report['passed'] and report['completed'] and report['all_source_bindings_unchanged'] and
         not report['numeric_conformance_claim'] and not report['production_trim_implemented'], 'original authoritative reference run')
    need(native['passed'] and native['completed'] and native['all_bound_inputs_current'] and native['target_executed'] and
         not native['production_firmware'] and not native['physical_device'] and not native['private_abi_used'], 'original public-vendor target run')
    need(report['native_report']['sha256'] == sha(files['evidence/native/report.json']) and
         report['native_measurements'] == native['measurements'], 'reference run is bound to this exact native PCM capture')
    for row in native['commands']:
        need(row['state'] == 'complete' and row['pid'] > 0 and row['exit_status'] == 0, 'actual native command terminal zero')
        for stream in ('stdout', 'stderr'):
            name = 'evidence/native/'+row['name']+'.'+stream+'.log'
            if name in files:
                need(sha(files[name]) == row[stream+'_sha256'], 'original native command log identity')
            else:
                need(name in omitted and omitted[name]['sha256'] == row[stream+'_sha256'], 'explicit original raw-log omission identity')
    need([row['name'] for row in native['commands']] == ['vendor-head','vendor-clean','sdk-head','sdk-clean','build','symbols','merge','qemu'],
         'complete original target command inventory')
    child = json.loads(files['evidence/native/sdk-child.json'].decode('utf-8-sig'))
    need(child['pid'] > 0 and child['exit_status'] == 0, 'actual SDK driver child terminal zero')
    for row in report['commands']:
        need(row['state'] == 'complete' and row['pid'] > 0 and row['exit_status'] == 0 and not row.get('timed_out'), 'actual public reference command terminal zero')
        for stream in ('stdout', 'stderr'):
            pin = row[stream]
            body = files['evidence/oracle/'+pin['path']]
            need(sha(body) == pin['sha256'] and len(body) == pin['bytes'], 'original host command log identity')
    need(report['libopus_identity'] == files['evidence/oracle/libopus-sha256.stdout.log'].decode().strip() ==
         files['evidence/oracle/libopus-post-sha256.stdout.log'].decode().strip(), 'unchanged public reference library')
    controls = 0
    for name, raw_frames, count in (('F20',528960,551),('F120',529920,92)):
        fixture = report['fixtures'][name]
        encoded = (ROOT / fixture['encoded']['path']).read_bytes()
        need(sha(encoded) == fixture['encoded']['sha256'] and len(encoded) == fixture['encoded']['bytes'],
             'complete current canonical encoded fixture identity')
        measured = json.loads(files['evidence/oracle/'+name+'-reference.stdout.log'])
        need(measured == fixture['comparison'], 'original independent comparison stdout and report agree')
        valid_metrics(measured, raw_frames, count)
        need(fixture['vendor_raw']['sha256'] == native['measurements']['cases'][name]['sha256'] and
             fixture['vendor_raw']['bytes'] == raw_frames*4 and fixture['reference_playback']['bytes'] == 2112000 and
             fixture['reference_raw']['bytes'] == raw_frames*4, 'full native/reference PCM extent bindings')
        for key in ('vendor_raw','reference_raw','reference_playback','packet_transport'):
            pin = fixture[key]
            local = omitted['evidence/oracle/'+pin['path']]
            need(local['sha256'] == pin['sha256'] and local['bytes'] == pin['bytes'], 'omitted full output retains exact identity')
        alterations = [dict(best_offset=313), dict(best_ties=2), dict(candidate_windows=1),
                       dict(samples_per_candidate=1024), dict(packets=count-1), dict(numeric_conformance_claim=True),
                       dict(second_squared_error=measured['best_squared_error'])]
        for change in alterations:
            candidate = copy.deepcopy(measured)
            candidate.update(change)
            try:
                valid_metrics(candidate, raw_frames, count)
            except ValueError:
                controls += 1
            else:
                raise ValueError('contradictory alignment witness accepted')
    need(controls == 14, 'all contradictory position witnesses rejected')
    print(json.dumps(dict(passed=True, published_files=len(files), omitted_local_payloads=len(omitted),
                          compared_complete_fixtures=2, rejected_witness_controls=controls,
                          executes_archived_or_native_code=False, omitted_pcm_errors_recomputed=False,
                          production_trim_implemented=False, numeric_conformance_claim=False)))


if __name__ == '__main__':
    verify()
