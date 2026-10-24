"""Rebuild SDK identity and transient Ghidra recovery evidence without running a VM."""
import argparse
import copy
import gzip
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import audit,sha
from match_factory_sdk import classify
from factory_sdk_match_test import controls
from reverse.native_sdk_links import describe
from reverse.xref_delta import apply


def unpack(manifest,root):
    """Verify every compressed payload and keep all archive paths inside parity/."""
    files={}
    for row in manifest['files']:
        file=(root/row['file']).resolve();assert file.is_relative_to(root.resolve())
        packed=file.read_bytes();assert sha(packed)==row['gzip_sha256'];data=gzip.decompress(packed)
        assert sha(data)==row['sha256'] and len(data)==row['bytes'] and row['source'] not in files
        files[row['source']]=data
    return files


def recovery_contract(before,after,recovery,matches,integrity):
    """Require exact matched owners, complete decoded bodies and unchanged project bytes."""
    assert recovery['program_sha256']==matches['factory_elf_sha256']
    assert recovery['program_bytes_unchanged'] and not recovery['whole_image_completeness_proved']
    memory={r['name']:r['sha256'] for r in before['memory_blocks'] if r['initialized']}
    assert recovery['memory_before']==recovery['memory_after']==memory
    assert recovery['instruction_count_before']==before['instruction_count']
    assert recovery['instruction_count_after']==after['instruction_count']
    expected={r['name']:r for r in matches['functions']};observed={r['name']:r for r in recovery['functions']}
    assert len(expected)==len(observed)==3 and set(expected)==set(observed)
    functions={r['entry']:r for r in after['functions'] if r['space']=='ram'}
    for name,row in expected.items():
        actual=observed[name]
        for field in ('start','end','site','caller_site'):assert actual[field]==row[field]
        owner=actual['recovered_owner'];assert owner['entry']==row['start'] and owner['name']==name
        assert owner['ranges']==[[row['start'],hex(int(row['end'],0)-1)]]
        assert functions[row['start']]['name']==name
        assert functions[row['start']]['body_bytes']==row['linked_bytes']
        assert actual['decoded_instructions']==row['linked_instruction_starts']
    assert len(after['functions'])-len(before['functions'])==3
    assert recovery['functions_after']-recovery['functions_before']==3
    assert after['instruction_count']-before['instruction_count']==sum(r['decoded_instructions'] for r in observed.values())
    assert integrity['passed'] and integrity['file_count']==10
    assert len({integrity[k] for k in ('before_sha256','copy_before_sha256','source_after_sha256','copy_after_sha256')})==1
    return dict(passed=True,recovered_functions=3,program_bytes_unchanged=True,project_files_unchanged=True)


def analysis_controls(before,after,recovery,matches,integrity,text,elf,selected):
    """Reject a restored gap, wrong SDK name, altered bytes/bounds or saved-project change."""
    rejected=[]
    for case in ('missing-gp','wrong-sdk-owner','changed-program-memory','wrong-function-end','saved-project-changed'):
        a,r,i=copy.deepcopy((after,recovery,integrity))
        if case=='missing-gp':
            target=next(n for n,row in enumerate(a['gp_accesses']) if row['from']=='0x42058280');a['gp_accesses'].pop(target)
        elif case=='wrong-sdk-owner':next(f for f in a['functions'] if f['entry']=='0x420581b6')['name']='wrong_owner'
        elif case=='changed-program-memory':r['memory_after'][next(iter(r['memory_after']))]='00'*32
        elif case=='wrong-function-end':r['functions'][0]['end']=hex(int(r['functions'][0]['end'],0)+2)
        else:i['source_after_sha256']='00'*32
        try:
            if case=='missing-gp':audit(a,text,elf,selected,expected_gaps=())
            else:recovery_contract(before,a,r,matches,i)
        except (AssertionError,ValueError,KeyError):rejected.append(case)
        else:raise AssertionError('Invalid recovery accepted: '+case)
    return rejected


def verify(path,root,dependency_root,libraries,assembly,revision=None):
    """Replay actual library bodies, ancestor/delta graphs and native SDK symbol links."""
    proof=json.loads(path.read_text());assert proof['schema_version']==1 and proof['passed']
    assert not any(proof[k] for k in ('whole_image_completeness_proved','semantic_equivalence_proved','physical_hardware_tested'))
    files=unpack(proof,path.parent)
    if revision:
        from verify_photo_format_matrix_evidence import source_hashes
        actual=source_hashes(root,proof['source_pins'],revision)
    else:actual={name:sha((root/name).read_bytes()) for name in proof['source_pins']}
    assert actual==proof['source_pins']
    for name,digest in proof['source_pins'].items():assert sha(files['producer/'+name])==digest
    base_bytes=files['base/manifest.json'];assert sha(base_bytes)==proof['base']['sha256']
    base_path=(path.parent/proof['base']['file']).resolve();assert base_path.is_relative_to(path.parent.resolve())
    base_manifest=json.loads(base_bytes);assert json.loads(base_path.read_text())==base_manifest
    base_files=unpack(base_manifest,path.parent)
    before=json.loads(base_files['ghidra.json']);after=apply(before,json.loads(files['graph-delta.json']))
    elf=(dependency_root/'.build/small-tv-reverse/factory-analysis.elf').read_bytes();text=assembly.read_text()
    selected={r['address'] for r in json.loads(base_files['producer/Small_TV/src/symbol-map.json'])['functions']}
    old=audit(before,text,elf,selected);expected=json.loads(base_files['audit.json']);expected.pop('inputs_sha256')
    assert old==expected
    matches=classify(elf,libraries);captured=json.loads(files['sdk-matches.json']);pins=captured.pop('inputs_sha256')
    for name,digest in pins.items():
        relative=name.replace('\\','/').split('/small-tv-improvement-plan/',1)[-1]
        assert proof['source_pins'][relative]==digest
    assert matches==captured
    manifest=json.loads(files['sdk-manifest.json']);assert manifest['commit']==matches['sdk_wifi_commit']
    provenance=json.loads(files['idf-provenance.json'])
    assert provenance['idf_tag']=='v5.5.4' and provenance['idf_commit']=='735507283d5b2f9fb363a1901172dbd9e847945d'
    assert provenance['gitlink']=='160000 commit '+matches['sdk_wifi_commit']+'\tcomponents/esp_wifi/lib'
    assert {r['path'] for r in manifest['files']}=={'esp32c2/'+n for n in matches['libraries']}
    for row in manifest['files']:
        actual=matches['libraries'][Path(row['path']).name]
        assert actual['sha256']==row['sha256'] and actual['git_blob']==row['git_blob']
        assert (libraries/Path(row['path']).name).stat().st_size==row['bytes']
    result=audit(after,text,elf,selected,expected_gaps=());assert result==json.loads(files['after-audit.json'])
    assert result['gp_coverage_agrees'] and result['gp_memory_instructions']==396 and not result['database_gp_gaps']
    recovery=json.loads(files['recovery.json']);integrity=json.loads(files['project-integrity.json'])
    recovery_contract(before,after,recovery,matches,integrity)
    native=(root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()
    links=describe(native);assert links==json.loads(files['native-links.json']) and sha(native)==proof['native_elf_sha256']
    app=(root/'firmware/development/small-tv-esp32c2-reconstructed/app.bin').read_bytes()
    assert sha(app)==proof['native_app_sha256'] and app[176:208]==bytes.fromhex(proof['native_elf_sha256'])
    sdk_tests=controls(elf,libraries);captured=json.loads(files['sdk-controls.json'])
    assert captured.pop('producer_sha256')==proof['source_pins']['Small_TV/src/tests/factory_sdk_match_test.py']
    assert sdk_tests==captured
    rejected=analysis_controls(before,after,recovery,matches,integrity,text,elf,selected)
    assert rejected==proof['analysis_controls']
    return dict(passed=True,matched_sdk_functions=3,source_bytes=sum(r['source_bytes'] for r in matches['functions']),
        linked_bytes=sum(r['linked_bytes'] for r in matches['functions']),
        local_branches_checked=sdk_tests['local_branches_checked'],gp_coverage_agrees=True,
        recovered_functions=3,analysed_functions=len(after['functions']),
        rejected_controls=len(sdk_tests['rejected_controls'])+len(rejected),
        native_symbols_present=3,whole_image_completeness_proved=False)


def main():
    """Use only local frozen analysis/SDK inputs; never connect to H10 or physical hardware."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--sdk-libraries',type=Path,required=True)
    parser.add_argument('--assembly',type=Path,required=True)
    parser.add_argument('--source-revision')
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root,args.dependency_root,args.sdk_libraries,args.assembly,args.source_revision)))


if __name__=='__main__':main()
