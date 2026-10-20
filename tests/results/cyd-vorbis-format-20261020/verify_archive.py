"""Offline, read-only archive verification. Never invokes SDK/QEMU/codec tools."""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path, PureWindowsPath
import re
import sys
sys.dont_write_bytecode = True

def sha(data): return hashlib.sha256(data).hexdigest()
def need(ok,message):
    if not ok: raise RuntimeError(message)
def norm(path): return str(path).replace('\\','/')

def verify(bundle):
    bundle = Path(bundle).resolve()
    m = json.loads((bundle/'manifest.json').read_text(encoding='utf-8-sig'))
    need(m['schema'] == 1,'Unknown manifest schema')
    raw,stored = {},{'manifest.json'}
    for original,row in m['files'].items():
        need(not original.startswith('/') and '..' not in original.split('/'),'Unsafe original path')
        if row['stored'] is None:
            need(row.get('omitted') and row['raw_bytes']>=0 and re.fullmatch('[0-9a-f]{64}',row['raw_sha256']),'Invalid omission')
            continue
        path = (bundle/row['stored']).resolve()
        need(path.is_relative_to(bundle) and row['stored'] not in stored,'Unsafe/duplicate stored path')
        stored.add(row['stored']); blob = path.read_bytes()
        need(len(blob) == row['stored_bytes'] and sha(blob) == row['stored_sha256'],'Stored hash/size mismatch: '+original)
        need(row['encoding'] in ('raw','gzip'),'Unknown encoding')
        data = gzip.decompress(blob) if row['encoding'] == 'gzip' else blob
        need(len(data) == row['raw_bytes'] and sha(data) == row['raw_sha256'],'Decoded hash/size mismatch: '+original)
        raw[original] = data
        if original.endswith('.py') or original.endswith('/fixture.h'): need(row['encoding'] == 'raw','Import/fixture must remain uncompressed')
    need({p.relative_to(bundle).as_posix() for p in bundle.rglob('*') if p.is_file()} == stored,'Stored file set differs from manifest')
    key = lambda role,name: m['roots'][role]+'/'+norm(name)
    data = lambda role,name: raw[key(role,name)]
    obj = lambda role,name: json.loads(data(role,name).decode('utf-8-sig'))
    identity = lambda role,name: m['files'][key(role,name)]['raw_sha256']
    acceptance,control = obj('acceptance','report.json'),obj('control','report.json')
    need(acceptance.get('passed') is True and acceptance.get('completed') is True and acceptance.get('format_acceptance_qualified') is True,'Acceptance not qualified')
    need(control.get('completed') is True and control.get('control_effective') is True and control.get('control') == 'old-guard' and control.get('format_acceptance_qualified') is False and control.get('passed') is False,'Control mislabeled/incomplete')
    helper = m['files'][key('acceptance','sources/helpers/windows_compile_command.py')]['stored']
    runner_path = bundle/m['files'][key('acceptance','sources/helpers/run.py')]['stored']
    need((bundle/helper).parent == runner_path.parent,'Frozen helper is not sibling to runner')
    sys.path.insert(0,str(runner_path.parent)); sys.modules.pop('windows_compile_command',None)
    spec = importlib.util.spec_from_file_location('frozen_cyd_format',runner_path)
    runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
    observed = {}
    for role,report in (('acceptance',acceptance),('control',control)):
        for row in report['inputs'].values(): need(identity(role,row['snapshot']) == row['sha256'],'Frozen input hash mismatch')
        for mapping in ('variant_sources','build_outputs'):
            for name,digest in report[mapping].items(): need(identity(role,name) == digest,'Report artifact hash mismatch: '+name)
        for path,digest in report['tools'].items(): need(m['external_omitted'][path]['raw_sha256'] == digest,'External tool pin mismatch')
        for command in report['commands']:
            need(command['state'] == 'complete' and command['exit_status'] == 0,'Nonterminal/nonzero command')
            for stream in ('stdout','stderr'): need(identity(role,command['name']+'.'+stream+'.log') == command[stream+'_sha256'],'Command log binding mismatch')
        context = report['setup_macro_context']; generated = context['generated_inputs']
        need(context['row'] in obj(role,'build/compile_commands.json'),'Macro row absent from actual compile database')
        need(len(generated) == 2,'Expected cflags/specs bindings')
        for path,row in generated.items():
            need(row['sha256_before'] == row['sha256_after'] == report['inputs'][path]['sha256'],'Generated compiler context changed')
        specs_path = next(path for path in generated if norm(path).endswith('/build/specs/picolibc.specs'))
        flags_path = next(path for path in generated if norm(path).endswith('/build/toolchain/cflags'))
        flags = data(role,report['inputs'][flags_path]['snapshot']).decode().splitlines()
        need(flags == ['-Wno-frame-address','-mlongcalls','-fno-builtin-memcpy','-fno-builtin-memset','-fno-builtin-bzero','"-specs='+norm(specs_path)+'"'],'Unexpected response content')
        original = context['original_argv']; need(original.count('-c') == original.count('-o') == 1,'Unexpected outer compile context')
        response = [arg for arg in original if arg.startswith('@')]
        need(len(response) == 1 and norm(response[0][1:]) == norm(flags_path),'Macro argv does not use bound cflags')
        stripped,skip = [],False
        for arg in original:
            if skip: skip=False; continue
            if arg == '-o': skip=True; continue
            if arg != '-c': stripped.append(arg)
        need(context['probe_argv'] == stripped+['-E','-dM'],'Macro probe changed original context')
        macros = data(role,'setup-macros.stdout.log').decode(errors='replace').replace('\r\n','\n')
        need(not re.search(r'^#define LIMIT_TO_64kHz\b',macros,re.M),'Optional rate cap active')
        for name in ('CONFIG_IDF_TARGET_ESP32','CONFIG_YORADIO_VORBIS_REPAIR'): need(re.search('^#define '+name+' 1$',macros,re.M),'Wrong actual setup macro context')
        log = data(role,'qemu.stdout.log').decode(errors='replace')+'\n'+data(role,'qemu.stderr.log').decode(errors='replace')
        observed[role] = runner.validate_log(log,'acceptance','old-guard' if role == 'control' else None,data(role,'sources/project/main/fixture.h').decode())
        need(observed[role] == report['observed'],'Observed protocol does not match report')
    need(observed['control']['exact_failure'] == 'legal_candidate_open_required','Wrong control failure')
    for role in ('baseline01','diagnostic01'):
        need(obj(role,'qualification.json')['state'] == 'NONPASS','Historical NONPASS lost')
        need(not obj(role,'report.json').get('format_acceptance_qualified',False),'Historical report falsely qualified')
        need(b'CYD_VORBIS_FORMAT_FAILURE vendor_high8192_metadata' in data(role,'qemu-command.stdout.log'),'Historical failure log absent')
    baseline,manual = obj('baseline02','report.json'),obj('baseline02','manual-qualification.json')
    need(baseline.get('passed') is False and baseline.get('completed') is False,'Original baseline02 NONPASS lost')
    need(manual['regression_reproduced'] is True and manual['format_acceptance_qualified'] is False and manual['passed'] is False,'Manual baseline mislabeled')
    need(manual['original_report_sha256'] == identity('baseline02','report.json'),'Original baseline02 report was rewritten')
    for row in baseline['inputs'].values(): need(identity('baseline02',row['snapshot']) == row['sha256'],'Baseline frozen input mismatch')
    for mapping in ('variant_sources','build_outputs'):
        for name,digest in baseline[mapping].items(): need(identity('baseline02',name) == digest,'Original baseline artifact mismatch')
    for name,digest in manual['outputs_sha256'].items(): need(identity('baseline02',name) == digest,'Manual target omission/output mismatch')
    need(identity('baseline02','manual-macro-context.json') == manual['response_context_sha256'],'Manual macro context changed')
    manual_context = obj('baseline02','manual-macro-context.json')
    for path,row in manual_context['response_inputs'].items(): need(identity('baseline02',row['snapshot']) == row['sha256'],'Manual response snapshot changed')
    need(manual_context['old_report_sha256'] == identity('baseline02','report.json'),'Manual context rewrote original report')
    for name,digest in manual['command_records_sha256'].items():
        need(identity('baseline02',name) == digest,'Manual command receipt changed')
        receipt = obj('baseline02',name); need(receipt['returncode'] == 0 and receipt['status'] == 'TERMINAL','Manual command not terminal0')
        for path,row in receipt['logs'].items(): need(identity('baseline02',PureWindowsPath(path).name) == row['sha256'],'Manual log binding mismatch')
    blog = data('baseline02','manual-qemu-command.stdout.log').decode(errors='replace')+'\n'+data('baseline02','manual-qemu-command.stderr.log').decode(errors='replace')
    observed['baseline02'] = runner.validate_log(blog,'baseline',None,data('baseline02','sources/project/main/fixture.h').decode())
    need(observed['baseline02'] == manual['observed'],'Manual baseline protocol mismatch')
    setup = 'variant/vorbis_repair/setup.c'; old = data('baseline02',setup)
    newline = b'\r\n' if b'\r\n' in old else b'\n'
    removed = b'#else\n  if(vi->rate<64000 && ci->blocksizes[1]>4096)goto err_out;\n'.replace(b'\n',newline)
    need(old.count(removed) == 1 and data('acceptance',setup) == old.replace(removed,b'',1),'Acceptance differs beyond the intended two lines')
    need(data('control',setup) == old,'Control does not restore baseline bytes')
    variants = [{name[len(m['roots'][role]+'/variant/'):]:row['raw_sha256'] for name,row in m['files'].items() if name.startswith(m['roots'][role]+'/variant/')} for role in ('baseline02','acceptance','control')]
    need(set(variants[0]) == set(variants[1]) == set(variants[2]),'Variant file set changed')
    for name in variants[0]:
        if name != 'vorbis_repair/setup.c': need(variants[0][name] == variants[1][name] == variants[2][name],'Unrelated variant source changed')
    combined = json.loads(raw['.build/cyd-vorbis-format-root-combined-qualification-01.json'])
    need(combined['state'] == 'NARROW_CYD_RAW8192_FIX_QUALIFIED' and combined['radio_integration'] is False and combined['C3_qualified'] is False,'Combined scope mislabeled')
    for role in ('acceptance','control'):
        need(combined[role+'_report_sha256'] == identity(role,'report.json') and combined[role+'_root_check_sha256'] == identity(role,'root-qualification.json'),'Combined root receipt mismatch')
    need(combined['baseline_manual_qualification_sha256'] == identity('baseline02','manual-qualification.json'),'Combined baseline receipt mismatch')
    need(combined['canonical_setup_sha256'] == identity('acceptance',setup),'Combined source pin mismatch')
    host_key = '.build/cyd-vorbis-format-host-canonical-02.json'; host = json.loads(raw[host_key])
    need(host['status'] == 'TERMINAL' and host['returncode'] == 0,'Canonical host02 receipt not terminal0')
    need(m['files']['.build/cyd-vorbis-format-command-01.py']['raw_sha256'] == host['runner_sha256'],'Host02 capture utility differs')
    promotion = json.loads(raw['.build/cyd-vorbis-format-source-promotion-02.json'])
    staged = json.loads(raw['.build/cyd-vorbis-format-index-check-02.json'])
    test_name = 'tests/test-cyd-vorbis-format-runner.py'
    need(m['files'][test_name]['raw_sha256'] == promotion['files'][test_name] == staged['files'][test_name], 'Host02 test source differs from pre-run promotion or post-run raw index check')
    for path,row in host['logs'].items(): need(m['files']['.build/'+PureWindowsPath(path).name]['raw_sha256'] == row['sha256'],'Host02 log binding mismatch')
    ref = obj('reference','reference/report.json')
    check = json.loads(raw['.build/cyd-vorbis-format-root-reference-check-01.json'])
    need(ref['host_reference_complete'] is True and check['host_reference_verified'] is True and check['reference_report_sha256'] == identity('reference','reference/report.json'),'Reference proof incomplete')
    need(check['independent_ogg_crc_and_edit_scope'] is True and check['per_decoder_rate_variant_pcm_equal'] is True and check['cross_decoder_exact_claimed'] is False,'Reference scope mislabeled')
    for command in ref['commands']:
        need(command['exit'] == 0,'Reference command nonzero')
        for stream in ('stdout','stderr'): need(identity('reference','reference/'+command['name']+'.'+stream+'.log') == command[stream+'_sha256'],'Reference command log mismatch')
    for rate,row in ref['variants'].items():
        need(identity('reference','reference/long8192-rate'+rate+'.ogg') == row['sha256'],'Reference Ogg mismatch')
        for decoder,pcm in row['decode'].items():
            blob = data('reference','reference/long8192-rate'+rate+'-'+decoder+'.s16le')
            need(len(blob) == pcm['bytes'] and sha(blob) == pcm['sha256'] and any(blob),'Reference PCM mismatch')
    for decoder in ('vorbis','libvorbis'):
        need(len({ref['variants'][rate]['decode'][decoder]['sha256'] for rate in ref['variants']}) == 1,'Rate-only PCM invariance lost')
    return dict(verified=True,observed=observed,physical_qualified=False,production_radio_qualified=False)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('bundle',type=Path)
    print(json.dumps(verify(p.parse_args().bundle),indent=2))
