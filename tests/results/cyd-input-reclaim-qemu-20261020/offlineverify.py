"""Verify retained bytes and declared omission metadata; run no SDK/QEMU/device."""
import gzip
import hashlib
import json
import re
from pathlib import Path
BASE=Path(__file__).resolve().parent

def sha(data): return hashlib.sha256(data).hexdigest()
def safe(relative):
    path=(BASE/relative).resolve()
    assert path.is_relative_to(BASE) and path.is_file(),relative
    return path

def main():
    manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
    actual={p.relative_to(BASE).as_posix() for p in BASE.rglob('*') if p.is_file()}
    assert actual==set(manifest['files'])|{'manifest.json'}
    for name,row in manifest['files'].items():
        data=safe(name).read_bytes()
        assert len(data)==row['bytes'] and sha(data)==row['sha256'],name
    decoded={}
    def payload(row):
        assert row['status']=='stored'
        key=(row['archive_path'],row['storage_encoding'])
        if key not in decoded:
            data=safe(row['archive_path']).read_bytes()
            decoded[key]=gzip.decompress(data) if row['storage_encoding']=='gzip' else data
        data=decoded[key]
        assert len(data)==row['bytes'] and sha(data)==row['sha256']
        return data
    counts={'stored_mappings':0,'omitted_binaries':0,'bundles':0}
    for campaign_name,campaign in manifest['campaigns'].items():
        entries=campaign['entries']
        def entry(name): return entries[name.replace('\\','/')]
        for name,row in entries.items():
            if row['status']=='stored':payload(row);counts['stored_mappings']+=1
            else:
                assert row['status']=='omitted' and row['bytes']>=0 and len(row['sha256'])==64 and row['reason']
                counts['omitted_binaries']+=1
        report=json.loads(payload(entry('report.json')))
        assert sha(payload(entry('report.json')))==campaign['report_sha256']
        assert report['passed']==campaign['passed']
        for command in report['commands']:
            log_name=command['name']+'.log'
            assert sha(payload(entry(log_name)))==command['sha256'],(campaign_name,log_name)
        terminal=json.loads(payload(entry('terminal-observation.json')))
        assert terminal['terminal'] and terminal['exit_status']==campaign['terminal_status']
        if campaign_name!='final05':
            assert not campaign['passed'] and campaign['terminal_status']==1
            assert campaign['qualified_positive_cases']==campaign['qualified_control_detections']==0
        else:
            assert report['actual_cases']==5 and report['exact_semantic_controls']==4 and report['all_bound_inputs_current']
        for original in campaign['bundle_paths']:
            bundle=json.loads(payload(entry(original)));counts['bundles']+=1
            for group in ['frozen_input_sha256','artifact_sha256']:
                for name,digest in bundle[group].items():assert entry(name)['sha256']==digest,(campaign_name,name)
            for name,digest in bundle['runtime_sha256'].items():assert manifest['runtime_hashes'][name]['sha256']==digest
        if campaign_name=='final05':
            for variant,result in report['variants'].items():
                path='variants/'+variant+'/execution-bundle.json'
                assert sha(payload(entry(path)))==result['bundle_sha256'] and result['passed']
                log=payload(entry(variant+'-qemu.log')).decode(errors='replace').replace('\r\n','\n')
                assert not re.search(r'Guru Meditation|assert failed|panic.ed|abort\(\)|Backtrace:|watchdog.*triggered|stack smashing|CORRUPT HEAP',log,re.I)
                if variant=='canonical':
                    assert re.findall(r'^CYD_INPUT_RECLAIM_CASE id=(R\d)\b',log,re.M)==['R0','R1','R2','R3','R4']
                    assert len(re.findall(r'^CYD_INPUT_RECLAIM_COMPLETE cases=5 ',log,re.M))==1
                    assert 'CYD_INPUT_RECLAIM_FAILURE' not in log
                else:
                    assert re.findall(r'^CYD_INPUT_RECLAIM_FAILURE (.+)$',log,re.M)==[result['expected_failure']]
                    assert len(re.findall(r'^CYD_INPUT_RECLAIM_CONTROLLED_STOP$',log,re.M))==1
                    assert 'CYD_INPUT_RECLAIM_COMPLETE' not in log
    preflight=json.loads(safe('preflight/report.json').read_text(encoding='utf-8'))
    assert preflight['passed'] and len(preflight['cases'])==13 and not preflight['build_or_qemu_started']
    review=json.loads(safe('parent-review/review.json').read_text(encoding='utf-8'))
    assert review['passed'] and review['report_sha256']==manifest['campaigns']['final05']['report_sha256']
    final=manifest['campaigns']['final05']['entries']
    for name,row in review['variants'].items():
        assert row['pointer_words_independently_checked']
        artifact=final['variants/'+name+'/artifacts/cyd_input_reclaim_qemu.elf']
        assert artifact['status']=='omitted' and artifact['sha256']==row['elf_sha256']
    print('PASS retained archive hashes/decoded bytes/omission consistency:',counts,'; final5+4, historical detections0, preflight13')
if __name__=='__main__': main()
