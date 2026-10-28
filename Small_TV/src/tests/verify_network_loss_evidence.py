"""Replay controlled packet-loss before/after data without running QEMU."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

from network_clients_contract import verify_abi,validate as peers_validate
from network_loss_contract import validate,rejection_checks,STAGES
from verify_network_clients_evidence import code_reader
from verify_photo_format_matrix_evidence import source_hashes


def sha(data):
    """Check raw observations, producer snapshots and historical emulator sources."""
    return hashlib.sha256(data).hexdigest()


def verify(path,root,dependencies,revision=None):
    """Require every stage on both builds and preserve the four real before failures."""
    proof=json.loads(path.read_text());assert proof['schema_version']==1 and proof['passed']
    assert not any(proof[k] for k in ('network_lifecycle_complete','all_functionality_verified',
        'lcd_acceptance','rf_acceptance','hardware_tested'))
    blobs={}
    for row in proof['blobs']:
        file=(path.parent/row['file']).resolve();assert file.is_relative_to(path.parent.resolve())
        data=file.read_bytes();assert sha(data)==row['gzip_sha256']
        data=gzip.decompress(data);assert len(data)==row['bytes'] and sha(data)==row['sha256']
        assert row['sha256'] not in blobs;blobs[row['sha256']]=data
    files={}
    for row in proof['raw']:
        assert row['source'] not in files;files[row['source']]=blobs[row['sha256']]
    assert source_hashes(root,proof['source_pins'],revision)==proof['source_pins']
    for name,digest in proof['source_pins'].items():assert sha(files['producer/'+name])==digest
    abi=json.loads(files['abi/layout.json']);verify_abi(abi,files['abi/wire.o'],files['abi/wire.c'])
    assert abi['app_sha256']==proof['app_sha256'] and abi['elf_sha256']==proof['elf_sha256']
    read=code_reader(root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf',proof['elf_sha256'])
    coverage=set();controls=0
    for run in proof['runs']:
        report=json.loads(files[run['source']]);key=run['build'],report['stage']
        assert key not in coverage;coverage.add(key)
        assert report['app_sha256']==proof['app_sha256'] and report['elf_sha256']==proof['elf_sha256']
        assert report['qemu_sha256']==proof['builds'][run['build']]['sha256']
        assert report['wire']==abi['wire']
        assert report['before_control'] is (run['build']=='before' and report['stage'] in STAGES[3:])
        for name,address in {**report['entries'],'WIFI_EVENT':report['event_base_object']}.items():
            assert {s['st_value'] for s in read.symbols if s.name==name and s['st_value']}=={address}
        assert validate(report,read)==run['result']
        rejected=rejection_checks(report,read);assert rejected==run['rejected_controls'];controls+=len(rejected)
        for name,digest in report['inputs_sha256'].items():
            name=name.replace('\\','/')
            if '/Small_TV/src/tests/' in name:
                assert proof['source_pins']['Small_TV/src/tests/'+name.rsplit('/',1)[1]]==digest
    assert coverage=={(build,stage) for build in ('before','after') for stage in STAGES}
    for build in proof['builds'].values():
        for row in build['files'].values():
            data=files[row['source']];assert sha(data)==row['sha256']
            assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob']
    unit=json.loads(files['unit/report.json']);assert unit['passed'] and len(unit['cases'])==351
    assert unit['guard_page_truncations']==905 and unit['random_non_dhcp_packets']==10000
    assert next(row for row in unit['cases'] if row['case']=='exponential-backoff-and-jitter')['combinations']==14007
    for name,digest in unit['inputs_sha256'].items():
        relative=name.replace('\\','/').split('/small-tv-ap-clients/',1)[-1]
        if relative.startswith(('tools/','hw/')):
            assert sha(files['unit/source/'+relative])==digest
    factory=json.loads(files['factory/report.json'])
    assert factory['qemu_sha256']==proof['builds']['after']['sha256']
    factory_read=code_reader(dependencies/'.build/small-tv-reverse/factory-analysis.elf',factory['elf_sha256'])
    factory_base=int.from_bytes(factory_read(factory['event_base_object'],4),'little')
    peers_validate(factory,abi['wire'],factory_read,factory_base)
    legacy=json.loads(files['c3/report.json']);assert set(legacy)=={'default','modular'}
    for row in legacy.values():
        assert row['passed'] and all(row['checks'].values()) and row['duration_seconds']==60
        assert row['qemu_sha256']==proof['builds']['after']['sha256']
    return dict(passed=True,before_cases=7,after_recoveries=7,expected_before_failures=4,
        unsafe_controls_rejected=controls,protocol_cases=351,jitter_combinations=14007,
        network_lifecycle_complete=False)


def main():
    """Read committed observations and exact ELF data, without changing current state."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--source-revision',help='Read historical producer bytes from Git without resetting')
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root,args.dependency_root,args.source_revision)))


if __name__=='__main__':main()
